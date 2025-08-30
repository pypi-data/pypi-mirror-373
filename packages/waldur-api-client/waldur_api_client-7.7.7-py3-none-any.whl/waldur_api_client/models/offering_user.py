import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.offering_user_state_enum import OfferingUserStateEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="OfferingUser")


@_attrs_define
class OfferingUser:
    """
    Attributes:
        url (Union[Unset, str]):
        uuid (Union[Unset, UUID]):
        user (Union[Unset, str]):
        offering (Union[Unset, str]):
        username (Union[None, Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        offering_name (Union[Unset, str]):
        user_uuid (Union[Unset, UUID]):
        user_username (Union[Unset, str]): Required. 128 characters or fewer. Lowercase letters, numbers and @/./+/-/_
            characters
        user_full_name (Union[Unset, str]):
        user_email (Union[Unset, str]):
        created (Union[Unset, datetime.datetime]):
        modified (Union[Unset, datetime.datetime]):
        customer_uuid (Union[Unset, UUID]):
        customer_name (Union[Unset, str]):
        is_restricted (Union[Unset, bool]): Signal to service if the user account is restricted or not
        state (Union[Unset, OfferingUserStateEnum]):
        service_provider_comment (Union[Unset, str]): Additional comment for pending states like validation or account
            linking
        service_provider_comment_url (Union[Unset, str]): URL link for additional information or actions related to
            service provider comment
    """

    url: Union[Unset, str] = UNSET
    uuid: Union[Unset, UUID] = UNSET
    user: Union[Unset, str] = UNSET
    offering: Union[Unset, str] = UNSET
    username: Union[None, Unset, str] = UNSET
    offering_uuid: Union[Unset, UUID] = UNSET
    offering_name: Union[Unset, str] = UNSET
    user_uuid: Union[Unset, UUID] = UNSET
    user_username: Union[Unset, str] = UNSET
    user_full_name: Union[Unset, str] = UNSET
    user_email: Union[Unset, str] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    modified: Union[Unset, datetime.datetime] = UNSET
    customer_uuid: Union[Unset, UUID] = UNSET
    customer_name: Union[Unset, str] = UNSET
    is_restricted: Union[Unset, bool] = UNSET
    state: Union[Unset, OfferingUserStateEnum] = UNSET
    service_provider_comment: Union[Unset, str] = UNSET
    service_provider_comment_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        uuid: Union[Unset, str] = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        user = self.user

        offering = self.offering

        username: Union[None, Unset, str]
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        offering_uuid: Union[Unset, str] = UNSET
        if not isinstance(self.offering_uuid, Unset):
            offering_uuid = str(self.offering_uuid)

        offering_name = self.offering_name

        user_uuid: Union[Unset, str] = UNSET
        if not isinstance(self.user_uuid, Unset):
            user_uuid = str(self.user_uuid)

        user_username = self.user_username

        user_full_name = self.user_full_name

        user_email = self.user_email

        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        modified: Union[Unset, str] = UNSET
        if not isinstance(self.modified, Unset):
            modified = self.modified.isoformat()

        customer_uuid: Union[Unset, str] = UNSET
        if not isinstance(self.customer_uuid, Unset):
            customer_uuid = str(self.customer_uuid)

        customer_name = self.customer_name

        is_restricted = self.is_restricted

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        service_provider_comment = self.service_provider_comment

        service_provider_comment_url = self.service_provider_comment_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if user is not UNSET:
            field_dict["user"] = user
        if offering is not UNSET:
            field_dict["offering"] = offering
        if username is not UNSET:
            field_dict["username"] = username
        if offering_uuid is not UNSET:
            field_dict["offering_uuid"] = offering_uuid
        if offering_name is not UNSET:
            field_dict["offering_name"] = offering_name
        if user_uuid is not UNSET:
            field_dict["user_uuid"] = user_uuid
        if user_username is not UNSET:
            field_dict["user_username"] = user_username
        if user_full_name is not UNSET:
            field_dict["user_full_name"] = user_full_name
        if user_email is not UNSET:
            field_dict["user_email"] = user_email
        if created is not UNSET:
            field_dict["created"] = created
        if modified is not UNSET:
            field_dict["modified"] = modified
        if customer_uuid is not UNSET:
            field_dict["customer_uuid"] = customer_uuid
        if customer_name is not UNSET:
            field_dict["customer_name"] = customer_name
        if is_restricted is not UNSET:
            field_dict["is_restricted"] = is_restricted
        if state is not UNSET:
            field_dict["state"] = state
        if service_provider_comment is not UNSET:
            field_dict["service_provider_comment"] = service_provider_comment
        if service_provider_comment_url is not UNSET:
            field_dict["service_provider_comment_url"] = service_provider_comment_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        _uuid = d.pop("uuid", UNSET)
        uuid: Union[Unset, UUID]
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        user = d.pop("user", UNSET)

        offering = d.pop("offering", UNSET)

        def _parse_username(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        username = _parse_username(d.pop("username", UNSET))

        _offering_uuid = d.pop("offering_uuid", UNSET)
        offering_uuid: Union[Unset, UUID]
        if isinstance(_offering_uuid, Unset):
            offering_uuid = UNSET
        else:
            offering_uuid = UUID(_offering_uuid)

        offering_name = d.pop("offering_name", UNSET)

        _user_uuid = d.pop("user_uuid", UNSET)
        user_uuid: Union[Unset, UUID]
        if isinstance(_user_uuid, Unset):
            user_uuid = UNSET
        else:
            user_uuid = UUID(_user_uuid)

        user_username = d.pop("user_username", UNSET)

        user_full_name = d.pop("user_full_name", UNSET)

        user_email = d.pop("user_email", UNSET)

        _created = d.pop("created", UNSET)
        created: Union[Unset, datetime.datetime]
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = isoparse(_created)

        _modified = d.pop("modified", UNSET)
        modified: Union[Unset, datetime.datetime]
        if isinstance(_modified, Unset):
            modified = UNSET
        else:
            modified = isoparse(_modified)

        _customer_uuid = d.pop("customer_uuid", UNSET)
        customer_uuid: Union[Unset, UUID]
        if isinstance(_customer_uuid, Unset):
            customer_uuid = UNSET
        else:
            customer_uuid = UUID(_customer_uuid)

        customer_name = d.pop("customer_name", UNSET)

        is_restricted = d.pop("is_restricted", UNSET)

        _state = d.pop("state", UNSET)
        state: Union[Unset, OfferingUserStateEnum]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = OfferingUserStateEnum(_state)

        service_provider_comment = d.pop("service_provider_comment", UNSET)

        service_provider_comment_url = d.pop("service_provider_comment_url", UNSET)

        offering_user = cls(
            url=url,
            uuid=uuid,
            user=user,
            offering=offering,
            username=username,
            offering_uuid=offering_uuid,
            offering_name=offering_name,
            user_uuid=user_uuid,
            user_username=user_username,
            user_full_name=user_full_name,
            user_email=user_email,
            created=created,
            modified=modified,
            customer_uuid=customer_uuid,
            customer_name=customer_name,
            is_restricted=is_restricted,
            state=state,
            service_provider_comment=service_provider_comment,
            service_provider_comment_url=service_provider_comment_url,
        )

        offering_user.additional_properties = d
        return offering_user

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
