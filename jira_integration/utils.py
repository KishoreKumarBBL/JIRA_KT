from django.conf import settings
import requests
import json
from .models import JiraUser

templates = {
    'business': [
                'com.atlassian.jira-core-project-templates:jira-core-simplified-content-management', 
                'com.atlassian.jira-core-project-templates:jira-core-simplified-document-approval', 
                'com.atlassian.jira-core-project-templates:jira-core-simplified-lead-tracking', 
                'com.atlassian.jira-core-project-templates:jira-core-simplified-process-control', 
                'com.atlassian.jira-core-project-templates:jira-core-simplified-procurement', 
                'com.atlassian.jira-core-project-templates:jira-core-simplified-project-management', 
                'com.atlassian.jira-core-project-templates:jira-core-simplified-recruitment', 
                'com.atlassian.jira-core-project-templates:jira-core-simplified-task-tracking'
            ], 
    'service_desk': [
                'com.atlassian.servicedesk:simplified-it-service-management', 
                'com.atlassian.servicedesk:simplified-general-service-desk-it', 
                'com.atlassian.servicedesk:simplified-general-service-desk-business', 
                'com.atlassian.servicedesk:simplified-external-service-desk', 
                'com.atlassian.servicedesk:simplified-hr-service-desk', 
                'com.atlassian.servicedesk:simplified-facilities-service-desk', 
                'com.atlassian.servicedesk:simplified-legal-service-desk', 
                'com.atlassian.servicedesk:simplified-analytics-service-desk', 
                'com.atlassian.servicedesk:simplified-marketing-service-desk', 
                'com.atlassian.servicedesk:simplified-design-service-desk', 
                'com.atlassian.servicedesk:simplified-sales-service-desk', 
                'com.atlassian.servicedesk:simplified-blank-project-business', 
                'com.atlassian.servicedesk:simplified-blank-project-it', 
                'com.atlassian.servicedesk:simplified-finance-service-desk', 
                'com.atlassian.servicedesk:next-gen-it-service-desk', 
                'com.atlassian.servicedesk:next-gen-hr-service-desk', 
                'com.atlassian.servicedesk:next-gen-legal-service-desk', 
                'com.atlassian.servicedesk:next-gen-marketing-service-desk', 
                'com.atlassian.servicedesk:next-gen-facilities-service-desk', 
                'com.atlassian.servicedesk:next-gen-general-it-service-desk', 
                'com.atlassian.servicedesk:next-gen-general-business-service-desk', 
                'com.atlassian.servicedesk:next-gen-analytics-service-desk', 
                'com.atlassian.servicedesk:next-gen-finance-service-desk', 
                'com.atlassian.servicedesk:next-gen-design-service-desk', 
                'com.atlassian.servicedesk:next-gen-sales-service-desk'
            ], 
    'software': [
                'com.pyxis.greenhopper.jira:gh-simplified-agility-kanban', 
                'com.pyxis.greenhopper.jira:gh-simplified-agility-scrum', 
                'com.pyxis.greenhopper.jira:gh-simplified-basic',
                'com.pyxis.greenhopper.jira:gh-simplified-kanban-classic', 
                'com.pyxis.greenhopper.jira:gh-simplified-scrum-classic'
            ]}

notification_types = [
        {
            "notificationType": "CurrentAssignee"
        },
        {
            "notificationType": "Reporter"
        },
        {
            "notificationType": "CurrentUser"
        },
        {
            "notificationType": "ProjectLead"
        },
        {
            "notificationType": "ComponentLead"
        },
        {
            "notificationType": "User",
            "parameter": "exampleuser"  
        },
        {
            "notificationType": "Group",
            "parameter": "jira-administrators"  
        },
        {
            "notificationType": "ProjectRole",
            "parameter": "10002"  
        },
        {
            "notificationType": "EmailAddress",
            "parameter": "example@example.com" 
        },
        {
            "notificationType": "AllWatchers"
        },
        {
            "notificationType": "UserCustomField",
            "parameter": "customfield_10000"  
        },
        {
            "notificationType": "GroupCustomField",
            "parameter": "customfield_10001"  
        }
    ]

def get_cloud_object(name):

    cloudObj = JiraUser.objects.get(name = name)
            
    refresh_url = "https://auth.atlassian.com/oauth/token"

    refresh_call = json.dumps({
        "grant_type": "refresh_token",
        "client_id": settings.JIRA_CLIENT_ID,
        "client_secret": settings.JIRA_CLIENT_SECRET,
        "refresh_token": cloudObj.refresh_token
    })
    refresh_headers = {
        'Content-Type': 'application/json'
    }

    auth_response = json.loads(requests.request("POST", refresh_url, headers=refresh_headers, data=refresh_call).text)
    
    cloudObj.access_token = auth_response.get('access_token')
    cloudObj.refresh_token = auth_response.get('refresh_token')
    cloudObj.save()
    
    return cloudObj