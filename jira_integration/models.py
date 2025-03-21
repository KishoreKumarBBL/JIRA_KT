from django.db import models
import uuid
from programs.models import User,Programs
from submissions.models import Submission
from django.utils import timezone

class JiraUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cloudId = models.CharField(max_length=255, null=False)
    name = models.TextField(null=False)
    url = models.TextField(null = False)
    access_token = models.TextField(null=True)
    refresh_token = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def __str__(self) -> str:
        return self.cloudId
    
class JiraProgramMapper(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable=False)
    program_id = models.ForeignKey(Programs, on_delete=models.CASCADE, null= True, blank= True)
    project_key = models.CharField(max_length= 255, null= True)
    project_name = models.CharField(max_length= 255, null= True)
    jira_instance = models.ForeignKey(JiraUser, on_delete= models.CASCADE, null=True, blank= True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    mapped_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return str(self.id)
class JiraProgramIssue(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable=False)
    issue_id = models.CharField(max_length=255, null= True)
    submission_id = models.ForeignKey(Submission, on_delete= models.CASCADE, null= True, blank= True)
    program_id = models.ForeignKey(Programs, on_delete=models.CASCADE, null= True, blank= True)
    project_key = models.CharField(max_length= 255, null= True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    
class JiraIssueConfigs(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    program_id = models.ForeignKey(Programs, on_delete=models.CASCADE, null= True, blank= True)
    submission_state = models.CharField(max_length= 255)
    issue_type = models.CharField(max_length= 255)
    include_public_and_private_comments = models.BooleanField(default = False)
    automatic_issue_creation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
