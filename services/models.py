from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator,MinValueValidator
from services.validators import validate_file_size
from cloudinary.models import CloudinaryField
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name
    

class Services(models.Model):
    title = models.CharField(max_length=100)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="services")
    requirements = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category,on_delete=models.CASCADE, related_name='services')
    delivery_time = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    service = models.ForeignKey(Services,on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now= True)


    def __str__(self):
        return f"Review by {self.buyer.first_name} on {self.service}"
    

class ServiceImage(models.Model):
    service = models.ForeignKey(Services,on_delete=models.CASCADE, related_name="images")
    image = CloudinaryField('image')
    # image = models.ImageField(upload_to= 'service/images/',validators=[validate_file_size]) 

    def __str__(self):
        return f"service {self.service} and id {self.id}"