from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.blank_enum import BlankEnum
from ..models.checklist_operators import ChecklistOperators
from ..models.question_type_enum import QuestionTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="QuestionAdminRequest")


@_attrs_define
class QuestionAdminRequest:
    """
    Attributes:
        checklist (str):
        description (Union[Unset, str]):
        user_guidance (Union[Unset, str]): Additional guidance text visible to users when answering and reviewing
        order (Union[Unset, int]):
        required (Union[Unset, bool]):
        question_type (Union[Unset, QuestionTypeEnum]):
        operator (Union[BlankEnum, ChecklistOperators, Unset]):
        review_answer_value (Union[Unset, Any]): Answer value that trigger review.
        always_requires_review (Union[Unset, bool]): This question always requires review regardless of answer
        guidance_answer_value (Union[Unset, Any]): Answer value that triggers display of user guidance.
        guidance_operator (Union[BlankEnum, ChecklistOperators, Unset]): Operator to use when comparing answer with
            guidance_answer_value
        always_show_guidance (Union[Unset, bool]): Show user guidance always, regardless of answer. If False, guidance
            is conditional on answer matching guidance_answer_value with guidance_operator
        min_value (Union[None, Unset, str]): Minimum value allowed for NUMBER type questions
        max_value (Union[None, Unset, str]): Maximum value allowed for NUMBER type questions
    """

    checklist: str
    description: Union[Unset, str] = UNSET
    user_guidance: Union[Unset, str] = UNSET
    order: Union[Unset, int] = UNSET
    required: Union[Unset, bool] = UNSET
    question_type: Union[Unset, QuestionTypeEnum] = UNSET
    operator: Union[BlankEnum, ChecklistOperators, Unset] = UNSET
    review_answer_value: Union[Unset, Any] = UNSET
    always_requires_review: Union[Unset, bool] = UNSET
    guidance_answer_value: Union[Unset, Any] = UNSET
    guidance_operator: Union[BlankEnum, ChecklistOperators, Unset] = UNSET
    always_show_guidance: Union[Unset, bool] = UNSET
    min_value: Union[None, Unset, str] = UNSET
    max_value: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        checklist = self.checklist

        description = self.description

        user_guidance = self.user_guidance

        order = self.order

        required = self.required

        question_type: Union[Unset, str] = UNSET
        if not isinstance(self.question_type, Unset):
            question_type = self.question_type.value

        operator: Union[Unset, str]
        if isinstance(self.operator, Unset):
            operator = UNSET
        elif isinstance(self.operator, ChecklistOperators):
            operator = self.operator.value
        else:
            operator = self.operator.value

        review_answer_value = self.review_answer_value

        always_requires_review = self.always_requires_review

        guidance_answer_value = self.guidance_answer_value

        guidance_operator: Union[Unset, str]
        if isinstance(self.guidance_operator, Unset):
            guidance_operator = UNSET
        elif isinstance(self.guidance_operator, ChecklistOperators):
            guidance_operator = self.guidance_operator.value
        else:
            guidance_operator = self.guidance_operator.value

        always_show_guidance = self.always_show_guidance

        min_value: Union[None, Unset, str]
        if isinstance(self.min_value, Unset):
            min_value = UNSET
        else:
            min_value = self.min_value

        max_value: Union[None, Unset, str]
        if isinstance(self.max_value, Unset):
            max_value = UNSET
        else:
            max_value = self.max_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "checklist": checklist,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if user_guidance is not UNSET:
            field_dict["user_guidance"] = user_guidance
        if order is not UNSET:
            field_dict["order"] = order
        if required is not UNSET:
            field_dict["required"] = required
        if question_type is not UNSET:
            field_dict["question_type"] = question_type
        if operator is not UNSET:
            field_dict["operator"] = operator
        if review_answer_value is not UNSET:
            field_dict["review_answer_value"] = review_answer_value
        if always_requires_review is not UNSET:
            field_dict["always_requires_review"] = always_requires_review
        if guidance_answer_value is not UNSET:
            field_dict["guidance_answer_value"] = guidance_answer_value
        if guidance_operator is not UNSET:
            field_dict["guidance_operator"] = guidance_operator
        if always_show_guidance is not UNSET:
            field_dict["always_show_guidance"] = always_show_guidance
        if min_value is not UNSET:
            field_dict["min_value"] = min_value
        if max_value is not UNSET:
            field_dict["max_value"] = max_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        checklist = d.pop("checklist")

        description = d.pop("description", UNSET)

        user_guidance = d.pop("user_guidance", UNSET)

        order = d.pop("order", UNSET)

        required = d.pop("required", UNSET)

        _question_type = d.pop("question_type", UNSET)
        question_type: Union[Unset, QuestionTypeEnum]
        if isinstance(_question_type, Unset):
            question_type = UNSET
        else:
            question_type = QuestionTypeEnum(_question_type)

        def _parse_operator(data: object) -> Union[BlankEnum, ChecklistOperators, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                operator_type_0 = ChecklistOperators(data)

                return operator_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, str):
                raise TypeError()
            operator_type_1 = BlankEnum(data)

            return operator_type_1

        operator = _parse_operator(d.pop("operator", UNSET))

        review_answer_value = d.pop("review_answer_value", UNSET)

        always_requires_review = d.pop("always_requires_review", UNSET)

        guidance_answer_value = d.pop("guidance_answer_value", UNSET)

        def _parse_guidance_operator(data: object) -> Union[BlankEnum, ChecklistOperators, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                guidance_operator_type_0 = ChecklistOperators(data)

                return guidance_operator_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, str):
                raise TypeError()
            guidance_operator_type_1 = BlankEnum(data)

            return guidance_operator_type_1

        guidance_operator = _parse_guidance_operator(d.pop("guidance_operator", UNSET))

        always_show_guidance = d.pop("always_show_guidance", UNSET)

        def _parse_min_value(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        min_value = _parse_min_value(d.pop("min_value", UNSET))

        def _parse_max_value(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        max_value = _parse_max_value(d.pop("max_value", UNSET))

        question_admin_request = cls(
            checklist=checklist,
            description=description,
            user_guidance=user_guidance,
            order=order,
            required=required,
            question_type=question_type,
            operator=operator,
            review_answer_value=review_answer_value,
            always_requires_review=always_requires_review,
            guidance_answer_value=guidance_answer_value,
            guidance_operator=guidance_operator,
            always_show_guidance=always_show_guidance,
            min_value=min_value,
            max_value=max_value,
        )

        question_admin_request.additional_properties = d
        return question_admin_request

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
