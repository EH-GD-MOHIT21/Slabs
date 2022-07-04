from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.conf import settings
import requests


def ParseLanguage(language):
    if 'c++' in language:
        return 'cpp'
    elif 'python' in language:
        return 'py'
    elif 'java' in language:
        return 'java'
    else:
        return 'c'



@shared_task(bind=True)
def execute_code(self, code, language, inputs=None):
    compiler_url = settings.COMPILER
    language = ParseLanguage(language)
    payload = {
        "code": code,
        "language":language,
        "input": inputs
    }
    response = requests.post(compiler_url,data=payload)
    return response.text