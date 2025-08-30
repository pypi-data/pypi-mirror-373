from enum import Enum


class QuestionTypeEnum(str, Enum):
    BOOLEAN = "boolean"
    DATE = "date"
    FILE = "file"
    MULTI_SELECT = "multi_select"
    NUMBER = "number"
    SINGLE_SELECT = "single_select"
    TEXT_AREA = "text_area"
    TEXT_INPUT = "text_input"

    def __str__(self) -> str:
        return str(self.value)
