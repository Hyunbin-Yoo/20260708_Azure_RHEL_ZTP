#version=DEVEL
# Language and Keyboard
lang en_US.UTF-8
keyboard --vckeymap=us --xlayouts='us'

# Network Configuration (Auto-activate via DHCP)
network --bootproto=dhcp --device=link --activate

# Root Password (Change 'password' to your preferred secure hash or plaintext for testing)
rootpw --plaintext password

# System Timezone
timezone Asia/Seoul --utc

# Disable Firstboot and Setup Agent
firstboot --disable
selinux --enforcing
firewall --enabled --service=ssh

# Storage Overrides (Blindly wipe and reinitialize partitions)
zerombr
clearpart --all --initlabel --drives=sda,nvme0n1
autopart --type=lvm --nohome

# Post-Installation Action
reboot

# Software Package Payload Selection
%packages
@^graphical-server-environment
%end