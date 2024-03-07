# wkpdia
Wikipedia downloader and parser in Python

## Install

```bash
pip install wkpdia
```

## Usage

```bash
from wkpdia import wkpdia_get

title = "R._Daneel_Olivaw"
item = wkpdia_get(title)
print(item["path"])
print(item["str"])
```
