"""Verbo — accounts URLlari."""
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from . import panel_views

urlpatterns = [
    path("", views.home, name="home"),
    path("intro/", views.intro, name="intro"),
    path("boshlash/", views.register_choice, name="register_choice"),

    path("royxat/", views.signup, name="signup"),                       # email
    path("royxat/telefon/", views.phone_register, name="phone_register"),
    path("royxat/telefon/tasdiq/", views.phone_verify, name="phone_verify"),

    path("kirish/", auth_views.LoginView.as_view(), name="login"),
    path("demo/", views.demo_login, name="demo_login"),
    path("chiqish/", auth_views.LogoutView.as_view(), name="logout"),
    path("tariflar/", views.tariffs, name="tariffs"),
    # O'qituvchi paneli (faqat is_staff)
    path("panel/", panel_views.dashboard, name="panel"),
    path("panel/oquvchilar/", panel_views.students, name="panel_students"),
    path("panel/oquvchi/<int:uid>/", panel_views.student_detail, name="panel_student"),
    path("panel/natijalar/", panel_views.all_results, name="panel_results"),

]
