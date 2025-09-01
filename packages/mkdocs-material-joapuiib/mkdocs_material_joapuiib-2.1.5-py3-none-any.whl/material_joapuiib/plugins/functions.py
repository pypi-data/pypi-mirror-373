import os

import re

from mkdocs.config import base, config_options as c
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import get_plugin_logger

log = get_plugin_logger("[functions]")

class _LoadFileConfig(base.Config):
    files_dir = c.Type(str, default='')

class FunctionsPluginConfig(base.Config):
    load_file = c.SubConfig(_LoadFileConfig)

class FunctionsPlugin(BasePlugin[FunctionsPluginConfig]):
    RE = re.compile(r'^( *)(\\)?!([a-z_]+) ([^\n]+)')

    supported_functions = [
        'load_file',
    ]

    def on_page_markdown(self, markdown, page, config, files):
        new_markdown = []
        for line in markdown.split('\n'):
            match = self.RE.match(line)
            if match:
                indent = match.group(1)
                escaped = match.group(2)
                function = match.group(3)
                args = match.group(4)

                if function not in self.supported_functions:
                    new_markdown.append(line)
                    continue

                if escaped:
                    line = line.replace(escaped, '')
                    new_markdown.append(line)
                    continue

                args = self.parse_args(args)
                line = self.call_function(page, function, indent, args)
            new_markdown.append(line)

        return '\n'.join(new_markdown)


    def parse_args(self, args):
        matches = re.findall(r'"([^"]*)"|(\S+)', args)
        return [match[0] or match[1] for match in matches]


    def call_function(self, page, function, indent, args):
        """
        Checks if the function exists and calls it
        """
        if hasattr(self, function):
            function_config = self.config.get(function, {})
            return getattr(self, function)(page, function_config, indent, args)
        return ''


    def load_file(self, page, config, indent, paths):
        files_dir = config.files_dir

        output = []

        for path in paths:
            path, title = path.split('|') if '|' in path else (path, None)
            classes, path = path.split(':') if ':' in path else (None, path)
            classes = f".{classes}" if classes else ""


            if not title:
                title = os.path.basename(path)

            language = os.path.splitext(title)[1][1:]

            # relative_path_from_docs = os.path.relpath(
            #     '.',
            #     os.path.dirname(page.file.src_uri)
            # )
            # relative_path_from_docs = os.path.join("..", relative_path_from_docs)
            # relative_path = os.path.join(relative_path_from_docs, files_dir, path)

            absolute_path = os.path.join("docs", files_dir, path)
            if not os.path.exists(absolute_path):
                log.error(f"{page.file.src_path}. File not found {path}")

            template = (
                f'/// collapse-code',
                f'```{language} {{title="{title}" {classes} data-download="1"}}',
                f'--8<-- "{absolute_path}"',
                f'```',
                f'///',
            )
            template = ''.join([indent + line + '\n' for line in template])
            output.append(template)

        return "\n".join(output)

