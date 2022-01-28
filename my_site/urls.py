
__author__ = "an.luzgarev"

"""Module stores urls"""

from django.contrib import admin
from django.urls import path
from django.urls import include
from rest_framework.authtoken import views as views_token

from work_app import views
from api import views as api_views


api_patterns = [
	path('get_auth_token/', views_token.obtain_auth_token, name="get_auth_token"),
    path('get_translation/<str:word>/', api_views.Translation.as_view(), name="get_translation"),
    path('get_training/', api_views.Training.as_view(), name="training_letter"),
    path('get_topics/', api_views.Topics.as_view(), name="get_topics"),
	path('get_grammar/', api_views.Grammar.as_view(), name="get_grammar"),
	path('get_essays/', api_views.Essay.as_view(), name="get_essays"),
	path('logs/', api_views.Log.as_view(), name="logs")
	]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
	path('cabinet/', views.cabinet, name="cabinet"),
    path('', views.index, name="index"),
    path('dictionary/', views.dictionary, name="dictionary"),
    path('dictionary/<str:letter>/', views.dictionary_letter, name="dictionary_letter"),
    path('load_data/', views.initial_settings, name="load_data"),
    path('trainings/', views.trainings, name="trainings"),
    path('trainings/word_translation', views.word_translation, name="word_translation"),
    path('trainings/translation_word', views.translation_word, name="translation_word"),
    path('trainings/make_a_sentence',views.make_a_sentence, name = "make_a_sentence"),
    path('trainings/phrasal_verbs', views.phrasal_verbs, name="phrasal_verbs"),
    path('trainings/words_series', views.words_series, name="phrasal_verbs"),
    path('trainings/essay_writing', views.essay_writing, name="essay_writing"),
    path('trainings/grammar_training',views.grammar_training, name="grammar_training"),
    path('trainings/categories_training', views.categories_training, name="grammar_training"),
    path('trainings/topics_training', views.topics_training, name="topics_training"),
    path('topics/', views.topics, name="topics"),
    path('new_topic/', views.new_topic, name="new_topic"),
    path('grammar/', views.grammar, name="grammar"),
	path("translator/", views.translator, name="translator"),
	path("my_essays/", views.my_essays, name="my_essays"),
    path('toefl/', views.toefl, name="toefl"),
    path('files/', views.files, name="files"),
    path('files/<str:filename>/',views.get_file, name="get_file"),	         
    path('calendar/', views.calendar_view, name="calendar"),   
    #API views
	path('api/', views.api_list, name="api_list"),
	path('api/', include(api_patterns))
    ]
