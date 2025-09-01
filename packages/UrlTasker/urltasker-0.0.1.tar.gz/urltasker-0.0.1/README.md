![UrlTasker Logo](https://mauricelambert.github.io/info/python/code/UrlTasker_small.png "UrlTasker logo")

# UrlTasker

## Description

UrlTasker is a flexible Python framework for defining, configuring, and executing asynchronous actions using simple URL. Designed for modern async workflows, it allows developers to expose and trigger actions (HTTP, processus, ect...) configured by simple URL.

## Requirements

This package require:

 - python3
 - python3 Standard Library
 - PegParser

## Installation

### Pip

```bash
python3 -m pip install UrlTasker
```

### Git

```bash
git clone "https://github.com/mauricelambert/UrlTasker.git"
cd "UrlTasker"
python3 -m pip install .
```

### Wget

```bash
wget https://github.com/mauricelambert/UrlTasker/archive/refs/heads/main.zip
unzip main.zip
cd UrlTasker-main
python3 -m pip install .
```

### cURL

```bash
curl -O https://github.com/mauricelambert/UrlTasker/archive/refs/heads/main.zip
unzip main.zip
cd UrlTasker-main
python3 -m pip install .
```

## Usages

### Python script

```python
from UrlTasker import *

run(run_tasks(
    "http://127.0.0.1:8000/",
    "http://127.0.0.1:8000/1",
    "http://127.0.0.1:8000/2",
    "http+POST://test:test@127.0.0.1:8000/2;Filename=toto123?whynot#mydata",
    "script:test.py;test=test&test2=test?test=test#mydata",
    "https+GET+insecure://31.172.239.74/",
    "webscripts://127.0.0.1:8000/show_license.py?codeheader",
    "webscripts://127.0.0.1:8000/test_config.py?select=test&password=test&password=test&--test-date=2025-07-18&test_input=trololo&test_number=45#select%0aarguments%0a",
))

run(get_task("script:test.py;test=test&test2=test?test=test#mydata").run())
```

## Links

 - [Pypi](https://pypi.org/project/UrlTasker)
 - [Github](https://github.com/mauricelambert/UrlTasker)
 - [Documentation](https://mauricelambert.github.io/info/python/code/UrlTasker.html)

## License

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).
