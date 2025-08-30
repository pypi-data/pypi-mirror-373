from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchedProtectedCallRequest")


@_attrs_define
class PatchedProtectedCallRequest:
    """
    Attributes:
        name (Union[Unset, str]):
        description (Union[Unset, str]):
        fixed_duration_in_days (Union[None, Unset, int]):
        backend_id (Union[Unset, str]):
        external_url (Union[None, Unset, str]):
        reviewer_identity_visible_to_submitters (Union[Unset, bool]): Whether proposal submitters can see reviewer
            identities
        reviews_visible_to_submitters (Union[Unset, bool]): Whether proposal submitters can see review comments and
            scores
        created_by (Union[None, Unset, str]):
        reference_code (Union[Unset, str]):
        compliance_checklist (Union[None, UUID, Unset]): Compliance checklist that proposals must complete before
            submission
    """

    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    fixed_duration_in_days: Union[None, Unset, int] = UNSET
    backend_id: Union[Unset, str] = UNSET
    external_url: Union[None, Unset, str] = UNSET
    reviewer_identity_visible_to_submitters: Union[Unset, bool] = UNSET
    reviews_visible_to_submitters: Union[Unset, bool] = UNSET
    created_by: Union[None, Unset, str] = UNSET
    reference_code: Union[Unset, str] = UNSET
    compliance_checklist: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        fixed_duration_in_days: Union[None, Unset, int]
        if isinstance(self.fixed_duration_in_days, Unset):
            fixed_duration_in_days = UNSET
        else:
            fixed_duration_in_days = self.fixed_duration_in_days

        backend_id = self.backend_id

        external_url: Union[None, Unset, str]
        if isinstance(self.external_url, Unset):
            external_url = UNSET
        else:
            external_url = self.external_url

        reviewer_identity_visible_to_submitters = self.reviewer_identity_visible_to_submitters

        reviews_visible_to_submitters = self.reviews_visible_to_submitters

        created_by: Union[None, Unset, str]
        if isinstance(self.created_by, Unset):
            created_by = UNSET
        else:
            created_by = self.created_by

        reference_code = self.reference_code

        compliance_checklist: Union[None, Unset, str]
        if isinstance(self.compliance_checklist, Unset):
            compliance_checklist = UNSET
        elif isinstance(self.compliance_checklist, UUID):
            compliance_checklist = str(self.compliance_checklist)
        else:
            compliance_checklist = self.compliance_checklist

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if fixed_duration_in_days is not UNSET:
            field_dict["fixed_duration_in_days"] = fixed_duration_in_days
        if backend_id is not UNSET:
            field_dict["backend_id"] = backend_id
        if external_url is not UNSET:
            field_dict["external_url"] = external_url
        if reviewer_identity_visible_to_submitters is not UNSET:
            field_dict["reviewer_identity_visible_to_submitters"] = reviewer_identity_visible_to_submitters
        if reviews_visible_to_submitters is not UNSET:
            field_dict["reviews_visible_to_submitters"] = reviews_visible_to_submitters
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if reference_code is not UNSET:
            field_dict["reference_code"] = reference_code
        if compliance_checklist is not UNSET:
            field_dict["compliance_checklist"] = compliance_checklist

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        def _parse_fixed_duration_in_days(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        fixed_duration_in_days = _parse_fixed_duration_in_days(d.pop("fixed_duration_in_days", UNSET))

        backend_id = d.pop("backend_id", UNSET)

        def _parse_external_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_url = _parse_external_url(d.pop("external_url", UNSET))

        reviewer_identity_visible_to_submitters = d.pop("reviewer_identity_visible_to_submitters", UNSET)

        reviews_visible_to_submitters = d.pop("reviews_visible_to_submitters", UNSET)

        def _parse_created_by(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        created_by = _parse_created_by(d.pop("created_by", UNSET))

        reference_code = d.pop("reference_code", UNSET)

        def _parse_compliance_checklist(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                compliance_checklist_type_0 = UUID(data)

                return compliance_checklist_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        compliance_checklist = _parse_compliance_checklist(d.pop("compliance_checklist", UNSET))

        patched_protected_call_request = cls(
            name=name,
            description=description,
            fixed_duration_in_days=fixed_duration_in_days,
            backend_id=backend_id,
            external_url=external_url,
            reviewer_identity_visible_to_submitters=reviewer_identity_visible_to_submitters,
            reviews_visible_to_submitters=reviews_visible_to_submitters,
            created_by=created_by,
            reference_code=reference_code,
            compliance_checklist=compliance_checklist,
        )

        patched_protected_call_request.additional_properties = d
        return patched_protected_call_request

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
