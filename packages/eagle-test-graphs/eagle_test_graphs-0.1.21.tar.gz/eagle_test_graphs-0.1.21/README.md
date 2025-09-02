# EAGLE Test repository
This is the testing repository for DALiuGE graphs created with EAGLE. This repository is not meant to be used to keep operational graphs or palettes.

Installing the repository using `pip` will install the `eagle_test_graphs/daliuge_tests` as the `daliuge_tests` module. These test files are kept up to date and act as the current state of supported graphs across DALiuGE and EAGLE. 

Accessing the graphs when installed may be done accordingly: 

```
# Get directory eagle_test_graphs/daliuge_tests/dropmake/logical_graphs
import daliuge_tests.dropmake.logical_graphs as test_graphs 

# Make sure to use importlib over deprecated pkg_resources
from importlib.resources import files

directory = files(test_graphs) # Returns a pathlib.Path object

for child in directory.iterdir():
    # Perform operation on child.
``` 
