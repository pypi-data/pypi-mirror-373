from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.plans_list_get_response_data_item import PlansListGetResponseDataItem
    from ..models.plans_list_get_response_included_item import (
        PlansListGetResponseIncludedItem,
    )
    from ..models.plans_list_get_response_links import PlansListGetResponseLinks
    from ..models.plans_list_get_response_meta import PlansListGetResponseMeta


T = TypeVar("T", bound="PlansListGetResponse")


@_attrs_define
class PlansListGetResponse:
    """
    Attributes:
        meta (Union[Unset, PlansListGetResponseMeta]):
        data (Union[Unset, list['PlansListGetResponseDataItem']]):
        included (Union[Unset, list['PlansListGetResponseIncludedItem']]): Related entities might be returned, see <a
            href="https://docs.sw.siemens.com/en-
            US/doc/230235217/PL20241023686685479.polarion_help_sc.xid2134849/xid2134871" target="_blank">REST API User
            Guide</a>.
        links (Union[Unset, PlansListGetResponseLinks]):
    """

    meta: Union[Unset, "PlansListGetResponseMeta"] = UNSET
    data: Union[Unset, list["PlansListGetResponseDataItem"]] = UNSET
    included: Union[Unset, list["PlansListGetResponseIncludedItem"]] = UNSET
    links: Union[Unset, "PlansListGetResponseLinks"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        meta: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()

        data: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.data, Unset):
            data = []
            for data_item_data in self.data:
                data_item = data_item_data.to_dict()
                data.append(data_item)

        included: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.included, Unset):
            included = []
            for included_item_data in self.included:
                included_item = included_item_data.to_dict()
                included.append(included_item)

        links: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.links, Unset):
            links = self.links.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if meta is not UNSET:
            field_dict["meta"] = meta
        if data is not UNSET:
            field_dict["data"] = data
        if included is not UNSET:
            field_dict["included"] = included
        if links is not UNSET:
            field_dict["links"] = links

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plans_list_get_response_data_item import (
            PlansListGetResponseDataItem,
        )
        from ..models.plans_list_get_response_included_item import (
            PlansListGetResponseIncludedItem,
        )
        from ..models.plans_list_get_response_links import PlansListGetResponseLinks
        from ..models.plans_list_get_response_meta import PlansListGetResponseMeta

        d = dict(src_dict)
        _meta = d.pop("meta", UNSET)
        meta: Union[Unset, PlansListGetResponseMeta]
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = PlansListGetResponseMeta.from_dict(_meta)

        data = []
        _data = d.pop("data", UNSET)
        for data_item_data in _data or []:
            data_item = PlansListGetResponseDataItem.from_dict(data_item_data)

            data.append(data_item)

        included = []
        _included = d.pop("included", UNSET)
        for included_item_data in _included or []:
            included_item = PlansListGetResponseIncludedItem.from_dict(
                included_item_data
            )

            included.append(included_item)

        _links = d.pop("links", UNSET)
        links: Union[Unset, PlansListGetResponseLinks]
        if isinstance(_links, Unset):
            links = UNSET
        else:
            links = PlansListGetResponseLinks.from_dict(_links)

        plans_list_get_response = cls(
            meta=meta,
            data=data,
            included=included,
            links=links,
        )

        plans_list_get_response.additional_properties = d
        return plans_list_get_response

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
