TARGET = pi@192.168.178.22
PROJECT_DIR = ~/segment-display/
SSH_DIRECTORY = ~/.ssh/id_rsa

# enforce password authentication
# sync:
# 	rsync --verbose --archive -r -e 'ssh -o PreferredAuthentications=password' \
# 	./ \
# 	$(TARGET)$(DIRECTORY)

# enforce ssh authentication example
sync:
	rsync --verbose --archive -e \
	'ssh -p 22' \
	./ \
	$(TARGET):$(PROJECT_DIR)

# install ssh on the Target
install-ssh:
	ssh-copy-id -i $(SSH_DIRECTORY) $(TARGET)

remote:
	ssh pi@192.168.178.22