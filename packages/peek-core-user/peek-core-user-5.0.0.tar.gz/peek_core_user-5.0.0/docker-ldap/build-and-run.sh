#!/bin/bash
set -e

echo "Building Samba AD Docker image..."

# Build the image
docker build -t ubuntu-samba-ad .

echo "Stopping any existing container and cleaning volumes..."
docker stop ubuntu-samba-ad 2>/dev/null || true
docker rm ubuntu-samba-ad 2>/dev/null || true
docker volume rm samba-data samba-config 2>/dev/null || true

echo "Starting Samba AD container with fresh volumes..."
docker run -d \
    --name ubuntu-samba-ad \
    --privileged \
    -p 389:389 \
    -p 636:636 \
    -e SAMBA_DOMAIN=TESTDOMAIN \
    -e SAMBA_REALM=testdomain.local \
    -e SAMBA_ADMIN_PASSWORD=AdminPass123! \
    ubuntu-samba-ad

echo "Waiting for container to start (60 seconds for full startup)..."
sleep 60

echo "Container logs:"
docker logs ubuntu-samba-ad

# Check if container is still running
if ! docker ps | grep -q ubuntu-samba-ad; then
    echo "Container stopped, attempting to restart..."
    docker start ubuntu-samba-ad
    sleep 30
    echo "Restarted container logs:"
    docker logs ubuntu-samba-ad --tail 20
fi

echo "Detailed Samba logs:"
docker exec ubuntu-samba-ad cat /var/log/supervisor/samba.out.log 2>/dev/null || echo "No Samba stdout logs yet"
docker exec ubuntu-samba-ad cat /var/log/supervisor/samba.err.log 2>/dev/null || echo "No Samba stderr logs yet"

# Check if Samba config exists and is valid
echo "Checking Samba configuration:"
docker exec ubuntu-samba-ad ls -la /etc/samba/ 2>/dev/null || echo "Cannot access /etc/samba"
docker exec ubuntu-samba-ad cat /etc/samba/smb.conf 2>/dev/null || echo "No smb.conf found"

# Try to run samba manually to see the error
echo "Trying to run Samba manually:"
docker exec ubuntu-samba-ad /usr/sbin/samba --help >/dev/null 2>&1 && echo "Samba binary is OK" || echo "Samba binary has issues"
docker exec ubuntu-samba-ad /usr/sbin/samba --foreground --no-process-group 2>&1 | head -20 || echo "Manual Samba start failed"

echo "Testing LDAP connectivity..."
docker exec ubuntu-samba-ad timeout 10 bash -c 'until nc -z localhost 389; do sleep 1; done' 2>/dev/null && echo "✓ LDAP port 389 is accessible" || echo "✗ LDAP connection failed"

echo "Testing authentication..."
docker exec ubuntu-samba-ad ldapsearch -H ldap://localhost:389 -x -D "Administrator@testdomain.local" -w AdminPass123! -b "DC=testdomain,DC=local" "(objectClass=user)" cn 2>/dev/null && echo "✓ LDAP authentication working" || echo "✗ LDAP authentication failed"

echo ""
echo "Setup complete!"
echo "If there are errors above, check the logs with:"
echo "  docker logs ubuntu-samba-ad"
echo "  docker exec ubuntu-samba-ad cat /var/log/supervisor/samba.err.log"