from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FileRenameOperation")


@_attrs_define
class FileRenameOperation:
    """
    Attributes:
        type_ (Literal['rename']):
        old_filename (str):
        new_filename (str):
    """

    type_: Literal["rename"]
    old_filename: str
    new_filename: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        old_filename = self.old_filename

        new_filename = self.new_filename

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "old_filename": old_filename,
                "new_filename": new_filename,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["rename"], d.pop("type"))
        if type_ != "rename":
            raise ValueError(f"type must match const 'rename', got '{type_}'")

        old_filename = d.pop("old_filename")

        new_filename = d.pop("new_filename")

        file_rename_operation = cls(
            type_=type_,
            old_filename=old_filename,
            new_filename=new_filename,
        )

        file_rename_operation.additional_properties = d
        return file_rename_operation

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
