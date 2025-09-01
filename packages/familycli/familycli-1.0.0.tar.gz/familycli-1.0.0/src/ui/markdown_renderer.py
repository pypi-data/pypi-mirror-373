
from markdown_it import MarkdownIt
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
import re

console = Console()
md = MarkdownIt()

def render_markdown(content: str, fallback_to_text: bool = True):
	"""Render markdown content with fallback to plain text if parsing fails."""
	try:
		# Clean up common markdown issues
		content = clean_markdown_content(content)

		# Use Rich's Markdown renderer
		markdown_obj = Markdown(content)
		console.print(markdown_obj)
		return True
	except Exception as e:
		if fallback_to_text:
			# Fallback to plain text with basic formatting
			console.print(Text(content, style="white"))
			return False
		else:
			raise e

def clean_markdown_content(content: str) -> str:
	"""Clean and normalize markdown content for better rendering."""
	# Remove excessive whitespace
	content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

	# Fix common markdown issues
	content = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', content)  # Fix bold formatting
	content = re.sub(r'\*([^*]+)\*', r'*\1*', content)  # Fix italic formatting
	content = re.sub(r'`([^`]+)`', r'`\1`', content)  # Fix code formatting

	# Ensure proper line breaks for lists
	content = re.sub(r'\n(\d+\.|\-|\*)', r'\n\n\1', content)

	return content.strip()

def is_markdown_content(content: str) -> bool:
	"""Check if content contains markdown formatting."""
	markdown_patterns = [
		r'\*\*.*?\*\*',  # Bold
		r'\*.*?\*',      # Italic
		r'`.*?`',        # Code
		r'^#+\s',        # Headers
		r'^\s*[\-\*\+]\s',  # Unordered lists
		r'^\s*\d+\.\s',  # Ordered lists
		r'\[.*?\]\(.*?\)',  # Links
	]

	for pattern in markdown_patterns:
		if re.search(pattern, content, re.MULTILINE):
			return True
	return False
