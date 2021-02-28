from django.contrib import admin
from .models import Card

# Register your models here.

class CardAdmin(admin.ModelAdmin):
    list_display = ('entity', 'family', 'updated_on')
    list_filter = ("family",)
    search_fields = ['entity', 'description']

admin.site.register(Card, CardAdmin)
