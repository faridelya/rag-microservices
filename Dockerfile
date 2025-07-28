FROM python:3.13-slim

# Install uv using the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Sync dependencies from pyproject.toml + uv.lock
RUN uv sync --frozen   
#--no-cache

# Copy wait script to wait for MSSQL/Redis
COPY ./wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Run migrations before starting FastAPI app
CMD ["/wait-for-it.sh", "mssql-server:1433", "--", "bash", "-c", "\
    uv venv && \
    . .venv/bin/activate && \
    alembic upgrade head && \
    .venv/bin/fastapi run app/main.py --port 80 --host 0.0.0.0"]
