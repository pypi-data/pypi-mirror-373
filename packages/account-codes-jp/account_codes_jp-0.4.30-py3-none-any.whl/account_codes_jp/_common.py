import warnings
from collections.abc import Mapping
from typing import Any, Callable, Literal, TypeVar

import networkx as nx
from strenum import StrEnum

SUNDRY = "諸口"
Account = TypeVar("Account", bound=str)
AccountSundry = Literal["諸口"]


class AccountType(StrEnum):
    Asset = "資産"
    """資産(借方/賃借対照表)"""
    Liability = "負債"
    """負債(貸方/賃借対照表)"""
    Equity = "純資産"
    """純資産(貸方/賃借対照表)"""
    Revenue = "収益"
    """収益(貸方/損益計算書)"""
    Expense = "費用"
    """費用(借方/損益計算書)"""
    Sundry = "諸口"
    """諸口"""

    @property
    def debit(self) -> bool | None:
        """借方(左)ならTrue, 貸方(右)ならFalse, 諸口ならNone"""
        if self == AccountType.Sundry:
            return None
        return self in (AccountType.Asset, AccountType.Expense)

    @property
    def static(self) -> bool | None:
        """賃借対照表ならTrue, 損益計算書ならFalse, 諸口ならNone"""
        if self == AccountType.Sundry:
            return None
        return self in (AccountType.Equity, AccountType.Liability, AccountType.Asset)


def get_account_ambiguous_factory(G: nx.DiGraph) -> Callable[[str], str]:
    """
    Estimate the correct account name from a possibly ambiguous account name.

    Uses both literal and japanese phonetic matching.

    Parameters
    ----------
    G : nx.DiGraph
        The account tree

    Returns
    -------
    Callable[[str], str]
        A function that takes an account name
        and returns the closest match from the account tree

    """
    from pykakasi import kakasi
    from rapidfuzz import fuzz
    from rapidfuzz.process import extractOne

    kks = kakasi()

    def processor(s: str) -> str:
        s = str(s)
        return s + "|" + "".join([item["hira"] for item in kks.convert(s)])

    accounts = list(nx.get_node_attributes(G, "label").values())
    return lambda account: extractOne(
        account, accounts, processor=processor, scorer=fuzz.QRatio
    )[0]


def get_node_from_label(
    G: nx.DiGraph,
    label: str,
    cond: Callable[[Mapping[Any, Any]], bool] | None = None,
    multiple: bool = False,
) -> Any:
    """
    Get the node from the label and condition

    Parameters
    ----------
    G : nx.DiGraph
        The account tree
    label : str
        The label of the node
    cond : Callable[Mapping[Any, Any], bool]
        The condition to satisfy
    multiple : bool, optional
        Whether to return multiple nodes, by default False

    Returns
    -------
    Any
        The node that satisfies the condition

    """
    nodes = [
        n
        for n, d in G.nodes.data()
        if (d["label"] == label and (cond(n) if cond is not None else True))
    ]
    if not nodes:
        raise ValueError(f"Node with label {label} not found")
    if multiple:
        return nodes
    if len(nodes) > 1:
        warnings.warn(f"Multiple nodes with label {label} found", stacklevel=2)
    return nodes[0]


def get_account_type_factory(
    G: nx.DiGraph, ambiguous: bool = False
) -> Callable[[str], AccountType | None]:
    """
    Get the account type from the account name

    Parameters
    ----------
    G : nx.DiGraph
        The account tree
    ambiguous : bool, optional
        Whether to use the ambiguous account name resolver, by default False

    Returns
    -------
    Callable[[str], AccountType | None]
        A function that takes an account name and returns the
        account type or None if the account is not found

    """
    nonabstract_nodes = {
        d["label"]: d.get("account_type")
        for _, d in G.nodes(data=True)
        if not d["abstract"]
    }
    if ambiguous:
        get_amb = get_account_ambiguous_factory(G)

    def _(account: str) -> AccountType | None:
        if account == SUNDRY:
            return AccountType.Sundry
        if ambiguous:
            account = get_amb(account)
        return nonabstract_nodes.get(account)

    return _
