from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.option_field_type_enum import OptionFieldTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="OptionFieldRequest")


@_attrs_define
class OptionFieldRequest:
    """
    Attributes:
        type_ (OptionFieldTypeEnum):
        label (str):
        help_text (Union[Unset, str]):
        required (Union[Unset, bool]):  Default: False.
        choices (Union[Unset, list[str]]):
        default (Union[Unset, str]):
        min_ (Union[Unset, int]):
        max_ (Union[Unset, int]):
    """

    type_: OptionFieldTypeEnum
    label: str
    help_text: Union[Unset, str] = UNSET
    required: Union[Unset, bool] = False
    choices: Union[Unset, list[str]] = UNSET
    default: Union[Unset, str] = UNSET
    min_: Union[Unset, int] = UNSET
    max_: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        label = self.label

        help_text = self.help_text

        required = self.required

        choices: Union[Unset, list[str]] = UNSET
        if not isinstance(self.choices, Unset):
            choices = self.choices

        default = self.default

        min_ = self.min_

        max_ = self.max_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "label": label,
            }
        )
        if help_text is not UNSET:
            field_dict["help_text"] = help_text
        if required is not UNSET:
            field_dict["required"] = required
        if choices is not UNSET:
            field_dict["choices"] = choices
        if default is not UNSET:
            field_dict["default"] = default
        if min_ is not UNSET:
            field_dict["min"] = min_
        if max_ is not UNSET:
            field_dict["max"] = max_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = OptionFieldTypeEnum(d.pop("type"))

        label = d.pop("label")

        help_text = d.pop("help_text", UNSET)

        required = d.pop("required", UNSET)

        choices = cast(list[str], d.pop("choices", UNSET))

        default = d.pop("default", UNSET)

        min_ = d.pop("min", UNSET)

        max_ = d.pop("max", UNSET)

        option_field_request = cls(
            type_=type_,
            label=label,
            help_text=help_text,
            required=required,
            choices=choices,
            default=default,
            min_=min_,
            max_=max_,
        )

        option_field_request.additional_properties = d
        return option_field_request

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
