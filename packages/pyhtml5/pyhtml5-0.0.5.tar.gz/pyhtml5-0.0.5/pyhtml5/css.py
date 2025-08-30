"""
css.py — Generic CSS builder for rules and common at-rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .utils import HAS_JS, _BuildStacks, _document, _hyphenate


def _css_prop_name(name: str) -> str:
    return _hyphenate(name)


@dataclass
class CSSDeclaration:
    prop: str
    value: str

    def to_css(self) -> str:
        return f"{self.prop}:{self.value};"


class CSSContainer:
    def __init__(self):
        self.children: List[
            Union["CSSStyleRule", "AtRule", "KeyframesRule", "PageRule", "FontFaceRule"]
        ] = []

    def __enter__(self):
        _BuildStacks.push_css(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        _BuildStacks.pop_css()
        return False

    def add(self, child):
        self.children.append(child)
        return child

    def rule(self, selector: str, **props) -> "CSSStyleRule":
        rule = CSSStyleRule(selector, props)
        container = _BuildStacks.current_css_container() or self
        container.add(rule)
        return rule

    def media(self, query: str) -> "AtRule":
        ar = AtRule("media", query)
        (_BuildStacks.current_css_container() or self).add(ar)
        return ar

    def supports(self, condition: str) -> "AtRule":
        ar = AtRule("supports", condition)
        (_BuildStacks.current_css_container() or self).add(ar)
        return ar

    def layer(self, name: Optional[str] = None) -> "AtRule":
        ar = AtRule("layer", name or "")
        (_BuildStacks.current_css_container() or self).add(ar)
        return ar

    def container(self, query: str) -> "AtRule":
        ar = AtRule("container", query)
        (_BuildStacks.current_css_container() or self).add(ar)
        return ar

    def page(self, selector: Optional[str] = None) -> "PageRule":
        pr = PageRule(selector)
        (_BuildStacks.current_css_container() or self).add(pr)
        return pr

    def keyframes(self, name: str) -> "KeyframesRule":
        kf = KeyframesRule(name)
        (_BuildStacks.current_css_container() or self).add(kf)
        return kf

    def font_face(self, **props) -> "FontFaceRule":
        ff = FontFaceRule(props)
        (_BuildStacks.current_css_container() or self).add(ff)
        return ff

    def to_css(self, indent: int = 0) -> str:
        return "".join(ch.to_css(indent) for ch in self.children)

    def mount(self, target: Optional[Union[str, Any]] = None):
        css_text = self.to_css()
        if not HAS_JS:
            raise RuntimeError(
                "Stylesheet.mount() requires PyScript / a browser (js.document)."
            )
        style_el = _document.createElement("style")
        style_el.setAttribute("type", "text/css")
        style_el.textContent = css_text
        if target is None:
            _document.head.appendChild(style_el)
        elif isinstance(target, str):
            parent = _document.querySelector(target)
            if parent is None:
                raise ValueError(f"mount target not found: {target}")
            parent.appendChild(style_el)
        else:
            target.appendChild(style_el)
        return style_el


class Stylesheet(CSSContainer):
    """Top-level CSS container (semantic alias)."""

    pass


class CSSStyleRule:
    def __init__(self, selector: str, props: Optional[Dict[str, Any]] = None):
        self.selector = selector
        self.decls: List[CSSDeclaration] = []
        if props:
            for k, v in props.items():
                if v is None or v is False:
                    continue
                self.decls.append(CSSDeclaration(_css_prop_name(k), str(v)))

    def __enter__(self):
        _BuildStacks.push_css(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        _BuildStacks.pop_css()
        return False

    def decl(self, prop: str, value: Any) -> "CSSStyleRule":
        self.decls.append(CSSDeclaration(_css_prop_name(prop), str(value)))
        return self

    def to_css(self, indent: int = 0) -> str:
        pad = "  " * indent if indent else ""
        inner = "".join("  " * (indent + 1) + d.to_css() + "\n" for d in self.decls)
        return f"{pad}{self.selector} {{\n{inner}{pad}}}\n"


class AtRule(CSSContainer):
    def __init__(self, name: str, prelude: str):
        super().__init__()
        self.name = name
        self.prelude = prelude

    def to_css(self, indent: int = 0) -> str:
        pad = "  " * indent if indent else ""
        inner = "".join(ch.to_css(indent + 1) for ch in self.children)
        return f"{pad}@{self.name} {self.prelude} {{\n{inner}{pad}}}\n"


class KeyframesRule(CSSContainer):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def frame(self, selector: str, **props) -> "CSSStyleRule":
        rule = CSSStyleRule(selector, props)
        (_BuildStacks.current_css_container() or self).add(rule)
        return rule

    def to_css(self, indent: int = 0) -> str:
        pad = "  " * indent if indent else ""
        inner = "".join(ch.to_css(indent + 1) for ch in self.children)
        return f"{pad}@keyframes {self.name} {{\n{inner}{pad}}}\n"


class PageRule(CSSContainer):
    def __init__(self, selector: Optional[str] = None):
        super().__init__()
        self.selector = selector

    def to_css(self, indent: int = 0) -> str:
        pad = "  " * indent if indent else ""
        head = "@page" + (f" {self.selector}" if self.selector else "")
        inner = "".join(ch.to_css(indent + 1) for ch in self.children)
        return f"{pad}{head} {{\n{inner}{pad}}}\n"


class FontFaceRule:
    def __init__(self, props: Optional[Dict[str, Any]] = None):
        self.decls: List[CSSDeclaration] = []
        if props:
            for k, v in props.items():
                if v is None or v is False:
                    continue
                self.decls.append(CSSDeclaration(_css_prop_name(k), str(v)))

    def __enter__(self):
        _BuildStacks.push_css(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        _BuildStacks.pop_css()
        return False

    def decl(self, prop: str, value: Any) -> "FontFaceRule":
        self.decls.append(CSSDeclaration(_css_prop_name(prop), str(value)))
        return self

    def to_css(self, indent: int = 0) -> str:
        pad = "  " * indent if indent else ""
        inner = "".join("  " * (indent + 1) + d.to_css() + "\n" for d in self.decls)
        return f"{pad}@font-face {{\n{inner}{pad}}}\n"


def css_string(sheet: Stylesheet) -> str:
    return sheet.to_css()


__all__ = [
    "CSSDeclaration",
    "CSSContainer",
    "CSSStyleRule",
    "AtRule",
    "KeyframesRule",
    "PageRule",
    "FontFaceRule",
    "Stylesheet",
    "css_string",
]
