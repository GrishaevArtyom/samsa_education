from backend.difficulty_adapter.service import (
    DifficultyAction,
    DifficultyAdapter,
    StudentPerformance,
)


def test_adapter_increases_level_for_high_accuracy():
    adapter = DifficultyAdapter()
    performance = StudentPerformance(
        correct_answers=9,
        total_questions=10,
    )

    decision = adapter.adapt(performance, current_level=5)

    assert decision.action == DifficultyAction.INCREASE
    assert decision.current_level == 5
    assert decision.recommended_level == 6
    assert decision.accuracy == 90.0


def test_adapter_keeps_level_for_medium_accuracy():
    adapter = DifficultyAdapter()
    performance = StudentPerformance(
        correct_answers=7,
        total_questions=10,
    )

    decision = adapter.adapt(performance, current_level=4)

    assert decision.action == DifficultyAction.KEEP
    assert decision.recommended_level == 4