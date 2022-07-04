from django.shortcuts import redirect, render
from .models import Playground, Problem
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import execute_code
# Create your views here.


def RenderCodePage(request,id=None):
    if id:
        playground = Playground.objects.get(id=id)
        code = playground.code
        language = playground.language
        return render(request,'codepage.html',{'code':code,'language':language,'id':id,'playground':True})
    return render(request,'codepage.html',{'playground':True})



def SavePlayground(request):
    if request.method != 'POST' or not request.user.is_authenticated:
        return redirect('/')
    body = request.POST
    lang = body.get('language')
    code = body.get('code_value')
    id = body.get('id')
    if id == None or id=='':
        model,created = Playground.objects.get_or_create(
            user = request.user,
            language = lang,
            code = code
        )
        return redirect(f'/playground/id={model.id}')
    else:
        model = Playground.objects.get(
            user = request.user,
            id = id
        )
        model.language = lang
        model.code = code
        model.save()
        return redirect(f'/playground/id={id}')
    


def RenderProblemPage(request):
    return render(request,'problems.html')


def RenderProblemSolvePage(request,url):
    problem = Problem.objects.get(url=url)
    return render(request,'problem_stat.html',{'problem':problem})



class ExecuteCode(APIView):
    def post(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            data = request.data

            try:
                code = data["code"]
                custom_input = data["input"]
                language = data["language"]

            except:
                return Response({'status':400,'message':'One or more required parameters missing.'})

            try:
                problem = data["problem"]
            except:
                problem = None

            if problem is None or problem == "":
                # run code and just return output
                print(language)
                task_id = execute_code.delay(code,language,custom_input)
                print(task_id)
                return Response({'status':200,'message':'success',"task_id": str(task_id)})

            else:
                # run code save details and return output
                pass
            return Response({'status':200,'message':'success'})
        return Response({'status':403,'message':'Please authenticate yourself'})