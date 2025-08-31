=======================
Peek Active Task Plugin
=======================

Overview
--------

The active task plugin manages tasks that Peek may issue to users.

For example, if a device user has a role of performing tasks, which are managed by Peek, Peek will issue tasks to the user via this plugin.

Functionality
-------------

*   The active task plugin receives tasks from other plugins

*   The new tasks are persisted within the Peek Storage database

*   Delivery to the users device is ensured

*   Once the task is on the user device, it may be :

    -   Selected, this will open a screen.

    -   Actioned, actions will be delivered back to the initiating plugin back on the peek server.

*   All tasks and the state of tasks are viewable from an administrators page.


Synerty Internal Design Document
--------------------------------

https://doc.synerty.com/display/PEEK/Active+Task

