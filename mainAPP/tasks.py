from datetime import datetime
from operator import mod
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.conf import settings
import requests
import json
from users.models import User
from django.utils import timezone

from mainAPP.models import Challenge, Problem, UserSubmission


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
def execute_code(self, code, language, inputs=None, user=None, original_outputs=None,problem_id=None,challenge=None):
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
            if challenge != "":
                challenge = Challenge.objects.get(id=int(challenge))
                if isinstance(challenge.open_time,datetime):
                    if challenge.open_time > timezone.now():
                        return 'Challenge Not Started Yet.'
                if isinstance(challenge.close_time,datetime):
                    if challenge.close_time < timezone.now():
                        return 'Challenge Has Ended.'
                model.challenge = challenge
            if output['output'].strip() == original_outputs.strip():
                # correct ans
                print('yes')
                model.submission_status = 'success'
                problem.total_submissions += 1
                problem.total_success_submissions += 1
                user.correct_submissions += 1
                flag = 0
            else:
                # wrong ans
                print('no')
                problem.total_submissions += 1
                user.incorrect_submissions += 1
            model.save()
            problem.save()
            user.save()
            if flag:
                return 'wrong answer, one or more test case wrong.'
            else:
                return 'success'
        except:
            return response.text