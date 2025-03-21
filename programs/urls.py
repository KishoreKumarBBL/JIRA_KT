from django.urls import path
from .views import (
    UserRegister,
    CustomerRegister,
    CustomerLoginView,
    CustomerUpdateView,
    ResearcherRegister,
    ResearcherLoginView,
    ResearcherUpdateView,
    CreateProgram,
    ResearcherProgram
)

urlpatterns = [
    path("Register/", UserRegister.as_view(), name="ulsr"),
    path("customer/", CustomerRegister.as_view(), name="Cust_reg"),
    path("customer/login/", CustomerLoginView.as_view(), name="Login"),
    path("customer/<uuid:id>/", CustomerUpdateView.as_view(), name="Update"),
    path("researcher/", ResearcherRegister.as_view(), name="Register"),
    path("researcher/login/", ResearcherLoginView.as_view(), name="Register"),
    path("researcher/<uuid:id>/", ResearcherUpdateView.as_view(), name="Register"),
    path("program/",CreateProgram.as_view(),name='Program'),
    path("program/researcher/",ResearcherProgram.as_view(), name="Programs"),
]
