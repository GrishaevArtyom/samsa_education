from dataclasses import dataclass
from enum import StrEnum


MIN_LEVEL = 1
MAX_LEVEL = 10

INCREASE_THRESHOLD = 85.0
KEEP_THRESHOLD = 60.0
FAILURE_THRESHOLD = 3


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

    def adapt(self, performance: StudentPerformance, current_level: int) -> DifficultyDecision:
        self._validate(performance, current_level)

        accuracy = performance.accuracy

        if self._should_repeat(performance):
            return self._build(
                DifficultyAction.REPEAT_TOPIC,
                current_level,
                self._clamp(current_level - 1),
                accuracy,
            )

        action = self._get_action(accuracy)
        next_level = self._apply_action(action, current_level)

        return self._build(action, current_level, next_level, accuracy)

    def _get_action(self, accuracy: float) -> DifficultyAction:
        if accuracy >= INCREASE_THRESHOLD:
            return DifficultyAction.INCREASE
        if accuracy >= KEEP_THRESHOLD:
            return DifficultyAction.KEEP
        return DifficultyAction.DECREASE

    def _apply_action(self, action: DifficultyAction, level: int) -> int:
        if action == DifficultyAction.INCREASE:
            return self._clamp(level + 1)
        if action == DifficultyAction.DECREASE:
            return self._clamp(level - 1)
        return level

    def _clamp(self, level: int) -> int:
        return max(MIN_LEVEL, min(MAX_LEVEL, level))

    def _should_repeat(self, p: StudentPerformance) -> bool:
        return p.consecutive_failures >= FAILURE_THRESHOLD

    def _validate(self, p: StudentPerformance, level: int) -> None:
        if p.total_questions <= 0:
            raise DifficultyValidationError()
        if p.correct_answers < 0:
            raise DifficultyValidationError()
        if p.correct_answers > p.total_questions:
            raise DifficultyValidationError()
        if level <= 0:
            raise DifficultyValidationError()

    @staticmethod
    def _build(action, current, recommended, accuracy):
        return DifficultyDecision(
            action=action,
            current_level=current,
            recommended_level=recommended,
            accuracy=accuracy,
        )