import json

from mcp.server.fastmcp import FastMCP

from wizlib.parser import WizParser
from wizlib.command import WizHelpCommand

from busy.command import BusyCommand


class MCPCommand(BusyCommand):

    name = 'mcp'

    @BusyCommand.wrap
    def execute(self):
        mcp = FastMCP("Busy")

        @mcp.tool()
        def perform(command: str) -> str:
            """Perform a Busy command"""
            try:
                result = self.app.do(command)
                return json.dumps(result)
            except Exception as error:
                return json.dumps({"Error": error})
        mcp.run()
