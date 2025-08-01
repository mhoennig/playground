include .env
export

SSH_HOME := $(shell ssh $(SSH_USER)@$(SSH_HOST) "echo \$$HOME")

.PHONY:  dist deploy-frontend deploy-backend deploy ssh

all: help

## lists all documented targets
help:
	@awk '/^##/ {sub(/^## /, "", $$0); desc=$$0; next} /^[a-zA-Z0-9][^:]*:/ { \
		print "\033[1m" $$1 "\033[0m"; \
		print "    " desc "\n" \
	}' Makefile

## builds a distribution of the React app
dist:
	npm run build
	sed -e "s|\$${SSH_HOME}|$(SSH_HOST)|g" \
		-e "s|\$${SSH_HOME}|$(SSH_HOME)|g" \
		-e "s|\$${NODE_VERSION}|$(NODE_VERSION)|g" \
		.htaccess >dist/.htaccess

## connects to the server using ssh and changes directory to the domain root
login:
	ssh -t $(SSH_USER)@$(SSH_HOST) 'cd $(SSH_PATH) && bash --rcfile ~/.bashrc -i'

## prints the tail of the logfiles from the server
logs:
	ssh -t $(SSH_USER)@$(SSH_HOST) 'tail -f var/*'

## installs the node version manager
install-nvm:
	@ssh $(SSH_USER)@$(SSH_HOST) "\
		echo "path: \$$PATH";\
		if [ ! -d \"$(SSH_HOME)/.nvm\" ]; then \
			echo \"Installing NVM...\"; \
			touch ~/.profile; \
            chmod u+x ~/.profile; \
			curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/$(NVM_VERSION)/install.sh | bash; \
		else \
			source \$$HOME/.nvm/nvm.sh && \
			echo \"$(SSH_HOME)/.nvm exists => NVM already installed, version: \$$(nvm --version)\";\
		fi"

## installs and uses the configured node version
install-node: install-nvm
	@ssh $(SSH_USER)@$(SSH_HOST) "\
		cd $(SSH_PATH)/app-ssl && \
		. $(SSH_HOME)/.nvm/nvm.sh && \
		nvm install $(NODE_VERSION); \
		nvm alias default $(NODE_VERSION)"

## installs the app
install: install-node
	@ssh $(SSH_USER)@$(SSH_HOST) "\
		cd $(SSH_PATH)/app-ssl && \
		. $(SSH_HOME)/.nvm/nvm.sh && \
		nvm use $(NODE_VERSION) && \
		npm install"

## syncs frontend files to server
deploy-frontend: dist
	rsync -avz dist/ $(SSH_USER)@$(SSH_HOST):$(SSH_PATH)/htdocs-ssl/
	ssh $(SSH_USER)@$(SSH_HOST) "cd $(SSH_PATH) && mv htdocs-ssl/.htaccess ." # hack

## syncs backend files to server
deploy-backend:
	rsync -avz --exclude-from=.gitignore --exclude .git api-mock/ $(SSH_USER)@$(SSH_HOST):$(SSH_PATH)/app-ssl/

## deploys frontend and backend and installs production dependencies on the server
deploy: deploy-backend deploy-frontend
	ssh $(SSH_USER)@$(SSH_HOST) "cd $(SSH_PATH)/app-ssl && npm install --omit=dev"

## tells Phusion Passenger NodeJS on the server to restart the backend app
restart:
	ssh $(SSH_USER)@$(SSH_HOST) "cd $(SSH_PATH)/app-ssl && passenger-config restart-app /home/$(SSH_PATH)"
	@echo $(APP_ROOT)