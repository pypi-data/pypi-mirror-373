#!/bin/bash
echo "Step-by-step LDAP debugging using HOST ldapsearch..."

# Set environment variables for host ldap commands
export LDAPTLS_REQCERT=never
export LDAP_OPT_X_TLS_REQUIRE_CERT=never

echo "1. Check if ldap-utils is installed on host:"
which ldapsearch >/dev/null && echo "✓ ldapsearch available on host" || echo "✗ ldapsearch not found - install with: apt-get install ldap-utils"

echo ""
echo "2. Test basic LDAP port connectivity from host:"
nc -z localhost 636 && echo "✓ LDAPS port 636 accessible from host" || echo "✗ LDAPS port 636 not accessible"
nc -z localhost 389 && echo "✓ LDAP port 389 accessible from host" || echo "✗ LDAP port 389 not accessible"

echo ""
echo "3. Test anonymous LDAP connection from host:"
ldapsearch -H ldap://localhost:389 -x -s base -b "" 2>&1 | head -20

echo ""
echo "4. Test LDAPS authentication from host (with certificate ignore):"
echo "Testing LDAPS admin authentication:"
LDAPTLS_REQCERT=never ldapsearch -H ldaps://localhost:636 -x -D "Administrator@testdomain.local" -w AdminPass123! -b "DC=testdomain,DC=local" -s base 2>&1 | head -10

echo ""
echo "5. Search for testuser from host using LDAPS:"
echo "Searching for testuser in entire domain:"
LDAPTLS_REQCERT=never ldapsearch -H ldaps://localhost:636 -x -D "Administrator@testdomain.local" -w AdminPass123! -b "DC=testdomain,DC=local" "(sAMAccountName=testuser)" dn 2>&1

echo ""
echo "6. List all users from host:"
echo "Getting all user objects:"
LDAPTLS_REQCERT=never ldapsearch -H ldaps://localhost:636 -x -D "Administrator@testdomain.local" -w AdminPass123! -b "DC=testdomain,DC=local" "(objectClass=user)" sAMAccountName dn 2>&1 | grep -E "(dn:|sAMAccountName:)"

echo ""
echo "7. Check CN=Users container from host:"
echo "Searching CN=Users container:"
LDAPTLS_REQCERT=never ldapsearch -H ldaps://localhost:636 -x -D "Administrator@testdomain.local" -w AdminPass123! -b "CN=Users,DC=testdomain,DC=local" "(objectClass=user)" sAMAccountName dn 2>&1

echo ""
echo "8. Test testuser authentication from host:"
echo "Testing if testuser can authenticate:"
LDAPTLS_REQCERT=never ldapwhoami -H ldaps://localhost:636 -x -D "testuser@testdomain.local" -w TestPass123! 2>&1

echo ""
echo "9. Show container user list for comparison:"
docker exec ubuntu-samba-ad samba-tool user list