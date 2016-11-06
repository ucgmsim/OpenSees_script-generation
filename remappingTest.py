#!/usr/bin/python


from jinja2 import Environment, FileSystemLoader
import os
import sys
import re
import csv

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

def create_nodes(y_nodes):
    x_nodes = 2*y_nodes
    increment = (y_max-y_min)/(y_nodes)
    counter = 1

    x_0 = x_min
    for i in range(x_nodes+1):

        y_0 = y_min
        for j in range(y_nodes+1):
            effective_nodes.append({'id':counter, 'x':x_0, 'y':y_0})
            y_0 += increment
            counter += 1
        x_0 += increment


def create_elements(y_nodes):
    x_nodes = 2*y_nodes
    starting = 1
    id = 1
    for x in range(x_nodes):
        for y in range(y_nodes):
            element = {'1':starting,'2':starting+1,'4':starting+y_nodes+1,'3':starting+y_nodes+2}
            effective_elements.append({'id':id, 'node':element})
            starting += 1
            id += 1
        starting += 1

def create_dashpot_nodes(y_nodes):
    x_nodes = 2*y_nodes
    increment = (y_max-y_min)/(y_nodes)
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

def create_dashpot_elements(y_nodes):
    x_nodes = 2*y_nodes
    increment = (y_max-y_min)/(y_nodes)
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
        elem_number=len(effective_elements)
    )


# opening and parsing input file
input_file = "original.tcl"
f = open(input_file,'r+')
input_lines = f.readlines()
node_regex = re.compile("\s*node\s+(\d+)\s+(\-{0,1}\d+\.\d+)\s+(\-{0,1}\d+\.\d+)\s*")
vertex_regex = re.compile("\s*element quad (\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*")
orig_nodes = []

for line in input_lines:
    result_node = node_regex.match(line)
    if result_node != None:
        nodeId = result_node.group(1)
        nodeX = result_node.group(2)
        nodeY = result_node.group(3)

        orig_nodes.append({'id':nodeId,'x':float(nodeX),'y':float(nodeY)})






if __name__ == '__main__':

    y_elements = 100

    create_nodes(y_elements)
    create_elements(y_elements)
    create_dashpot_nodes(y_elements)
    create_dashpot_elements(y_elements)
    middle_point = find_middle_point()
    if middle_point == -1:
        print "Could not find middle point"
        exit(1)

    mapping_file = "mapping.csv"
    node_remapping = {}
    if os.path.isfile(mapping_file):
        # read
        with open(mapping_file,'r') as csvfile:
            r = csv.reader(csvfile,delimiter=' ')
            for row in r:
                node_remapping[int(row[0])] = int(row[1])
    else:
        # create remapping

        for node in effective_nodes:
            id,x,y = node['id'],node['x'],node['y']
            idx = -1
            for orig_node in orig_nodes:
                if x == orig_node['x'] and y == orig_node['y']:
                    idx = orig_node['id']
                    break
            node_remapping[id] = idx
            if idx == -1:
                print "Did not find corresponding node to %i" %id

        # write remapping to disk:
        with open('mapping.csv','w') as csvfile:
            w = csv.writer(csvfile,delimiter=' ')
            for key,val in node_remapping.iteritems():
                w.writerow([key,val])

    # change all id's with the remappings
    for node in effective_nodes:
        node['id'] = node_remapping[node['id']]
    for element in effective_elements:
        node = element['node']
        node['1'] = node_remapping[node['1']]
        node['2'] = node_remapping[node['2']]
        node['3'] = node_remapping[node['3']]
        node['4'] = node_remapping[node['4']]

    for elem in dashpot_elements_bottom:
        elem['node1'] = node_remapping[elem['node1']]

    for elem in dashpot_elements_left:
        elem['node1'] = node_remapping[elem['node1']]

    for elem in dashpot_elements_right:
        elem['node1'] = node_remapping[elem['node1']]

    resolve_template()


