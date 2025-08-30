"""
utils.py — shared environment flags, attribute/style normalization, and build stacks
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

# ---- PyScript / browser detection -------------------------------------------------

HAS_JS = False
_document = None
try:
    from js import document as _document  # type: ignore

    HAS_JS = True
except Exception:
    HAS_JS = False


# ---- Attribute / style helpers ----------------------------------------------------


def _hyphenate(name: str) -> str:
    """Map pythonic identifiers to HTML/CSS attribute/property names."""
    if name.endswith("_"):
        name = name[:-1]
    name = name.replace("__", "-")
    name = name.replace("_", "-")
    return name


def _stringify(value: Any) -> str:
    if value is True:
        return ""
    if value is False or value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return " ".join(map(str, value))
    return str(value)


def _normalize_attrs(attrs: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in attrs.items():
        if v is None or v is False:
            continue
        name = _hyphenate(k)
        out[name] = _stringify(v)
    return out


def _normalize_style(style: Union[str, Dict[str, Any], None]) -> str:
    if style is None:
        return ""
    if isinstance(style, str):
        return style
    parts = []
    for k, v in style.items():
        if v is None or v is False:
            continue
        parts.append(f"{_hyphenate(k)}:{v}")
    return ";".join(parts)


# ---- Build stacks (shared by HTML + CSS) -----------------------------------------


class _BuildStacks:
    element_stack: List["Element"] = []
    css_stack: List["CSSContainer"] = []

    @classmethod
    def current_element_parent(cls) -> Optional["Element"]:
        return cls.element_stack[-1] if cls.element_stack else None

    @classmethod
    def push_element(cls, el: "Element") -> None:
        cls.element_stack.append(el)

    @classmethod
    def pop_element(cls) -> None:
        if cls.element_stack:
            cls.element_stack.pop()

    @classmethod
    def current_css_container(cls) -> Optional["CSSContainer"]:
        return cls.css_stack[-1] if cls.css_stack else None

    @classmethod
    def push_css(cls, c: "CSSContainer") -> None:
        cls.css_stack.append(c)

    @classmethod
    def pop_css(cls) -> None:
        if cls.css_stack:
            cls.css_stack.pop()


__all__ = [
    "HAS_JS",
    "_document",
    "_hyphenate",
    "_stringify",
    "_normalize_attrs",
    "_normalize_style",
    "_BuildStacks",
]
