from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchedIdentityProviderRequest")


@_attrs_define
class PatchedIdentityProviderRequest:
    """
    Attributes:
        provider (Union[Unset, str]):
        is_active (Union[Unset, bool]):
        client_id (Union[Unset, str]): ID of application used for OAuth authentication.
        verify_ssl (Union[Unset, bool]):
        enable_post_logout_redirect (Union[Unset, bool]):
        enable_pkce (Union[Unset, bool]):
        discovery_url (Union[Unset, str]): The endpoint for endpoint discovery.
        label (Union[Unset, str]): Human-readable identity provider is label.
        management_url (Union[Unset, str]): The endpoint for user details management.
        protected_fields (Union[Unset, Any]):
        extra_scope (Union[None, Unset, str]): Space-separated list of scopes to request during authentication.
    """

    provider: Union[Unset, str] = UNSET
    is_active: Union[Unset, bool] = UNSET
    client_id: Union[Unset, str] = UNSET
    verify_ssl: Union[Unset, bool] = UNSET
    enable_post_logout_redirect: Union[Unset, bool] = UNSET
    enable_pkce: Union[Unset, bool] = UNSET
    discovery_url: Union[Unset, str] = UNSET
    label: Union[Unset, str] = UNSET
    management_url: Union[Unset, str] = UNSET
    protected_fields: Union[Unset, Any] = UNSET
    extra_scope: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider = self.provider

        is_active = self.is_active

        client_id = self.client_id

        verify_ssl = self.verify_ssl

        enable_post_logout_redirect = self.enable_post_logout_redirect

        enable_pkce = self.enable_pkce

        discovery_url = self.discovery_url

        label = self.label

        management_url = self.management_url

        protected_fields = self.protected_fields

        extra_scope: Union[None, Unset, str]
        if isinstance(self.extra_scope, Unset):
            extra_scope = UNSET
        else:
            extra_scope = self.extra_scope

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if provider is not UNSET:
            field_dict["provider"] = provider
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if verify_ssl is not UNSET:
            field_dict["verify_ssl"] = verify_ssl
        if enable_post_logout_redirect is not UNSET:
            field_dict["enable_post_logout_redirect"] = enable_post_logout_redirect
        if enable_pkce is not UNSET:
            field_dict["enable_pkce"] = enable_pkce
        if discovery_url is not UNSET:
            field_dict["discovery_url"] = discovery_url
        if label is not UNSET:
            field_dict["label"] = label
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
        provider = d.pop("provider", UNSET)

        is_active = d.pop("is_active", UNSET)

        client_id = d.pop("client_id", UNSET)

        verify_ssl = d.pop("verify_ssl", UNSET)

        enable_post_logout_redirect = d.pop("enable_post_logout_redirect", UNSET)

        enable_pkce = d.pop("enable_pkce", UNSET)

        discovery_url = d.pop("discovery_url", UNSET)

        label = d.pop("label", UNSET)

        management_url = d.pop("management_url", UNSET)

        protected_fields = d.pop("protected_fields", UNSET)

        def _parse_extra_scope(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        extra_scope = _parse_extra_scope(d.pop("extra_scope", UNSET))

        patched_identity_provider_request = cls(
            provider=provider,
            is_active=is_active,
            client_id=client_id,
            verify_ssl=verify_ssl,
            enable_post_logout_redirect=enable_post_logout_redirect,
            enable_pkce=enable_pkce,
            discovery_url=discovery_url,
            label=label,
            management_url=management_url,
            protected_fields=protected_fields,
            extra_scope=extra_scope,
        )

        patched_identity_provider_request.additional_properties = d
        return patched_identity_provider_request

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
