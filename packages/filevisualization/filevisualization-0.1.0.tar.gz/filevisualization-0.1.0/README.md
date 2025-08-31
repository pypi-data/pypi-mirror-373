# filevisualization

![CI](https://github.com/hayashikunita/filevisualization/actions/workflows/ci.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/filevisualization.svg)

構造化ファイル（JSON / YAML / TOML / XML）を以下の方法で可視化するPythonライブラリです。
ビッグデータを扱う際、ワンコマンドで可視化します。

- ターミナル上のリッチな樹形図（Rich）
- Graphviz によるマインドマップ風グラフ（SVG/PNG などに保存）
- Plotly（インタラクティブHTML）
- pyvis（インタラクティブHTML）

CLI と Python API の両方で利用できます。

主な特徴
- 拡張子から自動判別（JSON / YAML / TOML / XML）
- 複数レンダラー（tree / graphviz / plotly / pyvis）
- レイアウト切替（hierarchical / radial / force）やエンジン指定（dot/twopi/sfdp/circo など）
- テーマ（pastel［既定］, light, dark, kawaii, chic, modern, business, caution）と型に基づくアイコン・形状
- フィルタリング・制限（max-depth / include-keys / exclude-keys / prune-arrays / max-nodes / max-edges）
- 大規模JSON向けストリーミング読み込み（--stream-json）
- グラフエクスポート（DOT / JSON-Graph / GraphML / CSV-edges）
- 診断コマンドで環境チェック（--diagnose）
- 単体テスト・型ヒント・CI（OS×Py×Graphviz 有無 マトリクス）、pre-commit、Bandit、ライセンスチェック

対応Python: 3.10–3.12（CIで検証済み）

---

## インストール

PyPI（推奨）
```
pip install filevisualization
```

最小構成（Rich + 主要パーサ）
```
pip install .
```

オプション（インタラクティブ表示用）
```
# Plotly を使う場合
pip install .[plotly]

# pyvis を使う場合
pip install .[pyvis]

# すべて（Plotly + pyvis + pygraphviz: pygraphviz は Python>=3.10 の環境で有効）
pip install .[all]
```

Graphviz（システム本体）のインストール（Graphviz出力をファイル保存する場合に必要）
- ダウンロード: https://graphviz.org/download/
- Windows はインストーラー実行後、`dot.exe` のパスが PATH に通っていることを確認してください。
	- PowerShell で確認: `dot -V`（バージョン表示されればOK）

---

## 使い方（CLI）

基本
```
fileviz <path> --format tree|graphviz|mindmap|plotly|pyvis \
	[--output <path>] [--layout <name>] [--engine <name>] [--theme <name>] \
	[--max-depth N] [--include-keys k1,k2] [--exclude-keys k1,k2] [--prune-arrays N] \
	[--max-nodes N] [--max-edges N] [--stream-json] \
	[--export-dot PATH] [--export-json-graph PATH] [--export-graphml PATH] [--export-csv-edges PATH] \
	[--diagnose]
```

例
```
# 樹形図（ターミナル表示）
fileviz example.json --format tree

# Graphviz をSVGで保存（階層: TB）
fileviz example.yaml --format graphviz --layout hierarchical --output out_tb.svg

# Graphviz（階層: LR）
fileviz example.yaml --format graphviz --layout lr --output out_lr.svg

# Graphviz（放射: twopi）
fileviz example.toml --format graphviz --layout radial --output radial.svg

# Graphviz（力学: sfdp）
fileviz example.xml --format graphviz --layout force --output force.svg

# Graphviz（エンジンを直接指定: circo）
fileviz example.json --format graphviz --engine circo --output circo.svg

# Plotly（HTML出力、オフラインで開けるようにJSをインライン埋め込み）
fileviz example.json --format plotly --output plotly.html

# pyvis（HTML出力）
fileviz example.yaml --format pyvis --output pyvis.html

# 診断（Graphvizやオプション依存の有無を表示）
fileviz --diagnose
```

オプションの概要（詳細）

- `--format`
	- 値: `tree` | `graphviz` | `mindmap`（= `graphviz` のエイリアス） | `plotly` | `pyvis`
	- 既定: `tree`
	- 出力未指定時（`--output`なし）の挙動:
		- `tree`: 端末にツリーを表示
		- `graphviz`/`mindmap`: DOTソースを標準出力
		- `plotly`: 図のJSON仕様を標準出力
		- `pyvis`: 一時HTMLファイルに書き出し、そのパスを標準出力
	- 依存関係/要件:
		- `graphviz`: システムにGraphviz本体（`dot`）が必要（ファイル保存時）。
		- `plotly`: 追加インストール `.[plotly]` が必要。
		- `pyvis`: 追加インストール `.[pyvis]` が必要。

- `--output <path>`
	- 値: 保存先のファイルパス（拡張子で形式判定します）
	- Graphvizの拡張子: 指定拡張子を尊重して保存（`.svg`推奨）。未指定なら `.svg` を自動付与。
	- 出力未指定時の挙動は上記 `--format` の項参照。
	- 例:
		- `--format graphviz --output graph.svg`
		- `--format plotly --output figure.html`
		- `--format pyvis --output network.html`

- `--layout <name>`（Graphviz系: `graphviz` / `mindmap`）
	- 値と意味:
		- `hierarchical` / `tree` / `tb` / `lr`:
			- 既定エンジンは `dot`。
			- 上下（TB）が既定。左右（LR）にしたい場合は `lr` を指定。
		- `radial` / `circle`:
			- 既定エンジンは `twopi`（放射状配置）。
		- `force` / `spring`:
			- 既定エンジンは `sfdp`（力学的配置）。
	- 備考: `--engine` を指定するとエンジンは上書きされます。`rankdir`（TB/LR）の効果は `dot` で有効です（他エンジンでは無視されることがあります）。

- `--engine <name>`（Graphviz系）
	- 値: `dot`, `twopi`, `sfdp`, `neato`, `circo` など Graphviz のエンジン名。
	- 既定: `dot`（`layout` により `twopi`/`sfdp` へ切替あり）。
	- `--layout` よりも優先され、指定したエンジンでレイアウトが実行されます。
	- 例: `--engine circo`（円環状に配置）

- `--theme <name>`
	- 値: `pastel`（既定）, `light`, `dark`, `kawaii`, `chic`, `modern`, `business`, `caution`
	- 影響範囲:
		- Rich（`tree`）: ラベル色とアイコン（絵文字）
		- Graphviz: 背景/ノード/エッジ色、ノード形状、（一部テーマで）グラデーション塗り
		- Plotly: 背景色、カラーパレット、マーカーシンボル
		- pyvis: 背景/ノード/エッジ色、ノード形状
	- 例: `--theme kawaii`（やわらか配色と親しみやすい記号）

	- フィルタリング / 制限
		- `--max-depth <N>`: 走査の最大深さ。超えた部分はサマリ表示。
		- `--include-keys <k1,k2>`: 部分一致で含めたいキー（dict対象）。
		- `--exclude-keys <k1,k2>`: 部分一致で除外したいキー（dict対象）。
		- `--prune-arrays <N>`: 配列が N を超えたら先頭 N 要素＋サマリに省略。
		- `--max-nodes <N>` / `--max-edges <N>`: ノード/エッジのハード上限（超えたら打ち切り＋警告）。

	- ストリーミング
		- `--stream-json`: ijson を利用してJSONをストリーミング読み込み（超大規模JSON向け）。
			- 追加インストール: `pip install .[stream]`

	- エクスポート
		- `--export-dot PATH`: DOTソースを書き出し。
		- `--export-json-graph PATH`: JSON-Graph（nodes/links）を書き出し。
		- `--export-graphml PATH`: GraphMLを書き出し。
		- `--export-csv-edges PATH`: エッジCSV（source,target,label）を書き出し。

拡張子の扱い（Graphviz）
- 出力ファイルの拡張子をそのまま尊重して保存します。`.svg` を指定すれば `.svg` で保存され、`.svg.svg` のような二重拡張子にはなりません。
- 拡張子未指定の場合は自動で `.svg` が付きます。

---

## 使い方（Python API）

簡単な例
```python
from filevisualization import visualize_path

# 樹形図を端末に表示
visualize_path("example.toml", format="tree")

# Graphviz（SVG保存）
visualize_path("example.xml", format="graphviz", layout="radial", output="graph.svg")
```

少し詳しい制御
```python
from filevisualization.core import load_file, visualize_data

data = load_file("tests/fixtures/sample.yaml")

# Plotly（HTML）
visualize_data(data, format="plotly", theme="business", output="plotly.html")

# pyvis（HTML）
visualize_data(data, format="pyvis", theme="kawaii", output="pyvis.html")
```

---

## テーマと型ベースのスタイリング

- テーマ（`--theme` / API引数 `theme`）
	- `pastel`（既定）, `light`, `dark`, `kawaii`, `chic`, `modern`, `business`, `caution`
	- 背景・ノード・エッジの色がテーマごとに調整されます。
- 型ベースのスタイル
	- 値の種類（オブジェクト/配列/文字列/数値/真偽/Null など）に応じて、
		- Rich: アイコン（絵文字）
		- Graphviz: 形状（box, ellipse, diamond など）
		- Plotly: マーカーシンボル
		- pyvis: ノード形状
		が自動で割り当てられます。

---

## サンプルデータ

テスト用サンプルは `tests/fixtures` にあります。
- `tests/fixtures/sample.json`
- `tests/fixtures/sample.yaml`
- `tests/fixtures/sample.toml`
- `tests/fixtures/sample.xml`

---

## トラブルシュート

Graphviz: `ExecutableNotFound` になる
- システムに Graphviz が未インストール、または `dot` が PATH にありません。
- Windows の場合: Graphviz インストール後、PowerShell で `dot -V` が通るか確認してください。
	- それでも失敗する場合は `fileviz --diagnose` の出力を確認してください。

Graphviz出力の拡張子が二重になる
- 本ライブラリは出力拡張子を尊重して保存する実装（`pipe` で書き込み）に更新済みです。
- `.svg` を指定すれば `.svg` のみで保存されます。

Plotly の HTML がオフラインで開けない
- 本ライブラリは `include_plotlyjs="inline"` で書き出すため、単体HTMLで開けます。

pygraphviz を使いたい
- オプション依存関係（`.[all]`）に含まれていますが、Python>=3.10 でのみ有効化されます。
- Windows では VC++ Build Tools が必要になることがあります。

---

## 開発

ローカル開発
```
pip install -e .[all]
pre-commit install
pre-commit run --all-files
ruff check .
mypy
bandit -r src
pytest -q
```

uv を使う場合（任意）
```
# ヘルプ
uv run fileviz -h
# 見つからない場合
uv run python -m filevisualization.cli -h

# 例: Graphviz（放射）
uv run fileviz example.toml --format graphviz --layout radial --output radial.svg

# Plotly / pyvis の追加
uv pip install .[plotly]
uv run fileviz example.json --format plotly --output plotly.html

uv pip install .[pyvis]
uv run fileviz example.yaml --format pyvis --output pyvis.html
```

CI/品質ゲート
- Ruff（lint & format）
- mypy（strict）
- pytest（DOT/JSON-Graph の最小ゴールデンテスト含む）
- pre-commit（コミット前に自動整形・解析）
- Bandit（セキュリティ静的解析）
- OSS ライセンス出力（CIで生成・保存可能）

構成
- ビルド: `pyproject.toml`（PEP 621, setuptools）
- パッケージ: `src/filevisualization`
- CLI: `fileviz` エントリポイント（`filevisualization/cli.py`）
- テスト: `tests/`
- CI: `.github/workflows/ci.yml`（OS×Python×Graphviz 有無のマトリクスで検証）

ライセンス: MIT（`LICENSE` を参照）

---

## 変更履歴（抜粋）
- Graphviz 出力時の拡張子処理を改善し、二重拡張子にならないように変更
- テーマと型ベースのスタイルを全レンダラーに適用
- フィルタ・制限・ストリーミングJSON・各種エクスポート・診断を追加
- CIマトリクス、pre-commit、Bandit、ライセンスチェックを追加
