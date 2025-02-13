from django.db import models
import uuid
from django.core.exceptions import ValidationError
from programs.models import User,Programs



def validate_file(value):
    max_size = 5 * 1024 * 1024  # 5 MB in bytes
    if value.size > max_size:
        raise ValidationError("File size too large. Max size is 5MB.")



class Submission(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("triaged", "Triaged"),
        ("review", "Review"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
        ("unresolved", "UnResolved"),
    )
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    submissions_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    # date = models.DateField()
    submission_title = models.CharField(max_length=255)
    program_id = models.ForeignKey(Programs, on_delete=models.CASCADE)
    detail_description = models.TextField()
    step_to_reproduce = models.TextField(null=True, blank=True)
    remediation_recommendation = models.TextField(null=True, blank=True)
    severity = models.CharField(max_length=50, null=True, blank=True)
    target_url = models.CharField(max_length=250, null=True, blank=True)
    submission_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, blank=True, null=True
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.submission_title


