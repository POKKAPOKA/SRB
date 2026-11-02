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

ターミナルに曲一覧が表示されます。曲番号を選び、プレイヤー名・スコア・MAX KPSを入力してください。送信内容を確認し、`y` を入力すると送信します。`0` を選ぶと、一覧にあるすべての曲へ同じテスト結果を送信します。最大コンボが1以上の場合、MAX KPSには0より大きい数値を入力してください。

通常は実行ごとに新しい端末IDを使い、新しいテスト記録を作ります。`--reuse-device` を付けるとローカルに保存した端末IDを再利用し、曲ごとの既存自己ベストを更新します。

```powershell
python -X utf8 test_submit_score.py --reuse-device
```

`--dry-run` を付けると、送信せずに送信予定の内容だけを表示します。

```powershell
python -X utf8 test_submit_score.py --dry-run
```

## 注意

このツールはランキングデータベースへ記録を送信します。一応作るとSRBに告知しましたが、作成が完了したと報告はしていません。
