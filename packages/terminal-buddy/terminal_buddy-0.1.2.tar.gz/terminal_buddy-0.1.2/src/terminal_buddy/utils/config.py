import os
import json
from pydantic import BaseModel, Field
from pathlib import Path


class Config(BaseModel):
    OLLAMA_MODEL_NAME: str = Field(default="qwen3:0.6b")
    OLLAMA_EMBEDDINGS_MODEL_NAME: str = Field(default="nomic-embed-text")
    EXAMPLES_JSON_PATH: str = Field(default="data/examples/text_2_command_examples.json")
    
    def get_config_file_path(self) -> Path:
        """Get the path to the config file."""
        config_dir = Path(__file__).parent.parent.parent.parent
        return config_dir / ".tb_config.json"
    
    def get_examples_path(self) -> str:
        """Get the absolute path to the examples JSON file."""
        # Get the directory where this config file is located
        config_dir = Path(__file__).parent.parent.parent.parent
        # Construct the absolute path relative to the project root
        return str(config_dir / self.EXAMPLES_JSON_PATH)
    
    def load_config(self):
        """Load configuration from file."""
        config_file = self.get_config_file_path()
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    self.OLLAMA_MODEL_NAME = data.get('OLLAMA_MODEL_NAME', self.OLLAMA_MODEL_NAME)
                    self.OLLAMA_EMBEDDINGS_MODEL_NAME = data.get('OLLAMA_EMBEDDINGS_MODEL_NAME', self.OLLAMA_EMBEDDINGS_MODEL_NAME)
                    self.EXAMPLES_JSON_PATH = data.get('EXAMPLES_JSON_PATH', self.EXAMPLES_JSON_PATH)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
    
    def save_config(self):
        """Save configuration to file."""
        config_file = self.get_config_file_path()
        try:
            with open(config_file, 'w') as f:
                json.dump({
                    'OLLAMA_MODEL_NAME': self.OLLAMA_MODEL_NAME,
                    'OLLAMA_EMBEDDINGS_MODEL_NAME': self.OLLAMA_EMBEDDINGS_MODEL_NAME,
                    'EXAMPLES_JSON_PATH': self.EXAMPLES_JSON_PATH
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def update_llm_model(self, model_name: str):
        """Update the LLM model name."""
        self.OLLAMA_MODEL_NAME = model_name
        self.save_config()
    
    def update_embeddings_model(self, model_name: str):
        """Update the embeddings model name."""
        self.OLLAMA_EMBEDDINGS_MODEL_NAME = model_name
        self.save_config()
    
    def update_examples_path(self, path: str):
        """Update the examples JSON path."""
        self.EXAMPLES_JSON_PATH = path
        self.save_config()


config = Config()
config.load_config()