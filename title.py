#!/usr/bin/env python3
"""
setWeeklyDefault.py

詢問使用者「本週進度」是系列幾、第幾題（以及可選的本週主題文字），
並將這個篇題同步設為：
  1. config.json 的預設篇目（"textFileUrl"，並置頂於 "chapters"）
  2. index.html 的：
     - <noscript> 內的 meta refresh 網址
     - 工具列上方的 #toolbarTitle 顯示文字（"牧養材料 本週進度 系列X 第Y題 主題文字"）

前提：該篇題必須已經存在於 config.json 的 "chapters" 裡
（也就是已經用 oneClickDump.py / batchDumpAll.py 下載轉檔過），
本程式只負責「切換預設」，不會下載新內容。

用法：
    python3 setWeeklyDefault.py
    python3 setWeeklyDefault.py --series 02 --chapter 07 --topic 生命的話
"""

import argparse
import json
import re
import sys
from pathlib import Path

CHINESE_DIGITS = "零一二三四五六七八九"


def toChineseNumeral(num: int) -> str:
    if num < 10:
        return CHINESE_DIGITS[num]
    if num < 20:
        ones = num - 10
        return "十" + (CHINESE_DIGITS[ones] if ones else "")
    tens, ones = divmod(num, 10)
    result = CHINESE_DIGITS[tens] + "十"
    if ones:
        result += CHINESE_DIGITS[ones]
    return result


def loadConfig(configPath: Path) -> dict:
    return json.loads(configPath.read_text(encoding="utf-8"))


def saveConfig(configPath: Path, config: dict) -> None:
    configPath.write_text(
        json.dumps(config, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )


def setDefaultChapter(config: dict, chapterTitle: str) -> str:
    """把指定篇題置頂並設為預設，回傳該篇的網址。"""
    chapters = config.get("chapters", {})

    if chapterTitle not in chapters:
        sys.exit(f"config.json 裡找不到「{chapterTitle}」，請先確認已下載並加入該篇。")

    chapterUrl = chapters.pop(chapterTitle)
    reorderedChapters = {chapterTitle: chapterUrl, **chapters}

    config["chapters"] = reorderedChapters
    config["textFileUrl"] = chapterUrl
    return chapterUrl


def updateIndexHtml(indexPath: Path, chapterUrl: str, labelText: str) -> None:
    html = indexPath.read_text(encoding="utf-8")

    html, refreshCount = re.subn(
        r'(<meta http-equiv="refresh" content="0; url=)[^"]+(")',
        lambda m: f"{m.group(1)}{chapterUrl}{m.group(2)}",
        html,
        count=1,
    )
    if refreshCount == 0:
        sys.exit("找不到 <noscript> 內的 meta refresh 標籤，請確認 index.html 內容。")

    html, titleCount = re.subn(
        r'(<span id="toolbarTitle">)[^<]*(</span>)',
        lambda m: f"{m.group(1)}{labelText}{m.group(2)}",
        html,
        count=1,
    )
    if titleCount == 0:
        sys.exit("找不到 #toolbarTitle 標籤，請確認 index.html 內容。")

    indexPath.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="更新本週進度預設篇目")
    parser.add_argument("--series", help="系列編號，例如 02")
    parser.add_argument("--chapter", help="章節編號，例如 07")
    parser.add_argument("--topic", default=None, help="本週主題文字，例如「生命的話」（可留白）")
    parser.add_argument("--config", default="config.json", help="config.json 路徑")
    parser.add_argument("--index", default="index.html", help="index.html 路徑")
    args = parser.parse_args()

    seriesNum = args.series or input("請輸入本週進度的系列編號（例如 02）：").strip()
    chapterNum = args.chapter or input("請輸入本週進度的章節編號（例如 07）：").strip()
    topic = args.topic
    if topic is None:
        topic = input("請輸入本週主題文字（可留白直接按 Enter）：").strip()

    configPath = Path(args.config)
    indexPath = Path(args.index)

    if not configPath.exists():
        sys.exit(f"找不到 config.json：{configPath}")
    if not indexPath.exists():
        sys.exit(f"找不到 index.html：{indexPath}")

    chapterTitle = f"系列{toChineseNumeral(int(seriesNum))} 第{toChineseNumeral(int(chapterNum))}題"

    config = loadConfig(configPath)
    chapterUrl = setDefaultChapter(config, chapterTitle)
    saveConfig(configPath, config)

    labelText = f"牧養材料 本週進度 {chapterTitle}" + (f" {topic}" if topic else "")
    updateIndexHtml(indexPath, chapterUrl, labelText)

    print(f"已將預設篇目切換為「{chapterTitle}」")
    print(f"config.json 的 textFileUrl -> {chapterUrl}")
    print(f"index.html 的顯示文字 -> {labelText}")


if __name__ == "__main__":
    main()

