# Debug python in Visual Code / [Cloud Shell](http://ide.cloud.google.com/?boost=true)
## Configuration Example
* launch.json
   * If you have arguement like ``python3 simulate_api_rqsts.py 1 http://www.google.com``
```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "args":   [      "1","http://www.google.com"  ], 
            "console": "integratedTerminal"
        } 
    ]
}
```
* reference: https://stackoverflow.com/questions/59638889/passing-java-an-argument-while-debugging-in-vs-code