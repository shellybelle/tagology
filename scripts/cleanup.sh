# Removes old libraries, packages, and kernels
sudo apt-get autoremove

# Clean up APT cache
#sudo du -sh /var/cache/apt
sudo apt-get autoclean

# Clear systemd journal logs
sudo journalctl --vacuum-time=3d

# Removes old revisions of snaps
#du -h /var/lib/snapd/snaps
# CLOSE ALL SNAPS BEFORE RUNNING THIS
set -eu
snap list --all | awk '/disabled/{print $1, $3}' |
    while read snapname revision; do
        snap remove "$snapname" --revision="$revision"
    done

# Clean thumbnail cache
#du -sh ~/.cache/thumbnails
rm -rf ~/.cache/thumbnails/*
