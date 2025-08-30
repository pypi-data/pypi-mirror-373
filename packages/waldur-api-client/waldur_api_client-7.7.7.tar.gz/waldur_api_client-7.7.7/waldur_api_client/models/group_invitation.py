import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="GroupInvitation")


@_attrs_define
class GroupInvitation:
    """
    Attributes:
        scope_uuid (UUID):
        scope_name (str):
        scope_type (Union[None, str]):
        customer_uuid (UUID):
        customer_name (str):
        role_name (str):
        role_description (str):
        created_by_full_name (str):
        created_by_username (str):
        url (str):
        uuid (UUID):
        role (UUID):
        created (datetime.datetime):
        expires (datetime.datetime):
        is_active (bool):
        scope_image (Union[None, str]):
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

    scope_uuid: UUID
    scope_name: str
    scope_type: Union[None, str]
    customer_uuid: UUID
    customer_name: str
    role_name: str
    role_description: str
    created_by_full_name: str
    created_by_username: str
    url: str
    uuid: UUID
    role: UUID
    created: datetime.datetime
    expires: datetime.datetime
    is_active: bool
    scope_image: Union[None, str]
    is_public: Union[Unset, bool] = UNSET
    auto_create_project: Union[Unset, bool] = UNSET
    project_name_template: Union[None, Unset, str] = UNSET
    project_role: Union[None, UUID, Unset] = UNSET
    user_affiliations: Union[Unset, Any] = UNSET
    user_email_patterns: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        scope_uuid = str(self.scope_uuid)

        scope_name = self.scope_name

        scope_type: Union[None, str]
        scope_type = self.scope_type

        customer_uuid = str(self.customer_uuid)

        customer_name = self.customer_name

        role_name = self.role_name

        role_description = self.role_description

        created_by_full_name = self.created_by_full_name

        created_by_username = self.created_by_username

        url = self.url

        uuid = str(self.uuid)

        role = str(self.role)

        created = self.created.isoformat()

        expires = self.expires.isoformat()

        is_active = self.is_active

        scope_image: Union[None, str]
        scope_image = self.scope_image

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
                "scope_uuid": scope_uuid,
                "scope_name": scope_name,
                "scope_type": scope_type,
                "customer_uuid": customer_uuid,
                "customer_name": customer_name,
                "role_name": role_name,
                "role_description": role_description,
                "created_by_full_name": created_by_full_name,
                "created_by_username": created_by_username,
                "url": url,
                "uuid": uuid,
                "role": role,
                "created": created,
                "expires": expires,
                "is_active": is_active,
                "scope_image": scope_image,
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
        scope_uuid = UUID(d.pop("scope_uuid"))

        scope_name = d.pop("scope_name")

        def _parse_scope_type(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        scope_type = _parse_scope_type(d.pop("scope_type"))

        customer_uuid = UUID(d.pop("customer_uuid"))

        customer_name = d.pop("customer_name")

        role_name = d.pop("role_name")

        role_description = d.pop("role_description")

        created_by_full_name = d.pop("created_by_full_name")

        created_by_username = d.pop("created_by_username")

        url = d.pop("url")

        uuid = UUID(d.pop("uuid"))

        role = UUID(d.pop("role"))

        created = isoparse(d.pop("created"))

        expires = isoparse(d.pop("expires"))

        is_active = d.pop("is_active")

        def _parse_scope_image(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        scope_image = _parse_scope_image(d.pop("scope_image"))

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

        group_invitation = cls(
            scope_uuid=scope_uuid,
            scope_name=scope_name,
            scope_type=scope_type,
            customer_uuid=customer_uuid,
            customer_name=customer_name,
            role_name=role_name,
            role_description=role_description,
            created_by_full_name=created_by_full_name,
            created_by_username=created_by_username,
            url=url,
            uuid=uuid,
            role=role,
            created=created,
            expires=expires,
            is_active=is_active,
            scope_image=scope_image,
            is_public=is_public,
            auto_create_project=auto_create_project,
            project_name_template=project_name_template,
            project_role=project_role,
            user_affiliations=user_affiliations,
            user_email_patterns=user_email_patterns,
        )

        group_invitation.additional_properties = d
        return group_invitation

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
