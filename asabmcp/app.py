import logging

import asab.api
import asab.web.rest


from .mcp import MCPService
from .markdown_notes import MarkdownNotesMCPHandler

#

L = logging.getLogger(__name__)

#

asab.Config.add_defaults({
	"web": {
		"listen": "8898",
	},
})


class ASABMCPApplication(asab.Application):

	def __init__(self):
		super().__init__()

		# Create the Web server
		web = asab.web.create_web_server(self, api=True)

		self.MCPService = MCPService(self, web)

		self.MarkdownNotesMCPHandler = MarkdownNotesMCPHandler(self)
