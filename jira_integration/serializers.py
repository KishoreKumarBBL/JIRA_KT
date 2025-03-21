from rest_framework import serializers
from programs.serializers import ProgramSerializer
from .models import JiraUser, JiraProgramMapper, JiraIssueConfigs


class JiraGetProjectSerializer(serializers.Serializer):
    cloud_name = serializers.CharField(max_length=100)


class JiraNotificationSerializer(serializers.Serializer):
    notification_type = serializers.CharField(max_length=100)
    event_id = serializers.IntegerField()
    notification_name = serializers.CharField(max_length=255)
    notificatin_description = serializers.CharField(max_length=1000)
    cloud_name = serializers.CharField(max_length=100)


class JiraIssueSerializer(serializers.Serializer):
    submission_id = serializers.CharField(max_length=255)
    program_id = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    project_key = serializers.CharField(max_length=100)
    cloud_name = serializers.CharField(max_length=100)


class JiraCreateProjectSerializer(serializers.Serializer):
    cloud_name = serializers.CharField(max_length=100)
    category_id = serializers.CharField(max_length=100)
    lead_account_id = serializers.CharField(max_length=255)
    project_name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    notification_scheme = serializers.IntegerField()
    project_type = serializers.CharField(max_length=100)


class JiraMapProgramProjectSerializer(serializers.Serializer):
    project_key = serializers.CharField(max_length=255)
    program_id = serializers.CharField(max_length=255)
    project_name = serializers.CharField(max_length=255)
    cloud_name = serializers.CharField(max_length=255)


class JiraIssueConfigSerializer(serializers.Serializer):
    program_id = serializers.CharField(max_length=255)  # F
    submission_state = serializers.CharField(max_length=255)
    issue_type = serializers.CharField(max_length=255)
    include_public_and_private_comments = serializers.BooleanField(
        default=False)
    automatic_issue_creation = serializers.BooleanField(default=False)


class JiraCommentSerialzier(serializers.Serializer):
    cloud_name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    submission_id = serializers.CharField(max_length=255)


class JiraMapIdSerializer(serializers.Serializer):
    mapped_id = serializers.CharField(max_length=255)


class JiraIssueConfigsGetSerializer(serializers.Serializer):
    program_id = serializers.CharField(max_length=255)


class JiraUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraUser
        fields = '__all__'


class JiraUserDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraUser
        fields = ['cloudId']


class JiraProgramMapperSerializer(serializers.ModelSerializer):
    program_details = ProgramSerializer(source="program_id", read_only=True)
    jira_instance = JiraUserSerializer(read_only=True)

    class Meta:
        model = JiraProgramMapper
        fields = '__all__'


class JiraIssueConfigSerializer(serializers.ModelSerializer):

    program_details = ProgramSerializer(source="program_id", read_only=True)

    class Meta:
        model = JiraIssueConfigs
        fields = '__all__'
