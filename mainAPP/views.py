from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render
from .models import Challenge, Playground, Problem, TextCase
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import execute_code
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
import random
from django.conf import settings
import os
from datetime import datetime
import pytz
from django.utils import timezone
# Create your views here.


def RenderCodePage(request, id=None):
    if id:
        playground = Playground.objects.get(id=id)
        code = playground.code
        language = playground.language
        return render(request, 'codepage.html', {'code': code, 'language': language, 'id': id, 'playground': True})
    return render(request, 'codepage.html', {'playground': True})


def SavePlayground(request):
    if request.method != 'POST' or not request.user.is_authenticated:
        return redirect('/')
    body = request.POST
    lang = body.get('language')
    code = body.get('code_value')
    id = body.get('id')
    if id == None or id == '':
        model, created = Playground.objects.get_or_create(
            user=request.user,
            language=lang,
            code=code
        )
        return redirect(f'/playground/id={model.id}')
    else:
        model = Playground.objects.get(
            user=request.user,
            id=id
        )
        model.language = lang
        model.code = code
        model.save()
        return redirect(f'/playground/id={id}')


def RenderProblemPage(request):
    return render(request, 'problems.html')


def RenderProblemSolvePage(request, url, cid=None):
    if cid == None:
        problem = Problem.objects.get(url=url)
        return render(request, 'problem_stat.html', {'problem': problem})
    else:
        print(cid)
        problem = Problem.objects.get(url=url)
        return render(request, 'problem_stat.html', {'problem': problem})


