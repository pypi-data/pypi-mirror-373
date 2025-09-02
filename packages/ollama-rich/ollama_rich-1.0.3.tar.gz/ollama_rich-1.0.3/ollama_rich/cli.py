import argparse
from rich.console import Console
from ollama_rich import OllamaRichClient, model_info_table, models_table, __version__
from ollama_rich.config import get_config, setup_config

console = Console()
ollama_host = get_config().get('ollama', {}).get('host', 'http://localhost:11434')

def main():
    parser = argparse.ArgumentParser(description="Ollama Client CLI with Rich UI")
    parser.add_argument('--host', default=ollama_host, help='Ollama server host URL')
    subparsers = parser.add_subparsers(dest="command")

    setup = subparsers.add_parser("setup", help="Setup the Ollama Rich Client configuration")
    setup.add_argument("-s","--host", help="Ollama server host URL")
    setup.add_argument("-m", "--model", help="Default model to use")

    # List models
    subparsers.add_parser("models", help="List all available models")

    # Info about a specific model
    model_parser = subparsers.add_parser("model", help="Get information about a specific model")
    model_parser.add_argument("model", help="Model name to get information about")

    pull_model = subparsers.add_parser("pull", help="Pull a model from the Ollama library")
    pull_model.add_argument("model", help="Model name to pull")
    pull_model.add_argument("-ns", "--nostream", action='store_true', help="Disable stream output")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with a model")
    chat_parser.add_argument("message", help="Message to send to the model")
    chat_parser.add_argument("-m","--model", help="Model name")
    chat_parser.add_argument("--stream", action="store_true", help="Stream the response live")

    parser.add_argument("--version", action="version", version="Ollama Rich Client CLI version " + __version__, 
                        help="Show the version of the Ollama Rich Client CLI")

    args = parser.parse_args()

    client = OllamaRichClient(host=args.host)

    try:
        if args.command == "setup":
            setup_config(host=args.host, model=args.model)
        
        elif args.command == "models":
            models = client.models()
            models_table(models)
        
        elif args.command == "model":
            if not args.model:
                model = get_config().get('ollama', {}).get('model', 'llama2')
            else:
                model = args.model
            model_info = client.model_info(model)
            model_info_table(model, model_info)
        
        elif args.command == "pull":
            if args.nostream:
                stream = False
            else:
                stream = True
            client.pull(args.model, stream=stream)

        elif args.command == "chat":
            if not args.model:
                model = get_config().get('ollama', {}).get('model', 'llama2')
            else:
                model = args.model
            console.print(f"[bold green]Using model:[/bold green] {model}")
            messages = [{"role": "user", "content": args.message}]
            if args.stream:
                client.chat_and_display(model, messages)
            else:
                md = client.chat(model, messages)
                console.print(md)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Execution interrupted by user (Ctrl+C). Exiting...[/bold yellow]")

if __name__ == "__main__":
    main()