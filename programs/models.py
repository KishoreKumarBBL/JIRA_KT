import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class UserManagement(BaseUserManager):
    def create_user(self,username,first_name,last_name,email,password=None,**extra_fields):
        if not username:
            raise ValueError('Users must have an username')
        if not email:
            raise ValueError('user must have a email id')
        user = self.model(username = username, 
                          email = self.normalize_email(email),
                          first_name = first_name,
                          last_name = last_name,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,username,first_name,last_name,email,password=None,**extra_fields):
        user = self.create_user(username= username,
                                first_name= first_name,
                                last_name=last_name ,
                                email=self.normalize_email(email),
                                **extra_fields)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_superadmin = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    USER_ROLE_CHOICES = (
        ("admin", "Admin"),
        ("customer", "Customer"),
        ("researcher", "Researcher"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255,unique=True)
    email = models.EmailField(max_length=255,unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    Phone_no = models.CharField(max_length=13,blank=True)
    role = models.CharField(max_length=10,choices=USER_ROLE_CHOICES,default="customer")
    display_pic = models.ImageField(upload_to='user/pic', blank=True,)
    Short_Description = models.CharField(max_length=250)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = ("email")
    REQUIRED_FIELDS = ["username","first_name", "last_name"]

    objects = UserManagement()

    def __str__(self):
        return self.email
    
    def has_module_perms(self, app_level):
        return True

class userprofile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=30)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        

def validate_file_size(value):
    filesize = value.size

    # Max file size (in bytes)
    max_file_size = 5 * 1024 * 1024  # 5 MB

    if filesize > max_file_size:
        raise ValidationError(_("The maximum file size that can be uploaded is 5MB"))

class Programs(models.Model):
    PROGRAM_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("in_progess", "In-Progress"),
        ("approved", "Approved"),
        ("hold", "Hold"),
        ("closed", "Closed"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "customer"},
        null=True,
        blank=True,
    )
    program_type = models.CharField(max_length=250)
    program_package = models.CharField(max_length=250)
    program_title = models.CharField(max_length=250)
    project_description = models.TextField()
    private_program = models.CharField(max_length=250, null=True, blank=True)
    program_attachments = models.FileField(
        upload_to="program/attachments/",
        validators=[validate_file_size],
        blank=True,
        null=True,
    )
    project_tags = models.CharField(max_length=250, null=True, blank=True)
    scope_title = models.CharField(max_length=250, null=True, blank=True)
    scope_items_url1 = models.CharField(max_length=250, null=True, blank=True)
    out_Of_scope_item_url1 = models.CharField(max_length=250, null=True, blank=True)
    severity = models.CharField(max_length=50)
    expected_vulnerability_types = models.TextField(null=True, blank=True)
    p1_reward_amt = models.FloatField(null=True, blank=True)
    maximun_budget = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    testing_allowed = models.CharField(max_length=250)
    language_framworks = models.CharField(max_length=250)
    asset_environments = models.CharField(max_length=250)
    taxonomy_doc1 = models.FileField(
        upload_to="program/taxonomy1/",
        validators=[validate_file_size],
        null=True,
        blank=True,
    )
    upload_doc1 = models.FileField(
        upload_to="program/doc1/",
        validators=[validate_file_size],
        null=True,
        blank=True,
    )
    program_status = models.CharField(
        max_length=10, choices=PROGRAM_STATUS_CHOICES, blank=True, null=True
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.program_title    