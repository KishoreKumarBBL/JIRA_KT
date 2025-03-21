from .serializers import JiraIssueConfigsGetSerializer, JiraIssueConfigSerializer, JiraMapIdSerializer, JiraGetProjectSerializer, JiraNotificationSerializer, JiraIssueSerializer, JiraCreateProjectSerializer, JiraMapProgramProjectSerializer, JiraIssueConfigSerializer, JiraCommentSerialzier, JiraUserSerializer, JiraProgramMapperSerializer
from .models import JiraUser, JiraProgramIssue, JiraIssueConfigs, JiraProgramMapper
import json
from .utils import get_cloud_object, templates
from rest_framework import status
import requests
from submissions.models import Submission
from programs.models import Programs


def add_jira_comment(submission_id, description, cloud_name):
    #     cloud_name = serializers.CharField(max_length = 255)
    #     description = serializers.CharField(max_length = 1000)
    #     submission_id = serializers.CharField(max_length = 255)

    data = {
        "description": description,
        "submission_id": submission_id,
        "cloud_name": cloud_name
    }

    try:
        issue_obj = JiraProgramIssue.objects.get(
            submission_id=data['submission_id'])
    except Exception as error:
        return {"error": "issue does not exists"}, status.HTTP_404_NOT_FOUND

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

    return response.json(), response.status_code


def create_submission_jira_ticket(cloud_name, program_id, project_key, submission_id, submission_bs_id, description, issue_type):
    
    data = {
        "cloud_name": cloud_name,
        "program_id": program_id,
        "project_key": project_key,
        "submission_id": submission_id,
        "description": description
    }
    
    print(f"[*] Creating Jira Ticket with Data: {data}")

    cloud_obj = get_cloud_object(data['cloud_name'])
    print(f"[*] Retrieved Cloud Object: {cloud_obj}")

    url = f"https://api.atlassian.com/ex/jira/{cloud_obj.cloudId}/rest/api/3/issue"
    headers = {
        "Content-Type": "application/json",
        'Authorization': f"Bearer {cloud_obj.access_token}"
    }
    
    payload = json.dumps({
        "fields": {
            "project": {"id": data['project_key']},
            "summary": submission_bs_id,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [
                        {"type": "text", "text": data['description']}]}
                ]
            },
            "issuetype": {"name": "Task"}
        }
    })

    print(f"[*] Sending Jira API Request to: {url}")
    print(f"[*] Headers: {headers}")
    print(f"[*] Payload: {payload}")

    response = requests.post(url, headers=headers, data=payload)
    status_code = response.status_code
    response_data = response.json()

    print(f"[*] Jira API Response Code: {status_code}")
    print(f"[*] Jira API Response Data: {response_data}")

    if status_code != 201:
        print(f"[!] Jira Ticket Creation Failed: {response_data}")
        return {"error": response_data}, status_code

    try:
        program = Programs.objects.get(id=data['program_id'])
        submission = Submission.objects.get(id=data['submission_id'])

        issue_obj = JiraProgramIssue(
            issue_id=response_data['id'], 
            submission_id=submission, 
            program_id=program, 
            project_key=data['project_key']
        )
        issue_obj.save()

        print(f"[*] Jira Issue Saved to Database: {issue_obj}")

    except Exception as error:
        print(f"[!] Failed to Save Jira Issue: {error}")
        return {"error": "failed to save issue"}, status.HTTP_500_INTERNAL_SERVER_ERROR

    return response_data, status_code