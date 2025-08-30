from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GroupInvitationRequest")


@_attrs_define
class GroupInvitationRequest:
    """
    Attributes:
        role (UUID):
        scope (str):
        is_public (Union[Unset, bool]): Allow non-authenticated users to see and accept this invitation. Only staff can
            create public invitations.
        auto_create_project (Union[Unset, bool]): Create project and grant project permissions instead of customer
            permissions
        project_name_template (Union[None, Unset, str]): Template for project name. Supports {username}, {email},
            {full_name} variables
        project_role (Union[None, UUID, Unset]):
        user_affiliations (Union[Unset, Any]):
        user_email_patterns (Union[Unset, Any]):
    """

    role: UUID
    scope: str
    is_public: Union[Unset, bool] = UNSET
    auto_create_project: Union[Unset, bool] = UNSET
    project_name_template: Union[None, Unset, str] = UNSET
    project_role: Union[None, UUID, Unset] = UNSET
    user_affiliations: Union[Unset, Any] = UNSET
    user_email_patterns: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = str(self.role)

        scope = self.scope

        is_public = self.is_public

        auto_create_project = self.auto_create_project

        project_name_template: Union[None, Unset, str]
        if isinstance(self.project_name_template, Unset):
            project_name_template = UNSET
        else:
            project_name_template = self.project_name_template

        project_role: Union[None, Unset, str]
        if isinstance(self.project_role, Unset):
            project_role = UNSET
        elif isinstance(self.project_role, UUID):
            project_role = str(self.project_role)
        else:
            project_role = self.project_role

        user_affiliations = self.user_affiliations

        user_email_patterns = self.user_email_patterns

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "scope": scope,
            }
        )
        if is_public is not UNSET:
            field_dict["is_public"] = is_public
        if auto_create_project is not UNSET:
            field_dict["auto_create_project"] = auto_create_project
        if project_name_template is not UNSET:
            field_dict["project_name_template"] = project_name_template
        if project_role is not UNSET:
            field_dict["project_role"] = project_role
        if user_affiliations is not UNSET:
            field_dict["user_affiliations"] = user_affiliations
        if user_email_patterns is not UNSET:
            field_dict["user_email_patterns"] = user_email_patterns

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = UUID(d.pop("role"))

        scope = d.pop("scope")

        is_public = d.pop("is_public", UNSET)

        auto_create_project = d.pop("auto_create_project", UNSET)

        def _parse_project_name_template(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        project_name_template = _parse_project_name_template(d.pop("project_name_template", UNSET))

        def _parse_project_role(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                project_role_type_0 = UUID(data)

                return project_role_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        project_role = _parse_project_role(d.pop("project_role", UNSET))

        user_affiliations = d.pop("user_affiliations", UNSET)

        user_email_patterns = d.pop("user_email_patterns", UNSET)

        group_invitation_request = cls(
            role=role,
            scope=scope,
            is_public=is_public,
            auto_create_project=auto_create_project,
            project_name_template=project_name_template,
            project_role=project_role,
            user_affiliations=user_affiliations,
            user_email_patterns=user_email_patterns,
        )

        group_invitation_request.additional_properties = d
        return group_invitation_request

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
