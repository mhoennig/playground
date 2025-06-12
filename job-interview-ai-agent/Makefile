APP_NAME := interview
BUNDLE_FILES := requirements.txt index.html src/*.py $(APP_NAME).service $(APP_NAME).sh data/*.md

REQUIRED_TOOLS := awk sed python3 systemctl journalctl
SERVICE_DIR := $(HOME)/.config/systemd/user
SERVICE_FILE := $(SERVICE_DIR)/$(APP_NAME).service
PWD := $(shell pwd)
GRADIO_PORT := $(shell grep ^GRADIO_PORT .env | cut -d= -f2)
LOCAL_DATA := $(shell grep ^LOCAL_DATA .env | cut -d= -f2)
PROD_TARGET := $(shell grep ^PROD_TARGET .env | cut -d= -f2)

.PHONY: default check-tools help bundle upload unbundle venv init run service install start status log restart stop uninstall clean

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

## bundle all source files embedded into this Makefile
bundle: Makefile.bundle

Makefile.bundle: check-tools Makefile $(BUNDLE_FILES)
	@echo "Bundling files into this Makefile..."
	@awk '/^#== BEGIN BUNDLE ==#/{exit} {print}' Makefile > Makefile.bundle
	@echo '#== BEGIN BUNDLE ==#' >> Makefile.bundle
	@for f in $(BUNDLE_FILES); do \
		echo "# cat > $$f <<'EOF_$$f'" >> Makefile.bundle; \
		sed 's/^/# /' $$f >> Makefile.bundle; \
		echo "# EOF_$$f" >> Makefile.bundle; \
	done

## uploads the bundle to the server
upload: Makefile.bundle
	@echo "Uploading bundled Makefile to the server..."
	@scp Makefile.bundle $(PROD_TARGET)/Makefile
	@scp $(LOCAL_DATA)/*.md $(PROD_TARGET)/data/

# unbundles the files from the Makefile
requirements.txt: check-tools
	@awk '/^#== BEGIN BUNDLE ==#/{found=1; next} found { sub(/^# ?/, ""); print }' $(MAKEFILE_LIST) | sh; \

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

.htaccess: Makefile
	@echo "creating proxy in .htaccess using port $$(GRADIO_PORT)"
	@echo "DirectoryIndex disabled" >.htaccess
	@echo "RewriteEngine On" >>.htaccess
	@echo "RewriteBase /interview/" >>.htaccess
	@echo "RequestHeader set Host localhost" >>.htaccess
	@echo "RewriteRule ^(.*)$$ http://127.0.0.1:$(GRADIO_PORT)/\$$1 [proxy,last]" >>.htaccess

## creates the systemd user service
service: check-tools
	@mkdir -p $(SERVICE_DIR)
	@sed \
		-e 's|{{PWD}}|$(PWD)|g' \
		-e 's|{{HOME}}|$(HOME)|g' \
		$(APP_NAME).service >$(SERVICE_FILE)

## creates .htaccess file and the the systemd service
install: .htaccess service

## starts the systemd service
start: check-tools .htaccess
	systemctl --user daemon-reexec
	systemctl --user daemon-reload
	systemctl --user enable --now $(APP_NAME).service

## prints the status of the systemd service
status: check-tools
	systemctl --user status $(APP_NAME).service

## restarts the systemd service
restart: check-tools
	systemctl --user restart --now $(APP_NAME).service

## unbundles the files from the Makefile and re-installs the service
reload:
	@make stop
	@make init
	@make install
	@make start

## shows the log of the service
log: check-tools
	journalctl --user -u $(APP_NAME).service

## stops the systemd service
stop: check-tools
	systemctl --user disable --now $(APP_NAME).service
	@rm -f .htaccess ||:	

## unsinstalls the systemd service
uninstall: check-tools
	systemctl --user disable --now $(APP_NAME).service
	@rm -f $(SERVICE_FILE)
	systemctl --user daemon-reload

## removes all extracted/generated files
clean: stop
	@echo rm -f $(BUNDLE_FILES)
	@rm -rf .venv 

# ------------------------------------------------------------------------------
