"""
Main entry point for the Job Interview AI Agent.
"""
from .interview import create_gradio_interface
from .config import settings

def main():
    """Main entry point for the application."""
    interface = create_gradio_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=settings.GRADIO_PORT,
        share=True
    )

if __name__ == "__main__":
    main() 