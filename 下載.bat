@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"
title YouTube 音樂下載器

:menu
cls
echo.
echo   ============================================
echo      YouTube 音樂下載器
echo   ============================================
echo.
echo     [1] 下載音樂 ^(貼網址^)
echo     [2] 用歌名搜尋
echo     [3] 下載影片 ^(貼網址^)
echo     [4] 同步追蹤的播放清單
echo     [5] 看下載過什麼
echo.
echo     [0] 離開
echo.
set "choice="
set /p "choice=  請選擇 (直接按 Enter = 1): "
if not defined choice set "choice=1"

if "%choice%"=="1" goto audio
if "%choice%"=="2" goto search
if "%choice%"=="3" goto video
if "%choice%"=="4" goto sync
if "%choice%"=="5" goto history
if "%choice%"=="0" exit /b 0
goto menu

:audio
echo.
set "url="
set /p "url=  貼上網址後按 Enter: "
if not defined url goto menu
python -m ytmusic dl "!url!"
goto done

:search
echo.
set "kw="
set /p "kw=  要找什麼歌? "
if not defined kw goto menu
python -m ytmusic search !kw!
goto done

:video
echo.
set "url="
set /p "url=  貼上網址後按 Enter: "
if not defined url goto menu
echo.
echo    畫質: [1] 720p  [2] 1080p  [3] 最高
set "q="
set /p "q=  請選擇 (直接按 Enter = 720p): "
if not defined q set "q=1"
if "%q%"=="1" set "res=720"
if "%q%"=="2" set "res=1080"
if "%q%"=="3" set "res=best"
python -m ytmusic dl "!url!" --video !res!
goto done

:sync
echo.
python -m ytmusic sync
goto done

:history
echo.
python -m ytmusic history list
goto done

:done
echo.
if errorlevel 1 (
  echo   [!] 沒有全部成功，上面有錯誤訊息。
) else (
  echo   [OK] 完成。
)
echo.
pause
goto menu
