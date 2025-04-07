from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


# Create your models here.

class News(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='news_images/', null=True, blank=True)
    description = models.TextField()
    content = CKEditor5Field()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title
