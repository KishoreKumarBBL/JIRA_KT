import requests
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
# from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.permissions import IsCustomer

from rest_framework.exceptions import ValidationError

from .models import JiraUser, JiraProgramIssue, JiraIssueConfigs, JiraProgramMapper
from programs.models import User
from submissions.models import Submission
from programs.models import Programs

from .serializers import JiraIssueConfigsGetSerializer, JiraIssueConfigSerializer, JiraMapIdSerializer, JiraGetProjectSerializer, JiraNotificationSerializer, JiraIssueSerializer, JiraCreateProjectSerializer, JiraMapProgramProjectSerializer, JiraIssueConfigSerializer, JiraCommentSerialzier, JiraUserSerializer, JiraProgramMapperSerializer
from .jira_services import get_cloud_object, templates
import json
import random
import string
# from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
# from bugbusterslabs.custompagination import CustomPageNumberPagination

from programs.permissions import IsCustomer



class JiraOAuthView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        authorization_url = (
            f"{settings.JIRA_AUTHORIZATION_URL}?"
            f"audience=api.atlassian.com&"
            f"client_id={settings.JIRA_CLIENT_ID}&"
            f"scope={settings.JIRA_SCOPES}&"
            f"redirect_uri={settings.JIRA_REDIRECT_URI}&"
            f"state=some_random_state_value&"
            f"response_type=code&"
            f"prompt=consent"
        )
        return Response({"authorization_url": authorization_url})


