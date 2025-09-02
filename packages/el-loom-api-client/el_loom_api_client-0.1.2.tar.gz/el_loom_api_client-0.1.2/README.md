# Entropica Labs Loom API Client

A frontend API for generating QEC Loom Experiments. Use of this client requires a valid API token and API URL.

If you would like access to the Loom APIs, get in touch with us at [Entropica Labs](https://entropicalabs.com/contact).

# Creating a Client

To create a client to interact with the Loom APIs, you can use the `LoomClient` class. This class reads the configuration required to establish successful connections from (in order of precedence): inline constructor arguments, environment variables, the configuration file located in the user's home folder at `~/.loom/config.json`. There are no default values for the configuration options, so you must provide them in one of the ways described below.

## Using a Configuration File `[RECOMMENDED]` (search path: `~/.loom/config.json`)

```json
{
    "api_url": "https://api.example.com",
    "api_token": "**********"
}
```

```python
from el_loom_api_client import LoomClient

# Create client (will read from configuration file, if it exists)
client = LoomClient()
```

## Using Environment Variables

```shell
export LOOM_API_URL="https://api.example.com"
export LOOM_API_TOKEN="**********"
```

```python
from el_loom_api_client import LoomClient

# Create client (will use environment variables)
client = LoomClient()
```

## Using the constructor directly `[NOT RECOMMENDED]`

Alternatively you can pass the configuration options directly to the client (this will override any environment variables or configuration file):

```python
from el_loom_api_client import LoomClient

# Create client with explicit configuration. (WARNING: This is NOT RECOMMENDED for code that must be committed to a repository or shared, as this will expose your API token)
client = LoomClient(api_url="https://api.example.com", api_token="**********")
```

# Using the Client

In order to use the client, you should have already obtained a valid API token and the API URL. These instructions assume you have already done so.

# Create the client configuration file

You can create the configuration file in your user's home folder with the following content:

## MacOS/Linux:

```bash
mkdir -p ~/.loom && echo '{"api_url": "https://api.example.com", "api_token": "**********"}' > ~/.loom/config.json
```

## Windows:

```powershell
New-Item -Path "$HOME\.loom" -ItemType Directory -Force
Set-Content -Path "$HOME\.loom\config.json" -Value '{"api_url": "https://api.example.com", "api_token": "**********"}'
```

# Build a QEC experiment

Using the provided Models and the client, you can build a QEC experiment. The following example shows how to create a simple QEC memory experiment using the `MemoryExperiment` model and submit it to the Loom API.

```python
from el_loom_api_client import LoomClient
from el_loom_api_client.models import QECExperiment, Qubit, ErrorCorrectionCode

# Create client
client = LoomClient()

# Build the experiment model
experiment = MemoryExperiment(
    qec_code=Code("rotatedsurfacecode"),
    distance=3,
    num_rounds=[3, 5, 7],
    memory_type="Z",
    decoder=Decoder("Pymatching"),
    noise_parameters=[NoiseParameters(
        depolarizing=0.01, measurement=0.01, reset=0.01
    ), NoiseParameters(
        depolarizing=0.05, measurement=0.05, reset=0.05
    )],
    gate_durations={"x": 3e-8, "cx": 2e-7},
)

# Submit the experiment to the Loom API
run_id = client.experiment_run(experiment)

# Wait for the experiment result (asynchronous)
result = await client.get_result_async(run_id)

# Or wait for the experiment result (blocking)
result = client.get_result_sync(run_id)

# Print the result
print(result)
```
