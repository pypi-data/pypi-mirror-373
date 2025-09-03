# 🛠️ Teams Alerter

A lightweight Python module to send alerts to Microsoft Teams via Google Cloud Pub/Sub.

---

## 📦 How to Build the Module

Make sure you have the `build` package installed:

```bash
python -m pip install --upgrade build
python -m build
```

This will generate `.whl` and `.tar.gz` files inside the `dist/` folder.

---

## 🔧 Install the Module Locally

From your project directory (with your virtual environment activated):

```bash
pip install ../teams-alerter/dist/teams_alerter-0.1.0-py3-none-any.whl
```

> Adjust the path according to your actual `.whl` file location.

---

## 🚀 How to Use the Module

```python
from teams_alerter import TeamsAlerter

# Example: error handling
try:
    raise RuntimeError("Test error")
except Exception as error:
    TeamsAlerter.handle_error(error, utils)
```

---

## 📤 How to Publish to PyPI

1. Install `twine`:

```bash
pip install twine
```

2. Upload the distribution files:

```bash
twine upload dist/*
```

> A PyPI account is required: https://pypi.org/account/register/

---

## 📁 Recommended Module Structure

```
teams-alerter/
├── teams_alerter/
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── pyproject.toml
├── README.md
└── dist/
```

---

## ✅ Requirements

- Python ≥ 3.8
- Google Cloud SDK if you are using Pub/Sub
- Dependencies:
  - `google-cloud-logging`
  - `google-cloud-pubsub`

These dependencies are already listed in your `pyproject.toml`.

---

LIB URL:
https://pypi.org/project/teams-alerter/0.1.0/

How to build and publish ?
pip install build twine
python -m build
twine upload dist/*
dans requirements.txt, ajouter teams-alerter==0.1.0
dans le code: from teams_alerter import TeamsAlerter
