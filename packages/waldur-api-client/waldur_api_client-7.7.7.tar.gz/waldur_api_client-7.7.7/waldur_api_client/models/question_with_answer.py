from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.question_type_enum import QuestionTypeEnum

if TYPE_CHECKING:
    from ..models.question_with_answer_existing_answer_type_0 import QuestionWithAnswerExistingAnswerType0


T = TypeVar("T", bound="QuestionWithAnswer")


@_attrs_define
class QuestionWithAnswer:
    """
    Attributes:
        uuid (UUID):
        description (str):
        user_guidance (Union[None, str]):
        question_type (QuestionTypeEnum):
        required (bool):
        order (int):
        existing_answer (Union['QuestionWithAnswerExistingAnswerType0', None]):
        question_options (Union[None, list[Any]]):
        min_value (Union[None, str]): Minimum value allowed for NUMBER type questions
        max_value (Union[None, str]): Maximum value allowed for NUMBER type questions
    """

    uuid: UUID
    description: str
    user_guidance: Union[None, str]
    question_type: QuestionTypeEnum
    required: bool
    order: int
    existing_answer: Union["QuestionWithAnswerExistingAnswerType0", None]
    question_options: Union[None, list[Any]]
    min_value: Union[None, str]
    max_value: Union[None, str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.question_with_answer_existing_answer_type_0 import QuestionWithAnswerExistingAnswerType0

        uuid = str(self.uuid)

        description = self.description

        user_guidance: Union[None, str]
        user_guidance = self.user_guidance

        question_type = self.question_type.value

        required = self.required

        order = self.order

        existing_answer: Union[None, dict[str, Any]]
        if isinstance(self.existing_answer, QuestionWithAnswerExistingAnswerType0):
            existing_answer = self.existing_answer.to_dict()
        else:
            existing_answer = self.existing_answer

        question_options: Union[None, list[Any]]
        if isinstance(self.question_options, list):
            question_options = self.question_options

        else:
            question_options = self.question_options

        min_value: Union[None, str]
        min_value = self.min_value

        max_value: Union[None, str]
        max_value = self.max_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "description": description,
                "user_guidance": user_guidance,
                "question_type": question_type,
                "required": required,
                "order": order,
                "existing_answer": existing_answer,
                "question_options": question_options,
                "min_value": min_value,
                "max_value": max_value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.question_with_answer_existing_answer_type_0 import QuestionWithAnswerExistingAnswerType0

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        description = d.pop("description")

        def _parse_user_guidance(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        user_guidance = _parse_user_guidance(d.pop("user_guidance"))

        question_type = QuestionTypeEnum(d.pop("question_type"))

        required = d.pop("required")

        order = d.pop("order")

        def _parse_existing_answer(data: object) -> Union["QuestionWithAnswerExistingAnswerType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                existing_answer_type_0 = QuestionWithAnswerExistingAnswerType0.from_dict(data)

                return existing_answer_type_0
            except:  # noqa: E722
                pass
            return cast(Union["QuestionWithAnswerExistingAnswerType0", None], data)

        existing_answer = _parse_existing_answer(d.pop("existing_answer"))

        def _parse_question_options(data: object) -> Union[None, list[Any]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                question_options_type_0 = cast(list[Any], data)

                return question_options_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list[Any]], data)

        question_options = _parse_question_options(d.pop("question_options"))

        def _parse_min_value(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        min_value = _parse_min_value(d.pop("min_value"))

        def _parse_max_value(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        max_value = _parse_max_value(d.pop("max_value"))

        question_with_answer = cls(
            uuid=uuid,
            description=description,
            user_guidance=user_guidance,
            question_type=question_type,
            required=required,
            order=order,
            existing_answer=existing_answer,
            question_options=question_options,
            min_value=min_value,
            max_value=max_value,
        )

        question_with_answer.additional_properties = d
        return question_with_answer

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
