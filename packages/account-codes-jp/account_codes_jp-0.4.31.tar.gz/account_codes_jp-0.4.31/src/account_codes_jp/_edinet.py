from collections.abc import Sequence
from io import BytesIO
from logging import getLogger
from pathlib import Path
from typing import Any, Literal, Protocol

import networkx as nx
import numpy as np
import pandas as pd
from requests_cache import CachedSession

from account_codes_jp._common import AccountType

# from strictly_typed_pandas import DataSet

LOG = getLogger(__name__)

Industry = Literal[
    "一般商工業",
    "建設業",
    "銀行・信託業",
    "銀行・信託業（特定取引勘定設置銀行）",
    "建設保証業",
    "第一種金融商品取引業",
    "生命保険業",
    "損害保険業",
    "鉄道事業",
    "海運事業",
    "高速道路事業",
    "電気通信事業",
    "電気事業",
    "ガス事業",
    "資産流動化業",
    "投資運用業",
    "投資業",
    "特定金融業",
    "社会医療法人",
    "学校法人",
    "商品先物取引業",
    "リース事業",
    "投資信託受益証券",
]


class ETaxAccountProtocol(Protocol):
    industry: Industry
    """EDINETで設定されている業種目（23業種）"""
    grounded: bool
    """会計基準及び業法等の法令規則に設定の根拠を有するか"""
    label: str
    """標準ラベル（日本語）"""
    label_en: str
    """標準ラベル（英語）"""
    label_long: str
    """冗長ラベル（日本語）"""
    label_long_en: str
    """冗長ラベル（英語）"""
    label_category: str
    """用途区分、財務諸表区分及び業種区分のラベル（日本語）"""
    label_category_en: str
    """用途区分、財務諸表区分及び業種区分のラベル（英語）"""
    prefix: Literal["jppfs_cor"]
    """名前空間プレフィックス"""
    element: str
    """要素名"""
    type: Literal["xbrli:stringItemType", "xbrli:monetaryItemType"]
    """データ型"""
    substitution_group: Literal["xbrli:item", "xbrldt:hypercubeItem"]
    """代替グループ"""
    duration: bool
    """持続かどうか（期間時点区分）
    >>> from account_codes_jp import get_etax_accounts
    >>> df = get_etax_accounts()
    >>> (df["duration"] == df["abstract"]).describe()
    count     3736
    unique       1
    top       True
    freq      3736
    dtype: object"""
    debit: bool
    """借方かどうか（貸借区分）"""
    abstract: bool
    """抽象かどうか
    >>> from account_codes_jp import get_etax_accounts
    >>> df = get_etax_accounts()
    >>> (df["duration"] == df["abstract"]).describe()
    count     3736
    unique       1
    top       True
    freq      3736
    dtype: object
    >>> from account_codes_jp import get_etax_accounts
    >>> df = get_etax_accounts()
    >>> df.loc[(df["title"] != df["abstract"]), "label"].unique()
    array(['貸借対照表'], dtype=object)
    """
    depth: Literal[0, 1, 2, 3, 4, 5, 6, 7]
    """階層の深さ"""
    title: bool
    """EDINETの勘定科目リストで冗長ラベルがタイトル項目
    >>> from account_codes_jp import get_etax_accounts
    >>> df = get_etax_accounts()
    >>> df.loc[(df["title"] != df["abstract"]), "label"].unique()
    array(['貸借対照表'], dtype=object)"""
    total: bool
    """EDINETの勘定科目リストで用途区分が合計と使用できる"""
    account_type: Literal[
        None,
        "資産",
        "流動資産",
        "固定資産",
        "有形固定資産",
        "無形固定資産",
        "投資その他の資産",
        "繰延資産",
        "負債",
        "流動負債",
        "固定負債",
        "特別法上の準備金等",
        "純資産",
        "株主資本",
        "資本金",
        "資本剰余金",
        "利益剰余金",
        "評価・換算差額等",
        "新株予約権",
        "売上高",
        "売上原価",
        "販売費及び一般管理費(売上原価)",
        "損益",
        "その他",
        "販売費及び一般管理費",
        "営業外収益",
        "営業外費用",
        "特別利益",
        "特別損失",
        "収益",
        "費用",
    ]
    """EDINETの勘定科目リストで使用されている勘定科目を財務諸表規則に基づき区分したもの"""
    code: str
    """貸借対照表のCSV形式データを作成するのに使用する勘定科目コード"""
    label_etax: str
    """EDINETの勘定科目リストで使用されている勘定科目及び勘定科目コードに対応する公表用e-Tax勘定科目（日本語）"""
    label_etax_en: str
    """EDINETの勘定科目リストで使用されている勘定科目及び勘定科目コードに対応する公表用e-Tax勘定科目（日本語）"""
    etax: Literal[
        None,
        "資産",
        "流動資産",
        "固定資産",
        "有形固定資産",
        "無形固定資産",
        "投資その他の資産",
        "繰延資産",
        "負債",
        "流動負債",
        "固定負債",
        "特別法上の準備金等",
        "純資産",
        "株主資本",
        "資本金",
        "資本剰余金",
        "利益剰余金",
        "評価・換算差額等",
        "新株予約権",
        "売上高",
        "売上原価",
        "損益",
        "その他",
        "販売費及び一般管理費",
        "営業外収益",
        "営業外費用",
        "特別利益",
        "特別損失",
    ]
    """e-Taxの勘定科目を財務諸表規則に基づき区分したもの"""


