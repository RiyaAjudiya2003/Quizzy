import mysql.connector

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="quizzy"

)
cursor=con.cursor(buffered=True)

print(con)