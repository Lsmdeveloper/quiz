from django.urls import path
from .views import (
    BulkCreateQuestions, CreateQuestion, CreateQuiz, Health, ListQuestions, StartQuiz, SaveAnswers, FinishQuiz, GetResult, MPWebhook
)

urlpatterns = [
    path("health", Health.as_view()),
    path("api/quiz/questions", ListQuestions.as_view()),     
    
    path("api/quiz", CreateQuiz.as_view()),                                   
    path("api/quiz/<slug:slug>/questions", CreateQuestion.as_view()),         
    path("api/quiz/<slug:slug>/questions/bulk", BulkCreateQuestions.as_view()),

    path("api/quiz/start", StartQuiz.as_view()),
    path("api/quiz/<str:session_id>/answer", SaveAnswers.as_view()),
    path("api/quiz/<str:session_id>/finish", FinishQuiz.as_view()), 
    path("api/result/<str:session_id>", GetResult.as_view()),
    path("api/webhooks/mercadopago", MPWebhook.as_view()),
]