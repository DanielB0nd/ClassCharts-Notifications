from datetime import datetime, time
from bs4 import BeautifulSoup
import requests
import json
import re

login_url = 'https://www.classcharts.com/apiv2student/login'

def GetHomework(code, dob):
    homeworkRequest = _request('homeworks', code, dob)
    homeworks = {}
    for count, r in enumerate(homeworkRequest['data'], start=1):
        data = {
          count:{
                'id': r['id'],
                'lesson': r['lesson'],
                'subject': r['subject'],
                'title': r['title'],
                'teacher': r['teacher'],
                'due_date': r['due_date'],
                'description': r['description'],
                'done': r['status']['ticked']
        }
        }
        homeworks.update(data)
    return(homeworks)

def GetBehaviour(code, dob):
    behaviourRequest = _request('activity', code, dob)
    PosCount = 0
    NegCount = 0
    points = {}
    for count, r in enumerate(behaviourRequest['data'], start=1):
        if r['polarity'] == 'Positive':
          PosCount+=1
        elif r['polarity'] == 'Negative':
          NegCount+=1
        data = {
            count: {
              'id': r['id'],
              'polarity': r['polarity'],
              'timestamp': datetime.fromisoformat(r['timestamp']),
              'type': r['type'],
              'teacher': r['teacher_name'],
              'score': r['score'],
              'reason': r['reason'],
              'lesson': r['lesson_name'],
              'note': r['note']
            }
        }
        points.update(data)
    return points

def GetDetentions(code, dob):
    detentionsRequest = _request('detentions', code, dob)
    detentions={}
    for count, r in enumerate(detentionsRequest['data'], start=1):
        data = {
            count: {
              'id': r['id'],
              'attended': True if r['attended'] == 'yes' else False,
              'time': datetime.strptime(r['time'], '%H:%M'),
              'date': datetime.fromisoformat(r['date']).replace(minute=time.minute, hour=time.hour),
              'length': int(r['length']),
              'location': r['location'],
              'lesson': r['lesson'],
              'teacher': r['teacher'],
              'lesson_pupil_behaviour': r['lesson_pupil_behaviour']['reason'],
              'detention_type': r['detention_type']['name']
            }
        }
        detentions.update(data)
    return detentions

def GetTimetable(code, dob):
    timetableRequest = _request('timetable', code, dob)
    lessons = {}
    for count, r in enumerate(timetableRequest['data'], start=1):
        data = {
          count: {
            'class': r['lesson_name'],
            'subject_name': r['subject_name'],
            'room': r['room_name'],
            'teacher': r['teacher_name']
          }
        }
        lessons.update(data)
    return(lessons)

def GetAnnouncements(code, dob):
  annoucementsRequest= _request('announcements', code, dob)
  announcements={}
  for count, r in enumerate(annoucementsRequest['data'], start=1):
    data = {
      count:{
        'id': r['id'],
        'title': r['title'],
        'description': _sanitise(r['description']),
        'teacher': r['teacher_name'],
        'viewed': True if r['state'] == 'viewed' else False,
        'timestamp': datetime.fromisoformat(r['timestamp']),
        'school_name':  r['school_name']
      }
    }
    announcements.update(data)
  return(announcements)

def GetBadges(code, dob):
  badgesRequest= _request('eventbadges', code, dob)
  badges={}
  for count, r in enumerate(badgesRequest['data'], start=1):
    data = {
      count:{
        'id': r['id'],
        'name': r['name'],
        'title': r['title'],
        'colour': r['colour'],
        'created_date': r['created_date'],
        'pupil_badges': r['pupil_badges'],
        'icon_url':  r['icon_url']
      }
    }
    badges.update(data)
  return(badges)

###---Workers---###

def _sanitise(content):
    return re.sub('\n\n+', '\n', BeautifulSoup(content, 'lxml').text).strip()

def _login(code, dob):
  payload = {'code': code, 'dob':dob, 'remember_me': '1', 'recaptcha-token': 'no-token-available'}
  session = requests.Session()
  headers = {'User-Agent': 'Mozilla/5.0'}
  response = session.post(login_url, headers=headers, data=payload)
  jsonResponse = response.json()
  studentID = jsonResponse['data']['id']
  sessionID = jsonResponse['meta']['session_id']
  return [session, studentID, sessionID]

def _request(type, code, dob):
    session, studentID, sessionID = _login(code, dob)
    response = session.get(f'https://www.classcharts.com/apiv2student/{type}/{studentID}', headers = {
      'authorization': f'Basic {sessionID}'
    })
    jsonResponse = response.json()
    return jsonResponse
  