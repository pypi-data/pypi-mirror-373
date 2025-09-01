# h2j

[![Tests](https://github.com/SimBeSim/h2j/actions/workflows/tests.yml/badge.svg)](https://github.com/SimBeSim/h2j/actions)

Lightweight HTML → JSON converter for Python, forked from `html-to-json` but with a cleaner and more compact style.

## ✨ Features
- Attributes stored as **`_attrs`**
- Text values stored as **`_val`** (single) or **`_vals`** (multiple)
- Class attributes normalized:  
  `"a b c"` → `"a.b.c"`
- Preserves spacing in text nodes
- 100% passing tests ✅

## 📦 Install
For now, install from GitHub:

```
pip install git+https://github.com/SimBeSim/h2j.git
```
(PyPI release coming soon!)

## 🚀 Usage
```
import h2j

html = '<div class="a b c" id="x">Hello <b>World</b></div>'
out = h2j.convert(html, capture_element_attributes=True)
print(out)
```
## Output:
```
{
  'div': [
    {
      '_attrs': {'class': 'a.b.c', 'id': 'x'},
      '_val': 'Hello ',
      'b': [{'_val': 'World'}]
    }
  ]
}

```

## 🧪 Tests

Run locally with:
```
pytest
```
## 📜 License

MIT License © 2025 Maxim Sergeyevich Shubin and Chatty Shubin



