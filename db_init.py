import mysql.connector

dataBase = mysql.connector.connect(
  host = 'localhost',
  user = 'root', # change username with your DB username (usually root)
  passwd = 'root' # change password with your DB password
) 

cursorObject = dataBase.cursor()

cursorObject.execute("CREATE DATABASE canteen") # change dbName to your database name

print("Database Creation Successful")