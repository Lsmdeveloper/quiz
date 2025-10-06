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
    list_display = ("id", "quiz", "created_at", "paid_display", "mp_pref_display", "mp_payment_display")
    list_filter = ("quiz", "created_at")  # remova 'paid' daqui pois não é Field
    search_fields = ("id",)

    def paid_display(self, obj):
        if hasattr(obj, "paid"):
            return getattr(obj, "paid")
        return bool(getattr(obj, "mp_payment_id", None))
    paid_display.boolean = True
    paid_display.short_description = "Paid"

    def mp_pref_display(self, obj):
        return getattr(obj, "mp_pref_id", "-")
    mp_pref_display.short_description = "MP Pref ID"

    def mp_payment_display(self, obj):
        return getattr(obj, "mp_payment_id", "-")
    mp_payment_display.short_description = "MP Payment ID"

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("session", "question")
    search_fields = ("session__id", "question__slug")