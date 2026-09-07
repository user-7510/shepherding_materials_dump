#!/bin/bash
set -euo pipefail

read -p "請輸入系列編號（例如 01）：" seriesNum
read -p "請輸入章節編號（例如 12）：" chapterNum

baseName="A${seriesNum}_${chapterNum}"
pdfFile="${baseName}.pdf"
htmlFile="${baseName}-html.html"
rawTxtFile="${baseName}.txt"
finalTxtFile="${baseName}s.txt"
pdfUrl="https://www.churchintaichung.org/shepherding_materials/series${seriesNum}/${baseName}.pdf"

curl -fO "$pdfUrl"
pdftohtml -s "$pdfFile"
w3m -dump "$htmlFile" > "$rawTxtFile"

python3 - "$rawTxtFile" > "$finalTxtFile" <<'PYEOF'
import re
import sys

fileName = sys.argv[1]

with open(fileName, 'r', encoding='utf-8') as f:
    rawLines = f.readlines()

cleanedLines = [re.sub(r'background\s*image', '', line, flags=re.IGNORECASE) for line in rawLines]

# 移除開頭因清除 background image 而變成空白的行
while cleanedLines and not cleanedLines[0].strip():
    cleanedLines.pop(0)

resText = f'{cleanedLines.pop(0)}\n\n{cleanedLines.pop(0)}\n\n'

comSet = set('、，。；：（）『』')
numSet = set('123456789')
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

print(finalText)
PYEOF

rm -f "$pdfFile" "$htmlFile" "$rawTxtFile" "${baseName}"*.png

echo "完成：${finalTxtFile}"
