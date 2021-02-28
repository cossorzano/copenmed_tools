from django.db import models

# Create your models here.

class Card(models.Model):
    entity = models.CharField(max_length=200)
    family = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    resources = models.URLField(max_length=200, null=True)
    updated_on = models.DateTimeField(auto_now= True)

    def __str__(self):
        return self.family + " - " + self.entity
