# Conditions

Conditions are always attached to a transition with a transition only being able to be triggered if **all** its conditions are satisfied. This provides the ability to conditionally turn on and off any transition by creating conditions. Conditions currently need an attached instance that can be evaluated which will look like this: `Attribute Name` &nbsp; &nbsp; &nbsp;`(Negate) Operator` &nbsp; &nbsp; &nbsp;`Expected Value`

## Columns:
Each column title has three lines on the right if you hover over it. Click on them to show options for that column. The second tab of the options menu will allow you to filter the column, the third to completely hide entire columns. Click on anywhere else on the column to order it, cycling between ascending, descending and no ordering. Hold shift while clicking to order multiple columns with individual weights.

### Transition:
The transition this condition is attached to.

### Attribute Name:
The name of the attribute on the attached instance. Its value will be evaluated against the condition.

### Operator:
The operator can be any of the following: `<`, `>`, `<=`, `>=`, `=`.

### Negate Operator:
Indicates if the operator should be negated. Will effectively reverse the result of the condition.

### Expected Value:
The expected value of the attribute that will satisfy the condition.

## Search Field:
Typing in the search field allows to filter the conditions by attribute name or expected value.
