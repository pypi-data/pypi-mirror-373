#!/bin/bash
set -e

DOMAIN=${SAMBA_DOMAIN:-TESTDOMAIN}
REALM=${SAMBA_REALM:-testdomain.local}
ADMIN_PASSWORD=${SAMBA_ADMIN_PASSWORD:-AdminPass123!}

echo "Starting Samba AD DC setup..."
echo "Domain: $DOMAIN"
echo "Realm: $REALM"

# Always remove existing smb.conf to avoid conflicts
echo "Removing any existing Samba configuration..."
rm -f /etc/samba/smb.conf

# Check if already provisioned
if [ ! -f /var/lib/samba/private/sam.ldb ]; then
    echo "Provisioning new Samba AD domain..."
    
    samba-tool domain provision \
        --use-rfc2307 \
        --domain="$DOMAIN" \
        --realm="$REALM" \
        --adminpass="$ADMIN_PASSWORD" \
        --server-role=dc \
        --dns-backend=SAMBA_INTERNAL \
        --option="dns forwarder = 8.8.8.8"
    
    echo "Domain provisioned successfully!"
    
    # Verify smb.conf was created
    if [ ! -f /etc/samba/smb.conf ]; then
        echo "ERROR: /etc/samba/smb.conf not created by provision!"
        exit 1
    fi
    
    echo "smb.conf created successfully:"
    head -10 /etc/samba/smb.conf
    
    # Start Samba temporarily to add users
    echo "Starting Samba daemon temporarily..."
    samba -D
    
    echo "Waiting for Samba to be ready..."
    sleep 20
    
    echo "Adding test users..."
    samba-tool user create testuser TestPass123! --given-name=Test --surname=User || echo "Failed to create testuser"
    samba-tool user create officeuser OfficePass123! --given-name=Office --surname=User || echo "Failed to create officeuser"
    
    echo "Test users creation attempted!"
    
    # Stop daemon for supervisord to take over
    pkill -f samba || echo "No samba process to kill"
    sleep 5
else
    echo "Samba AD domain already exists, skipping provision..."
fi

# Final verification
if [ ! -f /etc/samba/smb.conf ]; then
    echo "ERROR: /etc/samba/smb.conf not found!"
    echo "Listing /etc/samba contents:"
    ls -la /etc/samba/ || echo "Cannot access /etc/samba"
    exit 1
fi

echo "Starting supervised Samba daemon..."
exec "$@"