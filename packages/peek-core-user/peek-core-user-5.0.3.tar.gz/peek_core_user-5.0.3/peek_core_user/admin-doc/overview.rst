Overview
--------

The following sections describe the parts of the User plugin.

Other plugins can integrate with the user plugin, integrating login hooks,
loading the current user details, etc.

Credential Checking
```````````````````
The user plugin provides either internal password credential checking or validation
against LDAPS services such as AD LDS.

Logged In User Status
`````````````````````

The device plugin provides the logged in / logged out status of the users.

User and Group Importing
````````````````````````

The user plugin has APIs that allow other plugins to import users and groups
from other systems.

These imported users and groups will end up in the Internal Users and Internal Groups
in the Peek admin screen.