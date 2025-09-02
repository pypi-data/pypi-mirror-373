"""App URLs"""

# Django
from django.urls import path

# AA Mumble Quick Connect
from aa_mumble_quick_connect import views

app_name: str = "aa_mumble_quick_connect"

urlpatterns = [
    path(route="", view=views.index, name="index"),
    path(route="<slug:section>/", view=views.index, name="index"),
]
