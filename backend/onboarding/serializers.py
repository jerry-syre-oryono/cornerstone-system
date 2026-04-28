from rest_framework import serializers
from .models import SignupRequest, PasswordResetOTP
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class RegisterAlumniSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    graduation_year = serializers.IntegerField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_again = serializers.CharField(write_only=True)
    # Optional fields for when record is not found and a SignupRequest is created
    phone = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')], required=False, allow_null=True)
    course = serializers.CharField(required=False, allow_blank=True)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password_again = serializers.CharField(write_only=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetVerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class PasswordResetSetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, required=False)
    otp_code = serializers.CharField(max_length=6, required=False)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_again = serializers.CharField(write_only=True, min_length=8, required=False)
    confirm_password = serializers.CharField(write_only=True, min_length=8, required=False)

    def validate(self, data):
        otp = data.get('otp') or data.get('otp_code')
        if not otp:
            raise serializers.ValidationError("OTP code is required.")
        
        # Determine which password confirmation field to use
        confirm = data.get('confirm_password') or data.get('new_password_again')
        if not confirm:
            raise serializers.ValidationError("Password confirmation is required.")

        if data['new_password'] != confirm:
            raise serializers.ValidationError("Passwords do not match.")
        return data

class UserRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['admin', 'alumni'], help_text="The role to assign: 'admin' or 'alumni'")

class SignupRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignupRequest
        fields = ['full_name', 'email', 'graduation_year', 'phone', 'gender', 'course']

class AdminSignupRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignupRequest
        fields = '__all__'

class AdminCreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'is_alumni', 'gender']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
