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

T = TypeVar("T", bound="JobsSingleGetResponseDataLinks")


@_attrs_define
class JobsSingleGetResponseDataLinks:
    """
    Attributes:
        self_ (Union[Unset, str]):  Example: server-host-name/application-path/jobs/MyJobId.
        log (Union[Unset, str]):  Example: server-host-name/application-path/polarion/job-report?jobId=MyJobId.
        downloads (Union[Unset, list[str]]):  Example:
            ['https://polarion.stage.engineering.redhat.com/polarion/download/filename1',
            'https://polarion.stage.engineering.redhat.com/polarion/download/filename2'].
    """

    self_: Union[Unset, str] = UNSET
    log: Union[Unset, str] = UNSET
    downloads: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        self_ = self.self_

        log = self.log

        downloads: Union[Unset, list[str]] = UNSET
        if not isinstance(self.downloads, Unset):
            downloads = self.downloads

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if self_ is not UNSET:
            field_dict["self"] = self_
        if log is not UNSET:
            field_dict["log"] = log
        if downloads is not UNSET:
            field_dict["downloads"] = downloads

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        self_ = d.pop("self", UNSET)

        log = d.pop("log", UNSET)

        downloads = cast(list[str], d.pop("downloads", UNSET))

        jobs_single_get_response_data_links = cls(
            self_=self_,
            log=log,
            downloads=downloads,
        )

        jobs_single_get_response_data_links.additional_properties = d
        return jobs_single_get_response_data_links

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
