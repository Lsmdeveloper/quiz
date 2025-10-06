from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mercadopago import SDK
import requests, hmac, hashlib
from rest_framework.generics import ListAPIView
from .models import Quiz, QuizSession, Question, Choice, Answer
from .serializers import QuizSerializer, QuestionOutSerializer, SaveAnswersSerializer, QuizCreateSerializer, QuestionCreateSerializer, BulkQuestionsSerializer

sdk = SDK(settings.MP_ACCESS_TOKEN) if settings.MP_ACCESS_TOKEN else None

def calc_result(session: QuizSession, quiz: Quiz):
    """
    Regra de correção:
      - SINGLE: acerta se escolheu exatamente a opção correta.
      - MULTIPLE: acerto pleno se o conjunto de escolhas == conjunto de corretas.
      (Você pode alterar para crédito parcial depois.)
    """
    total_questions = quiz.questions.count()
    max_points = sum(q.weight for q in quiz.questions.all())
    points = 0.0
    correct_count = 0

    # mapeia respostas por question_id
    answers_map = {a.question_id: set(a.selected or []) for a in session.answers.select_related("question")}

    for q in quiz.questions.prefetch_related("choices"):
        correct_values = set(c.value for c in q.choices.all() if c.is_correct)
        chosen_values = answers_map.get(q.id, set())

        is_correct = (chosen_values == correct_values and len(correct_values) > 0)
        if is_correct:
            points += q.weight
            correct_count += 1

    percent = (points / max_points * 100.0) if max_points > 0 else 0.0
    # classificação simples (ajuste os limiares como preferir)
    if percent >= 90:
        cls = "Excelente"
    elif percent >= 70:
        cls = "Muito bom"
    elif percent >= 50:
        cls = "Mediano"
    else:
        cls = "Precisa melhorar"

    return {
        "quiz": quiz.slug,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "points": round(points, 2),
        "max_points": round(max_points, 2),
        "percent": round(percent, 2),
        "classification": cls,
        # Observação: isto NÃO é um teste clínico de QI padronizado.
        "disclaimer": "Este resultado é indicativo e não substitui testes psicométricos padronizados."
    }

class Health(APIView):
    def get(self, req): return Response({"ok": True})

