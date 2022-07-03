# Host Informations
HOST = 192.168.178.26
HOST_USER = pi
TARGET = $(HOST_USER)@$(HOST)

HOST_PROJECT_DIR = ~/segment-display/

SERVICE_DIR = /etc/systemd/system

# Environment
LOCAL_SRC_DIR = ./src/
LOCAL_SSH_DIR = ~/.ssh/id_rsa.pub
LOCAL_KNOWN_HOSTS = ~/.ssh/known_hosts

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

sync: 			## Sync to the target, enforce ssh authentication example
	rsync --verbose --archive --recursive --delete-before -e \
	'ssh -p 22' \
	$(LOCAL_SRC_DIR) \
	$(TARGET):$(HOST_PROJECT_DIR)

install-service: ## Moves the service file to the directory on the debian and registers the service
	ssh -t $(TARGET) "sudo cp ~/segment-display/segment-display.service /etc/systemd/system && \
	sudo chmod 644 /etc/systemd/system/segment-display.service && \
	sudo systemctl enable segment-display.service && \
	sudo systemctl daemon-reload && \
	sudo systemctl start segment-display.service"

install-ssh: 		## install my ssh key on the target
	-ssh-keygen -f $(LOCAL_KNOWN_HOSTS) -R $(HOST)
	-ssh-copy-id -i $(LOCAL_SSH_DIR) $(TARGET)

remote: 		## get the console of the target
	ssh $(TARGET)

# PHONY: remote