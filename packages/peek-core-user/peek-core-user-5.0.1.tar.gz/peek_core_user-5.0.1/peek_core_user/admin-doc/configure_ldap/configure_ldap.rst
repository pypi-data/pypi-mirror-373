.. _core_user_configure_ldap:


Configure LDAP for ADS
======================

This guide shows how to gather the necessary information from a Windows workstation to perform LDAP queries against Active Directory, using example data throughout.

Windows: Finding Your LDAP Distinguished Name
---------------------------------------------

From a Windows command prompt, get your full Distinguished Name (DN)::

    C:\> whoami /fqdn
    CN=John Smith,OU=IT Staff,OU=User Accounts,OU=Corporate,DC=utility,DC=com

From this output we can determine:
    - Your username: John Smith
    - Your OU path: IT Staff > User Accounts > Corporate
    - Your domain: utility.com

Windows: Finding Your Domain Controller
---------------------------------------

Get your authentication server's NetBIOS name: ::

    C:\> echo %logonserver%
    \\GOODAD


----

Convert the NetBIOS name to FQDN: ::

    C:\> nslookup GOODAD
    Server:  GOODAD.utility.com
    Address:  192.168.1.10

    Name:    GOODAD.utility.com
    Address:  192.168.1.10


Peek Node: Constructing Your :code:`ldapsearch` Command
-------------------------------------------------------

Start with this template and follow the substitution steps below:

1. Replace :code:`SERVER_FQDN` with the output of nslookup above
   - Example: :code:`ldap://GOODAD.utility.com`

2. Replace :code:`WHOAMI` with your full DN from whoami /fqdn
   - Example: :code:`CN=John Smith,OU=IT Staff,OU=User Accounts,OU=Corporate,DC=utility,DC=com`

3. Replace :code:`DOMAIN_DC` with just the DC portions of your DN
   - Look at your whoami /fqdn output
   - Take only the DC parts: :code:`DC=utility,DC=com`

::

    ldapsearch -H ldap://SERVER_FQDN \
      -D "WHOAMI" \
      -W \
      -b "DOMAIN_DC" \
      "(&(objectClass=group)(member=*))" \
      sAMAccountName description | tee ldapsearch.out


Final constructed command::

    # Basic group search
    ldapsearch -H ldap://GOODAD.utility.com \
      -D "CN=John Smith,OU=IT Staff,OU=User Accounts,OU=Corporate,DC=utility,DC=com" \
      -W \
      -b "DC=utility,DC=com" \
      "(&(objectClass=group)(member=*))" \
      sAMAccountName description | tee ldapsearch.out

Example output::

    # extended LDIF
    #
    # GOODAD.utility.com
    # base <DC=utility,DC=com> with scope subtree
    # filter: (&(objectClass=group)(member=*))
    # requesting: sAMAccountName description
    #

    dn: CN=Domain Admins,CN=Users,DC=utility,DC=com
    sAMAccountName: Domain Admins
    description: Designated administrators of the domain

    dn: CN=IT Support,OU=Security Groups,DC=utility,DC=com
    sAMAccountName: IT_Support
    description: IT Support staff access group

    dn: CN=Contractors,OU=Security Groups,DC=utility,DC=com
    sAMAccountName: Contractors
    description: External contractor access permissions

    # search result
    search: 2
    result: 0 Success

    # numResponses: 4
    # numEntries: 3

Command breakdown:
    - :code:`-H ldap://GOODAD.utility.com`: LDAP server URL from nslookup
    - :code:`-D "CN=John Smith..."}`: Your DN from whoami /fqdn
    - :code:`-W`: Prompt for password
    - :code:`-b "DC=utility,DC=com"`: Search base from domain components
    - Filter shows only groups with members
    - Returns group name and description

Alternative Searches
--------------------

Search for specific group patterns::

    # Search for IT-related groups
    ldapsearch -H ldap://GOODAD.utility.com \
      -D "CN=John Smith,OU=IT Staff,OU=User Accounts,OU=Corporate,DC=utility,DC=com" \
      -W \
      -b "DC=utility,DC=com" \
      "(&(objectClass=group)(sAMAccountName=IT*))" \
      sAMAccountName description | tee ldapsearch.out

Example output::

    dn: CN=IT Support,OU=Security Groups,DC=utility,DC=com
    sAMAccountName: IT_Support
    description: IT Support staff access group

    dn: CN=IT Admins,OU=Security Groups,DC=utility,DC=com
    sAMAccountName: IT_Admins
    description: IT Administrative access

Troubleshooting:
    - Verify connectivity: :code:`ping GOODAD.utility.com`
    - Test ports: :code:`telnet GOODAD.utility.com 389`
    - Verify DNS: :code:`nslookup GOODAD.utility.com`
    - Common error: "ldap_bind: Invalid credentials (49)"
      - Usually means wrong password or expired account
    - Common error: "ldap_sasl_bind(SIMPLE): Can't contact LDAP server (-1)"
      - Usually means firewall blocking port 389 or wrong hostname

Configuring Peek LDAP Settings
------------------------------

After gathering your LDAP information, populate the Peek LDAP Settings screen
with the following example configuration:

1. **Title**: A descriptive name for your organization
   - Example: :code:`CORP`

2. **URI** : The LDAP server URL with protocol prefix
   - Format: :code:`ldap://SERVER_FQDN`
   - Example: :code:`ldap://GOODAD.utility.com`

3. **Domain**: Your domain from the DC components
   - Example: :code:`utility.com`

4. **CN Folders**: Can be left empty if not needed
   - Used for specific CN path restrictions

5. **OU Folders**: The OU path for user accounts
   - Example: :code:`/IT Staff/User Accounts/Corporate`
   - Note: Must start with forward slash

6. **Groups**: The AD group for access control
   - Example: :code:`IT Support`

7. **Agent Host**: The IP address of the Peek Agent node that will make the
   LDAP queries, or blank to have Peek logic do it.
   - Example: :code:`192.168.1.10`

8. **Permission toggles**:
   - "For Admin": Disabled
   - "For Office": Enabled (blue)
   - "For Field": Disabled

Note: This configuration grants office-level access to IT Support members in the
:code:`/IT Staff/User Accounts/Corporate` organizational unit.


.. image:: ldap_example.png