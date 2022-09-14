import sys
import asyncio
import datetime
from time import sleep
from bs4 import BeautifulSoup
import sqlite3
import http.client, urllib
sys.path.append("./classcharts")
import classcharts


### Settings ###
ClassChartsCode='ENTER YOUR CODE'
## Date, Month, Year ##F
## 1-9 then double digits ##
DOB=[1, 1, 1970]


## Pushover Notif ##
APIKEY='YOUR API KEY'
USERID='YOUR USER ID'


## Database ##
def connect():
    con=sqlite3.connect("cc.db")
    cur = con.cursor()
    return [cur, con]


## CC ##
async def main():
    while True:
        sc = classcharts.StudentClient(ClassChartsCode, datetime.datetime(year=DOB[2], month=DOB[1], day=DOB[0]))
        await getActivity(sc)
        await getHomework(sc)
        await sc.logout()
        sleep(30)

### Pushover notification ###

def notification(title,message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": APIKEY,
        "user": USERID,
        "message": message,
        "title": title,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

## Functions ##

async def getActivity(sc):
    db = connect()
    array=(await sc.activity())
    for a in array:
        statement = f'SELECT * from activites WHERE id={a.id}'
        db[0].execute(statement)
        data= db[0].fetchone()
        if data != None:
            return
        else:
            title=f'You were given a {a.type} {a.point_type} point'
            message=f'In {a.lesson} by {a.teacher} for {a.reason} - {a.note}'
            notification(title,message)
            if a.note==None:
                a.note='Not Specified'
            statement=f'INSERT INTO activites (id, type, score, reason, notes) VALUES ({a.id}, "{a.type}", {a.score}, "{a.reason}", "{a.note}")'
            db[0].execute(statement)
            db[1].commit()

async def getHomework(sc):
    db = connect()
    array = await sc.homeworks()
    index=0
    #while len(array)-1 > index:
    for a in array:
        statement = f'SELECT * from homework WHERE id={a.id}'
        db[0].execute(statement)
        data= db[0].fetchone()
        if data == None:
            title=f'Homework set for {a.lesson} by {a.teacher}'
            message=f'{a.title}'
            notification(title,message) 
            statement=f'INSERT INTO homework (id, title) VALUES ({a.id}, "{a.title}")'
            db[0].execute(statement)
            db[1].commit()






if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()