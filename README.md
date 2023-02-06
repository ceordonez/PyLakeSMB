# PyLakeSMB

`PyLakeSMB` is a Python package that is able to conduct a mass balance in the surface mixed layer (SML) in lakes considering a 1D lateral transport model considering horizontal disperion. This model consider flux to the atmosphere, bubble dissolution, diffusive flux from the littoral sediment and a zero order production/consumption term in the water column as boundary conditions.

## Installation
`PyLakeSMB` has been tested on linux OS and requieres python >= 3.8

### Python dependencies
````
pandas
scipy
matplotlib
PyYaml
openpyxl
````

### Install from Github
Clone or extract this package from github

```
git clone https://github.com/cordonez/PyLakeSMB
cd PyLakeSMB
```

## Quick start
Inside the folder `PyLakeSMB` execute

`python3 main.py`

It will execute the test lake. For further details please read the manual located in the `Manual` folder.
