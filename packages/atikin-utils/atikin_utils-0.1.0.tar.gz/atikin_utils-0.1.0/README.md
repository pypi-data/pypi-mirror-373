# 🛠️ Atikin-Utils

[![PyPI version](https://img.shields.io/pypi/v/atikin-utils.svg)](https://pypi.org/project/atikin-utils/)
[![Python versions](https://img.shields.io/pypi/pyversions/atikin-utils.svg)](https://pypi.org/project/atikin-utils/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Atikin-Utils** is a lightweight collection of everyday developer utilities —
string formatting shortcuts, friendly datetime helpers, file handling (auto create + backup), `.env` manager, logging, config, network helpers, CLI utilities, security helpers, decorators, and async helpers.

Built by **Atikin Verse** for developers who love speed, simplicity, and productivity 🚀.

---

## ✨ Features

* 🔤 **String Helpers** → snake\_case, camelCase, kebab-case, slugify, truncate, safe\_format
* ⏰ **Date & Time** → now, today\_str, format\_datetime, timestamps, humanize\_timedelta
* 📂 **File Handling** → auto\_create, auto\_backup (with rotation), atomic writes, ensure\_dir
* ⚙️ **Environment Manager** → simple `.env` loader, get/set variables, type casting, persist back to file
* 📝 **Logging** → log\_info, log\_error, log\_warn
* ⚡ **Config Loader** → load JSON/YAML configs with defaults
* 🌐 **Network Helpers** → get\_json
* 💻 **CLI Utilities** → success, error, warn
* 🔒 **Security Helpers** → gen\_token, sha256
* ⏱️ **Decorators** → timeit, retry
* ⚡ **Async Helpers** → run\_async
* ✅ **Zero dependencies** → only Python standard library (except optional: `requests`, `rich`, `pyyaml`)

---

## 📦 Installation

Install via **PyPI**:

```bash
pip install atikin-utils
```

Or install locally for development:

```bash
git clone https://github.com/atikinverse/atikin-utils.git
cd atikin-utils
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux / Mac
source .venv/bin/activate
pip install -e .
```

---

## 🚀 Usage

### 🔤 String Helpers

```python
from atikin_utils import snake_case, camel_case, kebab_case, slugify, safe_format

print(snake_case("Hello World Example"))   # hello_world_example
print(camel_case("hello_world example"))   # HelloWorldExample
print(kebab_case("Hello World_Test"))      # hello-world-test
print(slugify("Hello, World!"))            # hello-world
print(safe_format("Hi {name} {x}", name="Jamshed"))  # Hi Jamshed {x}
```

### ⏰ Date & Time

```python
from atikin_utils import now, today_str, format_datetime, humanize_timedelta
from datetime import timedelta

print(now())                        # current datetime
print(today_str())                  # "2025-09-02"
print(format_datetime(now()))       # "2025-09-02 20:30:45"
print(humanize_timedelta(timedelta(days=2)))  # "2 days"
```

### 📂 File Helpers

```python
from atikin_utils import auto_create, auto_backup

file = auto_create("data.txt", "hello world")
backup = auto_backup("data.txt")
print("Backup created:", backup)
```

### ⚙️ Env Manager

```python
from atikin_utils import Env

env = Env(".env")
env.load()

print(env.get("SECRET_KEY", default="not-set"))
env.set("NEW_KEY", "value", persist=True)
```

### 📝 Logging + Config + Paths

```python
from atikin_utils import log_info, log_error, load_config, ensure_dir_path

log_info("Server started")
log_error("An error occurred")

cfg = load_config("config.json", defaults={"port":8000})
print(cfg)

ensure_dir_path("logs/")
```

### 🌐 Network + CLI + Security

```python
from atikin_utils import get_json, success, gen_token, sha256

data = get_json("https://api.github.com")
success("Fetched GitHub API!")
print(gen_token(16))      # e.g., "aX8bG72kPz9QwLmR"
print(sha256("hello"))    # SHA-256 hash
```

### ⏱️ Decorators + Async Helpers

```python
from atikin_utils import timeit, retry, run_async
import asyncio

@timeit
@retry(tries=3)
def fetch_data():
    print("Fetching data...")
    return 42

print(fetch_data())

async def main():
    result = await run_async(fetch_data)
    print("Async result:", result)

asyncio.run(main())
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
Copyright © 2025 **Atikin Verse**

---

## 🌐 Follow Us

| Platform  | Username    |
| --------- | ----------- |
| Facebook  | atikinverse |
| Instagram | atikinverse |
| LinkedIn  | atikinverse |
| X/Twitter | atikinverse |
| Threads   | atikinverse |
| Pinterest | atikinverse |
| Quora     | atikinverse |
| Reddit    | atikinverse |
| Tumblr    | atikinverse |
| Snapchat  | atikinverse |
| Skype     | atikinverse |
| GitHub    | atikinverse |

---

<div align="center">  
Made with ❤️ by the **Atikin Data** 🚀  
</div>

