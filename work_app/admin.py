from django.contrib import admin
from .models import Word
from .models import Topic
from .models import Event
from .models import WordTraining
from .models import UserSettings
from .models import EssayTheme
from .models import UserEssay
from .models import UserLog
from .models import WordPicture
from .models import GrammarSection
from .models import GrammarRule

# Register your models here.
admin.site.register(Word)
admin.site.register(Topic)
admin.site.register(Event)
admin.site.register(WordTraining)
admin.site.register(UserSettings)
admin.site.register(EssayTheme)
admin.site.register(UserEssay)
admin.site.register(UserLog)
admin.site.register(WordPicture)
admin.site.register(GrammarRule)
admin.site.register(GrammarSection)

class WordAdmin(admin.ModelAdmin):
    list_display = ('main_word')