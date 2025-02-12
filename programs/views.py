# from django.shortcuts import render
# from django.http import HttpResponseForbidden
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,GenericAPIView
from rest_framework.response import Response
from.serializers import Customerserializer,Userserializer,Researcherserializer,CustomAuthTokenSerializer
from.models import User
from .permissions import IsCustomer,IsResearcher
from rest_framework import permissions
from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.views import APIView
# from rest_framework.authtoken.views import ObtainAuthToken

# Create your views here.
class UserRegister(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = Userserializer

class CustomerRegister(ListCreateAPIView):

    queryset = User.objects.filter(role="customer").order_by("-created_at")
    serializer_class = Customerserializer

    
    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [IsCustomer]
        else:
            permission_classes = [permissions.AllowAny]

        return [permission() for permission in permission_classes]



class CustomerLoginView(GenericAPIView):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        role = serializer.validated_data["role"]  # Get role from validated data

        # Ensure the user is a customer
        if role.lower() != "customer":
            return Response({"error": "Access denied. Only customers can log in."}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            {
                "access_token": serializer.validated_data["access"],
                "refresh_token": serializer.validated_data["refresh"],
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": role,
            },
            status=status.HTTP_200_OK,
        )


class CustomerUpdateView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(role="customer")
    serializer_class = Customerserializer
    lookup_field = 'id'
    permission_classes = [IsCustomer]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if 'password' in serializer.validated_data:
            instance.set_password(serializer.validated_data.pop('password'))   # Hash password

        serializer.save()  # Save the instance

        return Response(serializer.data, status=status.HTTP_200_OK)


class ResearcherRegister(ListCreateAPIView):
    queryset = User.objects.filter(role="researcher").order_by("-created_at")
    serializer_class = Researcherserializer

    
    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [IsResearcher]
        else:
            permission_classes = [permissions.AllowAny]

        return [permission() for permission in permission_classes]


class ResearcherLoginView(GenericAPIView):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        role = serializer.validated_data["role"]  # Get role from validated data

        # Ensure the user is a researcher
        if role.lower() != "researcher":
            return Response({"error": "Access denied. Only Researchers can log in."}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            {
                "access_token": serializer.validated_data["access"],
                "refresh_token": serializer.validated_data["refresh"],
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": role,
            },
            status=status.HTTP_200_OK,
        )


class ResearcherUpdateView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(role="researcher")
    serializer_class = Researcherserializer
    lookup_field = 'id'
    permission_classes = [IsResearcher]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if 'password' in serializer.validated_data:
            instance.set_password(serializer.validated_data.pop('password'))   # Hash password

        serializer.save()  # Save the instance

        return Response(serializer.data, status=status.HTTP_200_OK)