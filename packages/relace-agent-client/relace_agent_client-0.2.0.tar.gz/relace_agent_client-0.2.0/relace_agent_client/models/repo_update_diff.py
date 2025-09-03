from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.file_delete_operation import FileDeleteOperation
    from ..models.file_rename_operation import FileRenameOperation
    from ..models.file_write_operation import FileWriteOperation


T = TypeVar("T", bound="RepoUpdateDiff")


@_attrs_define
class RepoUpdateDiff:
    """
    Attributes:
        type_ (Literal['diff']):
        operations (list[Union['FileDeleteOperation', 'FileRenameOperation', 'FileWriteOperation']]):
    """

    type_: Literal["diff"]
    operations: list[Union["FileDeleteOperation", "FileRenameOperation", "FileWriteOperation"]]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.file_delete_operation import FileDeleteOperation
        from ..models.file_write_operation import FileWriteOperation

        type_ = self.type_

        operations = []
        for operations_item_data in self.operations:
            operations_item: dict[str, Any]
            if isinstance(operations_item_data, FileWriteOperation):
                operations_item = operations_item_data.to_dict()
            elif isinstance(operations_item_data, FileDeleteOperation):
                operations_item = operations_item_data.to_dict()
            else:
                operations_item = operations_item_data.to_dict()

            operations.append(operations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "operations": operations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_delete_operation import FileDeleteOperation
        from ..models.file_rename_operation import FileRenameOperation
        from ..models.file_write_operation import FileWriteOperation

        d = dict(src_dict)
        type_ = cast(Literal["diff"], d.pop("type"))
        if type_ != "diff":
            raise ValueError(f"type must match const 'diff', got '{type_}'")

        operations = []
        _operations = d.pop("operations")
        for operations_item_data in _operations:

            def _parse_operations_item(
                data: object,
            ) -> Union["FileDeleteOperation", "FileRenameOperation", "FileWriteOperation"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    operations_item_type_0 = FileWriteOperation.from_dict(data)

                    return operations_item_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    operations_item_type_1 = FileDeleteOperation.from_dict(data)

                    return operations_item_type_1
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                operations_item_type_2 = FileRenameOperation.from_dict(data)

                return operations_item_type_2

            operations_item = _parse_operations_item(operations_item_data)

            operations.append(operations_item)

        repo_update_diff = cls(
            type_=type_,
            operations=operations,
        )

        repo_update_diff.additional_properties = d
        return repo_update_diff

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
