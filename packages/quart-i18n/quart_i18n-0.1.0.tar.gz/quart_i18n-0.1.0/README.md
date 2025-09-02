
# Quart i18n

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`quart-i18n` is a simple and easy-to-use **internationalization (i18n) extension** for [Quart](https://pgjones.gitlab.io/quart/) web applications. It allows you to manage multilingual content and inject localized strings directly into templates.

---

## Key Features

- Dynamic language handling
- JSON-based localization files
- Safe string formatting (missing keys do not raise errors)
- Async-compatible `render_template` wrapper
- Easy integration with Quart applications
- Multiple language support via a simple list configuration

---

## Installation

```bash
pip install quart-i18n
```

---

## Quick Start

1. **Create a Quart application**

```python
from quart import Quart
from quart_i18n import I18n

app = Quart(__name__)
```

2. **Create localization configuration files**

Create a `locales/` folder and add JSON files:

```
locales/
├── index.json
├── about.json
```

Example `index.json`:

```json
{
  "en": {
    "title": "Welcome, {username}!",
    "description": "This is the English version."
  },
  "hu": {
    "title": "Üdv, {username}!",
    "description": "This is the Hungarian version."
  }
}
```

3. **Initialize I18n**

```python
i18n = I18n(
    appInstance=app,
    languages=["en", "hu"],
    configPath="locales",
    defaultLanguage="en"
)
```

4. **Use in templates**

The `render_template` wrapper automatically injects localization:

```python
@app.route("/")
async def index():
    return await i18n.render_template("index.html", username="Bali")
```

Example `index.html`:

```html
<h1>{{ t.title }}</h1>
<p>{{ t.description }}</p>
```

---

## Cookie-based Language Selection

`I18n` selects the language in the following order:

1. `language` cookie value
2. If the cookie value is unsupported → `defaultLanguage`

---

## Error Handling

The package includes several custom exceptions:

* `ConfigNotFoundError` – configuration directory or file is missing
* `MissingPageError` – JSON file for the requested page does not exist
* `InvalidConfigError` – JSON parsing error
* `LanguageNotSupportedError` – requested language is not in the supported list

---

## Examples

### Dynamic String Formatting

```python
await i18n.render_template("index.html", displayname="Alice")
```

If `displayname` is not present in the JSON, SafeDict ensures no error is raised; the placeholder `{displayname}` remains in the template.

---

## License

MIT License © 2025 [Bali](mailto:info@1bali1.hu)

---

## Related Links

* [GitHub repository](https://github.com/1bali1/quart-i18n)
* [PyPI](https://pypi.org/project/quart-i18n)
* [Quart documentation](https://pgjones.gitlab.io/quart/)