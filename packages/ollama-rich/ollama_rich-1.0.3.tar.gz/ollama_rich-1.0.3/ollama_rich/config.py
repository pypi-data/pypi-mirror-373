import yaml
from pathlib import Path
from appdirs import user_config_dir
from rich.console import Console

console = Console()

# --- Constants ---
CONFIG_DIR = Path(user_config_dir("ollama-rich", "OllamaRich"))
CONFIG_FILE = CONFIG_DIR / 'config.yaml'

default_config = {
	'ollama': {
		'host': 'http://localhost:11434',
		'model': 'llama2'
	}
}

# --- Helper Functions ---
def ensure_config_dir() -> Path:
	"""Ensure the config file exists in the user's config directory."""
	if not CONFIG_DIR.exists():
		CONFIG_DIR.mkdir(parents=True, exist_ok=True)
	return CONFIG_DIR

def create_default_config() -> None:
	"""Create a default config file if it doesn't exist."""
	if not CONFIG_FILE.exists():
		with open(CONFIG_FILE, 'w') as config_file:
			yaml.dump(default_config, config_file)

def get_config() -> dict:
	"""Load and return the config parser object."""
	config = yaml.safe_load(open(CONFIG_FILE, 'r')) if CONFIG_FILE.exists() else default_config
	if not isinstance(config, dict):
		raise ValueError("Config file is not a valid dictionary.")
	create_default_config()  # Ensure the default config is created if it doesn't exist
	config = yaml.safe_load(open(CONFIG_FILE, 'r'))
	if not isinstance(config, dict):
		raise ValueError("Config file is not a valid dictionary.")
	return config

def set_config(new_config: dict) -> None:
	"""Set the config with a new dictionary and save it to the file."""
	if not isinstance(new_config, dict):
		raise ValueError("New config must be a dictionary.")
	with open(CONFIG_FILE, 'w') as config_file:
		yaml.dump(new_config, config_file)

def setup_config(host: str, model: str) -> None:
	"""Setup the Ollama Rich Client configuration."""
	config = get_config()
	if host or model:
		if host:
			config['ollama']['host'] = host
		if model:
			config['ollama']['model'] = model
	else:
		console.print("If you don't want to change the host or model, just press Enter.")
		host  = console.input("[bold yellow]Enter host URL: [/bold yellow]")
		if host:
			config['ollama']['host'] = host
		model = console.input("[bold yellow]Enter default model: [/bold yellow]")
		if model:
			config['ollama']['model'] = model
	set_config(config)
	console.print(f"[bold green]Configuration updated:[/bold green] Host: {config['ollama']['host']}, Default Model: {config['ollama']['model']}")
	return
	
# --- Config Initialization ---
ensure_config_dir()
