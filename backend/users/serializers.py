from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'is_alumni', 'gender',
            'profile_photo', 'phone_number', 'nationality', 'bio', 'marital_status',
            'spouse_full_name', 'spouse_phone', 'spouse_email', 'spouse_occupation',
            'cla_campus', 'high_school_graduation_year', 'academic_status',
            'university_institution', 'university_course', 'university_graduation_year',
            'expected_graduation_year', 'address_country', 'address_district_region',
            'address_city_town', 'address_po_box', 'address_physical_street',
            'employment_status', 'employer_company_name', 'job_title_role',
            'industry_sector', 'work_location', 'work_year_started', 'work_email',
            'work_phone', 'linkedin_profile'
        ]

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'gender',
            'profile_photo', 'phone_number', 'nationality', 'bio', 'marital_status',
            'spouse_full_name', 'spouse_phone', 'spouse_email', 'spouse_occupation',
            'cla_campus', 'high_school_graduation_year', 'academic_status',
            'university_institution', 'university_course', 'university_graduation_year',
            'expected_graduation_year', 'address_country', 'address_district_region',
            'address_city_town', 'address_po_box', 'address_physical_street',
            'employment_status', 'employer_company_name', 'job_title_role',
            'industry_sector', 'work_location', 'work_year_started', 'work_email',
            'work_phone', 'linkedin_profile'
        ]
        # Ensure all fields are optional for partial updates in Swagger/API
        extra_kwargs = {field: {'required': False} for field in fields}
