from django.urls import path
from . import views

app_name = "rattingtax"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("connect/", views.connect_corp_token, name="connect"),
]
