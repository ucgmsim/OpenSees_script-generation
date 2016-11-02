# OpenSees script generation via Templates

This is an example of the usage of Jinja templates on Python to generate a TCL input script for
OpenSees. The target problem is the Lamb's problemn

## Prerequisites
You need to install [Jinja2](http://jinja.pocoo.org/) on your local system. The easiest way to do 
so is to use either pip or easy_install:

```
easy_install Jinja2
pip install Jinja2
```

## The template file

In order to create the template file, I started with a complete model for the given problem and stripped
off all the sections that can be automated, like the node list, element list and Lysmer dashpots on the 
boundaries.

Please note that the mesh generation is quite simple as it consists of regular quad elements covering a 
rectangular region. 

Every variable on the template is defined as `{{variable}}`. 

The templating engine can iterate over arrays or lists using the following construct:
```
{% for node in nodes %}
    node    {{node.id}} {{node.x}} {{node.y}}
{% endfor %}
```
This supposes that we will provide a variable called `nodes` which is a list of hashes of the form
`{'id':1,'x':-1000.0,'y':-1000.0}`. Note that `{{node.number}}` could be replaced by `{{node['number']}}`.

## The code

The script createModel.py will complete all the missing fields of the file model.tcl.j2 after doing
some calculations to generate the mesh.

I have defined a number of functions that will calculate the nodes, elements etc. To illustrate,
the function `create_nodes` will create the nodes according to the number of elements on the Y axis that we want.

Finally, the function:
```
def resolve_template():
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                             trim_blocks=True)
    print j2_env.get_template('model.tcl.j2').render(
       nodes=effective_nodes, elements=effective_elements,
       ...
       )
```
will do the replacement on model.tcl.j2, so that the variable `{{nodes}}` will actually take the values defined on
`effective_nodes` on the python code.

