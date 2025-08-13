from django_filters.rest_framework import FilterSet
from services.models import Services

class ServiceFilter(FilterSet):
    class Meta:
        model = Services
        fields ={
            'category_id' : ['exact'],
            'price' : ['gt','lt']
        }
 
        
