import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.repo_metadata_metadata_type_0 import RepoMetadataMetadataType0


T = TypeVar("T", bound="RepoMetadata")


@_attrs_define
class RepoMetadata:
    """
    Attributes:
        repo_id (UUID):
        created_at (datetime.datetime):
        updated_at (Union[None, Unset, datetime.datetime]):
        metadata (Union['RepoMetadataMetadataType0', None, Unset]):
    """

    repo_id: UUID
    created_at: datetime.datetime
    updated_at: Union[None, Unset, datetime.datetime] = UNSET
    metadata: Union["RepoMetadataMetadataType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.repo_metadata_metadata_type_0 import RepoMetadataMetadataType0

        repo_id = str(self.repo_id)

        created_at = self.created_at.isoformat()

        updated_at: Union[None, Unset, str]
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, RepoMetadataMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repo_id": repo_id,
                "created_at": created_at,
            }
        )
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.repo_metadata_metadata_type_0 import RepoMetadataMetadataType0

        d = dict(src_dict)
        repo_id = UUID(d.pop("repo_id"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_updated_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        def _parse_metadata(data: object) -> Union["RepoMetadataMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = RepoMetadataMetadataType0.from_dict(data)

                return metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RepoMetadataMetadataType0", None, Unset], data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        repo_metadata = cls(
            repo_id=repo_id,
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata,
        )

        repo_metadata.additional_properties = d
        return repo_metadata

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
