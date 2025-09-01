<a href="https://www.oceandata.earth/">
    <img src="assets/ODP-SDK.png" alt="ODP SDK logo" title="ODP" align="right" height="100" />
</a>


# ODP Python SDK

Connect to the Ocean Data Platform with Python through the Python SDK. Download queried ocean data easily and efficiently into data frames, for easy exploring and further processing in your data science project.

## Documentation

[https://docs.hubocean.earth/sdk/](https://docs.hubocean.earth/sdk/)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the Ocean Data Platform Python SDK.

```bash
pip3 install odp_sdk
```
 
## Usage

*Note: Accessing the Ocean Data Platform requires an authorized account. Contact ODP to require one.*

```python
from odp.client import OdpClient

client = OdpClient()

for item in client.catalog.list():
    print(item)
```

Examples can be found in /examples. 


## Testing in Python Notebook
1. Build the Package Locally
```
cd python_sdk
poetry build
```

2. Create a python notebook and test the package
- Building a python vitual environment locally will help you avoid conflicts with other versions of this package.

3. Install the Package Locally from the dist folder
```
pip install dist/<your-package-name>-<version>-py3-none-any.whl
```

To install in editable mode:
```
pip install -e dist/<your-package-name>-<version>-py3-none-any.whl
```

4. Test the new functionalities pointing to PR, Dev or Prod

5. Uninstall the package
```
pip uninstall -y dist/<your-package-name>-<version>-py3-none-any.whl
```


