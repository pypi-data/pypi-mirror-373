from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.repo_create_legacy_request_metadata_type_0 import RepoCreateLegacyRequestMetadataType0


T = TypeVar("T", bound="RepoCreateLegacyRequest")


@_attrs_define
class RepoCreateLegacyRequest:
    """
    Attributes:
        template (Union[Unset, str]):  Default: 'squack-io/vite-base'.
        template_branch (Union[None, Unset, str]):
        metadata (Union['RepoCreateLegacyRequestMetadataType0', None, Unset]):
        description (Union[None, Unset, str]):
    """

    template: Union[Unset, str] = "squack-io/vite-base"
    template_branch: Union[None, Unset, str] = UNSET
    metadata: Union["RepoCreateLegacyRequestMetadataType0", None, Unset] = UNSET
    description: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.repo_create_legacy_request_metadata_type_0 import RepoCreateLegacyRequestMetadataType0

        template = self.template

        template_branch: Union[None, Unset, str]
        if isinstance(self.template_branch, Unset):
            template_branch = UNSET
        else:
            template_branch = self.template_branch

        metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, RepoCreateLegacyRequestMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if template is not UNSET:
            field_dict["template"] = template
        if template_branch is not UNSET:
            field_dict["template_branch"] = template_branch
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.repo_create_legacy_request_metadata_type_0 import RepoCreateLegacyRequestMetadataType0

        d = dict(src_dict)
        template = d.pop("template", UNSET)

        def _parse_template_branch(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        template_branch = _parse_template_branch(d.pop("template_branch", UNSET))

        def _parse_metadata(data: object) -> Union["RepoCreateLegacyRequestMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = RepoCreateLegacyRequestMetadataType0.from_dict(data)

                return metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RepoCreateLegacyRequestMetadataType0", None, Unset], data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        repo_create_legacy_request = cls(
            template=template,
            template_branch=template_branch,
            metadata=metadata,
            description=description,
        )

        repo_create_legacy_request.additional_properties = d
        return repo_create_legacy_request

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
