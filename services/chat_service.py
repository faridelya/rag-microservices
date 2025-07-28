from db_models import models
from fastapi import HTTPException
from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from pydantic import UUID4
from langchain.schema import BaseChatMessageHistory
from langchain_core.messages import get_buffer_string
from langchain_core.prompts import format_document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores.azuresearch import AzureSearch
from typing import Any
from langchain_core.runnables import RunnableLambda
from operator import itemgetter
from ai.gen_models import (openai_gpt_model1, openai_gpt_model2)
import json
import re
from cachetools import TTLCache
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


cache = TTLCache(maxsize=1000, ttl=60)
openai_gpt_llm_model1 = openai_gpt_model1()
openai_gpt_llm_model2 = openai_gpt_model2()


# ------------------ save Q&A in MSSQL db -----------------
def save_conversation_indb(
        chat_id,
        message,
        message_time,
        response,
        db: Session):
    # save input output for UI
    new_message = models.Messages(
        chat_id=chat_id,
        question=message,
        message_time=message_time,
        answer=response,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

# ----------- END -------------------------------------------


# -------------- Extrat follow up question from response ----
def extract_and_remove_follow_up_questions(text):
    # Adjusted regular expression pattern to find follow-up questions with
    # specific starting points
    pattern = re.compile(r"(Q\d+):\s*(.*?[\?؟.;])", re.IGNORECASE | re.DOTALL)

    # Search for the pattern and extract the follow-up questions
    follow_up_questions = pattern.findall(text)

    if follow_up_questions:
        follow_up_questions = [
            question.strip() for number,
            question in follow_up_questions]
        # Remove the follow-up questions section from the original text
        cleaned_text = pattern.sub('', text).strip()
        return cleaned_text, follow_up_questions
    else:
        # Return the original text and an empty list if no follow-up questions
        # are found
        return text.strip(), []

# ---------------- END ---------------------------------------


# ----------- RAG CHAIN for Indexes----------------------

def rag_chain_standalone_reprase_ques_prompt() -> PromptTemplate:

    _template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, REPHRASE in {language} language.


    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)
    return CONDENSE_QUESTION_PROMPT


def rag_chain_question_doc_prompt() -> ChatPromptTemplate:

    prompt = ChatPromptTemplate.from_messages([(
        "system", """Use the following pieces of context delimited by ------ to answer the user's question in the same language the question is asked.
    If you don't know the answer, just say that 'Sorry, I don't know you may ask another question. in the same language the question is asked, don't try to make up an answer.
    Note: Do not confuse in language selection for response. Please answer the user's question comprehensively in the same language it is asked and do not respond in Spanish until the original language of the user's question is determined.
    ------
    {context}
    ------
        """), ("human", """
    FOLLOW THE CRITICAL INSTRUCTON:
    1. ALWAYS Answer the user's current question in detail, in same language the question is asked.
    2. ALWAYS SUGGEST 3 FOLLOW-UP QUESTIONS FROM the context.
    3. ALWAYS FORMAT THE FOLLOW-UP QUESTION BY FOLLOWING THE BELOW FORMAT.

    4:FORMAT FOR FOLLOW-UP QUESTIONS that start with Q1:, Q2:, Q3:

        Q1: First follow-up question?
        Q2: Second follow-up question?
        Q3: Third follow-up question?

    5. ALWAYS MAKE ANSWER DECISION 95% ON BELOW PIECES OF CONTEXT.
    6: Answer the Question in detail and in the same language the question is asked


    ###{question}###

    Note: Please adhere strictly to the instructions to ensure clarity and conciseness in the response, The answer must be in {language}..
""")])
    return prompt


def complete_chain():
    condense_question_prompt = rag_chain_standalone_reprase_ques_prompt()
    ANSWER_PROMPT = rag_chain_question_doc_prompt()

    _inputs = RunnableParallel(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda x: get_buffer_string(x["chat_history"])
        )
        | condense_question_prompt
        | openai_gpt_llm_model1
        | StrOutputParser(),
    )
    return ANSWER_PROMPT, _inputs


ANSWER_PROMPT, _inputs = complete_chain()


async def generate_customer_response(
    sqlchat_history: BaseChatMessageHistory,  # sqldb chathistory instance
    # limited number of chathistory messages
    limit_histmemory: BaseChatMessageHistory,
    prompt: PromptTemplate,
    retriever: AzureSearch,
    chat_id: UUID4,
    message: str,
    message_time: str,
    db: Session,
    customer_id: str
): #-> AsyncGenerator[str, None]:

    try:
        # print('incoming')
        def retrieve_loaction_based_data(
                rep_quest: Any,
                acs=retriever):
            res = acs.similarity_search(
                query=rep_quest,
                k=4,
                search_type="hybrid"
                )
            return res

        DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(
            template="{page_content}")

        def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT,
                               document_separator="\n\n"):
            reference = [i.metadata['source'] for i in docs]
            cache[chat_id] = reference[:1]
            print(f"Current cache state: {list(cache.items())}")
            doc_strings = [
                format_document(
                    doc, document_prompt) for doc in docs]
            return document_separator.join(doc_strings)

        prompt_ = ChatPromptTemplate.from_template(
            "Indentify and return only the langauge name of the given sentence:\n{topic}")
        chain = prompt_ | openai_gpt_llm_model2
        language = chain.invoke({"topic": prompt})
        lang_dic = {"langauge": language.content}

        _context = {
            "context": itemgetter("standalone_question") | RunnableLambda(retrieve_loaction_based_data) | _combine_documents,
            "question": lambda x: x["standalone_question"],
            # lambda x: Lang(detect(x["standalone_question"])).name,
            "language": lambda x: lang_dic
        }

        conversational_qa_chain = _inputs | _context | ANSWER_PROMPT | openai_gpt_llm_model2

        response = conversational_qa_chain.invoke(
            {"question": prompt, "chat_history": limit_histmemory, "language": language.content})
        reference = cache[chat_id]
        cache.pop(chat_id)  # Remove it if necessary

        # save history in langchain MSSQL db
        sqlchat_history.add_user_message(message=message)
        sqlchat_history.add_ai_message(message=response)
        answer_text, followup_question = extract_and_remove_follow_up_questions(
            response.content)

        for_db_save_response = json.dumps(
            {"sources": reference, "answer": answer_text, "followUpQuestions": followup_question})
        # save conversation in PostgresSQL db
        save_conversation_indb(
            chat_id,
            message,
            message_time,
            for_db_save_response,
            db)
        # print("final response", response)
        return {"answer": answer_text, "Follow_upquestion":followup_question }

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Internal Server Error: {str(e)}")

# ---------- RAG END ------------------
