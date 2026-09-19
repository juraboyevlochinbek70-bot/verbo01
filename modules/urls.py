"""Verbo — modul URLlari."""
from django.urls import path
from . import views

urlpatterns = [
    path("speaking/", views.speaking, name="speaking"),
    path("speaking/boshlash/", views.speaking_start, name="speaking_start"),

    path("writing/", views.writing, name="writing"),
    path("writing/oz-savolim/", views.writing_own, name="writing_own"),
    path("writing/oz-savolim/yuborish/", views.writing_own_submit, name="writing_own_submit"),
    path("writing/<int:topic_id>/", views.writing_task, name="writing_task"),
    path("writing/<int:topic_id>/yuborish/", views.writing_submit, name="writing_submit"),

    path("natijalar/", views.results, name="results"),
    path("natija/<int:result_id>/", views.result_detail, name="result_detail"),

    path("kreditlar/", views.credits, name="credits"),
    path("lugat/", views.vocabulary, name="vocabulary"),
]
