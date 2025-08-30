import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.issue_type_enum import IssueTypeEnum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nested_feedback import NestedFeedback


T = TypeVar("T", bound="Issue")


@_attrs_define
class Issue:
    """
    Attributes:
        url (str):
        uuid (UUID):
        key (str):
        backend_id (Union[None, str]):
        backend_name (Union[None, str]):
        link (str): Link to issue in support system.
        summary (str):
        status (str):
        resolution (str):
        caller_uuid (Union[None, UUID]):
        caller_full_name (Union[None, str]):
        reporter (str):
        reporter_uuid (Union[None, UUID]):
        reporter_name (Union[None, str]):
        assignee_uuid (Union[None, UUID]):
        assignee_name (Union[None, str]):
        customer_uuid (Union[None, UUID]):
        customer_name (Union[None, str]):
        project_uuid (Union[None, UUID]):
        project_name (Union[None, str]):
        resource_type (str):
        resource_name (str):
        created (datetime.datetime):
        modified (datetime.datetime):
        first_response_sla (Union[None, datetime.datetime]):
        feedback (Union['NestedFeedback', None]):
        resolved (Union[None, bool]):
        update_is_available (bool):
        destroy_is_available (bool):
        add_comment_is_available (bool):
        add_attachment_is_available (bool):
        type_ (Union[Unset, IssueTypeEnum]):  Default: IssueTypeEnum.INFORMATIONAL.
        remote_id (Union[None, Unset, str]):
        description (Union[Unset, str]):
        priority (Union[Unset, str]):
        caller (Union[None, Unset, str]):
        assignee (Union[None, Unset, str]):
        customer (Union[None, Unset, str]):
        project (Union[None, Unset, str]):
        resource (Union[Unset, str]):
        template (Union[None, Unset, str]):
    """

    url: str
    uuid: UUID
    key: str
    backend_id: Union[None, str]
    backend_name: Union[None, str]
    link: str
    summary: str
    status: str
    resolution: str
    caller_uuid: Union[None, UUID]
    caller_full_name: Union[None, str]
    reporter: str
    reporter_uuid: Union[None, UUID]
    reporter_name: Union[None, str]
    assignee_uuid: Union[None, UUID]
    assignee_name: Union[None, str]
    customer_uuid: Union[None, UUID]
    customer_name: Union[None, str]
    project_uuid: Union[None, UUID]
    project_name: Union[None, str]
    resource_type: str
    resource_name: str
    created: datetime.datetime
    modified: datetime.datetime
    first_response_sla: Union[None, datetime.datetime]
    feedback: Union["NestedFeedback", None]
    resolved: Union[None, bool]
    update_is_available: bool
    destroy_is_available: bool
    add_comment_is_available: bool
    add_attachment_is_available: bool
    type_: Union[Unset, IssueTypeEnum] = IssueTypeEnum.INFORMATIONAL
    remote_id: Union[None, Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    priority: Union[Unset, str] = UNSET
    caller: Union[None, Unset, str] = UNSET
    assignee: Union[None, Unset, str] = UNSET
    customer: Union[None, Unset, str] = UNSET
    project: Union[None, Unset, str] = UNSET
    resource: Union[Unset, str] = UNSET
    template: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.nested_feedback import NestedFeedback

        url = self.url

        uuid = str(self.uuid)

        key = self.key

        backend_id: Union[None, str]
        backend_id = self.backend_id

        backend_name: Union[None, str]
        backend_name = self.backend_name

        link = self.link

        summary = self.summary

        status = self.status

        resolution = self.resolution

        caller_uuid: Union[None, str]
        if isinstance(self.caller_uuid, UUID):
            caller_uuid = str(self.caller_uuid)
        else:
            caller_uuid = self.caller_uuid

        caller_full_name: Union[None, str]
        caller_full_name = self.caller_full_name

        reporter = self.reporter

        reporter_uuid: Union[None, str]
        if isinstance(self.reporter_uuid, UUID):
            reporter_uuid = str(self.reporter_uuid)
        else:
            reporter_uuid = self.reporter_uuid

        reporter_name: Union[None, str]
        reporter_name = self.reporter_name

        assignee_uuid: Union[None, str]
        if isinstance(self.assignee_uuid, UUID):
            assignee_uuid = str(self.assignee_uuid)
        else:
            assignee_uuid = self.assignee_uuid

        assignee_name: Union[None, str]
        assignee_name = self.assignee_name

        customer_uuid: Union[None, str]
        if isinstance(self.customer_uuid, UUID):
            customer_uuid = str(self.customer_uuid)
        else:
            customer_uuid = self.customer_uuid

        customer_name: Union[None, str]
        customer_name = self.customer_name

        project_uuid: Union[None, str]
        if isinstance(self.project_uuid, UUID):
            project_uuid = str(self.project_uuid)
        else:
            project_uuid = self.project_uuid

        project_name: Union[None, str]
        project_name = self.project_name

        resource_type = self.resource_type

        resource_name = self.resource_name

        created = self.created.isoformat()

        modified = self.modified.isoformat()

        first_response_sla: Union[None, str]
        if isinstance(self.first_response_sla, datetime.datetime):
            first_response_sla = self.first_response_sla.isoformat()
        else:
            first_response_sla = self.first_response_sla

        feedback: Union[None, dict[str, Any]]
        if isinstance(self.feedback, NestedFeedback):
            feedback = self.feedback.to_dict()
        else:
            feedback = self.feedback

        resolved: Union[None, bool]
        resolved = self.resolved

        update_is_available = self.update_is_available

        destroy_is_available = self.destroy_is_available

        add_comment_is_available = self.add_comment_is_available

        add_attachment_is_available = self.add_attachment_is_available

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        remote_id: Union[None, Unset, str]
        if isinstance(self.remote_id, Unset):
            remote_id = UNSET
        else:
            remote_id = self.remote_id

        description = self.description

        priority = self.priority

        caller: Union[None, Unset, str]
        if isinstance(self.caller, Unset):
            caller = UNSET
        else:
            caller = self.caller

        assignee: Union[None, Unset, str]
        if isinstance(self.assignee, Unset):
            assignee = UNSET
        else:
            assignee = self.assignee

        customer: Union[None, Unset, str]
        if isinstance(self.customer, Unset):
            customer = UNSET
        else:
            customer = self.customer

        project: Union[None, Unset, str]
        if isinstance(self.project, Unset):
            project = UNSET
        else:
            project = self.project

        resource = self.resource

        template: Union[None, Unset, str]
        if isinstance(self.template, Unset):
            template = UNSET
        else:
            template = self.template

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "uuid": uuid,
                "key": key,
                "backend_id": backend_id,
                "backend_name": backend_name,
                "link": link,
                "summary": summary,
                "status": status,
                "resolution": resolution,
                "caller_uuid": caller_uuid,
                "caller_full_name": caller_full_name,
                "reporter": reporter,
                "reporter_uuid": reporter_uuid,
                "reporter_name": reporter_name,
                "assignee_uuid": assignee_uuid,
                "assignee_name": assignee_name,
                "customer_uuid": customer_uuid,
                "customer_name": customer_name,
                "project_uuid": project_uuid,
                "project_name": project_name,
                "resource_type": resource_type,
                "resource_name": resource_name,
                "created": created,
                "modified": modified,
                "first_response_sla": first_response_sla,
                "feedback": feedback,
                "resolved": resolved,
                "update_is_available": update_is_available,
                "destroy_is_available": destroy_is_available,
                "add_comment_is_available": add_comment_is_available,
                "add_attachment_is_available": add_attachment_is_available,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if remote_id is not UNSET:
            field_dict["remote_id"] = remote_id
        if description is not UNSET:
            field_dict["description"] = description
        if priority is not UNSET:
            field_dict["priority"] = priority
        if caller is not UNSET:
            field_dict["caller"] = caller
        if assignee is not UNSET:
            field_dict["assignee"] = assignee
        if customer is not UNSET:
            field_dict["customer"] = customer
        if project is not UNSET:
            field_dict["project"] = project
        if resource is not UNSET:
            field_dict["resource"] = resource
        if template is not UNSET:
            field_dict["template"] = template

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nested_feedback import NestedFeedback

        d = dict(src_dict)
        url = d.pop("url")

        uuid = UUID(d.pop("uuid"))

        key = d.pop("key")

        def _parse_backend_id(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        backend_id = _parse_backend_id(d.pop("backend_id"))

        def _parse_backend_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        backend_name = _parse_backend_name(d.pop("backend_name"))

        link = d.pop("link")

        summary = d.pop("summary")

        status = d.pop("status")

        resolution = d.pop("resolution")

        def _parse_caller_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                caller_uuid_type_0 = UUID(data)

                return caller_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        caller_uuid = _parse_caller_uuid(d.pop("caller_uuid"))

        def _parse_caller_full_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        caller_full_name = _parse_caller_full_name(d.pop("caller_full_name"))

        reporter = d.pop("reporter")

        def _parse_reporter_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reporter_uuid_type_0 = UUID(data)

                return reporter_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        reporter_uuid = _parse_reporter_uuid(d.pop("reporter_uuid"))

        def _parse_reporter_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        reporter_name = _parse_reporter_name(d.pop("reporter_name"))

        def _parse_assignee_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                assignee_uuid_type_0 = UUID(data)

                return assignee_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        assignee_uuid = _parse_assignee_uuid(d.pop("assignee_uuid"))

        def _parse_assignee_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        assignee_name = _parse_assignee_name(d.pop("assignee_name"))

        def _parse_customer_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                customer_uuid_type_0 = UUID(data)

                return customer_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        customer_uuid = _parse_customer_uuid(d.pop("customer_uuid"))

        def _parse_customer_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        customer_name = _parse_customer_name(d.pop("customer_name"))

        def _parse_project_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                project_uuid_type_0 = UUID(data)

                return project_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        project_uuid = _parse_project_uuid(d.pop("project_uuid"))

        def _parse_project_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        project_name = _parse_project_name(d.pop("project_name"))

        resource_type = d.pop("resource_type")

        resource_name = d.pop("resource_name")

        created = isoparse(d.pop("created"))

        modified = isoparse(d.pop("modified"))

        def _parse_first_response_sla(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                first_response_sla_type_0 = isoparse(data)

                return first_response_sla_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        first_response_sla = _parse_first_response_sla(d.pop("first_response_sla"))

        def _parse_feedback(data: object) -> Union["NestedFeedback", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                feedback_type_1 = NestedFeedback.from_dict(data)

                return feedback_type_1
            except:  # noqa: E722
                pass
            return cast(Union["NestedFeedback", None], data)

        feedback = _parse_feedback(d.pop("feedback"))

        def _parse_resolved(data: object) -> Union[None, bool]:
            if data is None:
                return data
            return cast(Union[None, bool], data)

        resolved = _parse_resolved(d.pop("resolved"))

        update_is_available = d.pop("update_is_available")

        destroy_is_available = d.pop("destroy_is_available")

        add_comment_is_available = d.pop("add_comment_is_available")

        add_attachment_is_available = d.pop("add_attachment_is_available")

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, IssueTypeEnum]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = IssueTypeEnum(_type_)

        def _parse_remote_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        remote_id = _parse_remote_id(d.pop("remote_id", UNSET))

        description = d.pop("description", UNSET)

        priority = d.pop("priority", UNSET)

        def _parse_caller(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        caller = _parse_caller(d.pop("caller", UNSET))

        def _parse_assignee(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        assignee = _parse_assignee(d.pop("assignee", UNSET))

        def _parse_customer(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        customer = _parse_customer(d.pop("customer", UNSET))

        def _parse_project(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        project = _parse_project(d.pop("project", UNSET))

        resource = d.pop("resource", UNSET)

        def _parse_template(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        template = _parse_template(d.pop("template", UNSET))

        issue = cls(
            url=url,
            uuid=uuid,
            key=key,
            backend_id=backend_id,
            backend_name=backend_name,
            link=link,
            summary=summary,
            status=status,
            resolution=resolution,
            caller_uuid=caller_uuid,
            caller_full_name=caller_full_name,
            reporter=reporter,
            reporter_uuid=reporter_uuid,
            reporter_name=reporter_name,
            assignee_uuid=assignee_uuid,
            assignee_name=assignee_name,
            customer_uuid=customer_uuid,
            customer_name=customer_name,
            project_uuid=project_uuid,
            project_name=project_name,
            resource_type=resource_type,
            resource_name=resource_name,
            created=created,
            modified=modified,
            first_response_sla=first_response_sla,
            feedback=feedback,
            resolved=resolved,
            update_is_available=update_is_available,
            destroy_is_available=destroy_is_available,
            add_comment_is_available=add_comment_is_available,
            add_attachment_is_available=add_attachment_is_available,
            type_=type_,
            remote_id=remote_id,
            description=description,
            priority=priority,
            caller=caller,
            assignee=assignee,
            customer=customer,
            project=project,
            resource=resource,
            template=template,
        )

        issue.additional_properties = d
        return issue

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
