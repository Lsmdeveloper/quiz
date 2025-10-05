from django.contrib import admin
from .models import Quiz, QuizSession, Question, Choice, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    fields = ("order", "label", "value", "is_correct")
    ordering = ("order",)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "is_active")
    search_fields = ("slug", "title")
    list_filter = ("is_active",)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "order", "slug", "title", "kind", "weight", "required")
    list_filter = ("quiz", "kind", "required")
    search_fields = ("slug", "title")
    ordering = ("quiz", "order")
    inlines = [ChoiceInline]

@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "paid", "mp_pref_id", "mp_payment_id", "created_at")
    list_filter = ("paid",)
    search_fields = ("id", "mp_payment_id")

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("session", "question")
    search_fields = ("session__id", "question__slug")