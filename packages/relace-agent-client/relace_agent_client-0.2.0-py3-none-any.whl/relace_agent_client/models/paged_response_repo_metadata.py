from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.repo_metadata import RepoMetadata


T = TypeVar("T", bound="PagedResponseRepoMetadata")


@_attrs_define
class PagedResponseRepoMetadata:
    """
    Attributes:
        items (list['RepoMetadata']):
        total_items (int):
        next_page (Union[None, Unset, int]):
    """

    items: list["RepoMetadata"]
    total_items: int
    next_page: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        total_items = self.total_items

        next_page: Union[None, Unset, int]
        if isinstance(self.next_page, Unset):
            next_page = UNSET
        else:
            next_page = self.next_page

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "items": items,
                "total_items": total_items,
            }
        )
        if next_page is not UNSET:
            field_dict["next_page"] = next_page

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.repo_metadata import RepoMetadata

        d = dict(src_dict)
        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = RepoMetadata.from_dict(items_item_data)

            items.append(items_item)

        total_items = d.pop("total_items")

        def _parse_next_page(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        next_page = _parse_next_page(d.pop("next_page", UNSET))

        paged_response_repo_metadata = cls(
            items=items,
            total_items=total_items,
            next_page=next_page,
        )

        paged_response_repo_metadata.additional_properties = d
        return paged_response_repo_metadata

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
