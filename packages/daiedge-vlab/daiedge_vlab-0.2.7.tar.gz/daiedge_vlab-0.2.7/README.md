# dAIEdge VLab 
The [dAIEdge VLab](https://vlab.daiedge.eu/) is a benchmarking platform for edge AI devices. It allows users to run benchmarks on various edge devices and retrieve the results.

## Prerequisites
- An account on the dAIEdge VLab platform. You can create an account [here](https://vlab.daiedge.eu/register).
- Python 3.7 or higher 

## Setup 

Create a file `.yaml` in the root directory of the project and add the following content to it : 

```yaml
api:
    url: "vlab.daiedge.eu"
    port: "443"
    base_path: ""  # Optional, can be left empty

user : 
    email: "your-email"
    password: "your-password"
    
```

## Use the package

Give the `.yaml` file path to the `dAIEdgeVLabAPI` constructor.  The `dAIEdgeVLabAPI` object will try to log in to the API using the credentials provided in the `.yaml` file immediately after the object is created. 

```python
from daiedge_vlab import dAIEdgeVLabAPI

SETUP_FILE = "setup.yaml"

TARGET = 'rpi5'
RUNTIME = 'tflite'
MODEL = 'models/small_model.tflite'

if __name__ == '__main__':

    api = dAIEdgeVLabAPI(SETUP_FILE)
    id = api.startBenchmark(TARGET, RUNTIME, MODEL)

    result = api.waitBenchmarkResult(id)
    
    print(result)
```
