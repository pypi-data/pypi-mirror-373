==============
Administration
==============

The active task plugin manages tasks that Peek may issue to users.

For example, if a device user has a role of performing tasks, which are managed by Peek,
Peek will issue tasks to the user via this plugin.

Functionality
-------------

#.  The active task plugin receives tasks from other plugins
#.  The new tasks are persisted within the Peek Storage database
#.  Delivery to the users device is ensured
#.  Once the task is on the user device, it may be :

    -   Selected, this will open a screen.
    -   Actioned, actions will be delievered back to the initiating plugin back on
        the peek server.

#.  All tasks and the state of tasks are viewable from an administrators page.

Examples
--------

The following are use case examples of what can be done with the Active Task plugin.

#.  Notifications that arrive as read, and require no action.
    This can create an audit trail for the user.

#.  Notification that are unread until the user selects them.
    Selecting them will navigate to another plugin, the initiating plugin will be notified
    and it can then mark the task as read or delete it.

#.  Actions that are required. Actions can be created by initiating plugins,
    and stay "unread / unactioned" until the user completes what ever action is required
    within another plugin.
    The initiating plugin then removes or marks the action as completed.

#.  Question. A task can be created with multiple actions, upon selecting an action,
    the initiating plugin will be notified, it can then remove the task.

Design Diagram
--------------

.. image:: design_diagram.png