import argparse
import json
from pathlib import Path
import re
import urllib.error
import urllib.request
import uuid

playername = "SGLに来てね!!!"
score = "1010000"
SITE_URL = "https://trill-skill-checker.vercel.app"

def load_rpc_settings() -> tuple[str, str]:
    """公開サイトのJavaScriptからRPC URLと公開anon keyを取得する。"""
    request = urllib.request.Request(
        f"{SITE_URL}/",
        headers={"User-Agent": "TAiKOTYPiNG-test-client/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8")

    script_paths = re.findall(r'<script[^>]+src="([^"]+\.js)"', html)
    for script_path in script_paths:
        script_url = script_path if script_path.startswith("http") else f"{SITE_URL}{script_path}"
        script_request = urllib.request.Request(
            script_url, headers={"User-Agent": "TAiKOTYPiNG-test-client/1.0"}
        )
        with urllib.request.urlopen(script_request, timeout=20) as response:
            javascript = response.read().decode("utf-8")
        match = re.search(r'var\s+\$a\s*=\s*Za\(`([^`]+)`,`([^`]+)`\)', javascript)
        if match:
            supabase_url, anon_key = match.groups()
            return f"{supabase_url}/rest/v1/rpc/submit_ranking_score", anon_key

    raise RuntimeError(
        "サイトの公開JavaScriptからランキングRPC設定を取得できませんでした。"
    )


def submit_score(url: str, apikey: str, payload: dict) -> tuple[int, object]:
    """Supabase RPC エンドポイントへ POST リクエストを送信する"""
    body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    headers = {
        "apikey": apikey,
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json",
    }

    request = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            resp_text = response.read().decode("utf-8")
            return response.status, json.loads(resp_text) if resp_text else None
    except urllib.error.HTTPError as e:
        err_text = e.read().decode("utf-8", errors="replace")
        try:
            err_body = json.loads(err_text)
        except json.JSONDecodeError:
            err_body = err_text
        return e.code, err_body


def choose_songs() -> list[tuple[dict, int]]:
    request = urllib.request.Request(
        f"{SITE_URL}/songs/index.json",
        headers={"User-Agent": "TAiKOTYPiNG-test-client/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        songs = json.loads(response.read().decode("utf-8"))

    print("=== 曲一覧 ===")
    print(f" 0. すべて ({len(songs)}曲)")
    for index, song in enumerate(songs, start=1):
        print(
            f"{index:>2}. ☆{song.get('difficulty', '?')} "
            f"{song.get('title', song.get('id', '不明'))} [{song.get('id', '?')}]"
        )

    while True:
        choice = input(f"曲番号を選択してください [0-{len(songs)}]: ").strip()
        try:
            selected = int(choice)
        except ValueError:
            print("番号を入力してください。")
            continue
        if 0 <= selected <= len(songs):
            selected_songs = songs if selected == 0 else [songs[selected - 1]]
            chosen = []
            for song in selected_songs:
                score_path = song.get("scorePath", "")
                if not score_path:
                    raise SystemExit(f"{song.get('title', song.get('id'))}: 譜面URLがありません。")
                chart_url = (
                    score_path
                    if score_path.startswith("http")
                    else f"{SITE_URL}/{score_path.removeprefix('./')}"
                )
                chart_request = urllib.request.Request(
                    chart_url, headers={"User-Agent": "TAiKOTYPiNG-test-client/1.0"}
                )
                with urllib.request.urlopen(chart_request, timeout=20) as response:
                    chart = json.loads(response.read().decode("utf-8"))
                notes = chart.get("notes", [])
                if not notes:
                    raise SystemExit(f"{song.get('title', song.get('id'))}: 譜面にノーツがありません。")
                chosen.append((song, int(song.get("notesCount") or len(notes))))
            return chosen
        print("一覧にある番号を入力してください。")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TAiKOTYPiNG のテストランキング送信スクリプト"
    )
    parser.add_argument(
        "--reuse-device",
        action="store_true",
        help="同じ端末IDを再利用して曲ごとの既存自己ベストを更新する",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際には通信せず、送信予定の内容だけを表示する",
    )
    args = parser.parse_args()

    url, apikey = load_rpc_settings()
    payload = {}
    selections = choose_songs()

    entered_name = input(f"プレイヤー名 [{playername}]: ").strip()
    entered_score = input(f"スコア [{score}]: ").strip()
    send_name = entered_name or playername
    send_score = int(entered_score or score)

    # Default to a new test entry. Reuse a stable local ID only when requested.
    device_file = Path(__file__).with_name(".device_id")
    if args.reuse_device:
        if device_file.exists():
            device_id = device_file.read_text(encoding="utf-8").strip()
        else:
            device_id = str(uuid.uuid4())
            device_file.write_text(device_id, encoding="utf-8")
    else:
        device_id = str(uuid.uuid4())
    submissions = []
    for song, note_count in selections:
        song_payload = dict(payload)
        song_payload.update(
            {
                "p_song_id": song["id"],
                "p_device_id": device_id,
                "p_player_name": send_name,
                "p_score": send_score,
                "p_max_combo": note_count,
                "p_max_kps": 0,
                "p_perfect_count": note_count,
                "p_good_count": 0,
                "p_miss_count": 0,
            }
        )
        submissions.append((song, song_payload))

    print(f"\n送信対象: {len(submissions)}曲")
    print("=== 送信先 URL ===")
    print(url)
    print("\n=== 送信ペイロード (JSON) ===")
    for song, song_payload in submissions:
        print(f"\n{song.get('title', song['id'])} (p_song_id: {song_payload['p_song_id']})")
        print(json.dumps(song_payload, indent=2, ensure_ascii=False))

    if args.dry_run:
        print("\n[dry-run] 送信をスキップしました。")
        return

    if input("\nこの内容を送信しますか？ [y/N]: ").strip().lower() != "y":
        print("送信をキャンセルしました。")
        return

    for index, (song, song_payload) in enumerate(submissions, start=1):
        print(f"\n[{index}/{len(submissions)}] {song.get('title', song['id'])} を送信中...")
        status, resp_data = submit_score(url, apikey, song_payload)
        print(f"=== レスポンス (HTTP {status}) ===")
        print(json.dumps(resp_data, indent=2, ensure_ascii=False))

        if isinstance(resp_data, dict):
            print(f"曲ID (song_id)           : {resp_data.get('song_id')}")
            print(f"レコードID (id / UUID)   : {resp_data.get('id')}")
            print(f"送信曲IDとの一致         : {resp_data.get('song_id') == song_payload['p_song_id']}")
            print(f"登録プレイヤー名         : {resp_data.get('player_name')}")
            print(f"登録スコア               : {resp_data.get('score')}")
            print(f"自己ベスト行を更新したか : {resp_data.get('updated')}")
            print(f"自己ベストになったか     : {resp_data.get('is_new_best')}")
            if resp_data.get("score") != song_payload.get("p_score"):
                print("注意: 同じ端末ID・曲IDの既存自己ベストが維持されました。")


if __name__ == "__main__":
    main()

