import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.permission import Permission


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        url (Union[Unset, str]):
        uuid (Union[Unset, UUID]):
        username (Union[Unset, str]): Required. 128 characters or fewer. Lowercase letters, numbers and @/./+/-/_
            characters
        slug (Union[Unset, str]):
        full_name (Union[Unset, str]):
        native_name (Union[Unset, str]):
        job_title (Union[Unset, str]):
        email (Union[Unset, str]):
        phone_number (Union[Unset, str]):
        organization (Union[Unset, str]):
        civil_number (Union[None, Unset, str]):
        description (Union[Unset, str]):
        is_staff (Union[Unset, bool]): Designates whether the user can log into this admin site.
        is_active (Union[Unset, bool]): Designates whether this user should be treated as active. Unselect this instead
            of deleting accounts.
        is_support (Union[Unset, bool]): Designates whether the user is a global support user.
        token (Union[Unset, str]):
        token_lifetime (Union[None, Unset, int]): Token lifetime in seconds.
        token_expires_at (Union[None, Unset, datetime.datetime]):
        registration_method (Union[Unset, str]): Indicates what registration method was used.
        date_joined (Union[Unset, datetime.datetime]):
        agreement_date (Union[None, Unset, datetime.datetime]): Indicates when the user has agreed with the policy.
        notifications_enabled (Union[Unset, bool]): Designates whether the user is allowed to receive email
            notifications.
        preferred_language (Union[Unset, str]):
        permissions (Union[Unset, list['Permission']]):
        requested_email (Union[None, Unset, str]):
        affiliations (Union[Unset, Any]): Person's affiliation within organization such as student, faculty, staff.
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        identity_provider_name (Union[Unset, str]):
        identity_provider_label (Union[Unset, str]):
        identity_provider_management_url (Union[Unset, str]):
        identity_provider_fields (Union[Unset, list[str]]):
        image (Union[None, Unset, str]):
        identity_source (Union[Unset, str]): Indicates what identity provider was used.
        has_active_session (Union[Unset, bool]):
    """

    url: Union[Unset, str] = UNSET
    uuid: Union[Unset, UUID] = UNSET
    username: Union[Unset, str] = UNSET
    slug: Union[Unset, str] = UNSET
    full_name: Union[Unset, str] = UNSET
    native_name: Union[Unset, str] = UNSET
    job_title: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    phone_number: Union[Unset, str] = UNSET
    organization: Union[Unset, str] = UNSET
    civil_number: Union[None, Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    is_staff: Union[Unset, bool] = UNSET
    is_active: Union[Unset, bool] = UNSET
    is_support: Union[Unset, bool] = UNSET
    token: Union[Unset, str] = UNSET
    token_lifetime: Union[None, Unset, int] = UNSET
    token_expires_at: Union[None, Unset, datetime.datetime] = UNSET
    registration_method: Union[Unset, str] = UNSET
    date_joined: Union[Unset, datetime.datetime] = UNSET
    agreement_date: Union[None, Unset, datetime.datetime] = UNSET
    notifications_enabled: Union[Unset, bool] = UNSET
    preferred_language: Union[Unset, str] = UNSET
    permissions: Union[Unset, list["Permission"]] = UNSET
    requested_email: Union[None, Unset, str] = UNSET
    affiliations: Union[Unset, Any] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    identity_provider_name: Union[Unset, str] = UNSET
    identity_provider_label: Union[Unset, str] = UNSET
    identity_provider_management_url: Union[Unset, str] = UNSET
    identity_provider_fields: Union[Unset, list[str]] = UNSET
    image: Union[None, Unset, str] = UNSET
    identity_source: Union[Unset, str] = UNSET
    has_active_session: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        uuid: Union[Unset, str] = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        username = self.username

        slug = self.slug

        full_name = self.full_name

        native_name = self.native_name

        job_title = self.job_title

        email = self.email

        phone_number = self.phone_number

        organization = self.organization

        civil_number: Union[None, Unset, str]
        if isinstance(self.civil_number, Unset):
            civil_number = UNSET
        else:
            civil_number = self.civil_number

        description = self.description

        is_staff = self.is_staff

        is_active = self.is_active

        is_support = self.is_support

        token = self.token

        token_lifetime: Union[None, Unset, int]
        if isinstance(self.token_lifetime, Unset):
            token_lifetime = UNSET
        else:
            token_lifetime = self.token_lifetime

        token_expires_at: Union[None, Unset, str]
        if isinstance(self.token_expires_at, Unset):
            token_expires_at = UNSET
        elif isinstance(self.token_expires_at, datetime.datetime):
            token_expires_at = self.token_expires_at.isoformat()
        else:
            token_expires_at = self.token_expires_at

        registration_method = self.registration_method

        date_joined: Union[Unset, str] = UNSET
        if not isinstance(self.date_joined, Unset):
            date_joined = self.date_joined.isoformat()

        agreement_date: Union[None, Unset, str]
        if isinstance(self.agreement_date, Unset):
            agreement_date = UNSET
        elif isinstance(self.agreement_date, datetime.datetime):
            agreement_date = self.agreement_date.isoformat()
        else:
            agreement_date = self.agreement_date

        notifications_enabled = self.notifications_enabled

        preferred_language = self.preferred_language

        permissions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = []
            for permissions_item_data in self.permissions:
                permissions_item = permissions_item_data.to_dict()
                permissions.append(permissions_item)

        requested_email: Union[None, Unset, str]
        if isinstance(self.requested_email, Unset):
            requested_email = UNSET
        else:
            requested_email = self.requested_email

        affiliations = self.affiliations

        first_name = self.first_name

        last_name = self.last_name

        identity_provider_name = self.identity_provider_name

        identity_provider_label = self.identity_provider_label

        identity_provider_management_url = self.identity_provider_management_url

        identity_provider_fields: Union[Unset, list[str]] = UNSET
        if not isinstance(self.identity_provider_fields, Unset):
            identity_provider_fields = self.identity_provider_fields

        image: Union[None, Unset, str]
        if isinstance(self.image, Unset):
            image = UNSET
        else:
            image = self.image

        identity_source = self.identity_source

        has_active_session = self.has_active_session

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if username is not UNSET:
            field_dict["username"] = username
        if slug is not UNSET:
            field_dict["slug"] = slug
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if native_name is not UNSET:
            field_dict["native_name"] = native_name
        if job_title is not UNSET:
            field_dict["job_title"] = job_title
        if email is not UNSET:
            field_dict["email"] = email
        if phone_number is not UNSET:
            field_dict["phone_number"] = phone_number
        if organization is not UNSET:
            field_dict["organization"] = organization
        if civil_number is not UNSET:
            field_dict["civil_number"] = civil_number
        if description is not UNSET:
            field_dict["description"] = description
        if is_staff is not UNSET:
            field_dict["is_staff"] = is_staff
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if is_support is not UNSET:
            field_dict["is_support"] = is_support
        if token is not UNSET:
            field_dict["token"] = token
        if token_lifetime is not UNSET:
            field_dict["token_lifetime"] = token_lifetime
        if token_expires_at is not UNSET:
            field_dict["token_expires_at"] = token_expires_at
        if registration_method is not UNSET:
            field_dict["registration_method"] = registration_method
        if date_joined is not UNSET:
            field_dict["date_joined"] = date_joined
        if agreement_date is not UNSET:
            field_dict["agreement_date"] = agreement_date
        if notifications_enabled is not UNSET:
            field_dict["notifications_enabled"] = notifications_enabled
        if preferred_language is not UNSET:
            field_dict["preferred_language"] = preferred_language
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if requested_email is not UNSET:
            field_dict["requested_email"] = requested_email
        if affiliations is not UNSET:
            field_dict["affiliations"] = affiliations
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if identity_provider_name is not UNSET:
            field_dict["identity_provider_name"] = identity_provider_name
        if identity_provider_label is not UNSET:
            field_dict["identity_provider_label"] = identity_provider_label
        if identity_provider_management_url is not UNSET:
            field_dict["identity_provider_management_url"] = identity_provider_management_url
        if identity_provider_fields is not UNSET:
            field_dict["identity_provider_fields"] = identity_provider_fields
        if image is not UNSET:
            field_dict["image"] = image
        if identity_source is not UNSET:
            field_dict["identity_source"] = identity_source
        if has_active_session is not UNSET:
            field_dict["has_active_session"] = has_active_session

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.permission import Permission

        d = dict(src_dict)
        url = d.pop("url", UNSET)

        _uuid = d.pop("uuid", UNSET)
        uuid: Union[Unset, UUID]
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        username = d.pop("username", UNSET)

        slug = d.pop("slug", UNSET)

        full_name = d.pop("full_name", UNSET)

        native_name = d.pop("native_name", UNSET)

        job_title = d.pop("job_title", UNSET)

        email = d.pop("email", UNSET)

        phone_number = d.pop("phone_number", UNSET)

        organization = d.pop("organization", UNSET)

        def _parse_civil_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        civil_number = _parse_civil_number(d.pop("civil_number", UNSET))

        description = d.pop("description", UNSET)

        is_staff = d.pop("is_staff", UNSET)

        is_active = d.pop("is_active", UNSET)

        is_support = d.pop("is_support", UNSET)

        token = d.pop("token", UNSET)

        def _parse_token_lifetime(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        token_lifetime = _parse_token_lifetime(d.pop("token_lifetime", UNSET))

        def _parse_token_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                token_expires_at_type_0 = isoparse(data)

                return token_expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        token_expires_at = _parse_token_expires_at(d.pop("token_expires_at", UNSET))

        registration_method = d.pop("registration_method", UNSET)

        _date_joined = d.pop("date_joined", UNSET)
        date_joined: Union[Unset, datetime.datetime]
        if isinstance(_date_joined, Unset):
            date_joined = UNSET
        else:
            date_joined = isoparse(_date_joined)

        def _parse_agreement_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                agreement_date_type_0 = isoparse(data)

                return agreement_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        agreement_date = _parse_agreement_date(d.pop("agreement_date", UNSET))

        notifications_enabled = d.pop("notifications_enabled", UNSET)

        preferred_language = d.pop("preferred_language", UNSET)

        permissions = []
        _permissions = d.pop("permissions", UNSET)
        for permissions_item_data in _permissions or []:
            permissions_item = Permission.from_dict(permissions_item_data)

            permissions.append(permissions_item)

        def _parse_requested_email(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        requested_email = _parse_requested_email(d.pop("requested_email", UNSET))

        affiliations = d.pop("affiliations", UNSET)

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        identity_provider_name = d.pop("identity_provider_name", UNSET)

        identity_provider_label = d.pop("identity_provider_label", UNSET)

        identity_provider_management_url = d.pop("identity_provider_management_url", UNSET)

        identity_provider_fields = cast(list[str], d.pop("identity_provider_fields", UNSET))

        def _parse_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image = _parse_image(d.pop("image", UNSET))

        identity_source = d.pop("identity_source", UNSET)

        has_active_session = d.pop("has_active_session", UNSET)

        user = cls(
            url=url,
            uuid=uuid,
            username=username,
            slug=slug,
            full_name=full_name,
            native_name=native_name,
            job_title=job_title,
            email=email,
            phone_number=phone_number,
            organization=organization,
            civil_number=civil_number,
            description=description,
            is_staff=is_staff,
            is_active=is_active,
            is_support=is_support,
            token=token,
            token_lifetime=token_lifetime,
            token_expires_at=token_expires_at,
            registration_method=registration_method,
            date_joined=date_joined,
            agreement_date=agreement_date,
            notifications_enabled=notifications_enabled,
            preferred_language=preferred_language,
            permissions=permissions,
            requested_email=requested_email,
            affiliations=affiliations,
            first_name=first_name,
            last_name=last_name,
            identity_provider_name=identity_provider_name,
            identity_provider_label=identity_provider_label,
            identity_provider_management_url=identity_provider_management_url,
            identity_provider_fields=identity_provider_fields,
            image=image,
            identity_source=identity_source,
            has_active_session=has_active_session,
        )

        user.additional_properties = d
        return user

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
