# Account Codes JP

<p align="center">
  <a href="https://github.com/34j/account-codes-jp/actions/workflows/ci.yml?query=branch%3Amain">
    <img src="https://img.shields.io/github/actions/workflow/status/34j/account-codes-jp/ci.yml?branch=main&label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://account-codes-jp.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/account-codes-jp.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/34j/account-codes-jp">
    <img src="https://img.shields.io/codecov/c/github/34j/account-codes-jp.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json" alt="Poetry">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/account-codes-jp/">
    <img src="https://img.shields.io/pypi/v/account-codes-jp.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/account-codes-jp.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/account-codes-jp.svg?style=flat-square" alt="License">
</p>

---

**Documentation**: <a href="https://account-codes-jp.readthedocs.io" target="_blank">https://account-codes-jp.readthedocs.io </a>

**Source Code**: <a href="https://github.com/34j/account-codes-jp" target="_blank">https://github.com/34j/account-codes-jp </a>

---

e-Tax / EDINETタクソノミ / 青色申告 の勘定科目(コード)表のラッパー (非公式)

![青色申告の勘定科目](./blue-return.png)

## Installation

Install this via pip (or your favourite package manager):

`pip install account-codes-jp`

## Usage

```shell
$ account-codes-jp list --industry "一般商工業"
    ├─╼ 貸借対照表/貸借対照表/jppfs_cor:BalanceSheetLineItems
    │   ├─╼ 資産の部[タイトル]/資産の部/jppfs_cor:AssetsAbstract
    │   │   ├─╼ 流動資産[タイトル]/資産/流動資産/jppfs_cor:CurrentAssetsAbstract
    │   │   │   ├─╼ 現金及び預金/資産/現金及び預金/jppfs_cor:CashAndDeposits
    │   │   │   ├─╼ 受取手形及び売掛金/資産/受取手形及び売掛金/jppfs_cor:NotesAndAccountsReceivableTrade
    │   │   │   │   ├─╼ 貸倒引当金/資産/貸倒引当金/jppfs_cor:AllowanceForDoubtfulAccountsNotesAndAccountsReceivableTrade
    │   │   │   │   └─╼ 受取手形及び売掛金（純額）/資産/受取手形及び売掛金（純額）/jppfs_cor:NotesAndAccountsReceivableTradeNet
...
```

```shell
$ account-codes-jp list --type blue-return
    ├─╼ 賃借対照表[タイトル]
    │   ├─╼ 資産[タイトル]/資産
    │   │   ├─╼ 資産[タイトル]/資産
    │   │   │   ├─╼ 現金/資産
    │   │   │   ├─╼ 当座預金/資産
```

```python
from account_codes_jp import get_blue_return_accounts, get_account_type_factory, AccountType

G = get_blue_return_accounts()
t = get_account_type_factory(G)
assert t("現金") == AccountType.Asset
```

## Notes

本パッケージは単なるラッパーであり、EDINETタクソノミを含みませんが、念の為「EDINETタクソノミの知的所有権について」を引用いたします。

## [EDINETタクソノミの知的所有権について（「本文書」）](https://www.fsa.go.jp/search/EDINET_Taxonomy_Legal_Statement.html)

### 著作権

「EDINETタクソノミ」は、金融商品取引法に基づく有価証券報告書等の開示書類に関する電子開示システム（EDINET）に開示書類をXBRL形式により電子的に提出するために金融庁が開発したものであり、著作権の対象となっています。当該著作権は日本国著作権法及び国際条約により保護されています。

なお、金融庁の事前の許可なくEDINETタクソノミの全部又は一部について改変、修正又は翻訳を行うことはできません。EDINETタクソノミには、XBRL International Inc.（以下「XII」という。）の著作権に帰属する内容が一部含まれており、当該内容は、XIIの許諾に基づきEDINETタクソノミ中に作成されています。

本文書を一体とし、かつ、次の文言を用いて出所を明示することを条件に、EDINETタクソノミの全部又は一部の引用、転載、複製、譲渡、貸与、公衆送信又は配布を行うことができます：

© Copyright 2014 Financial Services Agency, The Japanese Government

### 保証責任の否認

EDINETタクソノミは、「現状有姿」にて提供され、金融庁及びXIIは、明示的であるか暗黙的であるかを問わず、商業利用への適合性、特定目的への適合性若しくは所有権の保証又はEDINETタクソノミの使用が第三者の特許権、著作権、トレードマークその他の権利を侵害しないことの保証その他のあらゆる保証の責任を否認します。

### 免責事項

契約、不法行為、保証その他の方法であるかを問わず、EDINETタクソノミ若しくはその関連ファイルを使用すること、又はいかなる種類の内容物の動作若しくは導入により発生する、代替品若しくは代替サービスの調達費用又は逸失利益又は使用の喪失又はデータの喪失又は直接、間接、結果的、偶発的、懲罰的若しくは特別の損害について、当該損害の可能性についての事前の通知の有無にかかわらず、金融庁及びXIIは、いかなる利用者又は第三者に対しても責任を負いません。

### 使用許諾

上記の条件を承諾し、かつ、XIIの知的財産権ポリシー（www.xbrl.org/legal）に準拠して使用する場合に限り、EDINETタクソノミを無償で使用することを許諾します。

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- prettier-ignore-start -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/34j"><img src="https://avatars.githubusercontent.com/u/55338215?v=4?s=80" width="80px;" alt="34j"/><br /><sub><b>34j</b></sub></a><br /><a href="https://github.com/34j/account-codes-jp/commits?author=34j" title="Code">💻</a> <a href="#ideas-34j" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/34j/account-codes-jp/commits?author=34j" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-end -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Credits

This package was created with
[Copier](https://copier.readthedocs.io/) and the
[browniebroke/pypackage-template](https://github.com/browniebroke/pypackage-template)
project template.
