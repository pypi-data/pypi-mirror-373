# Cobalt Python API

Cobalt認識スタック用のPython APIです。このライブラリは、WebSocketベースのインターフェースを提供し、Cobalt認識システムに接続してオブジェクト検出データを受信します。

## 機能

- Cobalt認識スタックへのWebSocket接続
- 効率的なバイナリデータ処理のためのctypesを使用したオブジェクト検出データ構造
- オブジェクト検出ストリームの購読サポート
- リアルタイムデータ処理のためのAsync/awaitサポート

## インストール

### PyPIから（公開時）

```bash
pip install cobalt-sdk
```

### ソースから

```bash
git clone https://github.com/ceptontech/cobalt.git
cd cobalt/cobalt-py-sdk
pip install .
```

### requirements.txtを使用

```bash
pip install -r requirements.txt
```

## 開発用インストール

開発作業の場合、開発依存関係と共にパッケージを編集可能モードでインストールします：

```bash
# 開発依存関係と共に編集可能モードでインストール
pip install -e ".[dev]"

# またはrequirementsファイルを使用
pip install -r requirements-dev.txt
pip install -e .
```

### 開発依存関係

開発環境には以下が含まれます：
- `pytest>=7.0` - テストフレームワーク
- `black>=22.0` - コードフォーマッター
- `flake8>=4.0` - リンティング
- `mypy>=0.950` - 型チェック

## 使用方法

### APIリファレンス

#### 接続関数

- `proto_connect()` - プロトコルWebSocketに接続（ポート23787）
- `data_connect()` - データWebSocketに接続（ポート9030）
- `subscribe_objects(ws)` - WebSocket接続でオブジェクト検出データを購読

#### データ構造

**Object** - 単一の検出されたオブジェクトを表します：
- `x`, `y`, `z` (float) - 3D位置座標
- `length`, `width`, `height` (float) - オブジェクトの寸法
- `theta` (float) - 回転角度
- `classification` (uint32) - オブジェクト分類ID
- `object_id` (uint32) - 一意のオブジェクト識別子

**Objects** - 複数のオブジェクトを含むフレーム：
- `magic` - フレーム識別子（"COBJ"）
- `num_objects` (uint32) - フレーム内のオブジェクト数
- `sequence_id` (uint32) - フレームシーケンス番号
- `objects` - Objectインスタンスのリスト

## 開発

### テストの実行

```bash
pytest
```

### コードフォーマット

```bash
black src/ samples/
```

### リンティング

```bash
flake8 src/ samples/
```

### 型チェック

```bash
mypy src/
```

## 要件

- Python >= 3.8
- WebSocket接続用のwebsocketsライブラリ

## 例

完全な例については`samples/`ディレクトリを参照してください：
- `connection_example.py` - 基本的な接続とオブジェクト購読の例

## ライセンス

MIT License - 詳細はLICENSEファイルを参照

## 貢献

1. 開発依存関係をインストール：`pip install -e ".[dev]"`
2. 変更を行う
3. テストを実行：`pytest`
4. コードをフォーマット：`black .`
5. リンティングをチェック：`flake8`
6. プルリクエストを提出

## サポート

問題や質問については、こちらを訪問してください：https://github.com/ceptontech/cobalt/issues
