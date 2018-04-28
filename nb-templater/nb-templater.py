import json
import argparse
import datetime

desc = """\
A tool to generate a Python script that can generate a Jupyter
notebook programmatically, using an existing Jupyter notebook as
a template."""

parser = argparse.ArgumentParser(description=desc)
parser.add_argument('-f', '--filename', help='Filename of Jupyter noteboo to use as template')
parser.add_argument('-o', '--output', help='Filename of output script')
parser.add_argument('-n', '--nboutput', help='Filename of Jupyter notebook generated by output script.')

args = parser.parse_args()

filename = args.filename

# Read in Jupyter notebook template file
with open(filename, 'r') as file:
    ipynb = json.load(file)

nb_cells = []
output_str = ""

# Parse cells in Jupyter notebook template
for cell in ipynb['cells']:
    cell_type = cell['cell_type']
    source = cell['source']
    nb_cells.append([cell_type, source])

now = datetime.datetime.now()
datetime_now = now.strftime("%Y-%m-%d %H:%M %Z")

output_header="""\
# `nb_templater` generated Python script
# Generated from .ipynb template: {}
# www.github.com/ismailuddin/nb-templater/
# Generated on: {}

import nbformat as nbf 
import sys
nb = nbf.v4.new_notebook() \n\n""".format(args.filename, datetime_now)

cell_template_string = """\
cell_{0}=\"\"\"\\
{1}
\"\"\"\n
"""

output_str += output_header

# Generate string variable declarations of cell contents
for i, cell in enumerate(nb_cells):
    _source = ''.join(cell[1])
    _cell = cell_template_string.format(i, _source)
    output_str += _cell


nb_cells_generator_str = """\
nb['cells'] = [
{}
]
"""

mdown_cell_str = """\
    nbf.v4.new_markdown_cell({})"""

code_cell_str = """\
    nbf.v4.new_code_cell({})"""

_list_of_cells = []

# Generate Python list of cells
for i, cell in enumerate(nb_cells):
    if cell[0] == 'markdown':
        _cell = mdown_cell_str.format("cell_{}".format(i))
        _list_of_cells.append(_cell)
    elif cell[0] == 'code':
        _cell = code_cell_str.format("cell_{}".format(i))
        _list_of_cells.append(_cell)

list_of_cells = ',\n'.join(_list_of_cells)

nb_cells_generator = nb_cells_generator_str.format(list_of_cells)

output_str += nb_cells_generator

if args.nboutput:
    nb_output_name = args.nboutput 
else:
    nb_output_name = "_" + args.filename

write_nb = """\n
nbf.write(nb, '{0}')
print("Jupyter notebook {0} successfully generated.")
""".format(nb_output_name)

output_str += write_nb

# Output Python script file
with open(args.output, 'w') as output:
    output.write(output_str)

print("Python script {} generated sucessfully.".format(args.output))

