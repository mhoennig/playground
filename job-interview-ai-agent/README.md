# Job Interview AI Agent

A web-based application that provides an AI-powered job interview experience using Gradio interface.

This app is mostly a showcase for what I'm learning from ["The Complete Agentic AI Engineering Course (2025)"](https://www.udemy.com/course/the-complete-agentic-ai-engineering-course) by Ed Donner.


## Prerequisites

### For development and local testing:

- `make` (GU make)
- `python3`
- `awk`
- `sed`

 ### Optionally, for deployment as a systemd service in a webspace:

- possibility to run a deamon process and configure a reverse-proxy via `.htaccess`
- `scp`
- `systemctl`
- `journalctl`

## Quick Start

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd job-interview-ai-agent
   ```

2. Create a `.env` file with the following properties:
   ```
   GRADIO_PORT=[your-preferred-port]    # e.g. 7860 (default)
   LOCAL_DATA=[path-to-local-data]      # e.g. ~/projects/job-interview-local-data
   PROD_TARGET=[production-target-path] # e.g. username@host:domains/example.org/interview/
   ```

3. Initialize the project:
   ```bash
   make init
   ```

   This will:
   - Extract all bundled files if running from a bundle
   - Create a Python virtual environment (.venv)
   - Install the latest version of pip in the virtual environment
   - Install all required Python packages from requirements.txt

4. Run the application locally:
   ```bash
   make run
   ```

   This will:
   - Start the application inside the Python virtual environment (via interview.sh)
   - Launch the Gradio web interface on your configured port (default: 7860)
   - Monitor the application and automatically restart it if it crashes
   - Stop automatically after 3 consecutive startup failures
   - Allow the user to stop the application via Ctrl-C

    This is just meant for local testing.

5. Open your web browser and navigate to:
   ```
   http://localhost:7860
   ```
   (Replace 7860 with your configured GRADIO_PORT if you changed it in .env)


## Important Make Commands

- `make init` - Initialize the project (unbundle files and set up Python virtual environment)
- `make run` - Run the application locally
- `make help` - Display all available make targets with descriptions
- `make clean` - Remove all generated files and virtual environment

### Service Management (systemd + .htaccess)

- `make install` - Create systemd user service and .htaccess file
- `make start` - Start the systemd service
- `make stop` - Stop the systemd service
- `make restart` - Restart the systemd service
- `make status` - Check service status
- `make log` - View service logs
- `make uninstall` - Remove the systemd service

### Deployment

- `make bundle` - Bundle all source files into Makefile.bundle
- `make upload` - Upload bundled files to the production server
- `make reload` - Unbundle files, reinstall service, and restart

## Project Structure

```
.
├── src/
│   ├── main.py           # Main application entry point
│   ├── interview.py      # Interview interface implementation
│   ├── llm_service.py    # LLM service integration
│   ├── config.py         # Configuration management
│   ├── utils.py          # Utility functions
│   ├── models.py         # Data models
│   └── __init__.py       # Package initialization
├── data/                 # Interview data and prompts
├── requirements.txt      # Python dependencies
├── interview.sh          # Local development script
├── interview.service     # Systemd service configuration
└── Makefile              # Build and deployment automation
```

## Configuration

The application can be configured through the following files:
- `.env` - Environment variables for ports and paths
- `interview.service` - Systemd service configuration
- `.htaccess` - Apache proxy configuration (auto-generated my Makefile)
