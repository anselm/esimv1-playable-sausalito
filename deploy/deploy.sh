#!/usr/bin/env bash
# Put the view on its VM: deploy/deploy.sh [vm]   (default: sausalito, https://sausalito.exe.xyz/)
# Provisions on first use (Node, a systemd unit on port 8000), copies view/ and the server, restarts.
# Run by hand on Anselm's say; a push does not deploy.
set -euo pipefail
VM=${1:-sausalito}; HERE=$(cd "$(dirname "$0")/.." && pwd); HOST="exedev@$VM.exe.xyz"
SSH="ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=5"
$SSH "$HOST" 'command -v node >/dev/null || { curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - >/dev/null && sudo apt-get install -y -q nodejs >/dev/null; }; command -v rsync >/dev/null || sudo apt-get install -y -q rsync >/dev/null; sudo mkdir -p /srv/site && sudo chown -R $USER:$USER /srv/site'
rsync -az --delete -e "$SSH" --exclude tools --exclude prepare.py "$HERE/view" "$HERE/deploy/serve.mjs" "$HOST:/srv/site/"
$SSH "$HOST" 'sudo tee /etc/systemd/system/sausalito.service >/dev/null <<UNIT
[Unit]
Description=Playable Sausalito: the view
After=network-online.target
[Service]
User=exedev
Environment=PORT=8000
Environment=SITE_ROOT=/srv/site/view
ExecStart=/usr/bin/node /srv/site/serve.mjs
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload && sudo systemctl enable -q sausalito && sudo systemctl restart sausalito && sleep 1 && systemctl is-active sausalito'
echo "https://$VM.exe.xyz/"
