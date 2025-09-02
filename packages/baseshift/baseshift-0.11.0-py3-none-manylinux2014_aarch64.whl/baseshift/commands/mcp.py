from .base import BaseCommand


class McpCommand(BaseCommand):
    def add_arguments(self, parser):
        pass

    def run(self, args, server):
        from .mcp_server import start_mcp_server

        start_mcp_server()
