# TAiKOTYPiNG ランキング送信テストツール

TAiKOTYPiNG のランキング送信をテストするためのPythonスクリプトです。Python標準ライブラリだけで動作し、実行時にサイトから曲一覧と公開RPC設定を取得します。

## 動作環境

- Python 3.9以降
- インターネット接続

## 使い方

PowerShellでこのフォルダーを開き、次を実行します。

```powershell
python -X utf8 test_submit_score.py
```

ターミナルに曲一覧が表示されます。曲番号を選び、プレイヤー名とスコアを入力してください。送信内容を確認し、`y` を入力すると送信します。`0` を選ぶと、一覧にあるすべての曲へ同じテスト結果を送信します。

通常は実行ごとに新しい端末IDを使い、新しいテスト記録を作ります。`--reuse-device` を付けるとローカルに保存した端末IDを再利用し、曲ごとの既存自己ベストを更新します。

```powershell
python -X utf8 test_submit_score.py --reuse-device
```

`--dry-run` を付けると、送信せずに送信予定の内容だけを表示します。

```powershell
python -X utf8 test_submit_score.py --dry-run
```

## 注意

このツールはランキングデータベースへ記録を送信します。自分が所有またはテストを許可されている環境だけで使用してください。公開ランキングや本番環境にはテストデータを送信しないでください。
