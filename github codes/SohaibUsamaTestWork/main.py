from fastapi import FastAPI
import mysql.connector
from pydantic import BaseModel
from typing import List
app = FastAPI()

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="",
  database="SohaibUsamaPractice"
)
mycursor = mydb.cursor()
def createTableFunction(tableName):
    mycursor.execute(f"CREATE TABLE {tableName} (name VARCHAR(255), phone VARCHAR(255))")

@app.get('/createtable/{tableName}')
def createtable(tableName):
    print(tableName)
    createTableFunction(tableName)
    return tableName

class CreateTableModel(BaseModel):
    tableName: str

@app.post('/createtable')
def createtable(data:CreateTableModel):
    print(data.tableName)
    createTableFunction(data.tableName)
    return data.tableName

def insertData(tableName, name, phoneNumber):
    sql = f"INSERT INTO {tableName} (name, phone) VALUES (%s, %s)"
    val = (name, phoneNumber)
    mycursor.execute(sql, val)
    mydb.commit()
class CreateCustomerModel(BaseModel):
    tableName: str
    userName: List
    phone: List

@app.post('/createuser')
def createuser(data:CreateCustomerModel):
    for i, item in enumerate(data.userName):
        insertData(data.tableName, item, data.phone[i])
    return 'Success'


# print(helloworldfunction(5, 2))

# tableName = 'UsamaKaTable'
# dataSet = [
#     ("Abdullah", "123456789"),
#     ("Waqar", "0312165"),
#     ("Sohaib", "0654654"),
#     ("Rayyan", "abcd"),
# ]


# createTable(tableName)
# for data in dataSet:
#     insertData(tableName, data[0], data[1])