from rest_framework import serializers
from services.models import Category,Services,Review,ServiceImage
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    service_count = serializers.IntegerField(read_only = True)
    class Meta:
        model = Category
        fields = ['id','name','description','service_count']

    

class ServiceImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        ref_name = 'ServiceImageSerializerServices'
        model = ServiceImage
        fields = ['id','image']

class ServiceSerializer(serializers.ModelSerializer):
    images = ServiceImageSerializer(many = True, read_only = True)
    new_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(),write_only = True)

    seller = UserSerializer(read_only = True)
    class Meta:
        model = Services
        fields = ['id','title','images','price','requirements','delivery_time','seller','category','new_images','category_id']
        read_only_fields = ['seller']

    def validate_price(self,price):
        if price < 0:
            raise serializers.ValidationError("Price could not be negative")
        else:
            return price
        
    def create(self, validated_data):
        new_images = validated_data.pop('new_images', [])
        service = Services.objects.create(**validated_data)
        for image in new_images:
            ServiceImage.objects.create(service=service, image=image)
        return service

    def update(self, instance, validated_data):
        new_images = validated_data.pop('new_images', [])
        instance.title = validated_data.get('title', instance.title)
        instance.requirements = validated_data.get('requirements', instance.requirements)
        instance.price = validated_data.get('price', instance.price)
        instance.delivery_time = validated_data.get('delivery_time', instance.delivery_time)
        instance.category = validated_data.get('category_id', instance.category)
        instance.save()

        for image in new_images:
            ServiceImage.objects.create(service=instance, image=image)

        return instance



class SimpleUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(
        method_name='get_current_user_name'
    )
    class Meta:
        model = get_user_model()
        fields = ['id','name']

    def get_current_user_name(self,obj):
        return obj.get_full_name()


class ReviewSerializer(serializers.ModelSerializer):
    buyer = serializers.SerializerMethodField(
        method_name='get_user'
    )
    class Meta:
        model = Review
        fields = ['id','buyer','service','rating','comment']
        read_only_fields = ['buyer','service']
    
    def get_user(self,obj):
        return SimpleUserSerializer(obj.buyer).data
    
    # def create(self,validated_data):
    #     service_id = self.context['service_id']
    #     review = Review.objects.create(service_id = service_id, **validated_data) 
    #     return review



class ServiceImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = ServiceImage
        fields = ['id','image']


class SellerService(serializers.ModelSerializer):
    images = ServiceImageSerializer(many = True, read_only = True)
    class Meta:
        model = Services
        fields = ['id','title','images','price','requirements','delivery_time','seller','category']
        read_only_fields = ['seller']

    def validate_price(self,price):
        if price < 0:
            raise serializers.ValidationError("Price could not be negative")
        else:
            return price
