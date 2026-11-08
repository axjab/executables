# 1. System state
uname -a
lsb_release -a
systemctl is-active unattended-upgrades

# 2. Browser installs — figure out HOW they were installed
which firefox 2>/dev/null && echo "firefox: in PATH"
dpkg -l | grep -E "firefox|floorp" 2>/dev/null
flatpak list 2>/dev/null | grep -E "firefox|floorp|Firefox|Floorp"
snap list 2>/dev/null | grep -E "firefox|floorp"

# 3. Home directory
ls -la ~/

# 4. Existing bashrc
cat ~/.bashrc

# 5. DNS config
cat /etc/systemd/resolved.conf

# 6. XDG dirs
cat ~/.config/user-dirs.dirs
cat ~/.config/user-dirs.conf 2>/dev/null || echo "user-dirs.conf not present"

# 7. Fonts already installed
fc-list | grep -i "nerd\|jetbrains\|fira\|cascadia" 2>/dev/null || echo "no nerd fonts found"

# 8. Installed packages of interest
dpkg -l | grep -E "ufw|git|docker|micro|bat|eza|zoxide|tldr|btop|tmux|fzf|ripgrep|jq"

# 9. Flatpaks installed
flatpak list 2>/dev/null || echo "flatpak not installed"
