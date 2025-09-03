from collections.abc import Mapping
from typing import Any, Literal, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RepoCreateRelaceSource")


@_attrs_define
class RepoCreateRelaceSource:
    """
    Attributes:
        type_ (Literal['relace']):
        repo_id (UUID):
        copy_metadata (Union[Unset, bool]):  Default: False.
        copy_remote (Union[Unset, bool]):  Default: False.
    """

    type_: Literal["relace"]
    repo_id: UUID
    copy_metadata: Union[Unset, bool] = False
    copy_remote: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        repo_id = str(self.repo_id)

        copy_metadata = self.copy_metadata

        copy_remote = self.copy_remote

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "repo_id": repo_id,
            }
        )
        if copy_metadata is not UNSET:
            field_dict["copy_metadata"] = copy_metadata
        if copy_remote is not UNSET:
            field_dict["copy_remote"] = copy_remote

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["relace"], d.pop("type"))
        if type_ != "relace":
            raise ValueError(f"type must match const 'relace', got '{type_}'")

        repo_id = UUID(d.pop("repo_id"))

        copy_metadata = d.pop("copy_metadata", UNSET)

        copy_remote = d.pop("copy_remote", UNSET)

        repo_create_relace_source = cls(
            type_=type_,
            repo_id=repo_id,
            copy_metadata=copy_metadata,
            copy_remote=copy_remote,
        )

        repo_create_relace_source.additional_properties = d
        return repo_create_relace_source

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
