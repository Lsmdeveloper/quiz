from django.db import models
import secrets
import uuid

def gen_id():
    return secrets.token_hex(16)  # 32 chars

class Quiz(models.Model):
    slug = models.SlugField(max_length=64, unique=True)         
    title = models.CharField(max_length=200)                     
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return self.title
    
class QuizSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, related_name='sessions', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    result = models.JSONField(null=True, blank=True)

class Question(models.Model):
    KIND_SINGLE   = "single"     # uma alternativa correta
    KIND_MULTIPLE = "multiple"   # várias corretas
    KIND_CHOICES = [
        (KIND_SINGLE, "Múltipla (uma correta)"),
        (KIND_MULTIPLE, "Múltipla (várias corretas)"),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    slug = models.SlugField(max_length=64, help_text="ID usado na API (questionId)")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_SINGLE)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    weight = models.FloatField(default=1.0)   # valor da questão

    class Meta:
        ordering = ["quiz_id", "order", "id"]
        unique_together = (("quiz", "slug"),)

    def __str__(self):
        return f"{self.quiz.slug} · {self.order}. {self.title}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    label = models.CharField(max_length=200)             # texto visível ao usuário
    value = models.SlugField(max_length=64)              # ex: "opt_a"
    is_correct = models.BooleanField(default=False)      # gabarito!
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["question_id", "order", "id"]
        unique_together = (("question", "value"),)

    def __str__(self):
        return self.label

class Answer(models.Model):
    session  = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    # guarda as escolhas do usuário (lista de "value" das opções)
    selected = models.JSONField(default=list)

    class Meta:
        unique_together = (("session", "question"),)