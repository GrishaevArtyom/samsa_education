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

    assert decision.action == DifficultyAction.DECREASE