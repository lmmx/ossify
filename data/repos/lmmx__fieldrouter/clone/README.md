# fieldrouter: Data model validation for nested data routes

`fieldrouter` is a Python library that provides helpers for modelling routes in highly nested structured data.

It should be considered for cases when exhaustively modelling the tree structures involved is
surplus to requirements (in other cases you would simply use Pydantic in the regular way),
or perhaps if you want to specify 'routes' on an existing data model.

For example to access the number 30 in

```py
data = {"a": {"aa": {"aaa": [10, 20, 30]}}}
```

You would typically need to write Pydantic models for each level

```py
class A(BaseModel):
    a: AA

class AA(BaseModel):
    aa: AAA

class AAA(BaseModel):
    aaa: list[int]

thirty = A.model_validate(data).a.aa.aaa[2]
```

With `fieldrouter` you would instead specify a 'route' for the subpath on a 'router' model
(which is just a regular Pydantic model with default argument validation):

```py
from fieldrouter import Routing, RoutingModel

class A(RoutingModel):
    thirty: Routing(int, "a.aa.aaa.2")

thirty = A.model_validate(data).thirty
```

## Route syntax

### Relative references

You can reference another field in a route by prefixing its field name by a dot, such as `x` here:

```py
class B(RoutingModel):
    x: Routing(int, "foo.0.etc")
    b1: Routing(int, ".x.0.bar")
    b2: Routing(int, ".x.1.bar")
```

The prefix `.x` is substituted for `foo.0.etc` (the value of the Route for the field x).

This is equivalent to the following routes without references to the `x` field:

```py
class B(RoutingModel):
    x: Routing(int, "foo.0.etc")
    b1: Routing(int, "foo.0.etc.0.bar")
    b2: Routing(int, "foo.0.etc.1.bar")
```

Use this to keep your subpaths readable.


### The identity route

Sometimes when you're exploring nested data you want a reminder (or easy access to) the entire
data at a given route. This is available at the `.` route (the route string made up of a single
dot). This is known as the 'identity' route.

```py
class I(RoutingModel):
    full: Routing(dict, ".")
```

This will just give you the entire input, in this case as a dict field named `full`.

## Generics

> **Note**: deprecated since v1.0

You can also write routing models in a more 'longform' way, using one model for the routes and
another for the types:

```py
from fieldrouter.generic import RouterModel, Route

class Where(RouterModel):
    thirty: Route = "a.aa.aaa.2"
```

Then you can model the value at that route with a corresponding field on a 'routed' model
(which is a generic model which takes the router as a type argument):

```py
from fieldrouter.generic import Routed, R

class What(Routed[R]):
    thirty: int
```

Then you can use the router class as a generic type argument to the instance of the routee:

```py
model = What[Where].model_validate(data)
```
