from django.urls import path
from .views import Submissions

urlpatterns=[
    path('submission/',Submissions.as_view(),name='Submissions'),
    # path(),
]