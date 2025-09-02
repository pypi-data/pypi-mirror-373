JWATCH_URL = {
    'DEV': 'https://3xitucu0sd.execute-api.us-east-1.amazonaws.com/api/v1/track/', # 'http://localhost:3001/api/v1/track/', # 
    'PROD': 'https://ut19v988lc.execute-api.us-east-1.amazonaws.com/api/v1/track/'
}

EVENT = {
    'EVENT_TYPE': str,
    'OBJECT_ID': int,
    'USER_NAME': str,
    'USER_ID': int,
    'STATUS': {
        'SUCCESS': 'SUCCESS',
        'ERROR': 'ERROR',
        'WARNING': 'WARNING',
        'INFO': 'INFO'
    },
    'DATE': str,
    'START_DATE': str,
    'END_DATE': str,
    'DURATION': float,
    'COMMENT': str,
    'LOGS': list,
    'PROJECT_ID': int,
    'AMBIENTE': str,
    'VERSION': str
}

class EVENT_STATUS:
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'