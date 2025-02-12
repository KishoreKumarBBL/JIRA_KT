from django.urls import path
from .views import Submissions

urlpatterns=[
    path('Submissions/',Submissions.as_view(),name='test'),
    # path(),
]