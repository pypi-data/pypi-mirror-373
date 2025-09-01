from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TeststepresultAttachmentsListPostResponseDataItemLinks")


@_attrs_define
class TeststepresultAttachmentsListPostResponseDataItemLinks:
    """
    Attributes:
        self_ (Union[Unset, str]):  Example: server-host-name/application-path/projects/MyProjectId/testruns/MyTestRunId
            /testrecords/MyProjectId/MyTestcaseId/0/teststepresults/1/attachments/MyAttachmentId.
        content (Union[Unset, str]):  Example: server-host-name/application-path/projects/MyProjectId/testruns/MyTestRun
            Id/testrecords/MyProjectId/MyTestcaseId/0/teststepresults/1/attachments/MyAttachmentId/content.
    """

    self_: Union[Unset, str] = UNSET
    content: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        self_ = self.self_

        content = self.content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if self_ is not UNSET:
            field_dict["self"] = self_
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        self_ = d.pop("self", UNSET)

        content = d.pop("content", UNSET)

        teststepresult_attachments_list_post_response_data_item_links = cls(
            self_=self_,
            content=content,
        )

        teststepresult_attachments_list_post_response_data_item_links.additional_properties = d
        return teststepresult_attachments_list_post_response_data_item_links

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
