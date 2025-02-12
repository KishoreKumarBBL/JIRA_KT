from django.db import models

# Create your models here.
class Submission(models.Model):
    id = models.UUIDField(primary_key=True)

