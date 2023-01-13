import datetime
from time import sleep
import sqlite3
import http.client, urllib
#import api
from api import GetBehaviour, GetDetentions, GetHomework, GetAnnouncements, GetBadges
### Settings ###
from config import data as config


## Pushover Notif ##
APIKEY=config["apikey"]
USERID=config["userid"]


## Database ##
def connect():
    con=sqlite3.connect("cc.db")
    cur = con.cursor()
    return [cur, con]


## CC ##
def main():
    while True:
        getActivity()
        getHomework()
        getDetentions()
        getAnnouncements()
        getBadges()
        checkDue()
        print(f'Updated {datetime.datetime.now()}')
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

def getActivity():
    global data
    activity = GetBehaviour(config["code"], config["dob"])
    db = connect()
    for a in activity:
        if activity[a]["polarity"] == "blank":
            return
        statement = f'SELECT * from activites WHERE id={activity[a]["id"]}'
        db[0].execute(statement)
        data= db[0].fetchone()
        if data != None:
            return
        else:
            title=f'You were given a {activity[a]["polarity"]} {activity[a]["type"]} point'
            message=f'In {activity[a]["lesson"]} by {activity[a]["teacher"]} for {activity[a]["reason"]} - {activity[a]["note"]}'
            notification(title,message)
            if activity[a]["note"]==None:
                activity[a]["note"]='Not Specified'
            statement=f'INSERT INTO activites (id) VALUES ({activity[a]["id"]}, "{activity[a]["type"]}", {activity[a]["score"]}, "{activity[a]["reason"]}", "{activity[a]["note"]}")'
            db[0].execute(statement)
            db[1].commit()

def getHomework():
    global data
    homeworks = GetHomework(config["code"], config["dob"])
    db = connect()
    index=0
    for h in homeworks:
        statement = f'SELECT * from homework WHERE id={homeworks[h]["id"]}'
        db[0].execute(statement)
        data= db[0].fetchone()
        if data == None:
            title=f'Homework set for {homeworks[h]["lesson"]} by {homeworks[h]["teacher"]}'
            message=f'{homeworks[h]["title"]}'
            notification(title,message) 
            statement=f'INSERT INTO homework (id, title) VALUES ({homeworks[h]["id"]}, "{homeworks[h]["title"]}")'
            db[0].execute(statement)
            db[1].commit()

def getAnnouncements():
    global data
    annoucements=GetAnnouncements(config["code"], config["dob"])
    db = connect()
    for a in annoucements:
        statement = f'SELECT * from annoucements WHERE id={annoucements[a]["id"]}'
        db[0].execute(statement)
        data= db[0].fetchone()
        if data == None:
            title=f'Announcement from {annoucements[a]["teacher"]}'
            message=f'{annoucements[a]["title"]}'
            notification(title,message) 
            statement=f'INSERT INTO annoucements (id) VALUES ({annoucements[a]["id"]})'
            db[0].execute(statement)
            db[1].commit()        

def getBadges():
    global data
    badges=GetBadges(config["code"], config["dob"])
    db = connect()
    for b in badges:
        statement = f'SELECT * from badges WHERE id={badges[b]["id"]}'
        db[0].execute(statement)
        data= db[0].fetchone()
        if data == None:
            title=f'You were given a {badges[b]["name"]} badge'
            message=f'You now have {badges[b]["pupil_badges"]}'
            notification(title,message) 
            statement=f'INSERT INTO badges (id) VALUES ({badges[b]["id"]})'
            db[0].execute(statement)
            db[1].commit()        

def getDetentions():
    global data
    db = connect()    
    detentions = GetDetentions(config["code"], config["dob"])
    for d in detentions:
        statement = f'SELECT * from detentions WHERE id={detentions[d]["id"]}'
        db[0].execute(statement)
        data= db[0].fetchone()
        if data == None:
            title=f'Detention for {detentions[d]["reason"]}'
            message=f'On the {detentions[d]["date_set"]} by {detentions[d]["teacher"]}'
            notification(title,message) 
            statement=f'INSERT INTO detentions (id) VALUES ({detentions[d]["id"]}")'
            db[0].execute(statement)
            db[1].commit()

def checkDue():
    global data
    homeworks = GetHomework(config["code"], config["dob"])
    db=connect()
    now = datetime.datetime.now()
    for h in homeworks:
        statement = f'SELECT * from due WHERE id={homeworks[h]["id"]}'
        db[0].execute(statement)
        data= db[0].fetchone()
        if data is None and homeworks[h]["done"] == 'no' :
            time_of_timestamp = datetime.datetime.fromisoformat(str(homeworks[h]["due_date"]))
            time_diff = now - time_of_timestamp
            if time_diff <= datetime.timedelta(days=1) and time_of_timestamp <= datetime.datetime.now() and homeworks[h]["done"] is not True:
                title=f'Homework due today'
                message=f'You have {homeworks[h]["lesson"]} homework due in today'
                notification(title,message)
                statement=f'INSERT INTO due (id) VALUES ({homeworks[h]["id"]})'
                db[0].execute(statement)
                db[1].commit()
    
if __name__ == "__main__":
    main()
