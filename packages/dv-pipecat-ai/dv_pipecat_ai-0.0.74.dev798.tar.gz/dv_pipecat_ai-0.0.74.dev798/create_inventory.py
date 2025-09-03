# create_inventory.py
with open("machines.txt", "r") as f:
    machines = f.readlines()

with open("inventory.ini", "w") as f:
    f.write("[target_servers]\n")
    for machine in machines:
        machine = machine.strip()
        if machine:
            f.write(
                f"{machine} ansible_user=azureuser ansible_ssh_private_key_file=~/Documents/Code/rvcPipeline_key.pem\n"
            )

# Created/Modified files during execution:
print("inventory.ini")
