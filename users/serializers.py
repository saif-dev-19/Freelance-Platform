from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer




class CustomUserCreateSerializer(UserCreateSerializer): #post er jonno
    class Meta(UserCreateSerializer.Meta):
        fields = ['id','email','password','first_name','last_name','role','address','phone_number']


class CustomUserSerializer(UserSerializer): #get,put,patch er jonno
    class Meta(UserSerializer.Meta):
        fields = ['id','email','first_name','last_name','role','address','phone_number','is_staff', 'is_superuser']
        read_only_fields = ['email','role','is_staff', 'is_superuser']