class JiraOAuthCallbackView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        code = request.GET.get('code')
        token_response = requests.post(
            settings.JIRA_TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'client_id': settings.JIRA_CLIENT_ID,
                'client_secret': settings.JIRA_CLIENT_SECRET,
                'code': code,
                'redirect_uri': settings.JIRA_REDIRECT_URI,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        token_data = token_response.json()
        token_status = token_response.status_code

        if token_status >= 400:
            return Response(token_data, token_status)

        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')

        cloud_id_response = requests.get(
            'https://api.atlassian.com/oauth/token/accessible-resources',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        cloud_ids = cloud_id_response.json()
        cloud_response_status = cloud_id_response.status_code

        if cloud_response_status >= 400:
            return Response(cloud_ids, cloud_id_response)

        user_id = self.request.user.id
        user = User.objects.get(id=user_id)

        for cloud_data in cloud_ids:
            if not JiraUser.objects.filter(url=cloud_data["url"], name=cloud_data['name'], is_deleted=False).exists():
                cloud_obj = JiraUser(
                    cloudId=cloud_data["id"],
                    name=cloud_data["name"],
                    url=cloud_data["url"],
                    access_token=access_token,
                    refresh_token=refresh_token,
                    user_id=user
                )
                cloud_obj.save()
            else:
                cloud_obj = JiraUser.objects.get(url=cloud_data["url"])
                cloud_obj.access_token = access_token
                cloud_obj.refresh_token = refresh_token
                cloud_obj.save()

        return Response({
            "cloud_ids": cloud_ids,
            "access_token": access_token,
            "refresh_token": refresh_token
        })


class JiraOAuthRefreshToken(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = JiraGetProjectSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data.get('cloud_name')

        try:
            cloudObj = JiraUser.objects.get(name=name)
        except JiraUser.DoesNotExist:
            return Response({"error": "Cloud instance not found"}, status=status.HTTP_404_NOT_FOUND)

        refresh_url = "https://auth.atlassian.com/oauth/token"
        refresh_data = json.dumps({
            "grant_type": "refresh_token",
            "client_id": settings.JIRA_CLIENT_ID,
            "client_secret": settings.JIRA_CLIENT_SECRET,
            "refresh_token": cloudObj.refresh_token
        })
        refresh_headers = {'Content-Type': 'application/json'}

        auth_response = requests.post(
            refresh_url, headers=refresh_headers, data=refresh_data).json()

        cloudObj.access_token = auth_response.get('access_token')
        cloudObj.refresh_token = auth_response.get('refresh_token')
        cloudObj.save()

        return Response({
            'access_token': auth_response.get('access_token'),
            'refresh_token': auth_response.get('refresh_token')
        }, status=status.HTTP_200_OK)


class JiraGetProjects(APIView):
    permission_classes = [IsCustomer]

    """
    API endpoint to fetch projects under the given cloud unit using the latest token.
    """

    def post(self, request):
        serializer = JiraGetProjectSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data.get('cloud_name')

        try:
            cloudObj = JiraUser.objects.get(name=name)
        except JiraUser.DoesNotExist:
            return Response({"error": "Cloud instance not found"}, status=status.HTTP_404_NOT_FOUND)

        refresh_url = "https://auth.atlassian.com/oauth/token"
        refresh_call = json.dumps({
            "grant_type": "refresh_token",
            "client_id": settings.JIRA_CLIENT_ID,
            "client_secret": settings.JIRA_CLIENT_SECRET,
            "refresh_token": cloudObj.refresh_token
        })
        refresh_headers = {'Content-Type': 'application/json'}

        auth_response = requests.post(
            refresh_url, headers=refresh_headers, data=refresh_call).json()

        cloudObj.access_token = auth_response.get('access_token')
        cloudObj.refresh_token = auth_response.get('refresh_token')
        cloudObj.save()

        url = f"https://api.atlassian.com/ex/jira/{cloudObj.cloudId}/rest/api/3/project"
        headers = {
            'Authorization': f'Bearer {auth_response.get("access_token")}'}

        response = requests.get(url, headers=headers)

        return Response(response.json(), status=response.status_code)

class JiraRaiseTicket(APIView):
    """
    API endpoint to raise a ticket in a specific project of a cloud unit.
    """
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = JiraIssueSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        cloud_obj = get_cloud_object(data['cloud_name'])

        try:
            issue_config = JiraIssueConfigs.objects.get(
                program_id=data['program_id'])
            issue_type = issue_config.issue_type
        except Exception:
            return Response({"error": "no such configs present"}, status=status.HTTP_404_NOT_FOUND)

        url = f"https://api.atlassian.com/ex/jira/{cloud_obj.cloudId}/rest/api/3/issue"
        headers = {
            "Content-Type": "application/json",
            'Authorization': f"Bearer {cloud_obj.access_token}"
        }

        payload = json.dumps({
            "fields": {
                "project": {"key": data['project_key']},
                "summary": data['submission_id'],
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {"type": "paragraph", "content": [
                            {"type": "text", "text": data['description']}]}
                    ]
                },
                "issuetype": {"name": issue_type}
            }
        })

        response = requests.post(url, headers=headers, data=payload)
        status_code = response.status_code
        response = response.json()

        if status_code != 201:
            return Response({"error": response}, status_code)

        try:
            program = Programs.objects.get(id=data['program_id'])
            submission = Submission.objects.get(id=data['submission_id'])

            issue_obj = JiraProgramIssue(
                issue_id=response['id'], submission_id=submission, program_id=program, project_key=data['project_key'])
            issue_obj.save()
        except Exception as error:
            return Response({"error": "failed to save issue"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status_code)


class JiraGetProjectCategories(APIView):
    permission_classes = [IsCustomer]

    """
    API endpoint to fetch project categories defined by the user for a specific cloud unit.
    """

    def post(self, request):
        serializer = JiraGetProjectSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data.get('cloud_name')
        cloudObj = JiraUser.objects.get(name=name)

        url = f"https://api.atlassian.com/ex/jira/{cloudObj.cloudId}/rest/api/3/projectCategory"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {cloudObj.access_token}"
        }

        response = requests.get(url, headers=headers)

        return Response(response.json(), status=response.status_code)


class JiraGetProjectType(APIView):
    permission_classes = [IsCustomer]

    """
    API endpoint to fetch project types defined by Atlassian.
    """

    def post(self, request):
        serializer = JiraGetProjectSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data.get('cloud_name')
        cloudObj = get_cloud_object(name)

        url = f"https://api.atlassian.com/ex/jira/{cloudObj.cloudId}/rest/api/3/project/type"

        response = requests.get(url)
        project_keys = [{'type': types['key']} for types in response.json()]

        return Response(project_keys, status=response.status_code)

class JiraMapProjectProgram(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = JiraMapProgramProjectSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        project_key = data['project_key']
        project_name = data['project_name']
        cloud_name = data['cloud_name']
        user_id = self.request.user.id

        try:
            program = Programs.objects.get(id=data['program_id'])
            jira_instance = JiraUser.objects.get(name=cloud_name)
            user = User.objects.get(id=user_id)
            if JiraProgramMapper.objects.filter(project_key=project_key, program_id=program, jira_instance=jira_instance, is_deleted=False).exists():
                return Response({"error": "project already mapped to a program"}, status=status.HTTP_400_BAD_REQUEST)

            mapper_obj = JiraProgramMapper(program_id=program, project_key=project_key,
                                           project_name=project_name, jira_instance=jira_instance, user_id=user)
            mapper_obj.save()
        except Exception:
            return Response({"error": "unable to map program id with project id"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "project mapped successfully"}, status=status.HTTP_201_CREATED)


"""
    This api will setup issue configurations for a user.
"""


class JiraSetupIssueConfigs(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = JiraIssueConfigSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            program = Programs.objects.get(id=data['program_id'])

            config_obj = JiraIssueConfigs(program_id=program,
                                          submission_state=data['submission_state'],
                                          issue_type=data['issue_type'],
                                          include_public_and_private_comments=data[
                                              'include_public_and_private_comments'],
                                          automatic_issue_creation=data['automatic_issue_creation'])
            config_obj.save()

        except Exception:
            return Response({"error": "problem setting up user's issue configs."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "config successfully saved"}, status=status.HTTP_201_CREATED)


"""
    This api will register user's comment to some issue.
"""


class JiraRegisterCommentToIssue(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = JiraCommentSerialzier(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            issue_obj = JiraProgramIssue.objects.get(
                submission_id=data['submission_id'])
        except Exception as error:
            return Response({"error": "issue does not exists"}, status=status.HTTP_404_NOT_FOUND)

        cloud_obj = get_cloud_object(data['cloud_name'])

        url = f"https://api.atlassian.com/ex/jira/{cloud_obj.cloudId}/rest/api/3/issue/{issue_obj.issue_id}/comment"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            'Authorization': f'Bearer {cloud_obj.access_token}'
        }

        payload = json.dumps({
            "body": {
                "content": [
                    {
                        "content": [
                            {
                                "text": f"{data['description']}",
                                "type": "text"
                            }
                        ],
                        "type": "paragraph"
                    }
                ],
                "type": "doc",
                "version": 1
            }
        })

        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers,
        )

        return Response(response.json(), status=response.status_code)


class JiraGetAllInstances(generics.ListCreateAPIView):
    permission_classes = [IsCustomer]
    # pagination_class = CustomPageNumberPagination
    serializer_class = JiraUserSerializer
    
    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        user = get_object_or_404(User, id=user_id)

        id = request.GET.get('id')
        cloudId = request.GET.get('cloudId')
        name = request.GET.get('name')
        url = request.GET.get('url')

        # Apply filtering if parameters are present
        queryset = JiraUser.objects.filter(user_id=user, is_deleted=False)
        if id:
            queryset = queryset.filter(id__icontains=id)
        if cloudId:
            queryset = queryset.filter(cloudId__icontains=cloudId)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if url:
            queryset = queryset.filter(url__icontains=url)

        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JiraUserSerializer(queryset, many=True)
        return Response(serializer.data)


class JiraShutOfInstance(APIView):
    permission_classes = [IsCustomer]

    def delete(self, request, cloudId=None):
        queryset = JiraUser.objects.filter(is_deleted=False, name=cloudId)
        jira_user = get_object_or_404(queryset)
        jira_user.delete()
        return Response(status=status.HTTP_200_OK)


class JiraGetAllMappedProjects(generics.ListCreateAPIView):
    permission_classes = [IsCustomer]
    field_error = {"error": "field error"}
    serializer_class = JiraProgramMapperSerializer
    # pagination_class = CustomPageNumberPagination

    def list(self, request, *args, **kwargs):
        filters = {"user_id": request.user, "is_deleted": False}

        # Get query parameters
        program_id = request.GET.get("program_id")
        program_title = request.GET.get("program_title")
        cloud_name = request.GET.get("cloud_name")

        # Apply filters if parameters are present
        if program_id:
            filters["program_id__program_id__icontains"] = program_id
        if program_title:
            filters["program_id__program_title__icontains"] = program_title
        if cloud_name:
            filters["jira_instance__name__icontains"] = cloud_name

        # Query the SlackUser model with the filters
        # cloud_name = data['cloud_name']
        jira_user = JiraProgramMapper.objects.filter(**filters)
        page = self.paginate_queryset(jira_user)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JiraUserSerializer(filters, many=True)
        return Response(serializer.data)


class JiraUserDelete(generics.DestroyAPIView):
    permission_classes = [IsCustomer]
    field_error = {"error": "field error"}
    queryset = JiraProgramMapper.objects.filter(is_deleted=False)
    serializer_class = JiraProgramMapperSerializer
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            headers={"message": "project successfully unmapped"},
            status=status.HTTP_204_NO_CONTENT,
        )


class JiraGetMappedProjects(APIView):
    permission_classes = [IsCustomer]

    def get(self, request, *args, **kwargs):
        project_name = request.GET.get('project_name')
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        data = JiraProgramMapper.objects.filter(
            project_key__icontains=project_name, user_id=user)
        serializer = JiraProgramMapperSerializer(data, many=True)
        return Response(serializer.data)


class JiraGetIssueConfig(APIView):
    permission_classes = [IsCustomer]

    def get(self, request, *args, **kwargs):
        # Validate request data using the serializer
        serializer = JiraIssueConfigsGetSerializer(data=request.data)

        if not serializer.is_valid():
            raise ValidationError({"error": "field error"})

        data = serializer.validated_data

        program_id = data['program_id']
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        if not Programs.objects.filter(id=program_id).exists():
            raise ValidationError({"error": "program does not exist."})

        program = Programs.objects.get(id=program_id)

        id = request.GET.get('id')
        submission_state = request.GET.get('submission_state')
        issue_type = request.GET.get('issue_type')

        queryset = JiraIssueConfigs.objects.filter(
            program_id=program, user_id=user, is_deleted=False
        )

        if id:
            queryset = queryset.filter(id__icontains=id)
        if submission_state:
            queryset = queryset.filter(
                submission_state__icontains=submission_state)
        if issue_type:
            queryset = queryset.filter(issue_type__icontains=issue_type)

        # Serialize the filtered queryset
        serializer = JiraIssueConfigSerializer(queryset, many=True)
        return Response(serializer.data)