def to_bool_or_nan(
    x: "pd.Series[str]",
    true_values: Sequence[Any],
    false_values: Sequence[Any],
) -> "pd.Series[Any]":
    true_idx = x.isin(true_values)
    false_idx = x.isin(false_values)
    x = x.copy()
    x[true_idx] = True
    x[false_idx] = False
    x[~true_idx & ~false_idx] = pd.NA
    return x


def get_edinet_accounts(
    industry: Industry | None = None,
    debug_unique: bool = False,
    skip_non_line_elements: bool = True,
) -> nx.DiGraph:
    """
    EDINETの勘定科目リストのDataFrameを取得する

    Parameters
    ----------
    industry : Industry | None, optional
        EDINETで設定されている業種目（23業種）, by default None
        If None, all industries are returned.
    debug_unique : bool, optional
        Whether to print unique values per column,
        by default False
    skip_non_line_elements : bool, optional
        Whether to skip non-line elements,
        which was introduced due to the reference
        being the copy of EDINET account list,
        by default True

    Returns
    -------
    pd.DataFrame
        DataFrame representation of the EDINET account list

    """
    path = Path("~/.cache/aoiro/aoiro").expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with CachedSession(path) as s:
        dfs = []
        URLS = (
            "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho3/1/BScodeall_2019.xlsx",
            "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho3/2/PLcodeall_2019.xlsx",
        )
        for URL in URLS:
            r = s.get(URL)
            with BytesIO(r.content) as f:
                dfs.append(
                    pd.read_excel(
                        f,
                        sheet_name=1,
                        skiprows=2,
                        na_values=["-"],
                        true_values=["true"],
                        false_values=["false"],
                    )
                )
    df = pd.concat(dfs, ignore_index=True)
    df.rename(
        columns={
            "業種": "industry",
            "科目分類": "grounded",
            "標準ラベル（日本語）": "label",
            "標準ラベル（英語）": "label_en",
            "冗長ラベル（日本語）": "label_long",
            "冗長ラベル（英語）": "label_long_en",
            "用途区分、財務諸表区分及び業種区分のラベル（日本語）": "label_category",
            "用途区分、財務諸表区分及び業種区分のラベル（英語）": "label_category_en",
            "名前空間プレフィックス": "prefix",
            "要素名": "element",
            "type": "type",
            "substitutionGroup": "substitution_group",
            "periodType": "duration",
            "balance": "debit",
            "abstract": "abstract",
            "depth": "depth",
            "タイトル項目": "title",
            "合計\n（用途区分）": "total",
            "勘定科目区分": "account_type",
            "勘定科目コード": "account_code",
            "e-Tax対応勘定科目（日本語）": "label_etax",
            "e-Tax対応勘定科目（英語）": "label_etax_en",
            "e-Tax勘定科目区分": "etax",
        },
        inplace=True,
        errors="raise",
    )
    if debug_unique:
        for k, col in df.items():
            LOG.debug(f"{k}: {col.unique()[:100].tolist()}")
    if skip_non_line_elements:
        df = df[df["depth"] > 0]
        df = df[~df["element"].str.contains("Table")]
    if industry is not None:
        df = df[df["industry"] == industry]
    for k in ["total", "title"]:
        df[k] = to_bool_or_nan(df[k], ["○"], [np.nan])
    df["duration"] = to_bool_or_nan(df["duration"], ["duration"], ["instant"])
    df["debit"] = to_bool_or_nan(df["debit"], ["debit"], ["credit"])
    df = pd.concat([pd.DataFrame([{"depth": 0}]), df], join="outer", ignore_index=True)
    return edinet_accounts_as_graph(df)


def edinet_accounts_as_graph(df: pd.DataFrame) -> nx.DiGraph:
    """
    get_edinet_accounts()の結果をnx.DiGraphに変換する

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame representation of
        the EDINET account list

    Returns
    -------
    nx.DiGraph
        Tree representation of the EDINET account list

    Raises
    ------
    AssertionError
        If the "depth" values are inconsistent

    """
    G = nx.DiGraph()
    ancestors: list[Any] = []
    min_depth = df["depth"].min()
    for k, row in df.iterrows():
        if row["label"] not in G.nodes:
            G.add_node(k, **row.to_dict())
        if row["depth"] > len(ancestors) + 1 + min_depth:
            raise AssertionError(
                f"{k}: depth: {row['depth']}, depth_prev: {len(ancestors)}"
            )
        ancestors = ancestors[: row["depth"] - min_depth]
        if ancestors:
            G.add_edge(ancestors[-1], k)
        G.nodes[k]["ancestors"] = ancestors
        account_type = None
        ancestor_labels = [G.nodes[a]["label"] for a in ancestors]
        if "損益計算書" in ancestor_labels:
            if row["debit"] is AccountType.Expense.debit:
                account_type = AccountType.Expense
            elif row["debit"] is AccountType.Revenue.debit:
                account_type = AccountType.Revenue
        elif "貸借対照表" in ancestor_labels:
            for t in [
                AccountType.Asset,
                AccountType.Liability,
                AccountType.Equity,
            ]:
                if t.value + "の部" in ancestor_labels:
                    account_type = t
                    break
        G.nodes[k]["account_type"] = account_type
        ancestors.append(k)
    return G
