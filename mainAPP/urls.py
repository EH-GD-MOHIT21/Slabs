from django.urls import path
from . import views

urlpatterns = [
    path('playground',views.RenderCodePage),
    path('playground/id=<int:id>',views.RenderCodePage),
    path('saveplayground',views.SavePlayground),
    path('problems',views.RenderProblemPage),
    path('viewproblem/<slug:url>',views.RenderProblemSolvePage),
    path('viewproblem/<slug:url>/challenge=<int:cid>',views.RenderProblemSolvePage),
    path('executecode',views.ExecuteCode.as_view()),
    path('submitcode',views.SubmitCode.as_view()),
    path('create/challenge',views.RenderCreateChallenge),
    path('join/challenge=<int:cid>',views.HandleJoinChallenge),
    path('save/challenge',views.SaveChallenge),
    path('mychallenges',views.DisplayMyChallenges), # my (public+private) challenges
    path('challenges',views.DisplayAvailableChallenges), #public challenges
    path('search/challenge',views.SearchChallenge), # search a challenge
    path('leaderboard',views.LeaderBoardRankingChallenge.as_view()),
    path('searchleaderboard',views.SearchPlayerLeaderboard.as_view()),
]
