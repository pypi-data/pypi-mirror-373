from ollama import Client
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from ollama_rich.utils import progress

console = Console()

class OllamaRichClient:
    def __init__(self, host=''):
        self.client = Client(host=host)

    def chat_and_display(self, model, messages):
        response = self.client.chat(
            model=model,
            stream=True,
            messages=messages,
        )

        full_content = ""
        with Live(Markdown(full_content), console=console, refresh_per_second=2) as live:
            for chunk in response:
                full_content += chunk['message']['content']
                live.update(Markdown(full_content))


    def chat(self, model, messages):
        with console.status("[bold green]Thinking...", spinner="dots"):
            response = self.client.chat(
                model=model,
                stream=False,
                messages=messages,
            )
        return Markdown(response['message']['content'])
    
    def models(self):
        try:
            return self.client.list()
        except ConnectionError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return []
        
    def models_name_list(self):
        try:
            models = self.client.list()
            return [model.get('model') for model in models.get('models', [])]
        except ConnectionError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return []

    def model_info(self, model):
        try:
            models = self.client.list()
            for m in models.get('models', []):
                if m.get('model') == model:
                    return m
            console.print(f"[bold red]Model '{model}' not found.[/bold red]")
            return {}
        except ConnectionError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return {}

    def pull(self, model, stream: bool = True):
        try:
            if stream:
                console.print(f"[bold green] Pulling model [bold yellow]{model}[/bold yellow] with streaming...[/ bold green]")
                with progress:
                    task_id = None
                    for chunk in self.client.pull(model, stream=True):
                        # Initialize task when total size is known
                        if 'total' in chunk and task_id is None:
                            total_bytes = chunk['total']
                            task_id = progress.add_task("Downloading", total=total_bytes)

                        # Update progress
                        if task_id is not None and 'completed' in chunk:
                            progress.update(task_id, completed=chunk['completed'])
                    
                console.print(f"[bold green]:heavy_check_mark: Model '{model}' pulled successfully.[/bold green]")

            else:
                with console.status("[bold green]Pulling...") as status:
                    res = self.client.pull(model)
                    if res["status"] == "success":
                        console.print(f" [bold green]:heavy_check_mark: Model '{model}' pulled successfully.[/bold green]")
                    else:
                        console.print(f"[bold red]Error pulling model '{model}': {res['status']}[/bold red]")
        except ConnectionError as e:
            console.print(f"[bold red]Error pulling model '{model}': {e}[/bold red]")
