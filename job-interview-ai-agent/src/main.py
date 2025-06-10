"""
Main entry point for the Job Interview AI Agent.
"""
from .interview import create_gradio_interface
from .config import settings

def main():
    """Main entry point for the application."""
    create_gradio_interface().launch(
        server_name="127.0.0.1",
        server_port=settings.GRADIO_PORT,
        share=False
    )

if __name__ == "__main__":
    main() 