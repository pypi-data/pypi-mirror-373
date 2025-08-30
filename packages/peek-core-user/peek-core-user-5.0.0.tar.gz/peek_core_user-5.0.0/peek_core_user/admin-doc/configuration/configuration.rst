.. _core_user_configuration:

Configuration
-------------

Edit Internal Users
```````````````````

This screen is used to configure the internal users in Peek.

When LDAP is enabled, users will appear in this screen when they first login.

.. note:: Internal users can be imported from other systems.

.. image:: edit-internal-user.png

To Create an Internal User
~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Click on **Add**
#. Enter the **User Details**
#. Enter a **Password**
#. Click on the **Plus** icon.
#. Select a **group** for the user
#. Click **Save**

.. note:: Users can be in multiple groups.

.. image:: add_user.png

To Delete an Internal User
~~~~~~~~~~~~~~~~~~~~~~~~~~

Click on the **minus** icon next to the user.

Edit Internal Groups
````````````````````

This screen is used to configure the internal groups in Peek.

Internal groups are not used when the authentication is set to LDAP.

.. note:: Internal groups can be imported from other systems.

.. image:: edit-internal-groups.png

To Add an Internal Group
~~~~~~~~~~~~~~~~~~~~~~~~

#. Click on **Add**
#. Enter the group **Name**
#. Enter the group **Title**
#. Click **Save**

.. image:: add_group.png

To Delete and Internal Group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Click on the **minus** icon next to the group.

Edit General Settings
`````````````````````

Configure the General Settings to configure the user plugin.

:Mobile Login Group: Users in this group will be permitted to login to the Peek Field UI.
        This applies to the Internal Authentication.

:Admin Login Group: Users in this group will be permitted to login to the Peek Admin UI.
        This applies to the Internal Authentication.

:Show Vehicle Input: Should the Peek login screen show a box to take the users
    vehicle ID.

:Show Login as List: Should the Peek Field UI login screen show a list of users, or an
    input box for a user name. (See Mobile Login Group)

:Allow Multiple Logins: Should the Peek only allow a user to login to the system
    on one device at a time.

:LDAP Auth Enabled: LDAP authentication is enabled, see **Edit LDAP Settings** for more
    configuration.

:Internal Auth Enabled For Field: Internal authentication will be tried for users logging
    in from the Peek Field UI.

:Internal Auth Enabled For Office: Internal authentication will be tried for users logging
    in from the Peek Office UI.

:Internal Auth Enabled For Admin: Internal authentication will be tried for users logging
    in from the Peek Admin UI.

.. image:: settings-general.png

Edit LDAP Settings
``````````````````

Configure the LDAP Settings to configure the user plugin.

Attunes LDAP works seamlessly against the Microsoft Active Directory
Lightweight Directory Service (AD LDS).

Peek provides support for multiple LDAP setting server settings. Each LDAP configuration
that applies to the respective login (Admin, Field, Office), will be tried.

----

The following is a good article that describes how to enable LDAP over SSL (LDAPS)
on Windows 2012.

`<https://social.technet.microsoft.com/wiki/contents/articles/2980.ldap-over-ssl-ldaps-certificate.aspx>`_

----

To configure LDAP:

#.  Select the **LDAP Settings** from the settings dropdown box,

#.  Set the LDAP settings, including "LDAP Enabled"

#.  Click Save

Now attempt to login with an LDAP user.

----

.. image:: settings-ldap.png

----

:Title: A unique name for this LDAP entry.

:For Admin: Should Peek attempt LDAP authentication for logins via the Peek Admin UI.

:For Office: Should Peek attempt LDAP authentication for logins via the Peek Office UI.

:For Field: Should Peek attempt LDAP authentication for logins via the Peek Field UI.

:Domain Name: The domain name of the LDAP installation,
    for example :code:`domain.example.org` where domain.example.org is the name of your
    active directory domain.

:URI: The connection string to the LDAP server, example values are:

    *  :code:`ldap://server1.example.org`

    *  :code:`ldap://domain.example.org`

    *  :code:`ldaps://10.2.2.2`

:CN Folders: This is a comma separated lost of CN paths to search during login.
        (Optional)

:OU Folders: This is a comma separated lost of OU paths to search during login.
        (Optional)

:LGroups: This is a comma separated list of groups. The user must belong to one of these
        groups for a successful login. (Optional)


