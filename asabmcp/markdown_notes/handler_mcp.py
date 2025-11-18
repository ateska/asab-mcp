import os
import logging

import asab

from ..mcp import mcp_tool, mcp_resource_template
from ..mcp.datacls import MCPToolResultResourceLink

L = logging.getLogger(__name__)


NOTE_URI_PREFIX = "note://"
PICTURE_URI_PREFIX="img://"
NOTE_MIME_TYPE = "text/markdown"
NOTE_EXTENSION = ".md"
PICTURE_EXTENSIONS = {".jpg", ".png", ".jpeg", ".gif"}


class MarkdownNotesMCPHandler():

	def __init__(self, app):
		self.App = app

		self.NotesDirectory = asab.Config.get("general", "notes", fallback="notes")

		os.makedirs(self.NotesDirectory, exist_ok=True)

		self.App.MCPService.add_tool(self.tool_create_or_update_note)
		self.App.MCPService.add_tool(self.tool_delete_note)
		self.App.MCPService.add_tool(self.tool_read_note)

		self.App.MCPService.add_tool(self.tool_upload_picture)

		self.App.MCPService.add_tool(self.tool_list_notes)

		self.App.MCPService.add_resource_template(self.resource_template_notes)
		self.App.MCPService.add_resource_list(NOTE_URI_PREFIX, self.resource_list_notes)


	@mcp_tool(
		name="create_or_update_note",
		title="Create or update a note",
		description="""
			Create a new Markdown note or update the existing Markdown note at the given path with the given content.
			The note path can contain subdirectories, separated by '/'.
			Subdirectories are created if they do not exist.
			The result is a resource link to the created or updated note.
		""",
		inputSchema={
			"type": "object",
			"properties": {
				"path": {"type": "string"},
				"content": {"type": "string", "format": "markdown"},
			},
		},
	)
	async def tool_create_or_update_note(self, path, content):
		if '..' in path:
			raise ValueError("Path cannot contain '..'")

		while path.startswith('/'):
			path = path[1:]

		if not path.endswith(NOTE_EXTENSION):
			path += NOTE_EXTENSION

		note_path = os.path.join(self.NotesDirectory, path)
		os.makedirs(os.path.dirname(note_path), exist_ok=True)

		new_note = not os.path.isfile(note_path)
		with open(note_path, "w") as f:
			f.write(content)

		if new_note:
			L.log(asab.LOG_NOTICE, "Created a new Markdown note", struct_data={"path": path})
		else:
			L.log(asab.LOG_NOTICE, "Updated a Markdown note", struct_data={"path": path})

		return MCPToolResultResourceLink(
			uri=f"{NOTE_URI_PREFIX}/{path}",
			name=path,
			description=f"{'Created' if new_note else 'Updated'} a Markdown note",
			mimeType=NOTE_MIME_TYPE,
		)

	@mcp_tool(
		name="delete_note",
		title="Delete a note",
		description="""
			Delete the note with the given path.
			The note path can contain subdirectories, separated by '/'.
			Subdirectories are not deleted.
			The result is a message indicating that the note was deleted.
		""",
		inputSchema={
			"type": "object",
			"properties": {
				"path": {"type": "string"},
			},
		},
	)
	async def tool_delete_note(self, path):
		if '..' in path:
			raise ValueError("Path cannot contain '..'")

		while path.startswith('/'):
			path = path[1:]

		if not path.endswith(NOTE_EXTENSION):
			path += NOTE_EXTENSION

		note_path = os.path.join(self.NotesDirectory, path)
		if not os.path.isfile(note_path):
			raise ValueError(f"Note {path} does not exist")

		os.remove(note_path)

		L.log(asab.LOG_NOTICE, "Deleted a Markdown note", struct_data={"path": path})

		return "Note deleted."


	@mcp_tool(
		name="list_notes",
		title="List notes in a directory",
		description="""
			List all Markdown notes in the given directory.
			The result is a list of resource links to the notes.
			The resource links can be used as path to read the note content or other tools.
			To list a root directory, use an empty string or '/' for the directory.
		""",
		inputSchema={
			"type": "object",
			"properties": {
				"directory": {"type": "string"},
			},
		},
	)
	async def tool_list_notes(self, directory=""):
		if '..' in directory:
			raise ValueError("Directory cannot contain '..'")

		while directory.startswith('/'):
			directory = directory[1:]

		directory_path = os.path.join(self.NotesDirectory, directory)
		if not os.path.isdir(directory_path):
			raise ValueError(f"Directory {directory} does not exist")

		return [
			MCPToolResultResourceLink(
				uri=f"{NOTE_URI_PREFIX}/{directory}/{note}",
				name=f"{directory}/{note}",
				description="Markdown note",
				mimeType=NOTE_MIME_TYPE,
			) for note in os.listdir(directory_path) if note.endswith(NOTE_EXTENSION) and not note.startswith('.')
		]


	@mcp_tool(
		name="read_note",
		title="Read a note",
		description="Read the content of the note with the given path. The result is the content of the note in Markdown format.",
		inputSchema={
			"type": "object",
			"properties": {
				"path": {"type": "string"},
			},
		},
	)
	async def tool_read_note(self, path):
		if '..' in path:
			raise ValueError("Path cannot contain '..'")

		while path.startswith('/'):
			path = path[1:]

		if not path.endswith(NOTE_EXTENSION):
			path += NOTE_EXTENSION

		note_path = os.path.join(self.NotesDirectory, path)
		if not os.path.isfile(note_path):
			raise ValueError(f"Note {path} does not exist")

		with open(note_path, "r") as f:
			content = f.read()

		return content


	@mcp_tool(
		name="upload_picture",
		title="Upload a picture",
		description="""
			Upload a picture to the notes directory.
			The picture path can contain subdirectories, separated by '/'.
			Subdirectories are created if they do not exist.
			Supported picture extensions are: {}.
			The result is a resource link to the uploaded picture.
		""".format(PICTURE_EXTENSIONS),
		inputSchema={
			"type": "object",
			"properties": {
				"path": {"type": "string"},
				"content": {"type": "string", "format": "binary"},
			},
		},
	)
	async def tool_upload_picture(self, path, content):
		if '..' in path:
			raise ValueError("Path cannot contain '..'")

		while path.startswith('/'):
			path = path[1:]

		if not any(path.endswith(ext) for ext in PICTURE_EXTENSIONS):
			raise ValueError(f"Unsupported picture extension. Supported extensions are: {PICTURE_EXTENSIONS}")

		picture_path = os.path.join(self.NotesDirectory, path)
		os.makedirs(os.path.dirname(picture_path), exist_ok=True)

		with open(picture_path, "w") as f:
			f.write(content)

		return MCPToolResultResourceLink(
			uri=f"{PICTURE_URI_PREFIX}/{path}",
			name=path,
			description="Picture",
			mimeType="image/jpeg",
		)

	@mcp_resource_template(
		uri_prefix=NOTE_URI_PREFIX,
		uri_template=f"{NOTE_URI_PREFIX}/{{path*}}.md",
		name="notes",
		title="Markdown notes",
		description="Markdown notes stored in directories",
		mimeType=NOTE_MIME_TYPE
	)
	async def resource_template_notes(self, uri):
		'''
		Read the content of the resource.
		'''

		assert uri.startswith(NOTE_URI_PREFIX)
		path = uri[len(NOTE_URI_PREFIX):]
		if '..' in path:
			raise ValueError("Path cannot contain '..'")

		while path.startswith('/'):
			path = path[1:]

		if not path.endswith(NOTE_EXTENSION):
			path += NOTE_EXTENSION

		note_path = os.path.join(self.NotesDirectory, path)
		if not os.path.isfile(note_path):
			L.warning("Note not found", struct_data={"uri": uri})
			return None

		with open(note_path, "r") as f:
			content = f.read()

		return {
			"uri": uri,
			"mimeType": NOTE_MIME_TYPE,
			"text": content,
		}


	async def resource_list_notes(self):
		resources = []
		for root, dirs, files in os.walk(self.NotesDirectory):
			for file in files:
				if file.endswith(NOTE_EXTENSION):
					path = root[len(self.NotesDirectory):]
					resources.append(MCPToolResultResourceLink(
						uri=f"{NOTE_URI_PREFIX}/{path}/{file}",
						name=f"{file[:-len(NOTE_EXTENSION)]}",
						description="Markdown note",
						mimeType=NOTE_MIME_TYPE,
					))
		return resources
