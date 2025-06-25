APP_NAME := interview
BUNDLE_FILES := requirements.txt index.html src/*.py $(APP_NAME).service $(APP_NAME).sh

REQUIRED_TOOLS := awk python3

.PHONY: default check-tools help venv init run

default: init
	@echo "For help type: make help"

check-tools:
	@missing=0; \
	for tool in $(REQUIRED_TOOLS); do \
		if ! command -v $$tool >/dev/null 2>&1; then \
			echo "❌ Missing required tool: $$tool"; \
			missing=1; \
		fi; \
	done; \
	if [ $$missing -eq 1 ]; then \
		echo "💥 One or more required tools are missing."; \
		exit 1; \
	else \
		echo "✅ All required tools are available."; \
	fi

## print all targets with a short description
help: check-tools
	@awk '                                            \
		/^##/ {                                       \
			sub(/^## /, "", $$0);                     \
			help=$$0;                                 \
		}                                             \
		/^[a-zA-Z0-9][^:]*:/ {                        \
			if (help) {                               \
				printf "%-20s %s\n", $$1 ":", help;   \
				help="";                              \
			}                                         \
		}                                             \
	' FS=":" Makefile

## (re-) initialized the Python virtual environment (.venv)
venv: requirements.txt
	@if [ ! -d .venv ]; then python3 -m venv .venv; fi
	@. .venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt
	@echo
	@echo "Initialized. Use 'make clean' to reset initialization."
	@echo "Please make sure all required properties are set in .env, otherwise defaults apply."

## initially call this target to unbundle the files and initialize the Python .venv
init: venv

## directly runs the application on the port specified in PORT from the .env file
run: .venv
	sh interview.sh

## removes all generated files
clean:
	@rm -rf .venv

# ------------------------------------------------------------------------------
