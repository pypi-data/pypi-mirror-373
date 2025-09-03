from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FileWriteOperation")


@_attrs_define
class FileWriteOperation:
    """
    Attributes:
        type_ (Literal['write']):
        filename (str):
        content (str):
    """

    type_: Literal["write"]
    filename: str
    content: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        filename = self.filename

        content = self.content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "filename": filename,
                "content": content,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["write"], d.pop("type"))
        if type_ != "write":
            raise ValueError(f"type must match const 'write', got '{type_}'")

        filename = d.pop("filename")

        content = d.pop("content")

        file_write_operation = cls(
            type_=type_,
            filename=filename,
            content=content,
        )

        file_write_operation.additional_properties = d
        return file_write_operation

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
