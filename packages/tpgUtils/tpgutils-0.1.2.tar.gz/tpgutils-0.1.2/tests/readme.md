# TESTING

## NOTES

### from cmd line

Testing of the config module and the configparms_ext uses unittest.  This 
eliminates the need to install any package

1. cd to the tests directory
2. python -m unittest discover

All tests should pass

### in vs code

The tests are working in vscode when run from debug with this launch configuration in the workspace.

```
{
    "name": "Python: Current File",
    "type": "debugpy",
    "request": "launch",
    "program": "${file}",
    "env": {"PYTHONPATH": "${workspaceFolder}/tests"},
    "console": "integratedTerminal",
    "justMyCode": true
    },
```
