from rest_framework import serializers
from work_app import models

class TopicSerializer(serializers.Serializer):
	topic = serializers.CharField(max_length = 500)
	paragraph = serializers.CharField(max_length = 200)
	subject = serializers.CharField(max_length = 100)
	def create(self,validated_data):
		return models.Topic.objects.create(**validated_data)
	def update(self,instance,validated_data):
		instance.topic = validated_data.get('topic')
		instance.paragraph = validated_data.get('paragraph')
		instance.subject = validated_data.get('subject')
		instance.save()
		return instance
	
class WordSerializer(serializers.Serializer):
	word = serializers.CharField(max_length = 100)
	translation = serializers.CharField(max_length = 300)
	transcription = serializers.CharField(max_length = 100)
	
class GrammarSerializer(serializers.Serializer):
	section = serializers.CharField(max_length = 200)
	rule = serializers.CharField(max_length = 200)
	example = serializers.CharField(max_length = 500)
	
class EssaySerializer(serializers.Serializer):
	theme = serializers.CharField(max_length = 200)
	essay = serializers.CharField(max_length = 10000)
	