import random
import time
from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from pydantic import BaseModel

app = FastAPI(title="AI Learning Platform Monitoring Prototype")

# -------------------------
# Prometheus metrics
# -------------------------

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["endpoint", "method", "status"]
)

LLM_REQUESTS = Counter(
    "llm_requests_total",
    "Total number of fake LLM requests",
    ["operation"]
)

LLM_ERRORS = Counter(
    "llm_errors_total",
    "Total number of fake LLM errors",
    ["operation"]
)

DIAGNOSTICS_COMPLETED = Counter(
    "diagnostics_completed_total",
    "Total number of completed user diagnostics"
)

ACTIVE_USERS = Gauge(
    "active_users",
    "Current number of active users"
)

LESSON_GENERATION_TIME = Histogram(
    "lesson_generation_seconds",
    "Time spent generating a lesson"
)

ANSWER_SCORE = Histogram(
    "answer_score",
    "Distribution of student answer scores",
    buckets=[0, 20, 40, 60, 80, 100]
)


# -------------------------
# Request models
# -------------------------

class DiagnosticsRequest(BaseModel):
    user_id: int
    goal: str


class LessonRequest(BaseModel):
    user_id: int
    topic: str


class AnswerRequest(BaseModel):
    user_id: int
    lesson_id: int
    answer: str


# -------------------------
# Business logic
# -------------------------

@app.get("/health")
def health():
    HTTP_REQUESTS.labels(endpoint="/health", method="GET", status="200").inc()
    return {"status": "ok"}


@app.post("/diagnostics")
def diagnostics(request: DiagnosticsRequest):
    HTTP_REQUESTS.labels(endpoint="/diagnostics", method="POST", status="200").inc()
    DIAGNOSTICS_COMPLETED.inc()

    ACTIVE_USERS.set(random.randint(5, 50))

    level = random.choice(["beginner", "intermediate", "advanced"])
    learning_style = random.choice(["visual", "practice-based", "text-based"])

    return {
        "user_id": request.user_id,
        "goal": request.goal,
        "detected_level": level,
        "learning_style": learning_style
    }


@app.post("/generate-lesson")
def generate_lesson(request: LessonRequest):
    start = time.time()

    HTTP_REQUESTS.labels(endpoint="/generate-lesson", method="POST", status="200").inc()
    LLM_REQUESTS.labels(operation="generate_lesson").inc()

    # Имитация задержки LLM
    time.sleep(random.uniform(0.2, 1.5))

    # Имитация ошибки LLM примерно в 10% случаев
    if random.random() < 0.1:
        LLM_ERRORS.labels(operation="generate_lesson").inc()
        HTTP_REQUESTS.labels(endpoint="/generate-lesson", method="POST", status="500").inc()
        return {"error": "Fake LLM generation error"}

    duration = time.time() - start
    LESSON_GENERATION_TIME.observe(duration)

    return {
        "user_id": request.user_id,
        "topic": request.topic,
        "lesson": f"Краткое персонализированное объяснение темы: {request.topic}",
        "difficulty": random.choice(["easy", "medium", "hard"]),
        "generation_time_seconds": round(duration, 3)
    }


@app.post("/submit-answer")
def submit_answer(request: AnswerRequest):
    HTTP_REQUESTS.labels(endpoint="/submit-answer", method="POST", status="200").inc()
    LLM_REQUESTS.labels(operation="analyze_answer").inc()

    score = random.randint(0, 100)
    ANSWER_SCORE.observe(score)

    if score < 50:
        recommendation = "Повторить базовую теорию и решить дополнительные задачи."
    elif score < 80:
        recommendation = "Закрепить материал на задачах среднего уровня."
    else:
        recommendation = "Можно переходить к более сложной теме."

    return {
        "user_id": request.user_id,
        "lesson_id": request.lesson_id,
        "score": score,
        "recommendation": recommendation
    }


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
