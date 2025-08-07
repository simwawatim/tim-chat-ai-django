from rest_framework import serializers

class GeminiPromptSerializer(serializers.Serializer):
    prompt = serializers.CharField()
