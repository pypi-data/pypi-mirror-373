from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.repo_update_diff import RepoUpdateDiff
    from ..models.repo_update_files import RepoUpdateFiles
    from ..models.repo_update_git import RepoUpdateGit


T = TypeVar("T", bound="RepoUpdateRequest")


@_attrs_define
class RepoUpdateRequest:
    """
    Attributes:
        source (Union['RepoUpdateDiff', 'RepoUpdateFiles', 'RepoUpdateGit']):
    """

    source: Union["RepoUpdateDiff", "RepoUpdateFiles", "RepoUpdateGit"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.repo_update_diff import RepoUpdateDiff
        from ..models.repo_update_files import RepoUpdateFiles

        source: dict[str, Any]
        if isinstance(self.source, RepoUpdateFiles):
            source = self.source.to_dict()
        elif isinstance(self.source, RepoUpdateDiff):
            source = self.source.to_dict()
        else:
            source = self.source.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source": source,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.repo_update_diff import RepoUpdateDiff
        from ..models.repo_update_files import RepoUpdateFiles
        from ..models.repo_update_git import RepoUpdateGit

        d = dict(src_dict)

        def _parse_source(data: object) -> Union["RepoUpdateDiff", "RepoUpdateFiles", "RepoUpdateGit"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_type_0 = RepoUpdateFiles.from_dict(data)

                return source_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_type_1 = RepoUpdateDiff.from_dict(data)

                return source_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            source_type_2 = RepoUpdateGit.from_dict(data)

            return source_type_2

        source = _parse_source(d.pop("source"))

        repo_update_request = cls(
            source=source,
        )

        repo_update_request.additional_properties = d
        return repo_update_request

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
