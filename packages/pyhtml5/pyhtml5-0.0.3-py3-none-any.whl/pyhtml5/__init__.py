"""
pyhtml5 — A tiny HTML5 + CSS DSL for PyScript (non-abbreviated class names)

Public API re-exports from submodules:
- HTML nodes, dynamic element classes, mapping helpers (from .html)
- CSS builder (from .css)
- Environment / utilities (from .utils)

Usage:
    from pyhtml5 import Division, Paragraph, Stylesheet, html_string, css_string
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# Import submodules so they're initialized (and HTML classes are generated)
from . import css as _css
from . import html as _html
from . import utils as _utils

# ---- Static declarations for linters (pylint/pyright/mypy) ----
# This makes names like `Division` visible to static analyzers without changing runtime.
if TYPE_CHECKING:
    from .html import (
        Abbreviation,
        Address,
        Anchor,
        Article,
        Aside,
        Audio,
        Base,
        BidirectionalIsolation,
        BidirectionalOverride,
        BlockQuote,
        Body,
        Bold,
        Button,
        Canvas,
        Citation,
        Code,
        Data,
        DataList,
        Definition,
        Deletion,
        DescriptionDetails,
        DescriptionList,
        DescriptionTerm,
        Details,
        Dialog,
        Division,
        Embed,
        Emphasis,
        FieldSet,
        Figure,
        FigureCaption,
        Footer,
        Form,
        Head,
        Header,
        Heading1,
        Heading2,
        Heading3,
        Heading4,
        Heading5,
        Heading6,
        HeadingGroup,
        HorizontalRule,
        Html,
        Image,
        ImageMap,
        InlineFrame,
        Input,
        Insertion,
        Italic,
        KeyboardInput,
        Label,
        Legend,
        LineBreak,
        Link,
        ListItem,
        Main,
        MapArea,
        Mark,
        Menu,
        Meta,
        Meter,
        Navigation,
        NoScript,
        Object,
        Option,
        OptionGroup,
        OrderedList,
        Output,
        Paragraph,
        Parameter,
        Picture,
        Portal,
        PreformattedText,
        Progress,
        Quotation,
        RubyAnnotation,
        RubyParenthesis,
        RubyText,
        SampleOutput,
        Script,
        Section,
        Select,
        Slot,
        Small,
        Source,
        Span,
        Strikethrough,
        Strong,
        Style,
        Subscript,
        Summary,
        Superscript,
        Table,
        TableBody,
        TableCaption,
        TableColumn,
        TableColumnGroup,
        TableDataCell,
        TableFooter,
        TableHead,
        TableHeaderCell,
        TableRow,
        Template,
        TextArea,
        Time,
        Title,
        Track,
        Underline,
        UnorderedList,
        Variable,
        Video,
        WordBreakOpportunity,
    )

# Re-export core HTML classes/utilities
Node = _html.Node
Text = _html.Text
Comment = _html.Comment
Fragment = _html.Fragment
Element = _html.Element

create = _html.create
custom = _html.custom
html_string = _html.html_string
element_class_for_tag = _html.element_class_for_tag
tag_for_element_class_name = _html.tag_for_element_class_name

# Re-export CSS builder
CSSStyleRule = _css.CSSStyleRule
AtRule = _css.AtRule
KeyframesRule = _css.KeyframesRule
PageRule = _css.PageRule
FontFaceRule = _css.FontFaceRule
Stylesheet = _css.Stylesheet
css_string = _css.css_string

# Re-export env flags (optional; handy for advanced usage)
HAS_JS = _utils.HAS_JS

# Build a runtime __all__ that includes generated element class names
__all__ = [
    # Core nodes
    "Node",
    "Text",
    "Comment",
    "Fragment",
    "Element",
    # Helpers
    "create",
    "custom",
    "html_string",
    "element_class_for_tag",
    "tag_for_element_class_name",
    # CSS
    "CSSStyleRule",
    "AtRule",
    "KeyframesRule",
    "PageRule",
    "FontFaceRule",
    "Stylesheet",
    "css_string",
    # Env
    "HAS_JS",
] + list(_html.TAG_TO_CLASSNAME.values())


def __getattr__(name: str) -> Any:
    """
    Allow: from pyhtml5 import Division
    by forwarding dynamic element class lookup to .html module.
    """
    cls = _html.CLASSNAME_TO_CLASS.get(name)
    if cls is not None:
        return cls
    raise AttributeError(f"module 'pyhtml5' has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__))
