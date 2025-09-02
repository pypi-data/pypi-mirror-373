"""A sphinx theme for IATI documentation sites."""

from datetime import datetime
from os import path
from typing import Any

import sphinx.application
from docutils import nodes
from docutils.parsers.rst.states import Inliner

SUPPORTED_LANGUAGES = {
    "en": "English",
    "fr": "Français",
    "es": "Español",
}


def iati_reference_role(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    options: dict[str, Any] = {},
    content: list[Any] = [],
) -> tuple[list[nodes.Node], list[Any]]:
    node = nodes.inline(text=text)
    node["classes"].append("iati-reference")
    return [node], []


def setup(app: sphinx.application.Sphinx) -> None:
    app.add_html_theme("iati_sphinx_theme", path.abspath(path.dirname(__file__)))
    app.config["html_permalinks_icon"] = "#"
    app.config["html_favicon"] = "static/favicon-16x16.png"
    app.config["html_context"]["language"] = app.config["language"]
    app.config["html_context"]["current_year"] = datetime.now().year
    enabled_languages = app.config["html_theme_options"].get("languages", ["en"])
    app.config["html_context"]["languages"] = {
        code: value
        for code, value in SUPPORTED_LANGUAGES.items()
        if code in enabled_languages
    }
    app.add_js_file("language-switcher.js")
    locale_path = path.join(path.abspath(path.dirname(__file__)), "locale")
    app.add_message_catalog("sphinx", locale_path)
    app.add_role("iati-reference", iati_reference_role)
