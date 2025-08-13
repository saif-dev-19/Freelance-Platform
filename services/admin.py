from django.contrib import admin
from services.models import Services,Category,Review
# Register your models here.
admin.site.register(Services)
admin.site.register(Category)
admin.site.register(Review)