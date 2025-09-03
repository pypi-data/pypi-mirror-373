from collections.abc import Mapping
from typing import Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RepoCreateGitSource")


@_attrs_define
class RepoCreateGitSource:
    """
    Attributes:
        type_ (Literal['git']):
        url (str):
        branch (Union[None, Unset, str]):
    """

    type_: Literal["git"]
    url: str
    branch: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        url = self.url

        branch: Union[None, Unset, str]
        if isinstance(self.branch, Unset):
            branch = UNSET
        else:
            branch = self.branch

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "url": url,
            }
        )
        if branch is not UNSET:
            field_dict["branch"] = branch

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["git"], d.pop("type"))
        if type_ != "git":
            raise ValueError(f"type must match const 'git', got '{type_}'")

        url = d.pop("url")

        def _parse_branch(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        branch = _parse_branch(d.pop("branch", UNSET))

        repo_create_git_source = cls(
            type_=type_,
            url=url,
            branch=branch,
        )

        repo_create_git_source.additional_properties = d
        return repo_create_git_source

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
