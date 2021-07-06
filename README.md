# Klogpy

Python implementation of the [klog](https://github.com/jotaen/klog) plain-text format with some utilities.  
Includes a parser and CLI.

## Installation

Klogpy can be installed via [PyPi](https://pypi.org/project/klogpy/), to install via pip:

```console
pip install klogpy
```

## Usage

Example:

```python
from klogpy import parser

s = '''
2021-01-01
Work on new frontend button
    9:00-17:30
    -45m Lunch
    -30h Coffee break
'''

records = parser.parse(s)

print(records[0])
# Record(
#   date=datetime.date(2021, 1, 1), 
#   properties=[None], 
#   summary=['Work on new frontend button'], 
#   entries=[
#       Entry(time=Range(start=[False, datetime.time(9, 0)], end=(False, datetime.time(17, 30))), description=''), 
#       Entry(time=Duration(is_neg=True, hours=0, minutes='45'), description='Lunch'), 
#       Entry(time=Duration(is_neg=True, hours='30', minutes=0), description='Coffee break')
#   ], 
#   tags=[]
# )
```

**CLI**

```console
$ klogpy --help
Usage: klogpy [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  entry   Manipulate entries for the active day
  init    Initialize a new record store if it does not exist
  record  Create or modify records
```