class ExecuteCode(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            data = request.data

            try:
                code = data["code"]
                custom_input = data["input"]
                language = data["language"]

            except:
                return Response({'status': 400, 'message': 'One or more required parameters missing.'})

            try:
                problem = data["problem"]
            except:
                problem = None

            if problem is None or problem == "":
                # run code and just return output
                print(language)
                task_id = execute_code.delay(code, language, custom_input)
                print(task_id)
                return Response({'status': 200, 'message': 'success', "task_id": str(task_id)})

            else:
                # run code save details and return output
                pass
            return Response({'status': 200, 'message': 'success'})
        return Response({'status': 403, 'message': 'Please authenticate yourself'})


class SubmitCode(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                problem_code = request.data['problem_id']
                code = request.data["code"]
                language = request.data["language"]
                try:
                    test_case = TextCase.objects.get(
                        problem__id=int(problem_code))
                    task_id = execute_code.delay(code, language, test_case.inputs, request.user.username, test_case.output.replace(
                        '\r\n', '\n').replace('\r', '\n'), problem_code)
                    print(task_id)
                    return Response({'status': 200, 'message': 'success', "task_id": str(task_id)})
                except Exception as e:
                    print(e)
                    return Response({'status': 400, 'message': 'The given problem is missing testcases.'})
            except:
                return Response({'status': 400, 'message': 'One or more required parameters missing.'})
        else:
            return Response({'status': 403, 'message': 'Please authenticate yourself.'})


@login_required(login_url='/accounts/login')
def RenderCreateChallenge(request):
    tzs = []
    with open(os.path.join(settings.BASE_DIR, 'project_settings/timezones.txt'), 'r') as file:
        data = file.read()
        for line in data.split('\n'):
            tzs.append(line.strip())
    return render(request, 'challenge_customize.html', {'timezone': tzs})


@login_required(login_url='/accounts/login')
def HandleJoinChallenge(request, cid, redirected=False):
    try:
        challenge = Challenge.objects.get(id=int(cid))
    except:
        return HttpResponseNotFound()

    if not redirected and not (challenge.password == None or challenge.password == ''):
        # not entered password and trying to join
        return redirect('/challenges')

    if challenge.open_time <= timezone.now():
        if challenge.close_time == None or challenge.close_time > timezone.now():
            users = challenge.participates

            if(users.contains(request.user)):
                return render(request, 'challenge.html',{'roomName':challenge.id,'problems':challenge.problems.all()})
            else:
                challenge.participates.add(request.user)
                challenge.save()
                return render(request, 'challenge.html',{'roomName':challenge.id,'problems':challenge.problems.all()})

        users = challenge.participates
        if(users.contains(request.user)):
            return render(request, 'challenge.html',{'roomName':challenge.id,'problems':challenge.problems.all()})

        return HttpResponse('<h1>Time for joining this challenge has ended.</h1>')

    return HttpResponse('<h1>Time for joining this challenge is not begin yet.</h1>')


@login_required(login_url='/accounts/login')
def SaveChallenge(request):
    if request.method != 'POST':
        return redirect('/')
    # capture data
    data = request.POST
    user = request.user
    title = data['Contest_title']
    password = data['Contest_pass']
    open_time = data['Contest_Open_Time']
    close_time = data['Contest_Close_Time']
    time_zone = data['Contest_TimeZone']
    problem_count = int(data['Contest_Problem_Count'])
    problem_type = data['Contest_Problem_Type']
    contest_problems = data['Contest_Problems']

    model = Challenge()
    model.author = user
    model.title = title
    if password != "":
        model.password = make_password(password)
    model.open_time = ManageDate(open_time, time_zone)
    if close_time != '':
        model.close_time = ManageDate(close_time, time_zone)
    model.total_problems = problem_count
    model.save()
    all_problems = Problem.objects.all()
    all_problems_len = all_problems.count()
    try:
        if problem_type == 'random':
            problems_ids = random.sample(
                range(0, all_problems_len), problem_count)
            for ids in problems_ids:
                model.problems.add(all_problems[ids])
        else:
            problems_ids = contest_problems.split(',')
            for ids in problems_ids:
                try:
                    pblm = Problem.objects.get(id=int(ids))
                    model.problems.add(pblm)
                except:
                    pass
    except Exception as e:
        # not enough problems exists on server
        # add all problems to challenge
        for problem in all_problems:
            model.problems.add(problem)

    model.save()
    return redirect('/mychallenges')


def DisplayMyChallenges(request):
    challeges = Challenge.objects.filter(author=request.user)
    return render(request, 'display_challenges.html', {'challeges': ParseChallengesToDisplay(challeges)})


def DisplayAvailableChallenges(request):
    # public challenges
    challeges = Challenge.objects.filter(password=None)
    return render(request, 'display_challenges.html', {'challeges': ParseChallengesToDisplay(challeges)})


def ParseChallengesToDisplay(challenges):
    return_this = []
    for challenge in challenges:
        obj = {}
        obj['title'] = challenge.title
        obj['id'] = challenge.id
        obj['author'] = challenge.author
        obj['close_time'] = challenge.close_time
        obj['open_time'] = challenge.open_time
        obj['date_created'] = challenge.date_created
        obj['problems'] = challenge.problems.count()
        obj['participates'] = challenge.participates.count()
        obj['private'] = False
        if challenge.password:
            obj['private'] = True
        return_this.append(obj)

    return return_this


def SearchChallenge(request):
    id = request.POST['id']
    password = request.POST['password']
    try:
        challeges = Challenge.objects.get(id=int(id))
    except:
        return HttpResponseNotFound()
    render_it = False
    if not (challeges.password == None or challeges.password == ''):
        if check_password(password, challeges.password):
            return HandleJoinChallenge(request, challeges.id, True)
    else:
        render_it = True

    if render_it:
        return render(request, 'display_challenges.html', {'challeges': ParseChallengesToDisplay([challeges])})
    else:
        return HttpResponseNotFound()


def ManageDate(date, user_timezone):
    try:
        date, time = date.split('T')
        year, month, day = date.split('-')
        hour, minute = time.split(':')
        date = f'{day}/{month}/{year} {hour}:{minute}:00'
        format = "%d/%m/%Y %H:%M:%S"
        local = pytz.timezone(user_timezone)
        temp = datetime.strptime(date, format)
        local_dt = local.localize(temp, is_dst=None)
        temp = local_dt.astimezone(pytz.UTC)
        return temp
    except:
        return None