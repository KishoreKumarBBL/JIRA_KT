# from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from. models import Submission
from .serializers import Submissionserializer

# Create your views here.

class Submissions(ListCreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = Submissionserializer