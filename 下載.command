#!/usr/bin/env bash
# macOS：在 Finder 裡雙擊即可執行（第一次要先 chmod +x 下載.command）
cd "$(dirname "$0")" || exit 1

PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python

menu() {
  clear
  cat <<'EOF'

  ============================================
     YouTube 音樂下載器
  ============================================

    [1] 下載音樂（貼網址）
    [2] 用歌名搜尋
    [3] 下載影片（貼網址）
    [4] 同步追蹤的播放清單
    [5] 看下載過什麼

    [0] 離開

EOF
}

while true; do
  menu
  read -r -p "  請選擇（直接按 Enter = 1）: " choice
  choice=${choice:-1}
  echo

  case "$choice" in
    1)
      read -r -p "  貼上網址後按 Enter: " url
      [ -n "$url" ] && "$PY" -m ytmusic dl "$url"
      ;;
    2)
      read -r -p "  要找什麼歌？ " kw
      [ -n "$kw" ] && "$PY" -m ytmusic search $kw
      ;;
    3)
      read -r -p "  貼上網址後按 Enter: " url
      [ -z "$url" ] && continue
      echo
      echo "   畫質：[1] 720p  [2] 1080p  [3] 最高"
      read -r -p "  請選擇（直接按 Enter = 720p）: " q
      case "${q:-1}" in
        2) res=1080 ;;
        3) res=best ;;
        *) res=720 ;;
      esac
      "$PY" -m ytmusic dl "$url" --video "$res"
      ;;
    4) "$PY" -m ytmusic sync ;;
    5) "$PY" -m ytmusic history list ;;
    0) exit 0 ;;
    *) continue ;;
  esac

  echo
  read -r -p "  按 Enter 回到選單…" _
done
