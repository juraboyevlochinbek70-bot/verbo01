"""Verbo — asosiy URL yoʻnaltirishlari."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("boshqaruv/", admin.site.urls),   # oʻqituvchi paneli
    path("", include("accounts.urls")),
    path("", include("modules.urls")),
]

admin.site.site_header = "Verbo — Boshqaruv paneli"
admin.site.site_title = "Verbo"
admin.site.index_title = "Platforma boshqaruvi"
