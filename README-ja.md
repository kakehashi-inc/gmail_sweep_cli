# Gmail Sweep CLI

Gmailの「すべてのメール」から指定期間のメールをFromアドレス別に集計し、不要なメール送信元を特定・一括削除（ゴミ箱移動）するためのCLIツールです。

## 機能

- 送信元アドレス別にメールを集計（件数・頻度・件名情報）
- 件数降順でソートされたインタラクティブなページネーション表示
- 期間ナビゲーション（前後シフト）
- 送信元を削除対象としてマークし、メールを一括でゴミ箱へ移動
- 削除時にスター付き・重要マーク付きメールを自動スキップ
- 収集データのJSONキャッシュ（次回起動時の再収集をスキップ）

## 動作環境

- Python 3.10以上
- Gmail APIが有効化されたGoogle Cloudプロジェクト

## インストール

### 開発環境（venv）

```bash
git clone https://github.com/kakehashi-inc/gmail_sweep_cli.git
cd gmail_sweep_cli
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows
pip install -e ".[dev]"
```

### uvxでの実行

```bash
uvx gmail_sweep_cli user@gmail.com
```

## Google Cloud Console 設定手順

### 1. プロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. ページ上部のプロジェクトセレクタをクリック
3. **新しいプロジェクト** をクリック
4. プロジェクト名（例: `gmail_sweep_cli`）を入力し、**作成** をクリック
5. 新しいプロジェクトが選択されていることを確認

### 2. Gmail API の有効化

1. **APIとサービス > ライブラリ** に移動
2. **Gmail API** を検索
3. 検索結果の **Gmail API** をクリック
4. **有効にする** をクリック

### 3. OAuth 同意画面の設定

1. **APIとサービス > OAuth同意画面** に移動
2. ユーザータイプとして **外部** を選択し、**作成** をクリック
3. 必須項目を入力：
   - **アプリ名**: 例 `Gmail Sweep CLI`
   - **ユーザーサポートメール**: 自分のメールアドレス
   - **デベロッパーの連絡先メールアドレス**: 自分のメールアドレス
4. **保存して次へ** をクリック
5. **スコープ** ページで **スコープの追加または削除** をクリックし、以下を追加：
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
6. **保存して次へ** をクリック
7. **テストユーザー** ページで **ユーザーを追加** をクリックし、使用するGmailアドレスを追加
8. **保存して次へ** をクリック

### 4. OAuth クライアント ID の作成

1. **APIとサービス > 認証情報** に移動
2. **認証情報を作成 > OAuthクライアントID** をクリック
3. アプリケーションの種類として **デスクトップアプリ** を選択
4. 名前を入力（例: `Gmail Sweep CLI`）
5. **作成** をクリック
6. **JSONをダウンロード** をクリックして認証情報ファイルをダウンロード
7. ダウンロードしたファイルを `client_secret.json` にリネーム
8. ツール実行ディレクトリの `./credentials/client_secret.json` に配置

### 5. 注意事項

- **テストモードの制限**: テストユーザーは最大100名、リフレッシュトークンの有効期限は7日間
- **本番公開**: より広範なアクセスにはGoogleの審査・検証プロセスが必要

## 使い方

### 認証

最初に認証フローを実行します（ブラウザが開きます）：

```bash
# 開発環境
python -m gmail_sweep_cli --auth user@gmail.com

# インストール済み
gmail_sweep_cli --auth user@gmail.com
```

### 基本的な使い方

```bash
# デフォルト: 過去30日のメールを収集
gmail_sweep_cli user@gmail.com

# 過去60日のメールを収集
gmail_sweep_cli user@gmail.com --days 60

# 期間を指定して収集
gmail_sweep_cli user@gmail.com --start 2025-01-01 --end 2025-01-31

# トークン保存先を変更
gmail_sweep_cli user@gmail.com --token-dir /path/to/tokens/

# 認証情報ファイルのパスを変更
gmail_sweep_cli user@gmail.com --credentials /path/to/client_secret.json
```

### コマンドラインオプション

| オプション | 短縮 | 説明 | デフォルト |
|---|---|---|---|
| `email` | - | 対象Gmailアドレス（位置引数、必須） | - |
| `--auth` | `-a` | OAuth認証フローを実行 | `False` |
| `--days` | `-d` | 収集期間（過去N日） | `30` |
| `--start` | `-s` | 収集開始日（YYYY-MM-DD） | `None` |
| `--end` | `-e` | 収集終了日（YYYY-MM-DD） | `None` |
| `--credentials` | `-c` | `client_secret.json` のパス | `./credentials/client_secret.json` |
| `--token-dir` | `-t` | トークン保存ディレクトリ | `./credentials/` |
| `--cache-dir` | - | 収集データのキャッシュディレクトリ | `./cache/` |

## 操作説明

### メイン画面

メイン画面では、送信元アドレスが件数降順でソートされたページネーション付きテーブルが表示されます。

| 入力 | 操作 | 説明 |
|---|---|---|
| `r` | 再収集 | 現在の期間設定でGmail APIから再度収集 |
| `prev` | 前期間 | 収集期間を1期間分過去にシフト |
| `next` | 次期間 | 収集期間を1期間分未来にシフト |
| `<` | 前ページ | 前の20件を表示 |
| `>` | 次ページ | 次の20件を表示 |
| *数字* | 詳細表示 | 該当番号のアドレスの詳細画面を表示 |
| `l` | マーク一覧 | 削除対象としてマークしたアドレス一覧を表示 |
| `c` | マーククリア | すべてのマークを解除 |
| `all-delete` | 削除実行 | マークしたアドレスのメールをゴミ箱へ移動 |
| `q` | 終了 | プログラムを終了 |

### 詳細画面

選択した送信元アドレスの詳細情報（受信日時、重複なし件名一覧）を表示します。

| 入力 | 操作 | 説明 |
|---|---|---|
| `Enter`（空入力） | 戻る | メイン画面に戻る |
| `mark` | マーク | このアドレスを削除対象としてマーク |

### 削除機能について

- `all-delete` コマンドは、マークしたアドレスから受信した **全期間** のメールをゴミ箱に移動します（現在の表示期間に限りません）。
- **スター付き** および **重要マーク付き** メールは自動的にスキップされます。
- 大文字の `Y` のみが削除を確定します。それ以外の入力はキャンセルとなります。

## VSCode デバッグ設定

プロジェクトルートに `.vscode/launch.json` を作成してください：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Launch CLI",
      "module": "gmail_sweep_cli.main",
      "args": [
        "example@gmail.com"
      ],
      "console": "integratedTerminal",
      "justMyCode": true,
      "cwd": "${workspaceFolder}"
    },
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Launch CLI with Auth",
      "module": "gmail_sweep_cli.main",
      "args": [
        "--auth",
        "example@gmail.com"
      ],
      "console": "integratedTerminal",
      "justMyCode": true,
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

| 名前 | 説明 |
|---|---|
| **Launch CLI** | 対象メールアドレスを指定してCLIを実行（通常モード） |
| **Launch CLI with Auth** | 対象メールアドレスのOAuth認証フローを実行 |

> `example@gmail.com` を実際のGmailアドレスに置き換えてください。

## ライセンス

MIT License。詳細は [LICENSE](LICENSE) を参照してください。
