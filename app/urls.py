from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot', views.hot, name='hot'),
    path('question/<int:question_id>', views.question, name='question'),
    path('tag/<str:tag_name>', views.tag, name='tag'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
    path('profile/edit/', views.profile_edit, name='profile.edit'),
    path('logout/', views.logout, name='logout'),
    path('question/<int:question_id>/like', views.question_like, name='question.like'),
    path('answer/<int:answer_id>/correct', views.answer_correct, name='answer.correct'),
    path('answer/<int:answer_id>/like', views.answer_like, name='answer.like'),
]
