from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class Review(models.Model):
    username = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
