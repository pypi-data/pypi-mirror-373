from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.branch_one_branches_item_modules_item_retry_constant import (
        BranchOneBranchesItemModulesItemRetryConstant,
    )
    from ..models.branch_one_branches_item_modules_item_retry_exponential import (
        BranchOneBranchesItemModulesItemRetryExponential,
    )


T = TypeVar("T", bound="BranchOneBranchesItemModulesItemRetry")


@_attrs_define
class BranchOneBranchesItemModulesItemRetry:
    """
    Attributes:
        constant (Union[Unset, BranchOneBranchesItemModulesItemRetryConstant]):
        exponential (Union[Unset, BranchOneBranchesItemModulesItemRetryExponential]):
    """

    constant: Union[Unset, "BranchOneBranchesItemModulesItemRetryConstant"] = UNSET
    exponential: Union[Unset, "BranchOneBranchesItemModulesItemRetryExponential"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        constant: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.constant, Unset):
            constant = self.constant.to_dict()

        exponential: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.exponential, Unset):
            exponential = self.exponential.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if constant is not UNSET:
            field_dict["constant"] = constant
        if exponential is not UNSET:
            field_dict["exponential"] = exponential

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.branch_one_branches_item_modules_item_retry_constant import (
            BranchOneBranchesItemModulesItemRetryConstant,
        )
        from ..models.branch_one_branches_item_modules_item_retry_exponential import (
            BranchOneBranchesItemModulesItemRetryExponential,
        )

        d = src_dict.copy()
        _constant = d.pop("constant", UNSET)
        constant: Union[Unset, BranchOneBranchesItemModulesItemRetryConstant]
        if isinstance(_constant, Unset):
            constant = UNSET
        else:
            constant = BranchOneBranchesItemModulesItemRetryConstant.from_dict(_constant)

        _exponential = d.pop("exponential", UNSET)
        exponential: Union[Unset, BranchOneBranchesItemModulesItemRetryExponential]
        if isinstance(_exponential, Unset):
            exponential = UNSET
        else:
            exponential = BranchOneBranchesItemModulesItemRetryExponential.from_dict(_exponential)

        branch_one_branches_item_modules_item_retry = cls(
            constant=constant,
            exponential=exponential,
        )

        branch_one_branches_item_modules_item_retry.additional_properties = d
        return branch_one_branches_item_modules_item_retry

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
