# from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from. models import Submission

# Create your views here.

class Submissions(ListCreateAPIView):
    queryset = Submission.objects.all()