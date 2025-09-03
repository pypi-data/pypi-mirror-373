from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RepoRetrieveRequest")


@_attrs_define
class RepoRetrieveRequest:
    """
    Attributes:
        query (str):
        include_content (Union[Unset, bool]):  Default: False.
        token_limit (Union[Unset, int]):  Default: 32000.
        score_threshold (Union[Unset, float]):  Default: 0.3.
        rerank (Union[Unset, bool]):  Default: True.
    """

    query: str
    include_content: Union[Unset, bool] = False
    token_limit: Union[Unset, int] = 32000
    score_threshold: Union[Unset, float] = 0.3
    rerank: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        include_content = self.include_content

        token_limit = self.token_limit

        score_threshold = self.score_threshold

        rerank = self.rerank

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if include_content is not UNSET:
            field_dict["include_content"] = include_content
        if token_limit is not UNSET:
            field_dict["token_limit"] = token_limit
        if score_threshold is not UNSET:
            field_dict["score_threshold"] = score_threshold
        if rerank is not UNSET:
            field_dict["rerank"] = rerank

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        include_content = d.pop("include_content", UNSET)

        token_limit = d.pop("token_limit", UNSET)

        score_threshold = d.pop("score_threshold", UNSET)

        rerank = d.pop("rerank", UNSET)

        repo_retrieve_request = cls(
            query=query,
            include_content=include_content,
            token_limit=token_limit,
            score_threshold=score_threshold,
            rerank=rerank,
        )

        repo_retrieve_request.additional_properties = d
        return repo_retrieve_request

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
