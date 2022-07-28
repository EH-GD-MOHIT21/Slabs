from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render
from users.forms import User
from .models import Challenge, Playground, Problem, TextCase, UserSubmission
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import execute_code
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
import random
from django.conf import settings
import os
from datetime import datetime,timedelta
import pytz
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ModelSerializer
from users.models import User
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
    problems = Problem.objects.filter(published=True)[:]
    return render(request, 'problems.html', {'problems': problems})


def RenderProblemSolvePage(request, url, cid=None):
    if cid == None:
        problem = Problem.objects.get(url=url)
        if problem.published:
            return render(request, 'problem_stat.html', {'problem': problem})
        return redirect('/problems')
    else:
        challenge = Challenge.objects.get(id=int(cid))
        problem = Problem.objects.get(url=url)
        if request.user in challenge.participates.all():
            return render(request, 'problem_stat.html', {'problem': problem})
        return redirect('/')


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
                challenge = request.data['challenge']
                try:
                    test_case = TextCase.objects.get(
                        problem__id=int(problem_code))
                    task_id = execute_code.delay(code, language, test_case.inputs, request.user.username, test_case.output.replace(
                        '\r\n', '\n').replace('\r', '\n'), problem_code, challenge)
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
                return render(request, 'challenge.html', {'roomName': challenge.id, 'problems': challenge.problems.all()})
            else:
                challenge.participates.add(request.user)
                challenge.save()
                return render(request, 'challenge.html', {'roomName': challenge.id, 'problems': challenge.problems.all()})

        users = challenge.participates
        if(users.contains(request.user)):
            return render(request, 'challenge.html', {'roomName': challenge.id, 'problems': challenge.problems.all()})

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


class LeaderBoardSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name","last_name","username","country","profile_image"]


class UserSubmissionSerializer(ModelSerializer):
    class Meta:
        model = UserSubmission
        fields = "__all__"


class CustomPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page'
    page_query_param = 'p'

    def get_paginated_response(self, data):
        response = Response(data)
        response['count'] = self.page.paginator.count
        response['next'] = self.get_next_link()
        response['previous'] = self.get_previous_link()
        return response



def Date_avg(dates,any_reference_date,contest_start_time):
    if not dates:
        return None
    return any_reference_date + sum([date - any_reference_date for date in dates], timedelta()) / len(dates) - contest_start_time



class LeaderBoardRankingChallenge(APIView):
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # do stuff
            challenge = request.GET.get('challenge')
            try:
                challenge = Challenge.objects.get(id=int(challenge))
            except:
                return Response({'status':404,'message':'Challenge Not Found.'})
            
            users = challenge.participates.all()
            ref_date = challenge.open_time
            serializer = LeaderBoardSerializer(users, many=True)
            data = serializer.data
            for subdata in data:
                user = subdata['username']
                usertotalsubmission = UserSubmission.objects.filter(user=User.objects.get(username=user),challenge=challenge,submission_status='success')
                solved_problem_ids = []
                user_unique_submissions = []
                dates = []
                for submission in usertotalsubmission:
                    pid = submission.problem.id
                    if pid not in solved_problem_ids:
                        solved_problem_ids.append(pid)
                        submission_data = UserSubmissionSerializer(submission).data
                        user_unique_submissions.append(submission_data)
                        dates.append(submission.submission_time)
                subdata['user_submissions'] = user_unique_submissions
                subdata['avgtime'] = Date_avg(dates,ref_date,ref_date)
            res = sorted(serializer.data, key = lambda x: x['avgtime'])
            for index,user in enumerate(res):
                user["rank"] = index + 1
            page = self.paginate_queryset(res)
            return self.get_paginated_response(page)

        else:
            return Response({'status': 403, 'message': 'Please Register Yourself.', 'data': None})

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)



class SearchPlayerLeaderboard(APIView):
    pagination_class = CustomPagination

    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            challenge = request.GET.get('challenge',None)
            inps = request.GET.get('param','')
            try:
                challenge = Challenge.objects.get(id=int(challenge))
            except:
                return Response({'status':500,'message':'Challenge Not described.','data':None})
            usersrequired = challenge.participates.filter(first_name__contains=inps) | challenge.participates.filter(username__contains=inps) | challenge.participates.filter(last_name__contains=inps)
            users = challenge.participates.all()
            ref_date = challenge.open_time
            serializer = LeaderBoardSerializer(users, many=True)
            data = serializer.data
            for subdata in data:
                user = subdata['username']
                usertotalsubmission = UserSubmission.objects.filter(user=User.objects.get(username=user),challenge=challenge,submission_status='success')
                solved_problem_ids = []
                user_unique_submissions = []
                dates = []
                for submission in usertotalsubmission:
                    pid = submission.problem.id
                    if pid not in solved_problem_ids:
                        solved_problem_ids.append(pid)
                        submission_data = UserSubmissionSerializer(submission).data
                        user_unique_submissions.append(submission_data)
                        dates.append(submission.submission_time)
                subdata['user_submissions'] = user_unique_submissions
                subdata['avgtime'] = Date_avg(dates,ref_date,ref_date)
            res = sorted(serializer.data, key = lambda x: x['avgtime'])
            for index,user in enumerate(res):
                user["rank"] = index+1
            tres = []
            for user in res:
                for user1 in usersrequired:
                    if user["username"] == user1.username:
                        tres.append(user)
            page = self.paginate_queryset(tres)
            return self.get_paginated_response(page)

        else:
            return Response({'status': 403, 'message': 'Please Register Yourself.', 'data': None})


    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
