from rest_framework import serializers
from . models import User,Programs
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

class Userserializer(serializers.ModelSerializer):
    username = serializers.CharField(required =True)
    email = serializers.CharField(required = True)
    password = serializers.CharField(min_length=5, max_length=15, write_only=True)
    confirm_password = serializers.CharField(min_length=5, max_length=15, write_only=True)
    first_name = serializers.CharField(required =True)
    last_name = serializers.CharField(required =True)
    phone_no = serializers.CharField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    Short_Description = serializers.CharField(required=True)
    display_pic = serializers.FileField(required = False)
    class Meta:
        model = User
        fields = ('id', 
                  'username', 
                  'email', 
                  'first_name',
                  'last_name',
                  'password',
                  'phone_no',
                  'confirm_password',
                  'Short_Description',
                  'display_pic')

    def validate_username(self, value):
        user_name = self.instance.username if self.instance else None
        if User.objects.filter(username=value).exclude(username=user_name).exists(): #checks if username already exists!
            raise serializers.ValidationError("Username already exists!")
        if not value.isalnum():
            raise serializers.ValidationError("Username should contain only alphanumeric characters!")
        return value
    
    # Validation for email
    def validate_email(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email=value).exclude(id=user_id).exists():# checks if the email already exists
            raise serializers.ValidationError("Email already exists!")
        return value
       
    def validate(self, value):
        if value['password'] != value['confirm_password']:
         raise serializers.ValidationError({'password': 'Passwords do not match'})
        first_name = value.get('first_name', '')
        if first_name and first_name.isupper(): # checks if firstname exist and is uppercase
             serializers.ValidationError({'firstname': 'First name should not be in uppercase.'})
            
        return value
    
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        validated_data["role"] = "admin"
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user    
    

class Loginserializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields =['username','password','token']

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid username or password")
        return data  

class Customerserializer(serializers.ModelSerializer):
    username = serializers.CharField(required =True)
    email = serializers.CharField(required = True)
    password = serializers.CharField(min_length=5, max_length=15, write_only=True)
    confirm_password = serializers.CharField(min_length=5, max_length=15, write_only=True)
    first_name = serializers.CharField(required =True)
    last_name = serializers.CharField(required =True)
    Phone_no = serializers.CharField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    Short_Description = serializers.CharField(required=True)
    display_pic = serializers.FileField(required = False)

    def get_dispaly_pic(self, obj):
        request = self.context.get('request')
        if obj.display_pic:
            return request.build_absolute_uri(obj.display_pic.url)
        return None


    class Meta:
        model = User
        fields = ('id', 
                  'username', 
                  'email', 
                  'first_name',
                  'last_name',
                  'Phone_no',
                  'password',
                  'confirm_password',
                  'Short_Description',
                  'display_pic')

    def validate_username(self, value):
        user_name = self.instance.username if self.instance else None
        if User.objects.filter(username=value).exclude(username=user_name).exists(): #checks if username already exists!
            raise serializers.ValidationError("Username already exists!")
        if not value.isalnum():
            raise serializers.ValidationError("Username should contain only alphanumeric characters!")
        return value
    
    # Validation for email
    def validate_email(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email=value).exclude(id=user_id).exists():# checks if the email already exists
            raise serializers.ValidationError("Email already exists!")
        return value
       
    def validate(self, value):
        if value['password'] != value['confirm_password']:
         raise serializers.ValidationError({'password': 'Passwords do not match'})
        first_name = value.get('first_name', '')
        if first_name and first_name.isupper(): # checks if firstname exist and is uppercase
             serializers.ValidationError({'firstname': 'First name should not be in uppercase.'})
            
        return value
    
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            Phone_no=validated_data['Phone_no'],
            Short_Description= validated_data['Short_Description'],
            display_pic=validated_data['display_pic'],
            role='customer',
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user   

class Researcherserializer(serializers.ModelSerializer):
    username = serializers.CharField(required =True)
    email = serializers.CharField(required = True)
    password = serializers.CharField(min_length=5, max_length=15, write_only=True)
    confirm_password = serializers.CharField(min_length=5, max_length=15, write_only=True)
    first_name = serializers.CharField(required =True)
    last_name = serializers.CharField(required =True)
    Phone_no = serializers.CharField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    Short_Description = serializers.CharField(required=True)
    display_pic = serializers.FileField(required = False)
    class Meta:
        model = User
        fields = ('id', 
                  'username', 
                  'email', 
                  'first_name',
                  'last_name',
                  'Phone_no',
                  'password',
                  'confirm_password',
                  'Short_Description',
                  'display_pic')

    def validate_username(self, value):
        user_name = self.instance.username if self.instance else None
        if User.objects.filter(username=value).exclude(username=user_name).exists(): #checks if username already exists!
            raise serializers.ValidationError("Username already exists!")
        if not value.isalnum():
            raise serializers.ValidationError("Username should contain only alphanumeric characters!")
        return value
    
    # Validation for email
    def validate_email(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email=value).exclude(id=user_id).exists():# checks if the email already exists
            raise serializers.ValidationError("Email already exists!")
        return value
       
    def validate(self, value):
        if value['password'] != value['confirm_password']:
         raise serializers.ValidationError({'password': 'Passwords do not match'})
        first_name = value.get('first_name', '')
        if first_name and first_name.isupper(): # checks if firstname exist and is uppercase
             serializers.ValidationError({'firstname': 'First name should not be in uppercase.'})
            
        return value
    
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            Phone_no=validated_data['Phone_no'],
            Short_Description=validated_data['Short_Description'],
            display_pic=validated_data['display_pic'],
            role='researcher',
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user     


class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        # Check if user exists
        user_data = User.objects.filter(email=username).first()
        if not user_data:
            raise AuthenticationFailed("Incorrect login details. Please try again.")

        # Authenticate user
        user = authenticate(
            request=self.context.get("request"),
            username=user_data.email,
            password=password,
        )

        if not user:
            raise AuthenticationFailed("Invalid credentials. Please try again.")

        # Check if the user is a customer or researcher
        if user_data.role.lower() not in ["customer", "researcher"]:
            raise AuthenticationFailed("Access denied. Invalid role.")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user_data.role,  # Return role in response
            "user": user,
        }


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programs
        fields = '__all__'
