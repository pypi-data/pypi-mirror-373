# Adapted from Material for MkDocs: https://github.com/squidfunk/mkdocs-material/blob/master/src/overrides/hooks/shortcodes.py
# Copyright (c) 2016-2024 Martin Donath <martin.donath@squidfunk.com>

from __future__ import annotations

import posixpath
import shlex
import re

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page
from mkdocs.plugins import BasePlugin

from re import Match


class BadgesPlugin(BasePlugin):
    def on_page_markdown(
        self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files
    ):

        # Replace callback
        def replace(match: Match):
            type, args = match.groups()
            args = args.strip()
            if type == "package":        return self._badge_for_package(args, page, files)
            if type == "dir":            return self._badge_for_dir(args, page, files)
            if type == "eval":           return self._badge_for_eval(args, page, files)
            if type == "tag":            return self._badge_for_tag(args, page, files)
            if type == "branch":         return self._badge_for_branch(args, page, files)

            # Otherwise, raise an error
            raise RuntimeError(f"Unknown shortcode: {type}")

        # Find and replace all external asset URLs in current page
        return re.sub(
            r"<!-- md:(\w+)(.*?) -->",
            replace, markdown, flags = re.I | re.M
        )

    # Create a linkable option
    def option(self, type: str):
        _, *_, name = re.split(r"[.:]", type)
        return f"[`{name}`](#+{type}){{ #+{type} }}\n\n"

    # Create a linkable setting - @todo append them to the bottom of the page
    def setting(self, type: str):
        _, *_, name = re.split(r"[.*]", type)
        return f"`{name}` {{ #{type} }}\n\n[{type}]: #{type}\n\n"

    # -----------------------------------------------------------------------------

    # Resolve path of file relative to given page - the posixpath always includes
    # one additional level of `..` which we need to remove
    def _resolve_path(self, path: str, page: Page, files: Files):
        path, anchor, *_ = f"{path}#".split("#")
        path = _resolve(files.get_file_from_path(path), page)
        return "#".join([path, anchor]) if anchor else path

    # Resolve path of file relative to given page - the posixpath always includes
    # one additional level of `..` which we need to remove
    def _resolve(self, file: File, page: Page):
        path = posixpath.relpath(file.src_uri, page.file.src_uri)
        return posixpath.sep.join(path.split(posixpath.sep)[1:])

    # -----------------------------------------------------------------------------

    # Create badge
    def _badge(self, icon: str, text: str = "", type: str = ""):
        classes = f"mdx-badge mdx-badge--{type}" if type else "mdx-badge"
        text = text if isinstance(text, list) else [text]
        return "".join([
            f"<span class=\"{classes}\">",
            *([f"<span class=\"mdx-badge__icon\">{icon}</span>"] if icon else []),
            *[f"<span class=\"mdx-badge__text\">{t}</span>" for t in text],
            f"</span>",
        ])


    # Create badge for package
    def _badge_for_package(self, text: str, page: Page, files: Files):
        icon = "material-folder-zip"
        return self._badge(
            icon = f":{icon}:{{title=Package}}",
            text = f"`{text}`",
        )

    # Create badge for directory
    def _badge_for_dir(self, text: str, page: Page, files: Files):
        icon = "octicons-file-directory-open-fill-24"
        return self._badge(
            icon = f":{icon}:{{title=Directori}}",
            text = f"`{text}`",
        )

    # Create badge for eval
    def _badge_for_eval(self, text: str, page: Page, files: Files):
        icon = "material-check"
        return self._badge(
            icon = f":{icon}:{{title=Avaluació}}",
            text = shlex.split(text),
        )


    # Create badge for tag
    def _badge_for_tag(self, text: str, page: Page, files: Files):
        icon = "material-tag"
        return self._badge(
            icon = f":{icon}:{{title=Tag}}",
            text = f"`{text}`",
        )

    # Create badge for branch
    def _badge_for_branch(self, text: str, page: Page, files: Files):
        icon = "material-source-branch"
        return self._badge(
            icon = f":{icon}:{{title=Branch}}",
            text = f"`{text}`",
        )
