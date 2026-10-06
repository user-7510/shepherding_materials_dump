#!/usr/bin/env python3
"""
batchDumpAll.py

一次下載、轉換「6 個系列、每系列 16 篇」的牧養材料，並輸出：
  1. ./data/A{系列2碼}_{章節2碼}s.txt（例如 A03_09s.txt）
  2. 一份全新、完整的 config.json（含所有成功下載的篇目）

排序規則：新產生的 config.json 以「系列由大到小、同系列內章節由大到小」排列，
最上面（也是 textFileUrl 預設值）為系列/章節數字最大的那一篇。

注意：
  - 來源網站不一定每個系列都恰好有 16 篇，遇到 404 或轉檔失敗會印出警告並跳過，
    不會中斷整個批次；最終 config.json 只會收錄「真正下載成功」的篇目。
  - 因為需要對外連線抓取 PDF，本程式必須在你自己有網路的環境（本機、伺服器、
    GitHub Actions 等）執行，無法在這裡（雲端沙盒）直接跑出真正結果。

用法：
    python3 batchDumpAll.py
    python3 batchDumpAll.py --series-count 6 --chapters-per-series 16
    python3 batchDumpAll.py --delay 1.0        # 每篇下載間隔秒數，避免對來源網站太密集
    python3 batchDumpAll.py --push             # 全部完成後自動 git add/commit/push
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/user-7510/shepherding_materials_dump/refs/heads/main"
PDF_URL_TEMPLATE = "https://www.churchintaichung.org/shepherding_materials/series{seriesNum}/{baseName}.pdf"

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


def checkRequiredTools() -> None:
    missing = [tool for tool in ("curl", "pdftohtml", "w3m") if shutil.which(tool) is None]
    if missing:
        sys.exit(f"缺少必要工具：{', '.join(missing)}，請先安裝後再執行。")


def cleanDumpedText(rawTxtFile: Path) -> str:
    rawLines = rawTxtFile.read_text(encoding="utf-8").splitlines(keepends=True)

    cleanedLines = [re.sub(r"background\s*image", "", line, flags=re.IGNORECASE) for line in rawLines]

    while cleanedLines and not cleanedLines[0].strip():
        cleanedLines.pop(0)

    resText = f"{cleanedLines.pop(0)}\n\n{cleanedLines.pop(0)}\n\n"

    comSet = set("、，。；：（）『』")
    numSet = set("123456789")
    divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    for line in cleanedLines:
        strippedLine = line.strip()
        if not strippedLine:
            continue
        if divider in line:
            continue
        if line.startswith("    "):
            resText += "\n\n" + line.rstrip()
        elif strippedLine in numSet:
            continue
        elif not any(ch in comSet for ch in line):
            resText += "\n\n\n" + line.rstrip() + "\n\n"
        else:
            resText += strippedLine

    paragraphs = resText.split("\n")
    finalText = ""
    for idx, para in enumerate(paragraphs):
        if not para:
            if idx + 1 < len(paragraphs) and paragraphs[idx + 1]:
                finalText += "\n\n"
        else:
            finalText += para

    return finalText


def downloadAndConvertOne(seriesNum: str, chapterNum: str, dataDir: Path) -> Path | None:
    """下載並轉檔單篇；失敗回傳 None 並印出警告，不中斷批次。"""
    baseName = f"A{seriesNum}_{chapterNum}"
    pdfFile = Path(f"{baseName}.pdf")
    htmlFile = Path(f"{baseName}-html.html")
    rawTxtFile = Path(f"{baseName}.txt")
    finalTxtFile = Path(f"{baseName}s.txt")
    pdfUrl = PDF_URL_TEMPLATE.format(seriesNum=seriesNum, baseName=baseName)

    try:
        subprocess.run(
            ["curl", "-fsSO", pdfUrl],
            check=True,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ["pdftohtml", "-s", str(pdfFile)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        with rawTxtFile.open("w", encoding="utf-8") as outFile:
            subprocess.run(
                ["w3m", "-dump", str(htmlFile)],
                stdout=outFile,
                check=True,
                stderr=subprocess.PIPE,
            )

        finalText = cleanDumpedText(rawTxtFile)
        finalTxtFile.write_text(finalText, encoding="utf-8")

        dataDir.mkdir(parents=True, exist_ok=True)
        destPath = dataDir / finalTxtFile.name
        shutil.move(str(finalTxtFile), destPath)
        print(f"成功：{baseName}")
        return destPath
    except subprocess.CalledProcessError:
        print(f"跳過：{baseName}（找不到檔案或轉檔失敗）")
        return None
    finally:
        for tempFile in [pdfFile, htmlFile, rawTxtFile]:
            tempFile.unlink(missing_ok=True)
        for pngFile in Path(".").glob(f"{baseName}*.png"):
            pngFile.unlink(missing_ok=True)


def gitPush(repoDir: Path) -> None:
    subprocess.run(["git", "-C", str(repoDir), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(repoDir), "commit", "-m", "批次新增全系列篇目"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repoDir), "push"], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="批次下載全系列並產生完整 config.json")
    parser.add_argument("--series-count", type=int, default=6, help="系列總數，預設 6")
    parser.add_argument("--chapters-per-series", type=int, default=16, help="每系列篇數，預設 16")
    parser.add_argument("--config", default="config.json", help="輸出的 config.json 路徑")
    parser.add_argument("--data-dir", default="./data", help="輸出文字檔的資料夾")
    parser.add_argument("--delay", type=float, default=0.5, help="每篇下載間隔秒數")
    parser.add_argument("--push", action="store_true", help="完成後自動 git add/commit/push")
    args = parser.parse_args()

    checkRequiredTools()

    dataDir = Path(args.data_dir)
    configPath = Path(args.config)

    successes: list[tuple[int, int, Path]] = []

    for seriesInt in range(1, args.series_count + 1):
        for chapterInt in range(1, args.chapters_per_series + 1):
            seriesNum = f"{seriesInt:02d}"
            chapterNum = f"{chapterInt:02d}"
            destPath = downloadAndConvertOne(seriesNum, chapterNum, dataDir)
            if destPath is not None:
                successes.append((seriesInt, chapterInt, destPath))
            if args.delay:
                time.sleep(args.delay)

    if not successes:
        sys.exit("沒有任何篇目下載成功，未產生 config.json。")

    # 系列由大到小、章節由大到小排序，最新的排最上面
    successes.sort(key=lambda item: (item[0], item[1]), reverse=True)

    chapters = {}
    for seriesInt, chapterInt, destPath in successes:
        title = f"系列{toChineseNumeral(seriesInt)} 第{toChineseNumeral(chapterInt)}題"
        url = f"{GITHUB_RAW_BASE}/data/{destPath.name}"
        chapters[title] = url

    config = {
        "textFileUrl": next(iter(chapters.values())),
        "chapters": chapters,
    }

    configPath.write_text(
        json.dumps(config, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )

    print(f"\n共成功 {len(successes)} 篇，已寫入 {configPath}")

    if args.push:
        gitPush(configPath.parent)
        print("已完成 git commit 與 push")


if __name__ == "__main__":
    main()

