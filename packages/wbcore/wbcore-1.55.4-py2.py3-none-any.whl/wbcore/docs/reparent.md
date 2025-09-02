# Reparent View

A reparent view enables the user to switch a child's parent object inside a tree view by drag-and-dropping the child inside the new parent. Please note that this is currently only supported with level 1 children inside the tree view.

## Implementation Steps

1. Add a `PARENT_FK` class variable to the child's model and set it to the field name of the foreign key to the parent.
2. Add the `ReparentMixin` from `wbcore.viewsets.mixins` to your viewset.
3. Add both `tree_reparent_pk_field=f"{pk_field_name}"` and `tree_reparent_endpoint=reverse(f"{endpoint.basename}-reparent", args=["{{id}}"], request=self.request)` to the parent's list display.

## Example

For an example please take a look at _example_app/team_. Drag-and-dropping a child (Player) inside a new parent (Team) will transfer this player to a new team.
