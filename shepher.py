#將已轉換為TXT的牧養材料檔案放在同個資料夾中。也可填入預設值於下方。
import sys
try:name=sys.argv[1]
except:pass
with open(input().strip()or name,'r')as f:raw=f.readlines()
res=f'{raw.pop(0)}\n\n{raw.pop(0)}\n\n'
coms=['、','，','。','；','：','（','）','『','』'];nums=['1','2','3','4','5','6','7','8','9']
for line in raw:
    #if not line.startwith("    "):res=res+line.strip()
    #elif line.startwith("    ")or len(line)<18:res=res+"\n"+line.strip()
    if not line.strip():pass
    elif "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"in line:res=res#+"\n"
    #elif not line.startswith("    "):res=res+line.strip()
    elif line.startswith("    "):res=res+"\n\n"+line.rstrip()
    elif line.strip()in nums:pass
    elif not any(com in coms for com in line):res=res+"\n\n\n"+line.rstrip()+"\n\n"
    elif not line.startswith("    "):res=res+line.strip()
tmp=res.split("\n")
res=""
for n in range(len(tmp)):
    if not tmp[n]:
        try:
            if tmp[n+1]:res=res+"\n\n"
        except:pass
    else:res=res+tmp[n]
print(res)
