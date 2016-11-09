#!/usr/bin/python


from jinja2 import Environment, FileSystemLoader
import os
import sys

# Capture our current directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

x_min = -1000.0
x_max = 1000.0
y_min = -1000.0
y_max = 0.0
effective_nodes = []
effective_elements = []
dashpot_nodes_bottom = []
dashpot_nodes_left = []
dashpot_nodes_right = []
dashpot_elements_bottom = []
dashpot_elements_left = []
dashpot_elements_right = []
middle_point = -1
increment = 0.0
x_nodes = 0
y_nodes = 0

def create_nodes():
    counter = 1

    x_0 = x_min
    for i in range(x_nodes+1):

        y_0 = y_min
        for j in range(y_nodes+1):
            effective_nodes.append({'id':counter, 'x':x_0, 'y':y_0})
            y_0 += increment
            counter += 1
        x_0 += increment


def create_elements():

    starting = 1
    id = 1
    for x in range(x_nodes):
        for y in range(y_nodes):
            element = {'1':starting,'4':starting+1,'2':starting+y_nodes+1,'3':starting+y_nodes+2}
            effective_elements.append({'id':id, 'node':element})
            starting += 1
            id += 1
        starting += 1

def create_dashpot_nodes():

    id = len(effective_nodes) + 1

    y_0 = y_min
    x_0 = x_min
    # bottom
    for x in range(x_nodes+1):
        dashpot_nodes_bottom.append({'id':id,'x':x_0,'y':y_0})
        x_0 += increment
        id += 1

    # left
    y_0 = y_min
    x_0 = x_min

    for y in range(y_nodes+1):
        dashpot_nodes_left.append({'id':id,'x':x_0,'y':y_0})
        y_0 += increment
        id += 1


    # right
    y_0 = y_min
    x_0 = x_max
    for y in range(y_nodes+1):
        dashpot_nodes_right.append({'id':id,'x':x_0,'y':y_0})
        y_0 += increment
        id += 1


def create_dashpot_elements():

    id = len(effective_elements) + 1

    # bottom
    counter = 1
    for node in dashpot_nodes_bottom:
        mat = '2 3'
        if counter == 1 or counter == x_nodes+1:
            mat = '4 5'

        # find the node id of the normal node that corresponds to that node
        neighbor = -1
        for n in effective_nodes:
            if n['x'] == node['x'] and n['y'] == node['y']:
                neighbor = n['id']

        dashpot_elements_bottom.append({'node2':node['id'],'node1':neighbor,'id':id,'mat':mat})
        counter += 1
        id += 1

    # left
    counter = 1
    for node in dashpot_nodes_left:
        mat = '3 2'
        if counter == 1 or counter == y_nodes+1:
            mat = '5 4'

        dashpot_elements_left.append({'node2':node['id'],'node1':counter,'id':id,'mat':mat})
        id += 1
        counter += 1

    # right
    counter = 1
    for node in dashpot_nodes_right:
        mat = '3 2'
        if counter == 1 or counter == y_nodes+1:
            mat = '5 4'

        # find the node id of the normal node that corresponds to that node
        neighbor = -1
        for n in effective_nodes:
            if n['x'] == node['x'] and n['y'] == node['y']:
                neighbor = n['id']

        dashpot_elements_right.append({'node2':node['id'],'node1':neighbor,'id':id,'mat':mat})
        counter += 1
        id += 1


def find_middle_point():
    for node in effective_nodes:
        if node['x'] == 0.0 and node['y'] == 0.0:
            return node['id']
    return -1


def resolve_template():
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)
    print j2_env.get_template('model.tcl.j2').render(
        nodes=effective_nodes, elements=effective_elements,dashpot_nodes_bottom=dashpot_nodes_bottom,
        dashpot_nodes_right=dashpot_nodes_right,dashpot_nodes_left=dashpot_nodes_left,
        dashpot_elements_left=dashpot_elements_left,dashpot_elements_bottom=dashpot_elements_bottom,
        dashpot_elements_right=dashpot_elements_right, middle_point=middle_point, node_number=len(effective_nodes),
        elem_number=len(effective_elements),baseArea=increment
    )

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Please provide a resolution"
        print "%s resolution" %sys.argv[0]
        exit(1)

    y_nodes = int(sys.argv[1])
    x_nodes = 2*y_nodes
    increment = (y_max-y_min)/(y_nodes)

    create_nodes()
    create_elements()
    create_dashpot_nodes()
    create_dashpot_elements()
    middle_point = find_middle_point()
    if middle_point == -1:
        print "Could not find middle point"
        exit(1)
    resolve_template()


