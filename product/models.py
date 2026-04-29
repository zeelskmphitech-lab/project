from django.db import models
from users.models import Users

class Products(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    product_name = models.CharField(blank=False,null=False)
    product_type = models.CharField(blank=False,null=False,default="Not Available")
    company_name = models.CharField(blank=False,null=False,default="Not Available")
    section = models.CharField(blank=False,null=False,default="Not Available")
    description = models.TextField(blank=False,default="No Description Available.",null=False)
    price = models.DecimalField(decimal_places=1,max_digits=15)
    stoke = models.IntegerField(blank=False,null=False,default=1)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.product_name}"