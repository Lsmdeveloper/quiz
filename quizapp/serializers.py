from rest_framework import serializers
from .models import Question, Choice

class ChoiceOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("label", "value", "order")

class QuestionOutSerializer(serializers.ModelSerializer):
    choices = ChoiceOutSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ("slug", "title", "description", "kind", "required", "order", "weight", "choices")

class AnswerInSerializer(serializers.Serializer):
    questionId = serializers.CharField()
    choices = serializers.ListField(child=serializers.CharField(), allow_empty=False) 

class SaveAnswersSerializer(serializers.Serializer):
    answers = AnswerInSerializer(many=True)


class QuizCreateSerializer(serializers.Serializer):
    slug = serializers.SlugField(max_length=64)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(allow_blank=True, required=False)
    is_active = serializers.BooleanField(default=True)

class ChoiceCreateSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=200)
    value = serializers.SlugField(max_length=64)
    is_correct = serializers.BooleanField()
    order = serializers.IntegerField(default=0)

class QuestionCreateSerializer(serializers.Serializer):
    slug = serializers.SlugField(max_length=64)
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    kind = serializers.ChoiceField(choices=[Question.KIND_SINGLE, Question.KIND_MULTIPLE])
    required = serializers.BooleanField(default=True)
    order = serializers.IntegerField(default=0)
    weight = serializers.FloatField(default=1.0)
    choices = ChoiceCreateSerializer(many=True)

class BulkQuestionsSerializer(serializers.Serializer):
    questions = QuestionCreateSerializer(many=True)