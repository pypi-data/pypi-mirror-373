from mkdocs.plugins import BasePlugin

class EnviormentPlugin(BasePlugin):

    def __init__(self):
        self.enabled = True
        self.is_building = False

    def on_startup(self, *, command, dirty):
        self.is_building = command in ['build', 'gh-deploy']

    def on_page_context(self, context, page, config, nav):
        context['build'] = self.is_building
        return context
