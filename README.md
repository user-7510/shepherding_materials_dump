## Dump from `https://www.churchintaichung.org/shepherding_materials/seriesxx/Axx_xx.pdf` .
### Usage(Linux only... or you can try WSL):
```sh
export series = "01"
export chapter = "12"
curl -O https://www.churchintaichung.org/shepherding_materials/seriesxx/A${series}_${chapter}.pdf
pdftohtml A${series}_${chapter}.pdf
w3m A${series}_${chapter}s.html > A${series}_${chapter}.txt
python3 shepher.py A${series}_${chapter}.txt > A${series}_${chapter}s.txt
```
### The `A${series}_${chapter}.pdf` is the final file.

- You need to install `python/python3`, `pdftohtml in package poppler`, `w3m` first to run above code.

### Thanks to Church in Taichung for providing the original archives.
- `shepher.py` was written by H.L.2026
