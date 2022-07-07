from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.conf import settings
import requests
import json
from users.models import User
from django.utils import timezone

from mainAPP.models import Problem, UserSubmission


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
def execute_code(self, code, language, inputs=None, user=None, original_outputs=None,problem_id=None):
    compiler_url = settings.COMPILER
    language = ParseLanguage(language)
    payload = {
        "code": code,
        "language":language,
        "input": inputs
    }
    response = requests.post(compiler_url,data=payload)
    if user==None:
        return response.text
    else:
        # submit attempt
        try:
            flag = 1
            output = json.loads(response.text)
            user = User.objects.get(username=user)
            problem = Problem.objects.get(id=int(problem_id))
            model = UserSubmission()
            model.user = user
            model.code = code
            model.submission_time = timezone.now()
            model.problem = problem
            model.save()
            if output['output'].strip() == original_outputs.strip():
                # correct ans
                print('yes')
                problem.total_submissions += 1
                problem.total_success_submissions += 1
                user.correct_submissions += 1
                flag = 0
            else:
                # wrong ans
                print('no')
                problem.total_submissions += 1
                user.incorrect_submissions += 1
            problem.save()
            user.save()
            if flag:
                return 'wrong answer'
            else:
                return 'success'
        except:
            return response.text