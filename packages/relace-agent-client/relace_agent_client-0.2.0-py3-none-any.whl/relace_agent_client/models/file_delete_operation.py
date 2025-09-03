from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FileDeleteOperation")


@_attrs_define
class FileDeleteOperation:
    """
    Attributes:
        type_ (Literal['delete']):
        filename (str):
    """

    type_: Literal["delete"]
    filename: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        filename = self.filename

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "filename": filename,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["delete"], d.pop("type"))
        if type_ != "delete":
            raise ValueError(f"type must match const 'delete', got '{type_}'")

        filename = d.pop("filename")

        file_delete_operation = cls(
            type_=type_,
            filename=filename,
        )

        file_delete_operation.additional_properties = d
        return file_delete_operation

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
