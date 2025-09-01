from mkdocs.plugins import BasePlugin
import re
import unidecode

def remove_accents(s):
    return unidecode.unidecode(s)


class FiltersPlugin(BasePlugin):
    def on_config(self, config):
        macros_plugin = config.plugins.get('macros')
        if macros_plugin:
            macros_plugin.register_filters({'remove_accents': remove_accents})

    def on_env(self, env, config, files):
        if not self.config.get('enabled', True):
            return

        env.filters['remove_accents'] = remove_accents
        return env
