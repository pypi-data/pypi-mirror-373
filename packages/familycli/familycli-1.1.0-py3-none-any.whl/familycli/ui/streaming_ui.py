
import asyncio
import time
from typing import AsyncGenerator, Optional
from rich.live import Live
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

console = Console()

class ProductionStreamingUI:
    """Production-grade streaming UI with configurable timing and error handling."""

    def __init__(self, typing_speed: float = 0.03, refresh_rate: int = 20):
        self.typing_speed = typing_speed
        self.refresh_rate = refresh_rate
        self.console = Console()

    async def live_typing_indicator(self, persona_name: str, duration: float = 2.0):
        """Show typing indicator for specified duration."""
        try:
            with Live(
                Text(f"💭 {persona_name} is thinking...", style="italic dim yellow"),
                refresh_per_second=4,
                console=self.console
            ) as live:
                await asyncio.sleep(duration)
        except Exception as e:
            # Fallback to simple message
            self.console.print(f"[dim]{persona_name} is responding...[/dim]")

    async def stream_message_bubble(self, persona_name: str, message_tokens: AsyncGenerator[str, None],
                                  color: str = "cyan", show_panel: bool = True):
        """Stream message tokens with real-time display."""
        try:
            msg = ""
            start_time = time.time()

            if show_panel:
                with Live(refresh_per_second=self.refresh_rate, console=self.console) as live:
                    async for token in message_tokens:
                        msg += token
                        panel = Panel(
                            Text(msg, style=color),
                            title=f"[bold]{persona_name}[/bold]",
                            border_style=color
                        )
                        live.update(panel)
                        await asyncio.sleep(self.typing_speed)
            else:
                with Live(refresh_per_second=self.refresh_rate, console=self.console) as live:
                    async for token in message_tokens:
                        msg += token
                        live.update(Text(f"{persona_name}: {msg}", style=color))
                        await asyncio.sleep(self.typing_speed)

            # Log completion time for performance monitoring
            duration = time.time() - start_time
            if duration > 10:  # Log slow responses
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Slow streaming response from {persona_name}: {duration:.2f}s")

        except Exception as e:
            # Fallback to static message display
            self.console.print(f"[{color}]{persona_name}: {msg}[/{color}]")
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Streaming UI error: {e}")

    def display_static_message(self, persona_name: str, message: str, color: str = "cyan"):
        """Display a static message without streaming."""
        panel = Panel(
            Text(message, style=color),
            title=f"[bold]{persona_name}[/bold]",
            border_style=color
        )
        self.console.print(panel)

# Legacy function wrappers for backward compatibility
def live_typing_indicator(persona_name: str, duration: float = 2.0):
    """Legacy wrapper for typing indicator."""
    ui = ProductionStreamingUI()
    asyncio.run(ui.live_typing_indicator(persona_name, duration))

async def stream_message_bubble(persona_name: str, message_tokens: AsyncGenerator[str, None], color: str = "magenta"):
    """Legacy wrapper for message streaming."""
    ui = ProductionStreamingUI()
    await ui.stream_message_bubble(persona_name, message_tokens, color)
