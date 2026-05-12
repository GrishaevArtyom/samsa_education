from dataclasses import dataclass
from enum import StrEnum


MIN_DIFFICULTY_LEVEL = 1
MAX_DIFFICULTY_LEVEL = 10

INCREASE_THRESHOLD = 85.0
KEEP_THRESHOLD = 60.0
FAILURE_REPEAT_THRESHOLD = 3


class DifficultyAction(StrEnum):
    INCREASE = "increase"
    KEEP = "keep"
    DECREASE = "decrease"
    REPEAT_TOPIC = "repeat_topic"


@dataclass(slots=True, frozen=True)
class StudentPerformance:
    correct_answers: int
    total_questions: int
    consecutive_failures: int = 0

    @property
    def accuracy(self) -> float:
        return (self.correct_answers / self.total_questions) * 100


@dataclass(slots=True, frozen=True)
class DifficultyDecision:
    action: DifficultyAction
    current_level: int
    recommended_level: int
    accuracy: float


class DifficultyValidationError(ValueError):
    pass


class DifficultyAdapter:
    def __init__(
        self,
        min_level: int = MIN_DIFFICULTY_LEVEL,
        max_level: int = MAX_DIFFICULTY_LEVEL,
        increase_threshold: float = INCREASE_THRESHOLD,
        keep_threshold: float = KEEP_THRESHOLD,
        failure_repeat_threshold: int = FAILURE_REPEAT_THRESHOLD,
    ) -> None:
        self._min_level = min_level
        self._max_level = max_level
        self._increase_threshold = increase_threshold
        self._keep_threshold = keep_threshold
        self._failure_repeat_threshold = failure_repeat_threshold

    def adapt(
        self,
        performance: StudentPerformance,
        current_level: int,
    ) -> DifficultyDecision:
        self._validate(
            performance=performance,
            current_level=current_level,
        )

        if self._should_repeat_topic(performance):
            return self._build_decision(
                action=DifficultyAction.REPEAT_TOPIC,
                current_level=current_level,
                recommended_level=self._decrease_level(current_level),
                accuracy=performance.accuracy,
            )

        action = self._determine_action(performance.accuracy)

        recommended_level = self._calculate_next_level(
            action=action,
            current_level=current_level,
        )

        return self._build_decision(
            action=action,
            current_level=current_level,
            recommended_level=recommended_level,
            accuracy=performance.accuracy,
        )

    def _determine_action(
        self,
        accuracy: float,
    ) -> DifficultyAction:
        if accuracy >= self._increase_threshold:
            return DifficultyAction.INCREASE

        if accuracy >= self._keep_threshold:
            return DifficultyAction.KEEP

        return DifficultyAction.DECREASE

    def _calculate_next_level(
        self,
        action: DifficultyAction,
        current_level: int,
    ) -> int:
        action_handlers = {
            DifficultyAction.INCREASE: self._increase_level,
            DifficultyAction.KEEP: lambda level: level,
            DifficultyAction.DECREASE: self._decrease_level,
            DifficultyAction.REPEAT_TOPIC: self._decrease_level,
        }

        return action_handlers[action](current_level)

    def _increase_level(
        self,
        current_level: int,
    ) -> int:
        return min(
            self._max_level,
            current_level + 1,
        )

    def _decrease_level(
        self,
        current_level: int,
    ) -> int:
        return max(
            self._min_level,
            current_level - 1,
        )

    def _should_repeat_topic(
        self,
        performance: StudentPerformance,
    ) -> bool:
        return performance.consecutive_failures >= self._failure_repeat_threshold

    @staticmethod
    def _build_decision(
        action: DifficultyAction,
        current_level: int,
        recommended_level: int,
        accuracy: float,
    ) -> DifficultyDecision:
        return DifficultyDecision(
            action=action,
            current_level=current_level,
            recommended_level=recommended_level,
            accuracy=accuracy,
        )

    @staticmethod
    def _validate(
        performance: StudentPerformance,
        current_level: int,
    ) -> None:
        if performance.total_questions <= 0:
            raise DifficultyValidationError("total_questions must be > 0")

        if performance.correct_answers < 0:
            raise DifficultyValidationError("correct_answers cannot be negative")

        if performance.correct_answers > performance.total_questions:
            raise DifficultyValidationError(
                "correct_answers cannot exceed " "total_questions"
            )

        if performance.consecutive_failures < 0:
            raise DifficultyValidationError(
                "consecutive_failures " "cannot be negative"
            )

        if current_level <= 0:
            raise DifficultyValidationError("current_level must be > 0")