class ListQuizzes(ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class ListQuestions(APIView):
    def get(self, req):
        slug = req.query_params.get("slug", "iq")
        try:
            quiz = Quiz.objects.get(slug=slug, is_active=True)
        except Quiz.DoesNotExist:
            return Response({"error": "quiz not found"}, status=404)
        qs = quiz.questions.prefetch_related("choices").all()
        data = QuestionOutSerializer(qs, many=True).data
        return Response({"quiz": quiz.slug, "title": quiz.title, "questions": data})

class CreateQuiz(APIView):
    """Cria ou atualiza um Quiz (POST /api/quizzes)"""
    def post(self, req):
        ser = QuizCreateSerializer(data=req.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        quiz, created = Quiz.objects.get_or_create(
            slug=data["slug"],
            defaults={
                "title": data["title"],
                "description": data.get("description", ""),
                "is_active": data.get("is_active", True),
            }
        )
        if not created:
            quiz.title = data["title"]
            quiz.description = data.get("description", "")
            quiz.is_active = data.get("is_active", True)
            quiz.save(update_fields=["title","description","is_active"])
        return Response({
            "slug": quiz.slug, "title": quiz.title, "is_active": quiz.is_active
        }, status=201 if created else 200)

def _upsert_question_with_choices(quiz: Quiz, qdata: dict):
    """Cria/atualiza Question e substitui Choices pelo payload recebido."""
    question, _ = Question.objects.get_or_create(
        quiz=quiz, slug=qdata["slug"],
        defaults={
            "title": qdata["title"],
            "description": qdata.get("description",""),
            "kind": qdata["kind"],
            "required": qdata.get("required", True),
            "order": qdata.get("order", 0),
            "weight": qdata.get("weight", 1.0),
        }
    )
    # Atualiza metadados
    question.title = qdata["title"]
    question.description = qdata.get("description","")
    question.kind = qdata["kind"]
    question.required = qdata.get("required", True)
    question.order = qdata.get("order", 0)
    question.weight = qdata.get("weight", 1.0)
    question.save()

    # Substitui as choices pelo que veio no payload
    question.choices.all().delete()
    for ch in qdata["choices"]:
        question.choices.create(
            label=ch["label"],
            value=ch["value"],
            is_correct=ch["is_correct"],
            order=ch.get("order", 0),
        )
    return question

class CreateQuestion(APIView):
    """Cria/atualiza 1 pergunta com choices (POST /api/quizzes/<slug>/questions)"""
    def post(self, req, slug):
        try:
            quiz = Quiz.objects.get(slug=slug, is_active=True)
        except Quiz.DoesNotExist:
            return Response({"error":"quiz not found"}, status=404)

        ser = QuestionCreateSerializer(data=req.data)
        ser.is_valid(raise_exception=True)
        q = _upsert_question_with_choices(quiz, ser.validated_data)
        out = QuestionOutSerializer(q).data
        return Response(out, status=201)

class BulkCreateQuestions(APIView):
    """Cria/atualiza várias perguntas (POST /api/quizzes/<slug>/questions/bulk)"""
    def post(self, req, slug):
        try:
            quiz = Quiz.objects.get(slug=slug, is_active=True)
        except Quiz.DoesNotExist:
            return Response({"error":"quiz not found"}, status=404)

        ser = BulkQuestionsSerializer(data=req.data)
        ser.is_valid(raise_exception=True)
        created = []
        for qdata in ser.validated_data["questions"]:
            q = _upsert_question_with_choices(quiz, qdata)
            created.append(QuestionOutSerializer(q).data)
        return Response({"created": created}, status=201)


# class StartQuiz(APIView):
#     def post(self, req):
#         slug = req.data.get("slug")
#         if not slug:
#             return Response({"error": "Missing slug"}, status=400)

#         try:
#             quiz = Quiz.objects.get(slug=slug, is_active=True)
#         except Quiz.DoesNotExist:
#             return Response({"error": "quiz not found"}, status=404)

#         qs = quiz.questions.prefetch_related("choices").all()
#         questions_data = QuestionOutSerializer(qs, many=True).data

#         return Response({
#             "session_id": None,
#             "quiz": QuizSerializer(quiz).data,
#             "questions": questions_data
#         })
class StartQuiz(APIView):
    def post(self, req):
        slug = req.data.get("slug")
        if not slug:
            return Response({"error": "Missing slug"}, status=400)

        try:
            quiz = Quiz.objects.get(slug=slug, is_active=True)
        except Quiz.DoesNotExist:
            return Response({"error": "quiz not found"}, status=404)

        # cria e salva a sessão atrelada ao quiz
        s = QuizSession.objects.create(quiz=quiz)

        qs = quiz.questions.prefetch_related("choices").all()
        questions_data = QuestionOutSerializer(qs, many=True).data

        return Response({
            "session_id": s.pk,                      
            "quiz": QuizSerializer(quiz).data,
            "questions": questions_data
        })
class SaveAnswers(APIView):
    def post(self, req, session_id):
        try: s = QuizSession.objects.get(pk=session_id)
        except QuizSession.DoesNotExist:
            return Response({"error":"session not found"}, status=404)

        ser = SaveAnswersSerializer(data=req.data)
        ser.is_valid(raise_exception=True)
        # upsert por (session, question)
        for a in ser.validated_data["answers"]:
            qid = a["questionId"]
            choices = a["choices"]
            try:
                # questionId vem como slug; precisamos achar a Question real
                q = Question.objects.get(slug=qid)
            except Question.DoesNotExist:
                continue
            Answer.objects.update_or_create(
                session=s, question=q,
                defaults={"selected": choices},
            )
        return Response({"ok": True})

class FinishQuiz(APIView):
    def post(self, req, session_id):
        slug = req.query_params.get("slug", "iq")
        try:
            quiz = Quiz.objects.get(slug=slug, is_active=True)
        except Quiz.DoesNotExist:
            return Response({"error":"quiz not found"}, status=404)
        try:
            s = QuizSession.objects.get(pk=session_id)
        except QuizSession.DoesNotExist:
            return Response({"error":"session not found"}, status=404)

        # calcula e salva o resultado (sem expor ainda)
        s.result = calc_result(s, quiz)
        s.save(update_fields=["result"])

        # sem token MP → mock pra dev
        if not settings.MP_ACCESS_TOKEN or not sdk:
            return Response({
                "preference_id": "pref_mock",
                "init_point": f"{settings.APP_BASE_URL}/quiz/mock-checkout?sid={s.pk}&quiz={quiz.slug}",
                "sessionId": s.pk
            })

        pref = sdk.preference().create({
            "items": [{
                "title": f"Resultado do Quiz: {quiz.title}",
                "quantity": 1,
                "currency_id": settings.CURRENCY,
                "unit_price": settings.QUIZ_PRICE,
            }],
            "back_urls": {
                "success": f"{settings.APP_BASE_URL}/quiz/sucesso",
                "failure": f"{settings.APP_BASE_URL}/quiz/erro",
                "pending": f"{settings.APP_BASE_URL}/quiz/aguardando",
            },
            "auto_return": "approved",
            "notification_url": f"{settings.API_BASE_URL}/api/webhooks/mercadopago",
            "external_reference": s.pk,
        })["response"]

        s.mp_pref_id = pref.get("id")
        s.save(update_fields=["mp_pref_id"])
        return Response({
            "preference_id": pref.get("id"),
            "init_point": pref.get("init_point"),
            "sessionId": s.pk
        })

def verify_mp_signature(x_signature: str, x_request_id: str, payment_id: str) -> bool:
    secret = settings.MP_WEBHOOK_SECRET
    if not (secret and x_signature and x_request_id and payment_id): return False
    try:
        parts = dict(p.split("=", 1) for p in x_signature.split(","))
        ts = parts.get("ts"); v1 = parts.get("v1")
        if not (ts and v1): return False
        manifest = f"id:{payment_id};request-id:{x_request_id};ts:{ts};"
        digest = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
        return digest == v1
    except Exception:
        return False

@method_decorator(csrf_exempt, name="dispatch")
class MPWebhook(APIView):
    def post(self, req):
        body = req.data if isinstance(req.data, dict) else {}
        data = body.get("data") or {}
        pay_id = str(data.get("id") or data.get("payment_id") or "")

        _ = verify_mp_signature(
            req.headers.get("x-signature", ""),
            req.headers.get("x-request-id", ""),
            pay_id
        )

        if pay_id and settings.MP_ACCESS_TOKEN:
            r = requests.get(
                f"https://api.mercadopago.com/v1/payments/{pay_id}",
                headers={"Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}"}
            )
            payment = r.json()
            if payment.get("status") == "approved":
                ext = payment.get("external_reference")
                if ext:
                    try:
                        s = QuizSession.objects.get(pk=ext)
                        if not s.paid:
                            s.paid = True
                            s.mp_payment_id = s.mp_payment_id or str(pay_id)
                            s.save(update_fields=["paid","mp_payment_id"])
                    except QuizSession.DoesNotExist:
                        pass
        return Response(status=200)

class GetResult(APIView):
    def get(self, req, session_id):
        try: s = QuizSession.objects.get(pk=session_id)
        except QuizSession.DoesNotExist:
            return Response({"error":"session not found"}, status=404)
        if not s.paid:
            return Response({"error":"payment_required"}, status=402)
        return Response({"result": s.result})
