# OpenSees script generation via Templates

This is an example of the usage of Jinja templates on Python to generate a TCL input script for
OpenSees. The target problem is the Lamb's problemn

## Prerequisites
You need to install [Jinja2](http://jinja.pocoo.org/) on your local system. The easiest way to do 
so is to use either pip or easy_install:

`east_install Jinja2`

`pip install Jinja2`

## The code

The script createModel.py will complete all the missing fields of the file model.tcl.j2 after doing
some calculations to generate the mesh. We need to define a number of elements on the Y direction. 

In order to create the template file, I started with a complete model for the given problem and stripped
off all the sections that can be automated, like the node list, element list and Lysmer dashpots on the 
boundaries.

Please note that the mesh generation is quite simple as it consists of regular quad elements covering a 
rectangular region. 

