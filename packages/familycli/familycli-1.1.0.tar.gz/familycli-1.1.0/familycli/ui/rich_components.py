
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

console = Console()

def message_bubble(sender, message, color="cyan"):
	bubble = Panel(f"{sender}: {message}", style=color, expand=False)
	console.print(bubble)

def show_panel(title, content, style="green"):
	panel = Panel(content, title=title, style=style)
	console.print(panel)

def show_table(title, columns, rows):
	table = Table(title=title)
	for col in columns:
		table.add_column(col)
	for row in rows:
		table.add_row(*[str(cell) for cell in row])
	console.print(table)

def show_progress(task_description: str, total: int, auto_advance: bool = False):
	"""Production-grade progress indicator with proper completion handling."""
	with Progress(SpinnerColumn(), BarColumn(), TextColumn("{task.description}")) as progress:
		task = progress.add_task(task_description, total=total)

		if auto_advance:
			# Auto-advance mode for demonstration
			import time
			for i in range(total):
				progress.update(task, advance=1)
				time.sleep(0.1)  # Simulate work
		else:
			# Return progress object for manual control
			return progress, task

def create_progress_context(task_description: str, total: int):
	"""Create a progress context for manual control."""
	return Progress(SpinnerColumn(), BarColumn(), TextColumn("{task.description}")), task_description, total
