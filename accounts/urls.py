from django.urls import path
from . import views

urlpatterns=[
    path("signup/",views.signup,name="signup"),
    path("signin/",views.signin,name="signin"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("logout/",views.signout,name="logout"),
    path("coin-transfer/",views.coin_transfer,name="coin-transfer"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
]