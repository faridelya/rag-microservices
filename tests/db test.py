import pymssql


conn = pymssql.connect(
    server="localhost",
    port=1433,
    user="sa",
    password="yourStrong)_1_(Password",
    database="master"
)

