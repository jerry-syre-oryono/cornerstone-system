from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class RegisterAlumniSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    graduation_year = serializers.IntegerField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_again = serializers.CharField(write_only=True)
