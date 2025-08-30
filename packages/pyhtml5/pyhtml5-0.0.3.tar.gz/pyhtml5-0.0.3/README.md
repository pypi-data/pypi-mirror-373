# pyhtml5

A tiny Python library for writing **HTML** and **CSS** in code — with clear, full element names like `Division`, `Paragraph`, and `Button`. Render to a string in regular Python, or mount directly into the browser DOM when running under **PyScript**.

---

## Why use it?

- **Readable structure**: `with Division(): Paragraph("Hello")`
- **Works anywhere**: strings in CPython, live DOM in PyScript
- **Built-in CSS**: `Stylesheet().rule(".card", padding="16px")`

---

## Install

```bash
pip install pyhtml5
```

---

## Quick start

### Build HTML (string)

```python
from pyhtml5 import Division, Paragraph, Anchor, html_string

with Division(class_="card") as root:
    Paragraph("Hello from pyhtml5! ")
    Anchor("Read more", href="https://example.com", target="_blank")

print(html_string(root))
```

### Use in PyScript (mount to the DOM)

```python
from pyhtml5 import Division, Paragraph

with Division(class_="notice") as box:
    Paragraph("Running inside PyScript!")

box.mount("#app")   # or just box.mount() to append to <body>
```

### CSS in code

```python
from pyhtml5 import Stylesheet, css_string

with Stylesheet() as css:
    css.rule(":root", color_scheme="light dark")
    css.rule(".card", padding="16px", border="1px solid #ddd", border_radius="12px")

print(css_string(css))  # in PyScript, use css.mount() to inject a <style>
```

---

## License

MIT License

See [LICENSE](LICENSE) for details.
