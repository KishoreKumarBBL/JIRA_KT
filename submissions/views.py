# from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from. models import Submission
from .serializers import Submissionserializer
from jira_integration.jira_services import create_submission_jira_ticket
from jira_integration.models import JiraUser,JiraProgramMapper
from rest_framework import status

class Submissions(ListCreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = Submissionserializer

    def create(self, request, *args, **kwargs):
        try:
            print("Received request data:", request.data)  # Debugging

            # Get program_id correctly
            program_id = request.data.get("program_id")  
            print("Extracted program_id:", program_id)

            if not program_id:
                return Response({"error": "Program ID is missing"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            submission = serializer.save()

            # Find Jira mapping
            jira_user_details = JiraProgramMapper.objects.filter(
                program_id=program_id, is_deleted=False
            ).first()

            if not jira_user_details:
                print(f"No JiraProgramMapper found for program_id: {program_id}")
                return Response({"error": "No Jira mapping found for this program"}, status=status.HTTP_404_NOT_FOUND)

            print("Jira User Details:", jira_user_details)

            # Find Jira user details
            jira_details = JiraUser.objects.filter(
                id=jira_user_details.jira_instance_id,  
                is_deleted=False,
            ).values().first()

            if not jira_details:
                print(f"No JiraUser found for ID: {jira_user_details.jira_instance_id}")
                return Response({"error": "No Jira user found"}, status=status.HTTP_404_NOT_FOUND)

            print("Jira Details:", jira_details)

            # Create Jira ticket
            create_submission_jira_ticket(
                cloud_name=jira_details.get("name"),
                program_id=program_id,
                description=serializer.data.get("detail_description"),
                submission_id=serializer.data.get("id"),
                project_key=jira_user_details.project_key,  
                submission_bs_id=serializer.data.get("submission_title"),  # Correct field
                issue_type=serializer.data.get("severity"),
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("Error:", str(e))  # Debugging
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)