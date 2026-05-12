import pytest

from backend.app.difficulty_adapter.service import (
    DifficultyAction, DifficultyAdapter,
    DifficultyValidationError,
    StudentPerformance,
)


@pytest.fixture
def adapter() -> DifficultyAdapter:
    return DifficultyAdapter()


class TestDifficultyAdapter:
    def test_should_increase_difficulty(
        self,
        adapter: DifficultyAdapter,
    ) -> None:
        performance = StudentPerformance(
            correct_answers=9,
            total_questions=10,
        )

        result = adapter.adapt(
            performance=performance,
            current_level=5,
        )

        assert result.action == DifficultyAction.INCREASE
        assert result.current_level == 5
        assert result.recommended_level == 6
        assert result.accuracy == 90.0

    def test_should_keep_difficulty(
        self,
        adapter: DifficultyAdapter,
    ) -> None:
        performance = StudentPerformance(
            correct_answers=7,
            total_questions=10,
        )

        result = adapter.adapt(
            performance=performance,
            current_level=5,
        )

        assert result.action == DifficultyAction.KEEP
        assert result.recommended_level == 5
        assert result.accuracy == 70.0

    def test_should_decrease_difficulty(
        self,
        adapter: DifficultyAdapter,
    ) -> None:
        performance = StudentPerformance(
            correct_answers=4,
            total_questions=10,
        )

        result = adapter.adapt(
            performance=performance,
            current_level=5,
        )

        assert result.action == DifficultyAction.DECREASE
        assert result.recommended_level == 4
        assert result.accuracy == 40.0

    def test_should_repeat_topic_after_consecutive_failures(
        self,
        adapter: DifficultyAdapter,
    ) -> None:
        performance = StudentPerformance(
            correct_answers=6,
            total_questions=10,
            consecutive_failures=3,
        )

        result = adapter.adapt(
            performance=performance,
            current_level=5,
        )

        assert result.action == DifficultyAction.REPEAT_TOPIC
        assert result.recommended_level == 4

    def test_should_not_exceed_max_level(
        self,
        adapter: DifficultyAdapter,
    ) -> None:
        performance = StudentPerformance(
            correct_answers=10,
            total_questions=10,
        )

        result = adapter.adapt(
            performance=performance,
            current_level=10,
        )

        assert result.action == DifficultyAction.INCREASE
        assert result.recommended_level == 10

    def test_should_not_go_below_min_level(
        self,
        adapter: DifficultyAdapter,
    ) -> None:
        performance = StudentPerformance(
            correct_answers=1,
            total_questions=10,
        )

        result = adapter.adapt(
            performance=performance,
            current_level=1,
        )

        assert result.action == DifficultyAction.DECREASE
        assert result.recommended_level == 1


class TestStudentPerformance:
    def test_should_calculate_accuracy(
        self,
    ) -> None:
        performance = StudentPerformance(
            correct_answers=8,
            total_questions=10,
        )

        assert performance.accuracy == 80.0


class TestDifficultyValidation:
    @pytest.mark.parametrize(
        (
            "correct_answers",
            "total_questions",
            "consecutive_failures",
            "current_level",
        ),
        [
            (0, 0, 0, 1),
            (-1, 10, 0, 1),
            (20, 10, 0, 1),
            (5, 10, -1, 1),
            (5, 10, 0, 0),
        ],
    )
    def test_should_raise_validation_error(
        self,
        adapter: DifficultyAdapter,
        correct_answers: int,
        total_questions: int,
        consecutive_failures: int,
        current_level: int,
    ) -> None:
        performance = StudentPerformance(
            correct_answers=correct_answers,
            total_questions=total_questions,
            consecutive_failures=(consecutive_failures),
        )

        with pytest.raises(DifficultyValidationError):
            adapter.adapt(
                performance=performance,
                current_level=current_level,
            )


class TestDifficultyThresholds:
    def test_should_use_custom_thresholds(
        self,
    ) -> None:
        adapter = DifficultyAdapter(
            increase_threshold=95.0,
            keep_threshold=75.0,
        )

        performance = StudentPerformance(
            correct_answers=8,
            total_questions=10,
        )

        result = adapter.adapt(
            performance=performance,
            current_level=5,
        )

        assert result.action == DifficultyAction.KEEP
        assert result.recommended_level == 5
