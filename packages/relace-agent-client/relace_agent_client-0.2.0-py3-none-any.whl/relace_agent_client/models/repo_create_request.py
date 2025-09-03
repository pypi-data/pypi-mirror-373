from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.repo_create_files_source import RepoCreateFilesSource
    from ..models.repo_create_git_source import RepoCreateGitSource
    from ..models.repo_create_relace_source import RepoCreateRelaceSource
    from ..models.repo_create_request_metadata_type_0 import RepoCreateRequestMetadataType0


T = TypeVar("T", bound="RepoCreateRequest")


@_attrs_define
class RepoCreateRequest:
    """
    Attributes:
        source (Union['RepoCreateFilesSource', 'RepoCreateGitSource', 'RepoCreateRelaceSource', None, Unset]):
        metadata (Union['RepoCreateRequestMetadataType0', None, Unset]):
    """

    source: Union["RepoCreateFilesSource", "RepoCreateGitSource", "RepoCreateRelaceSource", None, Unset] = UNSET
    metadata: Union["RepoCreateRequestMetadataType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.repo_create_files_source import RepoCreateFilesSource
        from ..models.repo_create_git_source import RepoCreateGitSource
        from ..models.repo_create_relace_source import RepoCreateRelaceSource
        from ..models.repo_create_request_metadata_type_0 import RepoCreateRequestMetadataType0

        source: Union[None, Unset, dict[str, Any]]
        if isinstance(self.source, Unset):
            source = UNSET
        elif isinstance(self.source, RepoCreateGitSource):
            source = self.source.to_dict()
        elif isinstance(self.source, RepoCreateFilesSource):
            source = self.source.to_dict()
        elif isinstance(self.source, RepoCreateRelaceSource):
            source = self.source.to_dict()
        else:
            source = self.source

        metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, RepoCreateRequestMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if source is not UNSET:
            field_dict["source"] = source
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.repo_create_files_source import RepoCreateFilesSource
        from ..models.repo_create_git_source import RepoCreateGitSource
        from ..models.repo_create_relace_source import RepoCreateRelaceSource
        from ..models.repo_create_request_metadata_type_0 import RepoCreateRequestMetadataType0

        d = dict(src_dict)

        def _parse_source(
            data: object,
        ) -> Union["RepoCreateFilesSource", "RepoCreateGitSource", "RepoCreateRelaceSource", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_type_0_type_0 = RepoCreateGitSource.from_dict(data)

                return source_type_0_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_type_0_type_1 = RepoCreateFilesSource.from_dict(data)

                return source_type_0_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_type_0_type_2 = RepoCreateRelaceSource.from_dict(data)

                return source_type_0_type_2
            except:  # noqa: E722
                pass
            return cast(
                Union["RepoCreateFilesSource", "RepoCreateGitSource", "RepoCreateRelaceSource", None, Unset], data
            )

        source = _parse_source(d.pop("source", UNSET))

        def _parse_metadata(data: object) -> Union["RepoCreateRequestMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = RepoCreateRequestMetadataType0.from_dict(data)

                return metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RepoCreateRequestMetadataType0", None, Unset], data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        repo_create_request = cls(
            source=source,
            metadata=metadata,
        )

        repo_create_request.additional_properties = d
        return repo_create_request

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
