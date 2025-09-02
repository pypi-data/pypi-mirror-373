#!/bin/bash
echo "Testing Samba AD LDAP functionality..."

# Track test failures
FAILED=0

echo "1. Container status:"
docker ps | grep ubuntu-samba-ad || { echo "Container not running"; FAILED=1; }

echo "2. Port connectivity:"
nc -z localhost 389 && echo "✓ Port 389 open" || { echo "✗ Port 389 closed"; FAILED=1; }
nc -z localhost 636 && echo "✓ Port 636 (LDAPS) open" || { echo "✗ Port 636 closed"; FAILED=1; }

echo "3. Basic LDAP connection:"
docker exec ubuntu-samba-ad ldapsearch -H ldap://127.0.0.1:389 -x -s base -b "" >/dev/null 2>&1 && echo "✓ Basic LDAP works" || { echo "✗ Basic LDAP failed"; FAILED=1; }

echo "4. Testing Samba process status:"
docker exec ubuntu-samba-ad pgrep samba >/dev/null 2>&1 && echo "✓ Samba process running" || { echo "✗ Samba process not running"; FAILED=1; }

echo "5. Testing configuration files exist:"
docker exec ubuntu-samba-ad test -f /etc/samba/smb.conf && echo "✓ smb.conf exists" || { echo "✗ smb.conf missing"; FAILED=1; }

echo "6. Testing domain database exists:"
docker exec ubuntu-samba-ad test -f /var/lib/samba/private/sam.ldb && echo "✓ Domain database exists" || { echo "✗ Domain database missing"; FAILED=1; }

echo ""
echo "Testing basic LDAP structure:"
echo "7. Testing LDAP root DSE query:"
docker exec ubuntu-samba-ad ldapsearch -H ldap://127.0.0.1:389 -x -s base -b "" "objectClass=*" >/dev/null 2>&1 && echo "✓ LDAP root DSE accessible" || { echo "✗ LDAP root DSE failed"; FAILED=1; }

# Exit with non-zero code if any tests failed
if [ $FAILED -eq 1 ]; then
    echo ""
    echo "❌ One or more tests failed!"
    exit 1
else
    echo ""
    echo "✅ All tests passed!"
    exit 0
fi