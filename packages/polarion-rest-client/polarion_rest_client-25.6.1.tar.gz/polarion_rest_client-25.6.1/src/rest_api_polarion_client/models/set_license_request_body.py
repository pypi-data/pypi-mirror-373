from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.set_license_request_body_license import SetLicenseRequestBodyLicense
from ..types import UNSET, Unset

T = TypeVar("T", bound="SetLicenseRequestBody")


@_attrs_define
class SetLicenseRequestBody:
    """
    Attributes:
        license_ (Union[Unset, SetLicenseRequestBodyLicense]): User's license type
        group (Union[Unset, str]): License group Example: Department.
        concurrent (Union[Unset, bool]): Is concurrent user Example: True.
    """

    license_: Union[Unset, SetLicenseRequestBodyLicense] = UNSET
    group: Union[Unset, str] = UNSET
    concurrent: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        license_: Union[Unset, str] = UNSET
        if not isinstance(self.license_, Unset):
            license_ = self.license_.value

        group = self.group

        concurrent = self.concurrent

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if license_ is not UNSET:
            field_dict["license"] = license_
        if group is not UNSET:
            field_dict["group"] = group
        if concurrent is not UNSET:
            field_dict["concurrent"] = concurrent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _license_ = d.pop("license", UNSET)
        license_: Union[Unset, SetLicenseRequestBodyLicense]
        if isinstance(_license_, Unset):
            license_ = UNSET
        else:
            license_ = SetLicenseRequestBodyLicense(_license_)

        group = d.pop("group", UNSET)

        concurrent = d.pop("concurrent", UNSET)

        set_license_request_body = cls(
            license_=license_,
            group=group,
            concurrent=concurrent,
        )

        set_license_request_body.additional_properties = d
        return set_license_request_body

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
