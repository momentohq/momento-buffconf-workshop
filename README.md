# Momento Buffconf Workshop

Hands-on materials for the Momento workshop at Buffconf. The repo is a complete, reproducible sandbox: you'll install the deps, run the interactive notebooks, and hack on the code that powers the demos.

---

## 🧰 Pre-requisites

- Python 3.11+

## 🚀 Quick‑start (2-3 lines)

### 🏗️ Set up the dev environment

```bash
# 1️⃣  Install Poetry (one‑time)
make install-poetry           # ⇢ https://python-poetry.org

# 2️⃣  Install the project & all dev tools
make install
```

> **Tip:** prefer VS Code? The `.venv` created by Poetry is auto‑picked up by the Python extension.

Now load the notebooks either in VS Code or Jupyter Lab:

### Option 1: 🖥️ Run the notebooks in VS Code

Prefer a local IDE over the browser? VS Code's built‑in Jupyter support will run every notebook exactly as in Colab.

Install the extensions → Python and Jupyter (both from Microsoft).

File → Open Folder... and point VS Code at the repo root.

Run `make install` once. VS Code should auto‑detect the Poetry venv. If it doesn’t, click the interpreter picker in the bottom‑left and select .venv.

Open `notebooks/01-intro-to-representation-and-search.ipynb`, hit `Run All`, and you're off.

### Option 2: 🖥️ Run the notebooks in Jupyter Lab

````bash
# 3️⃣  Fire up Jupyter and open the first notebook
poetry run jupyter lab notebooks/01-intro-to-representation-and-search.ipynb
```

---

## 🛠️ Makefile cheat‑sheet

| Target            | What it does                                               |
| ----------------- | ---------------------------------------------------------- |
| `make all`        | Runs **format → lint → tests** (same as `make precommit`)  |
| `make format-fix` | Auto‑formats with **ruff**                                 |
| `make lint-check` | Ruff + mypy in check‑only mode                             |
| `make test`       | Executes all `pytest` suites                               |
| `make clean`      | Wipes build artefacts, `__pycache__`, MyPy & pytest caches |
| `make help`       | Pretty‑prints this table                                   |

---

## 🧪 Running the notebooks

The key material lives in `notebooks/`. They rely only on the packages declared in `pyproject.toml`, so once `make install` succeeds you can:

```bash
poetry run jupyter lab
````

then navigate to any notebook.

---

## 🗂️ Project structure

```
📦momento-buffconf-workshop
 ┣ 📂data                          ← assets produced or consumed by notebooks
 ┣ 📂images                        ← images used by notebooks
 ┣ 📂momento_buffconf_workshop     ← application code & helpers used in notebooks
 ┣ 📂notebooks                     ← interactive demos
 ┣ 📂tests                         ← unit tests for the helper code
 ┣ 📜Makefile                      ← dev workflow commands
 ┣ 📜README.md                     ← (you are here)
 ┣ 📜poetry.lock                   ← pinned dependency versions
 ┗ 📜pyproject.toml                ← project + dev‑tool config
```

---
