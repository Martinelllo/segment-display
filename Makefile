TARGET = pi@192.168.178.35
PROJECT_DIR = ~/segment-display/

SSH_DIRECTORY = ~/.ssh/id_rsa

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'


sync: 			## Sync to the target, enforce ssh authentication example
	rsync --verbose --archive -e \
	'ssh -p 22' \
	./ \
	$(TARGET):$(PROJECT_DIR)


install-ssh: 		## install my ssh key on the target
	ssh-copy-id -i $(SSH_DIRECTORY) $(TARGET)


remote: 		## get the console of the target
	ssh $(TARGET)