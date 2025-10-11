from rest_framework import serializers
from .models import Question, Choice, Quiz

class ChoiceOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("label", "value", "order")

class QuestionOutSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("slug", "title", "description", "kind", "required", "order", "weight", "options")

    def get_options(self, obj):
        # Ordena e mapeia para a,b,c,d
        letters = ["a", "b", "c", "d"]
        opts = {}
        for i, ch in enumerate(obj.choices.all().order_by("order", "id")):
            if i >= len(letters):
                break
            # Mostre o texto que você quer (label ou value). Aqui uso label como texto visível:
            opts[letters[i]] = ch.label
        return opts
    
class AnswerInSerializer(serializers.Serializer):
    questionId = serializers.CharField()
    choices = serializers.ListField(child=serializers.CharField(), allow_empty=False) 

class SaveAnswersSerializer(serializers.Serializer):
    answers = AnswerInSerializer(many=True)

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class QuizCreateSerializer(serializers.Serializer):
    slug = serializers.SlugField(max_length=64)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(allow_blank=True, required=False)
    is_active = serializers.BooleanField(default=True)
    cover = serializers.ImageField(required=False, allow_null=True)

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