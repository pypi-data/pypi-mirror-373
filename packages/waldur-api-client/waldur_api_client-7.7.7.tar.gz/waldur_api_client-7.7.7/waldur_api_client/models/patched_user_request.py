from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="PatchedUserRequest")


@_attrs_define
class PatchedUserRequest:
    """
    Attributes:
        username (Union[Unset, str]): Required. 128 characters or fewer. Lowercase letters, numbers and @/./+/-/_
            characters
        native_name (Union[Unset, str]):
        job_title (Union[Unset, str]):
        phone_number (Union[Unset, str]):
        organization (Union[Unset, str]):
        description (Union[Unset, str]):
        is_staff (Union[Unset, bool]): Designates whether the user can log into this admin site.
        is_active (Union[Unset, bool]): Designates whether this user should be treated as active. Unselect this instead
            of deleting accounts.
        is_support (Union[Unset, bool]): Designates whether the user is a global support user.
        token_lifetime (Union[None, Unset, int]): Token lifetime in seconds.
        agree_with_policy (Union[Unset, bool]): User must agree with the policy to register.
        notifications_enabled (Union[Unset, bool]): Designates whether the user is allowed to receive email
            notifications.
        preferred_language (Union[Unset, str]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        image (Union[File, None, Unset]):
    """

    username: Union[Unset, str] = UNSET
    native_name: Union[Unset, str] = UNSET
    job_title: Union[Unset, str] = UNSET
    phone_number: Union[Unset, str] = UNSET
    organization: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    is_staff: Union[Unset, bool] = UNSET
    is_active: Union[Unset, bool] = UNSET
    is_support: Union[Unset, bool] = UNSET
    token_lifetime: Union[None, Unset, int] = UNSET
    agree_with_policy: Union[Unset, bool] = UNSET
    notifications_enabled: Union[Unset, bool] = UNSET
    preferred_language: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    image: Union[File, None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        native_name = self.native_name

        job_title = self.job_title

        phone_number = self.phone_number

        organization = self.organization

        description = self.description

        is_staff = self.is_staff

        is_active = self.is_active

        is_support = self.is_support

        token_lifetime: Union[None, Unset, int]
        if isinstance(self.token_lifetime, Unset):
            token_lifetime = UNSET
        else:
            token_lifetime = self.token_lifetime

        agree_with_policy = self.agree_with_policy

        notifications_enabled = self.notifications_enabled

        preferred_language = self.preferred_language

        first_name = self.first_name

        last_name = self.last_name

        image: Union[None, Unset, types.FileTypes]
        if isinstance(self.image, Unset):
            image = UNSET
        elif isinstance(self.image, File):
            image = self.image.to_tuple()

        else:
            image = self.image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if native_name is not UNSET:
            field_dict["native_name"] = native_name
        if job_title is not UNSET:
            field_dict["job_title"] = job_title
        if phone_number is not UNSET:
            field_dict["phone_number"] = phone_number
        if organization is not UNSET:
            field_dict["organization"] = organization
        if description is not UNSET:
            field_dict["description"] = description
        if is_staff is not UNSET:
            field_dict["is_staff"] = is_staff
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if is_support is not UNSET:
            field_dict["is_support"] = is_support
        if token_lifetime is not UNSET:
            field_dict["token_lifetime"] = token_lifetime
        if agree_with_policy is not UNSET:
            field_dict["agree_with_policy"] = agree_with_policy
        if notifications_enabled is not UNSET:
            field_dict["notifications_enabled"] = notifications_enabled
        if preferred_language is not UNSET:
            field_dict["preferred_language"] = preferred_language
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if image is not UNSET:
            field_dict["image"] = image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username", UNSET)

        native_name = d.pop("native_name", UNSET)

        job_title = d.pop("job_title", UNSET)

        phone_number = d.pop("phone_number", UNSET)

        organization = d.pop("organization", UNSET)

        description = d.pop("description", UNSET)

        is_staff = d.pop("is_staff", UNSET)

        is_active = d.pop("is_active", UNSET)

        is_support = d.pop("is_support", UNSET)

        def _parse_token_lifetime(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        token_lifetime = _parse_token_lifetime(d.pop("token_lifetime", UNSET))

        agree_with_policy = d.pop("agree_with_policy", UNSET)

        notifications_enabled = d.pop("notifications_enabled", UNSET)

        preferred_language = d.pop("preferred_language", UNSET)

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        def _parse_image(data: object) -> Union[File, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                image_type_0 = File(payload=BytesIO(data))

                return image_type_0
            except:  # noqa: E722
                pass
            return cast(Union[File, None, Unset], data)

        image = _parse_image(d.pop("image", UNSET))

        patched_user_request = cls(
            username=username,
            native_name=native_name,
            job_title=job_title,
            phone_number=phone_number,
            organization=organization,
            description=description,
            is_staff=is_staff,
            is_active=is_active,
            is_support=is_support,
            token_lifetime=token_lifetime,
            agree_with_policy=agree_with_policy,
            notifications_enabled=notifications_enabled,
            preferred_language=preferred_language,
            first_name=first_name,
            last_name=last_name,
            image=image,
        )

        patched_user_request.additional_properties = d
        return patched_user_request

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
