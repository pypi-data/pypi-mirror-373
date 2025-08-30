import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.blank_enum import BlankEnum
from ..models.country_enum import CountryEnum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nested_price_estimate import NestedPriceEstimate
    from ..models.organization_group import OrganizationGroup
    from ..models.payment_profile import PaymentProfile
    from ..models.permission_project import PermissionProject


T = TypeVar("T", bound="Customer")


@_attrs_define
class Customer:
    """
    Attributes:
        url (Union[Unset, str]):
        uuid (Union[Unset, UUID]):
        created (Union[Unset, datetime.datetime]):
        organization_groups (Union[Unset, list['OrganizationGroup']]):
        display_name (Union[Unset, str]):
        projects (Union[Unset, list['PermissionProject']]):
        backend_id (Union[Unset, str]): Organization identifier in another application.
        image (Union[None, Unset, str]):
        blocked (Union[Unset, bool]):
        archived (Union[Unset, bool]):
        default_tax_percent (Union[Unset, str]):
        accounting_start_date (Union[Unset, datetime.datetime]):
        projects_count (Union[Unset, int]):
        users_count (Union[Unset, int]):
        sponsor_number (Union[None, Unset, int]): External ID of the sponsor covering the costs
        country_name (Union[Unset, str]):
        max_service_accounts (Union[None, Unset, int]): Maximum number of service accounts allowed
        project_metadata_checklist (Union[None, UUID, Unset]):
        name (Union[Unset, str]):
        slug (Union[Unset, str]):
        native_name (Union[Unset, str]):
        abbreviation (Union[Unset, str]):
        contact_details (Union[Unset, str]):
        agreement_number (Union[Unset, str]):
        email (Union[Unset, str]):
        phone_number (Union[Unset, str]):
        access_subnets (Union[Unset, str]): Enter a comma separated list of IPv4 or IPv6 CIDR addresses from where
            connection to self-service is allowed.
        registration_code (Union[Unset, str]):
        homepage (Union[Unset, str]):
        domain (Union[Unset, str]):
        vat_code (Union[Unset, str]): VAT number
        postal (Union[Unset, str]):
        address (Union[Unset, str]):
        bank_name (Union[Unset, str]):
        latitude (Union[None, Unset, float]):
        longitude (Union[None, Unset, float]):
        bank_account (Union[Unset, str]):
        country (Union[BlankEnum, CountryEnum, Unset]):
        payment_profiles (Union[Unset, list['PaymentProfile']]):
        customer_credit (Union[None, Unset, float]):
        customer_unallocated_credit (Union[None, Unset, float]):
        is_service_provider (Union[Unset, bool]):
        service_provider (Union[None, Unset, str]):
        service_provider_uuid (Union[None, UUID, Unset]):
        call_managing_organization_uuid (Union[None, Unset, str]):
        billing_price_estimate (Union[Unset, NestedPriceEstimate]):
    """

    url: Union[Unset, str] = UNSET
    uuid: Union[Unset, UUID] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    organization_groups: Union[Unset, list["OrganizationGroup"]] = UNSET
    display_name: Union[Unset, str] = UNSET
    projects: Union[Unset, list["PermissionProject"]] = UNSET
    backend_id: Union[Unset, str] = UNSET
    image: Union[None, Unset, str] = UNSET
    blocked: Union[Unset, bool] = UNSET
    archived: Union[Unset, bool] = UNSET
    default_tax_percent: Union[Unset, str] = UNSET
    accounting_start_date: Union[Unset, datetime.datetime] = UNSET
    projects_count: Union[Unset, int] = UNSET
    users_count: Union[Unset, int] = UNSET
    sponsor_number: Union[None, Unset, int] = UNSET
    country_name: Union[Unset, str] = UNSET
    max_service_accounts: Union[None, Unset, int] = UNSET
    project_metadata_checklist: Union[None, UUID, Unset] = UNSET
    name: Union[Unset, str] = UNSET
    slug: Union[Unset, str] = UNSET
    native_name: Union[Unset, str] = UNSET
    abbreviation: Union[Unset, str] = UNSET
    contact_details: Union[Unset, str] = UNSET
    agreement_number: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    phone_number: Union[Unset, str] = UNSET
    access_subnets: Union[Unset, str] = UNSET
    registration_code: Union[Unset, str] = UNSET
    homepage: Union[Unset, str] = UNSET
    domain: Union[Unset, str] = UNSET
    vat_code: Union[Unset, str] = UNSET
    postal: Union[Unset, str] = UNSET
    address: Union[Unset, str] = UNSET
    bank_name: Union[Unset, str] = UNSET
    latitude: Union[None, Unset, float] = UNSET
    longitude: Union[None, Unset, float] = UNSET
    bank_account: Union[Unset, str] = UNSET
    country: Union[BlankEnum, CountryEnum, Unset] = UNSET
    payment_profiles: Union[Unset, list["PaymentProfile"]] = UNSET
    customer_credit: Union[None, Unset, float] = UNSET
    customer_unallocated_credit: Union[None, Unset, float] = UNSET
    is_service_provider: Union[Unset, bool] = UNSET
    service_provider: Union[None, Unset, str] = UNSET
    service_provider_uuid: Union[None, UUID, Unset] = UNSET
    call_managing_organization_uuid: Union[None, Unset, str] = UNSET
    billing_price_estimate: Union[Unset, "NestedPriceEstimate"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        uuid: Union[Unset, str] = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        organization_groups: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.organization_groups, Unset):
            organization_groups = []
            for organization_groups_item_data in self.organization_groups:
                organization_groups_item = organization_groups_item_data.to_dict()
                organization_groups.append(organization_groups_item)

        display_name = self.display_name

        projects: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.projects, Unset):
            projects = []
            for projects_item_data in self.projects:
                projects_item = projects_item_data.to_dict()
                projects.append(projects_item)

        backend_id = self.backend_id

        image: Union[None, Unset, str]
        if isinstance(self.image, Unset):
            image = UNSET
        else:
            image = self.image

        blocked = self.blocked

        archived = self.archived

        default_tax_percent = self.default_tax_percent

        accounting_start_date: Union[Unset, str] = UNSET
        if not isinstance(self.accounting_start_date, Unset):
            accounting_start_date = self.accounting_start_date.isoformat()

        projects_count = self.projects_count

        users_count = self.users_count

        sponsor_number: Union[None, Unset, int]
        if isinstance(self.sponsor_number, Unset):
            sponsor_number = UNSET
        else:
            sponsor_number = self.sponsor_number

        country_name = self.country_name

        max_service_accounts: Union[None, Unset, int]
        if isinstance(self.max_service_accounts, Unset):
            max_service_accounts = UNSET
        else:
            max_service_accounts = self.max_service_accounts

        project_metadata_checklist: Union[None, Unset, str]
        if isinstance(self.project_metadata_checklist, Unset):
            project_metadata_checklist = UNSET
        elif isinstance(self.project_metadata_checklist, UUID):
            project_metadata_checklist = str(self.project_metadata_checklist)
        else:
            project_metadata_checklist = self.project_metadata_checklist

        name = self.name

        slug = self.slug

        native_name = self.native_name

        abbreviation = self.abbreviation

        contact_details = self.contact_details

        agreement_number = self.agreement_number

        email = self.email

        phone_number = self.phone_number

        access_subnets = self.access_subnets

        registration_code = self.registration_code

        homepage = self.homepage

        domain = self.domain

        vat_code = self.vat_code

        postal = self.postal

        address = self.address

        bank_name = self.bank_name

        latitude: Union[None, Unset, float]
        if isinstance(self.latitude, Unset):
            latitude = UNSET
        else:
            latitude = self.latitude

        longitude: Union[None, Unset, float]
        if isinstance(self.longitude, Unset):
            longitude = UNSET
        else:
            longitude = self.longitude

        bank_account = self.bank_account

        country: Union[Unset, str]
        if isinstance(self.country, Unset):
            country = UNSET
        elif isinstance(self.country, CountryEnum):
            country = self.country.value
        else:
            country = self.country.value

        payment_profiles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.payment_profiles, Unset):
            payment_profiles = []
            for payment_profiles_item_data in self.payment_profiles:
                payment_profiles_item = payment_profiles_item_data.to_dict()
                payment_profiles.append(payment_profiles_item)

        customer_credit: Union[None, Unset, float]
        if isinstance(self.customer_credit, Unset):
            customer_credit = UNSET
        else:
            customer_credit = self.customer_credit

        customer_unallocated_credit: Union[None, Unset, float]
        if isinstance(self.customer_unallocated_credit, Unset):
            customer_unallocated_credit = UNSET
        else:
            customer_unallocated_credit = self.customer_unallocated_credit

        is_service_provider = self.is_service_provider

        service_provider: Union[None, Unset, str]
        if isinstance(self.service_provider, Unset):
            service_provider = UNSET
        else:
            service_provider = self.service_provider

        service_provider_uuid: Union[None, Unset, str]
        if isinstance(self.service_provider_uuid, Unset):
            service_provider_uuid = UNSET
        elif isinstance(self.service_provider_uuid, UUID):
            service_provider_uuid = str(self.service_provider_uuid)
        else:
            service_provider_uuid = self.service_provider_uuid

        call_managing_organization_uuid: Union[None, Unset, str]
        if isinstance(self.call_managing_organization_uuid, Unset):
            call_managing_organization_uuid = UNSET
        else:
            call_managing_organization_uuid = self.call_managing_organization_uuid

        billing_price_estimate: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.billing_price_estimate, Unset):
            billing_price_estimate = self.billing_price_estimate.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if created is not UNSET:
            field_dict["created"] = created
        if organization_groups is not UNSET:
            field_dict["organization_groups"] = organization_groups
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if projects is not UNSET:
            field_dict["projects"] = projects
        if backend_id is not UNSET:
            field_dict["backend_id"] = backend_id
        if image is not UNSET:
            field_dict["image"] = image
        if blocked is not UNSET:
            field_dict["blocked"] = blocked
        if archived is not UNSET:
            field_dict["archived"] = archived
        if default_tax_percent is not UNSET:
            field_dict["default_tax_percent"] = default_tax_percent
        if accounting_start_date is not UNSET:
            field_dict["accounting_start_date"] = accounting_start_date
        if projects_count is not UNSET:
            field_dict["projects_count"] = projects_count
        if users_count is not UNSET:
            field_dict["users_count"] = users_count
        if sponsor_number is not UNSET:
            field_dict["sponsor_number"] = sponsor_number
        if country_name is not UNSET:
            field_dict["country_name"] = country_name
        if max_service_accounts is not UNSET:
            field_dict["max_service_accounts"] = max_service_accounts
        if project_metadata_checklist is not UNSET:
            field_dict["project_metadata_checklist"] = project_metadata_checklist
        if name is not UNSET:
            field_dict["name"] = name
        if slug is not UNSET:
            field_dict["slug"] = slug
        if native_name is not UNSET:
            field_dict["native_name"] = native_name
        if abbreviation is not UNSET:
            field_dict["abbreviation"] = abbreviation
        if contact_details is not UNSET:
            field_dict["contact_details"] = contact_details
        if agreement_number is not UNSET:
            field_dict["agreement_number"] = agreement_number
        if email is not UNSET:
            field_dict["email"] = email
        if phone_number is not UNSET:
            field_dict["phone_number"] = phone_number
        if access_subnets is not UNSET:
            field_dict["access_subnets"] = access_subnets
        if registration_code is not UNSET:
            field_dict["registration_code"] = registration_code
        if homepage is not UNSET:
            field_dict["homepage"] = homepage
        if domain is not UNSET:
            field_dict["domain"] = domain
        if vat_code is not UNSET:
            field_dict["vat_code"] = vat_code
        if postal is not UNSET:
            field_dict["postal"] = postal
        if address is not UNSET:
            field_dict["address"] = address
        if bank_name is not UNSET:
            field_dict["bank_name"] = bank_name
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if longitude is not UNSET:
            field_dict["longitude"] = longitude
        if bank_account is not UNSET:
            field_dict["bank_account"] = bank_account
        if country is not UNSET:
            field_dict["country"] = country
        if payment_profiles is not UNSET:
            field_dict["payment_profiles"] = payment_profiles
        if customer_credit is not UNSET:
            field_dict["customer_credit"] = customer_credit
        if customer_unallocated_credit is not UNSET:
            field_dict["customer_unallocated_credit"] = customer_unallocated_credit
        if is_service_provider is not UNSET:
            field_dict["is_service_provider"] = is_service_provider
        if service_provider is not UNSET:
            field_dict["service_provider"] = service_provider
        if service_provider_uuid is not UNSET:
            field_dict["service_provider_uuid"] = service_provider_uuid
        if call_managing_organization_uuid is not UNSET:
            field_dict["call_managing_organization_uuid"] = call_managing_organization_uuid
        if billing_price_estimate is not UNSET:
            field_dict["billing_price_estimate"] = billing_price_estimate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nested_price_estimate import NestedPriceEstimate
        from ..models.organization_group import OrganizationGroup
        from ..models.payment_profile import PaymentProfile
        from ..models.permission_project import PermissionProject

        d = dict(src_dict)
        url = d.pop("url", UNSET)

        _uuid = d.pop("uuid", UNSET)
        uuid: Union[Unset, UUID]
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        _created = d.pop("created", UNSET)
        created: Union[Unset, datetime.datetime]
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = isoparse(_created)

        organization_groups = []
        _organization_groups = d.pop("organization_groups", UNSET)
        for organization_groups_item_data in _organization_groups or []:
            organization_groups_item = OrganizationGroup.from_dict(organization_groups_item_data)

            organization_groups.append(organization_groups_item)

        display_name = d.pop("display_name", UNSET)

        projects = []
        _projects = d.pop("projects", UNSET)
        for projects_item_data in _projects or []:
            projects_item = PermissionProject.from_dict(projects_item_data)

            projects.append(projects_item)

        backend_id = d.pop("backend_id", UNSET)

        def _parse_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image = _parse_image(d.pop("image", UNSET))

        blocked = d.pop("blocked", UNSET)

        archived = d.pop("archived", UNSET)

        default_tax_percent = d.pop("default_tax_percent", UNSET)

        _accounting_start_date = d.pop("accounting_start_date", UNSET)
        accounting_start_date: Union[Unset, datetime.datetime]
        if isinstance(_accounting_start_date, Unset):
            accounting_start_date = UNSET
        else:
            accounting_start_date = isoparse(_accounting_start_date)

        projects_count = d.pop("projects_count", UNSET)

        users_count = d.pop("users_count", UNSET)

        def _parse_sponsor_number(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        sponsor_number = _parse_sponsor_number(d.pop("sponsor_number", UNSET))

        country_name = d.pop("country_name", UNSET)

        def _parse_max_service_accounts(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_service_accounts = _parse_max_service_accounts(d.pop("max_service_accounts", UNSET))

        def _parse_project_metadata_checklist(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                project_metadata_checklist_type_0 = UUID(data)

                return project_metadata_checklist_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        project_metadata_checklist = _parse_project_metadata_checklist(d.pop("project_metadata_checklist", UNSET))

        name = d.pop("name", UNSET)

        slug = d.pop("slug", UNSET)

        native_name = d.pop("native_name", UNSET)

        abbreviation = d.pop("abbreviation", UNSET)

        contact_details = d.pop("contact_details", UNSET)

        agreement_number = d.pop("agreement_number", UNSET)

        email = d.pop("email", UNSET)

        phone_number = d.pop("phone_number", UNSET)

        access_subnets = d.pop("access_subnets", UNSET)

        registration_code = d.pop("registration_code", UNSET)

        homepage = d.pop("homepage", UNSET)

        domain = d.pop("domain", UNSET)

        vat_code = d.pop("vat_code", UNSET)

        postal = d.pop("postal", UNSET)

        address = d.pop("address", UNSET)

        bank_name = d.pop("bank_name", UNSET)

        def _parse_latitude(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        latitude = _parse_latitude(d.pop("latitude", UNSET))

        def _parse_longitude(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        longitude = _parse_longitude(d.pop("longitude", UNSET))

        bank_account = d.pop("bank_account", UNSET)

        def _parse_country(data: object) -> Union[BlankEnum, CountryEnum, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                country_type_0 = CountryEnum(data)

                return country_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, str):
                raise TypeError()
            country_type_1 = BlankEnum(data)

            return country_type_1

        country = _parse_country(d.pop("country", UNSET))

        payment_profiles = []
        _payment_profiles = d.pop("payment_profiles", UNSET)
        for payment_profiles_item_data in _payment_profiles or []:
            payment_profiles_item = PaymentProfile.from_dict(payment_profiles_item_data)

            payment_profiles.append(payment_profiles_item)

        def _parse_customer_credit(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        customer_credit = _parse_customer_credit(d.pop("customer_credit", UNSET))

        def _parse_customer_unallocated_credit(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        customer_unallocated_credit = _parse_customer_unallocated_credit(d.pop("customer_unallocated_credit", UNSET))

        is_service_provider = d.pop("is_service_provider", UNSET)

        def _parse_service_provider(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        service_provider = _parse_service_provider(d.pop("service_provider", UNSET))

        def _parse_service_provider_uuid(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_provider_uuid_type_0 = UUID(data)

                return service_provider_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        service_provider_uuid = _parse_service_provider_uuid(d.pop("service_provider_uuid", UNSET))

        def _parse_call_managing_organization_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        call_managing_organization_uuid = _parse_call_managing_organization_uuid(
            d.pop("call_managing_organization_uuid", UNSET)
        )

        _billing_price_estimate = d.pop("billing_price_estimate", UNSET)
        billing_price_estimate: Union[Unset, NestedPriceEstimate]
        if isinstance(_billing_price_estimate, Unset):
            billing_price_estimate = UNSET
        else:
            billing_price_estimate = NestedPriceEstimate.from_dict(_billing_price_estimate)

        customer = cls(
            url=url,
            uuid=uuid,
            created=created,
            organization_groups=organization_groups,
            display_name=display_name,
            projects=projects,
            backend_id=backend_id,
            image=image,
            blocked=blocked,
            archived=archived,
            default_tax_percent=default_tax_percent,
            accounting_start_date=accounting_start_date,
            projects_count=projects_count,
            users_count=users_count,
            sponsor_number=sponsor_number,
            country_name=country_name,
            max_service_accounts=max_service_accounts,
            project_metadata_checklist=project_metadata_checklist,
            name=name,
            slug=slug,
            native_name=native_name,
            abbreviation=abbreviation,
            contact_details=contact_details,
            agreement_number=agreement_number,
            email=email,
            phone_number=phone_number,
            access_subnets=access_subnets,
            registration_code=registration_code,
            homepage=homepage,
            domain=domain,
            vat_code=vat_code,
            postal=postal,
            address=address,
            bank_name=bank_name,
            latitude=latitude,
            longitude=longitude,
            bank_account=bank_account,
            country=country,
            payment_profiles=payment_profiles,
            customer_credit=customer_credit,
            customer_unallocated_credit=customer_unallocated_credit,
            is_service_provider=is_service_provider,
            service_provider=service_provider,
            service_provider_uuid=service_provider_uuid,
            call_managing_organization_uuid=call_managing_organization_uuid,
            billing_price_estimate=billing_price_estimate,
        )

        customer.additional_properties = d
        return customer

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
