# User Steps

A user step needs an assigned user or user group to manually pick the next transition.

## Columns:
Each column title has three lines on the right if you hover over it. Click on them to show options for that column. The second tab of the options menu will allow you to filter the column, the third to completely hide entire columns. Click on anywhere else on the column to order it, cycling between ascending, descending and no ordering. Hold shift while clicking to order multiple columns with individual weights.

### Name:
The name of the step.

### Workflow:
The workflow this step belongs to.

### Status:
The status that will be set in the attached instance's status field upon transitioning to this step. Only applicable if attached model is set.

### Code:
A number representation of this step. Must be unique per workflow.

### Permission:
Defines which permission is needed to be able to view this step being executed.

### Assignee:
A selected assignee needs to choose the next transition.

### Group:
From a selected group anyone can progress the workflow by choosing the next transition. Exclusive with assignee field.

### Assignee Method:
Automatically chooses a the step's assignee possibly picking from the provided group depending on the method's implementation. Exclusive with assignee field.

### Notify User:
If True, sends a notification to all assigned users to remind them that they need to pick the next transition.

## Filters:
Filters are accessed by clicking on the symbol in the top left corner of the window.

### Associated Transition:
Displays every step that the specified transition is a part of.

## Search Field:
Typing in the search field allows to filter the steps by name, assignee or group.
