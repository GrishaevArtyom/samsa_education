from dataclasses import dataclass
from enum import StrEnum


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


@dataclass(slots=True, frozen=True)
class DifficultyDecision:
    action: DifficultyAction
    current_level: int
    recommended_level: int
    accuracy: float


class DifficultyValidationError(ValueError):
    pass


class DifficultyAdapter:

    def adapt(self, performance: StudentPerformance, current_level: int):
        if performance.total_questions <= 0:
            raise DifficultyValidationError("total_questions must be > 0")

        if performance.correct_answers < 0:
            raise DifficultyValidationError("correct_answers cannot be negative")

        if performance.correct_answers > performance.total_questions:
            raise DifficultyValidationError("correct_answers cannot exceed total_questions")

        if current_level <= 0:
            raise DifficultyValidationError("current_level must be > 0")

        accuracy = (performance.correct_answers / performance.total_questions) * 100

        if performance.consecutive_failures >= 3:
            return DifficultyDecision(
                action=DifficultyAction.REPEAT_TOPIC,
                current_level=current_level,
                recommended_level=max(1, current_level - 1),
                accuracy=accuracy,
            )

        if accuracy >= 85:
            return DifficultyDecision(
                action=DifficultyAction.INCREASE,
                current_level=current_level,
                recommended_level=min(10, current_level + 1),
                accuracy=accuracy,
            )

        if accuracy >= 60:
            return DifficultyDecision(
                action=DifficultyAction.KEEP,
                current_level=current_level,
                recommended_level=current_level,
                accuracy=accuracy,
            )

        return DifficultyDecision(
            action=DifficultyAction.DECREASE,
            current_level=current_level,
            recommended_level=max(1, current_level - 1),
            accuracy=accuracy,
        )