# godto

Data Transfer Object (DTO) codegen from JSON schemas following the OpenAPI spec 

## Usage

### Full OpenAPI schema model

To work with an OpenAPI schema, load it with the `Model` class,
which is a Pydantic model (however note that the class name 'Model' comes from the OpenAPI spec).

```py
from godto.openapi.v3 import Model

model = Model.parse_raw(schema_json)
```

For example the Transport for London `StopPoint` API schema
is [shipped as package data][StopPoint_schema] in `tubeulator`.

[StopPoint_schema]: https://github.com/lmmx/tubeulator/blob/master/src/tubeulator/data/openapi/StopPoint/StopPoint.json

```py
from pathlib import Path

path_to_schema = Path("data/openapi/StopPoint/StopPoint.json")
schema_json = path_to_schema.read_text()
```

### Model helper functions

You can also work with partial views on the model, such as the paths and their parameters.

The examples in the following code block show `model_paths` which loads the schema for a given spec
(by default OpenAPI v3) and returns its parameters for a specific method (by default GET):

- `required`: whether the parameter is required or optional
- `schema_`: the schema for parsing the parameter
- `description`: the human-readable parameter docstring

```py
>>> from godto.api.model import model_paths
>>> param_requirements = model_paths(schema_json, extract="required")
>>> pprint(param_requirements)                                                      
{'/': {'categories': False,                                                         
       'lat': True,                                                                 
       'lon': True,                                                                 
       'modes': False,                                                              
       'radius': False,                                                             
       'returnLines': False,                                                        
       'stopTypes': True,                                                           
       'useStopPointHierarchy': False},                                             
 '/*': {},
 '/Meta/Categories': {},
 '/Meta/Modes': {},
...
>>> param_schemas = model_paths(schema_json, extract="schema_")
>>> param_descs = model_paths(schema_json, extract="description")            
>>> pprint(param_descs)                                                        
>>> pprint(param_descs)                                                             
{'/': {'categories': 'an optional list of comma separated property categories '     
                     "to return in the StopPoint's property bag. If null or "   
                     'empty, all categories of property are returned. Pass the '    
                     'keyword "none" to return no properties (a valid list of '     
                     'categories can be obtained from the '                         
                     '/StopPoint/Meta/categories endpoint)',                   
       'lat': 'Format - double. the latitude of the centre of the bounding '    
              'circle',                                                             
       'lon': 'Format - double. the longitude of the centre of the bounding '  
              'circle',                                                             
       'modes': 'the list of modes to search (comma separated mode names e.g. '
                'tube,dlr)',                                                        
       'radius': 'Format - int32. the radius of the bounding circle in metres '     
                 '(default : 200)',
...                  
```

## Requirements

Python 3.9+
