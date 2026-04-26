#!/usr/bin/env bash
set -euo pipefail

DOMAIN_OR_IP="${1:-}"

if [ -z "$DOMAIN_OR_IP" ]; then
  echo "Foydalanish: sudo bash deploy/nginx/enable-nginx.sh <domain-yoki-ip>"
  exit 1
fi

if ! command -v nginx >/dev/null 2>&1; then
  apt-get update
  apt-get install -y nginx
fi

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TEMPLATE="$PROJECT_DIR/deploy/nginx/sales-analyzer.conf"
TARGET="/etc/nginx/sites-available/sales-analyzer"

sed "s/YOUR_DOMAIN_OR_IP/$DOMAIN_OR_IP/g" "$TEMPLATE" > "$TARGET"
ln -sf "$TARGET" /etc/nginx/sites-enabled/sales-analyzer

if [ -f /etc/nginx/sites-enabled/default ]; then
  rm -f /etc/nginx/sites-enabled/default
fi

nginx -t
systemctl enable nginx
systemctl restart nginx

echo "Nginx aktivlashtirildi. Tekshirish: systemctl status nginx"
