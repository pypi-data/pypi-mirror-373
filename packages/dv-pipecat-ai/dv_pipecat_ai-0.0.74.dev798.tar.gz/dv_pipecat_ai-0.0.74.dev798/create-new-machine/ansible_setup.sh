#!/bin/bash

# Run ansible playbook
ansible-playbook -i inventory.ini setup_playbook.yml

# Created/Modified files during execution:
echo "ansible_setup.sh"