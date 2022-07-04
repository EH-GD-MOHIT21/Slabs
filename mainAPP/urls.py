from django.urls import path
from . import views

urlpatterns = [
    path('playground',views.RenderCodePage),
    path('playground/id=<int:id>',views.RenderCodePage),
    path('saveplayground',views.SavePlayground),
    path('problems',views.RenderProblemPage),
    path('viewproblem/<slug:url>',views.RenderProblemSolvePage),
    path('executecode',views.ExecuteCode.as_view()),
]