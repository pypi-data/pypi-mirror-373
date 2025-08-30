from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="IdentityProvider")


@_attrs_define
class IdentityProvider:
    """
    Attributes:
        provider (str):
        client_id (str): ID of application used for OAuth authentication.
        discovery_url (str): The endpoint for endpoint discovery.
        userinfo_url (str): The endpoint for fetching user info.
        token_url (str): The endpoint for obtaining auth token.
        auth_url (str): The endpoint for authorization request flow.
        logout_url (str): The endpoint used to redirect after sign-out.
        label (str): Human-readable identity provider is label.
        is_active (Union[Unset, bool]):
        verify_ssl (Union[Unset, bool]):
        enable_post_logout_redirect (Union[Unset, bool]):
        enable_pkce (Union[Unset, bool]):
        management_url (Union[Unset, str]): The endpoint for user details management.
        protected_fields (Union[Unset, Any]):
        extra_scope (Union[None, Unset, str]): Space-separated list of scopes to request during authentication.
    """

    provider: str
    client_id: str
    discovery_url: str
    userinfo_url: str
    token_url: str
    auth_url: str
    logout_url: str
    label: str
    is_active: Union[Unset, bool] = UNSET
    verify_ssl: Union[Unset, bool] = UNSET
    enable_post_logout_redirect: Union[Unset, bool] = UNSET
    enable_pkce: Union[Unset, bool] = UNSET
    management_url: Union[Unset, str] = UNSET
    protected_fields: Union[Unset, Any] = UNSET
    extra_scope: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider = self.provider

        client_id = self.client_id

        discovery_url = self.discovery_url

        userinfo_url = self.userinfo_url

        token_url = self.token_url

        auth_url = self.auth_url

        logout_url = self.logout_url

        label = self.label

        is_active = self.is_active

        verify_ssl = self.verify_ssl

        enable_post_logout_redirect = self.enable_post_logout_redirect

        enable_pkce = self.enable_pkce

        management_url = self.management_url

        protected_fields = self.protected_fields

        extra_scope: Union[None, Unset, str]
        if isinstance(self.extra_scope, Unset):
            extra_scope = UNSET
        else:
            extra_scope = self.extra_scope

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider": provider,
                "client_id": client_id,
                "discovery_url": discovery_url,
                "userinfo_url": userinfo_url,
                "token_url": token_url,
                "auth_url": auth_url,
                "logout_url": logout_url,
                "label": label,
            }
        )
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if verify_ssl is not UNSET:
            field_dict["verify_ssl"] = verify_ssl
        if enable_post_logout_redirect is not UNSET:
            field_dict["enable_post_logout_redirect"] = enable_post_logout_redirect
        if enable_pkce is not UNSET:
            field_dict["enable_pkce"] = enable_pkce
        if management_url is not UNSET:
            field_dict["management_url"] = management_url
        if protected_fields is not UNSET:
            field_dict["protected_fields"] = protected_fields
        if extra_scope is not UNSET:
            field_dict["extra_scope"] = extra_scope

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        provider = d.pop("provider")

        client_id = d.pop("client_id")

        discovery_url = d.pop("discovery_url")

        userinfo_url = d.pop("userinfo_url")

        token_url = d.pop("token_url")

        auth_url = d.pop("auth_url")

        logout_url = d.pop("logout_url")

        label = d.pop("label")

        is_active = d.pop("is_active", UNSET)

        verify_ssl = d.pop("verify_ssl", UNSET)

        enable_post_logout_redirect = d.pop("enable_post_logout_redirect", UNSET)

        enable_pkce = d.pop("enable_pkce", UNSET)

        management_url = d.pop("management_url", UNSET)

        protected_fields = d.pop("protected_fields", UNSET)

        def _parse_extra_scope(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        extra_scope = _parse_extra_scope(d.pop("extra_scope", UNSET))

        identity_provider = cls(
            provider=provider,
            client_id=client_id,
            discovery_url=discovery_url,
            userinfo_url=userinfo_url,
            token_url=token_url,
            auth_url=auth_url,
            logout_url=logout_url,
            label=label,
            is_active=is_active,
            verify_ssl=verify_ssl,
            enable_post_logout_redirect=enable_post_logout_redirect,
            enable_pkce=enable_pkce,
            management_url=management_url,
            protected_fields=protected_fields,
            extra_scope=extra_scope,
        )

        identity_provider.additional_properties = d
        return identity_provider

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
