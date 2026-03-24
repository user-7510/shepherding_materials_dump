## Dump from `https://www.churchintaichung.org/shepherding_materials/seriesxx/Axx_xx.pdf` .
### Usege(Linux only... or you can try WSL):
```curl -O https://www.churchintaichung.org/shepherding_materials/seriesxx/Axx_xx.pdf
pdftohtml Axx_xx.pdf Axx_xx.html
w3m Axx_xxs.html > Axx_xx.txt
python/python3 shepher.py Axx_xx.txt > Axx_xxs.html
```
### The `Axx_xxs.html` is the final file.
