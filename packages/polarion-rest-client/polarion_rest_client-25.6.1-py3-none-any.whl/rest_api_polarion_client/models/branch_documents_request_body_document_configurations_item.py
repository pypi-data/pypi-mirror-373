from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BranchDocumentsRequestBodyDocumentConfigurationsItem")


@_attrs_define
class BranchDocumentsRequestBodyDocumentConfigurationsItem:
    """
    Attributes:
        source_document (str): Reference path of the source Document. Example: MyProjectId/MySpaceId/MyDocumentId.
        source_revision (Union[Unset, str]): Revision of the source Document. Example: 1234.
        target_project_id (Union[Unset, str]): Project where new document will be created. Example: MyProjectId.
        target_space_id (Union[Unset, str]): Space where new document will be created. Example: MySpaceId.
        target_document_name (Union[Unset, str]): Name for new Document. Example: MyDocumentId.
        copy_workflow_status_and_signatures (Union[Unset, bool]): Specifies that workflow status and signatures should
            be copied to the branched document.
        query (Union[Unset, str]): Specifies optional filtering query. Example: status:open.
        target_document_title (Union[Unset, str]): Title for new Document. Example: My Document Title.
        update_title_heading (Union[Unset, bool]): Specifies that title heading of the target Document should be set to
            the new Document's title.
        overwrite_work_items (Union[Unset, bool]): Specifies that Work Items in the branched Document should be
            overwritten (instead of being referenced).
        initialized_fields (Union[Unset, list[str]]): Specifies fields of overwritten Work Items that should be
            initialized (instead of being copied from source Work Items).
    """

    source_document: str
    source_revision: Union[Unset, str] = UNSET
    target_project_id: Union[Unset, str] = UNSET
    target_space_id: Union[Unset, str] = UNSET
    target_document_name: Union[Unset, str] = UNSET
    copy_workflow_status_and_signatures: Union[Unset, bool] = UNSET
    query: Union[Unset, str] = UNSET
    target_document_title: Union[Unset, str] = UNSET
    update_title_heading: Union[Unset, bool] = UNSET
    overwrite_work_items: Union[Unset, bool] = UNSET
    initialized_fields: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_document = self.source_document

        source_revision = self.source_revision

        target_project_id = self.target_project_id

        target_space_id = self.target_space_id

        target_document_name = self.target_document_name

        copy_workflow_status_and_signatures = self.copy_workflow_status_and_signatures

        query = self.query

        target_document_title = self.target_document_title

        update_title_heading = self.update_title_heading

        overwrite_work_items = self.overwrite_work_items

        initialized_fields: Union[Unset, list[str]] = UNSET
        if not isinstance(self.initialized_fields, Unset):
            initialized_fields = self.initialized_fields

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sourceDocument": source_document,
            }
        )
        if source_revision is not UNSET:
            field_dict["sourceRevision"] = source_revision
        if target_project_id is not UNSET:
            field_dict["targetProjectId"] = target_project_id
        if target_space_id is not UNSET:
            field_dict["targetSpaceId"] = target_space_id
        if target_document_name is not UNSET:
            field_dict["targetDocumentName"] = target_document_name
        if copy_workflow_status_and_signatures is not UNSET:
            field_dict["copyWorkflowStatusAndSignatures"] = (
                copy_workflow_status_and_signatures
            )
        if query is not UNSET:
            field_dict["query"] = query
        if target_document_title is not UNSET:
            field_dict["targetDocumentTitle"] = target_document_title
        if update_title_heading is not UNSET:
            field_dict["updateTitleHeading"] = update_title_heading
        if overwrite_work_items is not UNSET:
            field_dict["overwriteWorkItems"] = overwrite_work_items
        if initialized_fields is not UNSET:
            field_dict["initializedFields"] = initialized_fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        source_document = d.pop("sourceDocument")

        source_revision = d.pop("sourceRevision", UNSET)

        target_project_id = d.pop("targetProjectId", UNSET)

        target_space_id = d.pop("targetSpaceId", UNSET)

        target_document_name = d.pop("targetDocumentName", UNSET)

        copy_workflow_status_and_signatures = d.pop(
            "copyWorkflowStatusAndSignatures", UNSET
        )

        query = d.pop("query", UNSET)

        target_document_title = d.pop("targetDocumentTitle", UNSET)

        update_title_heading = d.pop("updateTitleHeading", UNSET)

        overwrite_work_items = d.pop("overwriteWorkItems", UNSET)

        initialized_fields = cast(list[str], d.pop("initializedFields", UNSET))

        branch_documents_request_body_document_configurations_item = cls(
            source_document=source_document,
            source_revision=source_revision,
            target_project_id=target_project_id,
            target_space_id=target_space_id,
            target_document_name=target_document_name,
            copy_workflow_status_and_signatures=copy_workflow_status_and_signatures,
            query=query,
            target_document_title=target_document_title,
            update_title_heading=update_title_heading,
            overwrite_work_items=overwrite_work_items,
            initialized_fields=initialized_fields,
        )

        branch_documents_request_body_document_configurations_item.additional_properties = d
        return branch_documents_request_body_document_configurations_item

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
