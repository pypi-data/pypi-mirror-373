# Orderable View

An orderable view enables the user to freely reorder rows inside AG Grid by drag-and-drop.

**NOTE**: As these changes are saved in a model field, this will change the order globally for each user! Reordering on a per-user basis requires a way more sophisticated approach that is currently out of scope. Please also keep in mind that this also means that different orders for different views of the same model are not possible.

## Implementation Steps

### Simple Reordering

Reorder rows inside a basic list view. Also includes the first level of tree views (level 0).

1. Add the `OrderableModel` from `wbcore.models.orderable` to your model and migrate. Set initial values for existing instances by either `Model.orderable_objects.reset_order()` or calling `save()` on every object.
2. Add the `order` field to your serializer.
3. Add the `OrderableMixin` from `wbcore.viewsets.mixins` to your viewset. If you have defined a viewset ordering, make sure to first order by `order`.
4. Add both `reorderable_column="order"` and `reorderable_endpoint=reverse(f"{endpoint.basename}-reorder", args=["{{id}}"], request=self.request)` to your list display.

### Tree Child Reordering

We currently only support reordering the first child row (i.e. level 1).

1. Add the `OrderableModel` from `wbcore.models.orderable` to your model and migrate. Also add the class variable `PARTITION_BY` to your class and set it to the name of the foreign key field to the child's parent to partition the order values based on the parent. In this case the order number is unique only for the parent and not over the entire model anymore. Set initial values for existing instances by either `Model.orderable_objects.reset_order()` or calling `save()` on every object.
2. Add the `order` field to your serializer.
3. Add the `OrderableMixin` from `wbcore.viewsets.mixins` to your viewset. If you have defined a viewset ordering, make sure to first order by `order`.
4. Add both `tree_reorderable_column="order"` and `tree_reorderable_endpoint=reverse(f"{endpoint.basename}-reorder", args=["{{id}}"], request=self.request)` to **the parent's** list display.

## Example

For an example please take a look at _example_app/team_. In this case we wanted both level 0 (Team) and level 1 (Player) to be reorderable so this example incorporates both a simple reordering for the parent level and a tree child reordering for the child level.
