from django.urls import path

from . import views
from .views import JiraOAuthView, JiraOAuthCallbackView, JiraUserDelete

urlpatterns = [
    path("jira/auth/login", JiraOAuthView.as_view(), name="jira_auth"),
    path("jira/auth/refresh-token", views.JiraOAuthRefreshToken.as_view()),
    path("jira/callback", JiraOAuthCallbackView.as_view(), name="jira_callback"),
    path("jira/list-project", views.JiraGetProjects.as_view(), name="list-project"),
    path("jira/raise-issue", views.JiraRaiseTicket.as_view(), name="raise-issue"),
    path(
        "jira/get-project-type",
        views.JiraGetProjectType.as_view(),
        name="get-project-type",
    ),
    path(
        "jira/get-project-categories",
        views.JiraGetProjectCategories.as_view(),
        name="get-project-categories",
    ),
    path(
        "jira/map-project",
        views.JiraMapProjectProgram.as_view(),
        name="map-project-program",
    ),
    path(
        "jira/set-issue-configs",
        views.JiraSetupIssueConfigs.as_view(),
        name="issue-configs",
    ),
    
    path(
        'jira/get-instances', 
        views.JiraGetAllInstances.as_view(), 
        name='get-instances'
    ),
    
    path(
        'jira/project-operation',
        views.JiraGetAllMappedProjects.as_view(),
        name='get-projects'
    ),
    
    path(
        'jira/get-issue-config',
        views.JiraGetIssueConfig.as_view(),
        name='get-issue-configs'
    ),
    path('jira/delete_mapping/<uuid:id>',
         JiraUserDelete.as_view(), name='delete_jira_user'),
]
