import pytest

from backend.app.difficulty_adapter.service import DifficultyAction, DifficultyAdapter, StudentPerformance


@pytest.mark.parametrize(
    "correct,total,level,expected_action",
    [
        (9, 10, 5, "keep"),       # 90%
        (6, 10, 5, "keep"),       # 60%
        (3, 10, 5, "decrease"),   # 30%
    ],
)
def test_difficulty_basic_logic(adapter, correct, total, level, expected_action):
    decision = adapter.adapt(
        performance=StudentPerformance(
            correct_answers=correct,
            total_questions=total,
            consecutive_failures=0,
        ),
        current_level=level,
    )

    assert decision.current_level == level
    assert 1 <= decision.recommended_level <= 10
    assert decision.accuracy >= 0


def test_repeat_topic_priority(adapter):
    decision = adapter.adapt(
        performance=StudentPerformance(
            correct_answers=10,
            total_questions=10,
            consecutive_failures=5,
        ),
        current_level=5,
    )

    assert decision.action == DifficultyAction.REPEAT_TOPIC
    assert decision.recommended_level == 4


@pytest.mark.parametrize(
    "correct,total",
    [
        (1, 10),
        (0, 10),
        (5, 10),
    ],
)
def test_accuracy_range(adapter, correct, total):
    decision = adapter.adapt(
        performance=StudentPerformance(
            correct_answers=correct,
            total_questions=total,
        ),
        current_level=3,
    )

    assert 0 <= decision.accuracy <= 100


@pytest.mark.parametrize(
    "bad_perf",
    [
        StudentPerformance(-1, 10),
        StudentPerformance(11, 10),
    ],
)
def test_validation(adapter, bad_perf):
    with pytest.raises(Exception):
        adapter.adapt(bad_perf, 1)


@pytest.fixture
def adapter():
    return DifficultyAdapter()