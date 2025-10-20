from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers


class CustomUserCreateSerializer(UserCreateSerializer): #post er jonno
    class Meta(UserCreateSerializer.Meta):
        fields = ['id','email','password','first_name','last_name','role','address','phone_number']
        ref_name = 'CustomUserCreate'

class CustomUserSerializer(UserSerializer): #get,put,patch er jonno
    class Meta(UserSerializer.Meta):
        fields = ['id','email','first_name','last_name','role','address','phone_number','is_staff', 'is_superuser']
        read_only_fields = ['email','role','is_staff', 'is_superuser']
        ref_name = 'CustomUser'

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        ref_name = 'MyUserModelSerializer'