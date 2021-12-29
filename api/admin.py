from django.contrib import admin
from .models import Word
from .models import Topic

# Register your models here.
admin.site.register(Word)
admin.site.register(Topic)

class WordAdmin(admin.ModelAdmin):
    list_display = ('main_word')