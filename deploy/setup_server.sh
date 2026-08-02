#!/usr/bin/env bash
set -euo pipefail

echo "==> 1/5 Installing Docker + compose plugin"
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker || true

echo "==> 1b/5 Adding 2 GB swap (safety net for 2 GB RAM)"
if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
sysctl -w vm.swappiness=10 || true
echo 'vm.swappiness=10' > /etc/sysctl.d/99-swappiness.conf

echo "==> 1c/5 Firewall: allow SSH, HTTP, HTTPS"
apt-get update -y
apt-get install -y ufw >/dev/null 2>&1 || true
ufw allow 22/tcp >/dev/null 2>&1 || true
ufw allow 80/tcp >/dev/null 2>&1 || true
ufw allow 443/tcp >/dev/null 2>&1 || true
echo "y" | ufw enable >/dev/null 2>&1 || true

echo "==> 2/5 Creating project directory"
PROJECT_DIR=/opt/pmautomation
mkdir -p "$PROJECT_DIR/deploy"
cd "$PROJECT_DIR"

echo "==> 3/5 DuckDNS (free hostname)"
if [ ! -f deploy/.env.prod ]; then
  read -rp "DuckDNS domain name (e.g. pmautomation): " DUCKDNS_DOMAIN
  read -rp "DuckDNS token (from duckdns.org after login): " DUCKDNS_TOKEN
  cat > deploy/.env.prod <<EOF
SITE_URL=${DUCKDNS_DOMAIN}.duckdns.org
DUCKDNS_DOMAIN=${DUCKDNS_DOMAIN}
DUCKDNS_TOKEN=${DUCKDNS_TOKEN}
EOF
fi
source deploy/.env.prod

echo "==> 4/5 DuckDNS auto-update every 5 min (keeps IP in sync)"
cat > /etc/cron.d/duckdns <<EOF
*/5 * * * * root curl -s "https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}&ip=" -o /dev/null
EOF
chmod 644 /etc/cron.d/duckdns
systemctl restart cron || service cron restart || true

echo "==> 5/5 Done. Next steps:"
echo "   1) Copy project files onto this server, e.g. on your PC:"
echo "      scp -r pmautomation root@YOUR_SERVER_IP:/opt/"
echo "      (make sure .env is in pmautomation/.env)"
echo "   2) Then run:"
echo "      cd /opt/pmautomation && docker compose -f deploy/docker-compose.prod.yml up -d --build"
echo "   3) Open http://${DUCKDNS_DOMAIN}.duckdns.org in a browser."
