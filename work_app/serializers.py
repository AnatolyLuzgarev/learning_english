from rest_framework import serializers
from work_app import models



class WordSerializer(serializers.Serializer):
	word = serializers.CharField(max_length = 100)
	translation = serializers.CharField(max_length = 300)
	transcription = serializers.CharField(max_length = 100)