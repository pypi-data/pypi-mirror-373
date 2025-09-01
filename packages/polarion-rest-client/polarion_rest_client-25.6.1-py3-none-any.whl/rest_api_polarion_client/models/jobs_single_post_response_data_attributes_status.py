from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.jobs_single_post_response_data_attributes_status_type import (
    JobsSinglePostResponseDataAttributesStatusType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="JobsSinglePostResponseDataAttributesStatus")


@_attrs_define
class JobsSinglePostResponseDataAttributesStatus:
    """
    Attributes:
        type_ (Union[Unset, JobsSinglePostResponseDataAttributesStatusType]):
        message (Union[Unset, str]):  Example: message.
    """

    type_: Union[Unset, JobsSinglePostResponseDataAttributesStatusType] = UNSET
    message: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, JobsSinglePostResponseDataAttributesStatusType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = JobsSinglePostResponseDataAttributesStatusType(_type_)

        message = d.pop("message", UNSET)

        jobs_single_post_response_data_attributes_status = cls(
            type_=type_,
            message=message,
        )

        jobs_single_post_response_data_attributes_status.additional_properties = d
        return jobs_single_post_response_data_attributes_status

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
