from dataclasses import dataclass, field
from enum import Enum


class Level(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class UserProfile:
    user_id: int
    goal: str
    level: Level
    solved_tasks: int = 0
    average_score: float = 0.0


@dataclass
class Lesson:
    topic: str
    difficulty: str
    theory: str
    tasks: list[str] = field(default_factory=list)


class LearningPlanBuilder:
    def build_topics(self, goal: str, level: Level) -> list[str]:
        topics = ["Диагностика", "Базовая теория", "Практика", "Итоговый тест"]

        if "егэ" in goal.lower():
            topics.append("Разбор экзаменационных задач")

        if level == Level.ADVANCED:
            return topics[2:] + ["Олимпиадные задачи"]

        if level == Level.INTERMEDIATE:
            return topics + ["Задачи повышенной сложности"]

        return ["Повторение школьной базы"] + topics


class AdaptiveLearningService:
    def __init__(self, plan_builder: LearningPlanBuilder | None = None) -> None:
        self.plan_builder = plan_builder or LearningPlanBuilder()

    def diagnose(self, user_id: int, goal: str, answers: list[int]) -> UserProfile:
        average = sum(answers) / len(answers) if answers else 0

        if average >= 80:
            level = Level.ADVANCED
        elif average >= 50:
            level = Level.INTERMEDIATE
        else:
            level = Level.BEGINNER

        return UserProfile(
            user_id=user_id,
            goal=goal,
            level=level,
            average_score=average,
        )

    def generate_lesson(self, profile: UserProfile, topic: str) -> Lesson:
        difficulty = "easy"

        if profile.level == Level.INTERMEDIATE:
            difficulty = "medium"
        elif profile.level == Level.ADVANCED:
            difficulty = "hard"

        theory = f"Краткое объяснение темы: {topic}"
        tasks = [f"Задача по теме: {topic}", "Проверочный вопрос"]

        return Lesson(
            topic=topic,
            difficulty=difficulty,
            theory=theory,
            tasks=tasks,
        )

    def analyze_answer(self, answer: str, expected_keywords: list[str]) -> int:
        normalized_answer = answer.lower()
        matches = sum(
            1 for keyword in expected_keywords
            if keyword.lower() in normalized_answer
        )

        if not expected_keywords:
            return 0

        return round(matches / len(expected_keywords) * 100)

    def next_action(self, score: int) -> str:
        if score < 50:
            return "repeat_theory"

        if score < 80:
            return "more_practice"

        return "next_topic"