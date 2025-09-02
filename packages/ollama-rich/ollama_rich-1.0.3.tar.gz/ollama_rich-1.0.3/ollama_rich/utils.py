from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, DownloadColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn

console = Console()

def to_gb(size: int):
	return round(int(size)/(1024*1024*1024), 1)

def models_table(models: list):
	if 'models' in models:
		table = Table(show_header=True, header_style="bold magenta")
		table.add_column("Model", style="red")
		table.add_column("Size (GB)", style="blue")
		table.add_column("Parameters", style="green")
		for model in models['models']:
			table.add_row(
				model.get('model', ''),
				f"{to_gb(model.get('size', 0))}",
				str(model.get('details', {}).get('parameter_size', ''))
			)
		console.print(table)
	else:
		console.print("[bold red]No models found.[/bold red]")
	
def model_info_table(model: str, model_info: dict):
	if model_info:
		table = Table(show_header=True, header_style="bold magenta")
		table.add_column("Field", style="red")
		table.add_column("Value", style="blue")
		for key, value in model_info.dict().items():
			if key == "details" and isinstance(value, dict):
				details_table = Table(show_header=True, header_style="bold cyan")
				details_table.add_column("Detail", style="yellow")
				details_table.add_column("Value", style="green")
				for d_key, d_value in value.items():
					details_table.add_row(str(d_key), str(d_value))
				table.add_row(key, Panel(details_table, title="Details", expand=False))
			else:
				if key == "size":
					value = f"{to_gb(value)} GB"
					table.add_row(key, value)
				else:
					table.add_row(key, str(value))
		console.print(f"[bold green]Model Information for '{model}':[/bold green]")
		console.print(table)
	else:
		console.print(f"[bold red]Model '{model}' not found.[/bold red]")

progress = Progress(
    TextColumn("[bold blue]{task.description}"),
    BarColumn(),
    DownloadColumn(),
    TransferSpeedColumn(),
    TimeRemainingColumn(),
)
