#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-}"
EMAIL="${2:-}"

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
  echo "Foydalanish: sudo bash deploy/nginx/enable-https.sh <domain> <email>"
  exit 1
fi

apt-get update
apt-get install -y certbot python3-certbot-nginx

certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" --redirect
systemctl reload nginx

echo "HTTPS yoqildi: https://$DOMAIN"
