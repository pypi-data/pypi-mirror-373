# Join Steps

A join step joins multiple steps into one. Waits until all incoming transitions are done by default. If _Wait For All_ is False the first incoming transition cancels all other active incoming transitions. The step of choice for merging different workflow trees back into one.

## Columns:
Each column title has three lines on the right if you hover over it. Click on them to show options for that column. The second tab of the options menu will allow you to filter the column, the third to completely hide entire columns. Click on anywhere else on the column to order it, cycling between ascending, descending and no ordering. Hold shift while clicking to order multiple columns with individual weights.

### Name:
The name of the step.

### Workflow:
The workflow this step belongs to.

### Wait For All:
Indicates wether the step will wait for all incoming transitions to be finished until triggering the next transition. If False, the step will instead cancel all other active incoming transitions as soon as it is reached before triggering the next transition.

### Status:
The status that will be set in the attached instance's status field upon transitioning to this step. Only applicable if attached model is set.

### Code:
A number representation of this step. Must be unique per workflow.

### Permission:
Defines which permission is needed to be able to view this step being executed.

## Filters:
Filters are accessed by clicking on the symbol in the top left corner of the window.

### Associated Transition:
Displays every step that the specified transition is a part of.

## Search Field:
Typing in the search field allows to filter the steps by name.
