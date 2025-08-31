# secbrowser

A simple interface to interact with SEC filings. Built as a debugging tool for [datamule](https://github.com/john-friedman/datamule-python).

## Installation
```
pip install secbrowser
```

# Usage
```
from secbrowser.server import secbrowser

secbrowser()
```

## Why this was made

- I needed a visual interface to improve doc2dict.
- I needed a visual interface to explore nlp.
- I wanted to stress test datamule's functionality. This is an opportunity to improve architecture / add useful stuff.

## Why it may be useful for you
- Easier UI
- You like visualizations


## Features TBD
- Making this visual pleasing.
- chatbot integration.
- notes explaining how things work.
- sheet integration.
- option to set api key, rather than via environment.

## Improvements to be made to datamule
- Change how submissions load from list based to hash. O(1).
- Change how to select type and cik.
- make document.text tables nicer
- make tables failsoft.
- fix how sentiment dictionaries are accessed. right now it needs the dict, but doesnt specify it when called.
- document should have ability to rewrite links to point to other documents, e.g. in case of 10-Ks with graphics