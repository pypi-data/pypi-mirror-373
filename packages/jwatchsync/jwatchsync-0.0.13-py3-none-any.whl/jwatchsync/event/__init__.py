import os
import json
import requests
from datetime import datetime
from jwatchsync.utils.config import JWATCH_URL, EVENT

class Event:

    def __init__(
            self, 
            env=os.getenv('JWATCH_ENV'), 
            public_key=os.getenv('JWATCH_PUBLIC_KEY'),
            event_type=None, 
            object_id=None,
            username='ANONYMOUS', 
            userid=None
        ):
        DATE_NOW = datetime.now()

        self.URL = JWATCH_URL.get(env, JWATCH_URL['PROD'])
        self.public_key = public_key or os.getenv('JWATCH_PUBLIC_KEY')
        self.START_DATE = DATE_NOW
        self.END_DATE = None
        self.EVENT_TYPE = event_type
        self.OBJECT_ID = object_id
        self.STATUS = 'SUCCESS'
        self.USER_NAME = username or 'ANONYMOUS'
        self.USER_ID = userid
        self.COMMENT = None
        self.LOGS = [{
            'START_DATE': DATE_NOW.isoformat(),
            'END_DATE': DATE_NOW.isoformat(),
            'DURATION': 0,
            'MESSAGE': 'Event tracking started',
            'STATUS': 'SUCCESS'
        }]
        self.DURATION = 0
        # INTERNAL
        self.log_start_date = DATE_NOW
    
    def log_track(self, mesage='', status='SUCCESS'):
        START_DATE = self.log_start_date
        END_DATE = datetime.now()
        DURATION = (END_DATE - START_DATE).total_seconds() * 1000
        self.LOGS.append({
            'START_DATE': START_DATE.isoformat(),
            'END_DATE': END_DATE.isoformat(),
            'DURATION': DURATION,
            'MESSAGE': mesage,
            'STATUS': status
        })
        self.log_start_date = datetime.now()

    def end_track(self, comment='', status='SUCCESS'):
        self.STATUS = status
        self.COMMENT = comment
        self.END_DATE = datetime.now()
        self.DURATION = (self.END_DATE - self.START_DATE).total_seconds() * 1000
        self.START_DATE = self.START_DATE.isoformat()
        self.END_DATE = self.END_DATE.isoformat()
        self.log_track(mesage='Event tracking ended', status=status)
        response = self.send()
        # print("[JWatchSync]: ", response)
        return self.LOGS
    
    def send(self):
        try:
            data = {}
            for key, value in EVENT.items():
                record = self.__dict__.get(key)
                if record is not None:
                    data[key] = record
            response = requests.post(f"{self.URL}event", json=data, headers={ 'Authorization': self.public_key })
            return response.json()
        except Exception as e:
            return { 'error': str(e) }