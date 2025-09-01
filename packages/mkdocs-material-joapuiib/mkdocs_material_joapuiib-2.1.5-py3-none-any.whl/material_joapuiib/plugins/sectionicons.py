from mkdocs.plugins import BasePlugin
import re

# This regex allows to match a icon with no text
ICON_RE = re.compile(r'^:(\S+):(?: ([^\n]+))?$')


def extract_icon(section_title):
    match = ICON_RE.match(section_title)
    if match:
        return match.group(1)
    return None


def remove_icon(section_title):
    match = ICON_RE.match(section_title)
    if match:
        return match.group(2) or ''
    return section_title


class SectionIconsPlugin(BasePlugin):
    def on_env(self, env, config, files):
        if not self.config.get('enabled', True):
            return

        env.filters['extract_icon'] = extract_icon
        env.filters['remove_icon'] = remove_icon
