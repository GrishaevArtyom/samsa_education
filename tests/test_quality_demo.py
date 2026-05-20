from backend.quality_demo import AdaptiveLearningService, Level, LearningPlanBuilder


def test_diagnose_detects_beginner_level():
    service = AdaptiveLearningService()

    profile = service.diagnose(
        user_id=1,
        goal="Разобраться в физике",
        answers=[20, 40, 30],
    )

    assert profile.user_id == 1
    assert profile.level == Level.BEGINNER
    assert profile.average_score == 30


def test_diagnose_detects_advanced_level():
    service = AdaptiveLearningService()

    profile = service.diagnose(
        user_id=2,
        goal="Подготовиться к ЕГЭ",
        answers=[90, 85, 95],
    )

    assert profile.level == Level.ADVANCED


def test_generate_lesson_uses_profile_level():
    service = AdaptiveLearningService()
    profile = service.diagnose(
        user_id=3,
        goal="Изучить Python",
        answers=[70, 75],
    )

    lesson = service.generate_lesson(profile, "Циклы")

    assert lesson.topic == "Циклы"
    assert lesson.difficulty == "medium"
    assert len(lesson.tasks) == 2


def test_answer_analysis_returns_score():
    service = AdaptiveLearningService()

    score = service.analyze_answer(
        answer="Сила равна произведению массы на ускорение",
        expected_keywords=["сила", "массы", "ускорение"],
    )

    assert score == 100


def test_next_action_depends_on_score():
    service = AdaptiveLearningService()

    assert service.next_action(40) == "repeat_theory"
    assert service.next_action(70) == "more_practice"
    assert service.next_action(90) == "next_topic"


def test_plan_builder_adds_exam_topic_for_ege_goal():
    builder = LearningPlanBuilder()

    topics = builder.build_topics("Подготовиться к ЕГЭ", Level.INTERMEDIATE)

    assert "Разбор экзаменационных задач" in topics
    assert "Задачи повышенной сложности" in topics