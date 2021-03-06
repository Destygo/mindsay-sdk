# mindsay-sdk

<img src="https://assets.website-files.com/5cd5a36e899e7006018481c6/5cd5a3cc00916566208b8bfc_logo.svg" align="right" width="248" height="54">

The mindsay-sdk is a python client that makes it easy to interact with the Mindsay's chatbot platform.
A Mindsay account is required.

## Installation
Install latest release: `pip install mindsay-sdk`

Install latest dev version: `pip install git+https://github.com/destygo/mindsay-sdk@staging`

## Usage
```python
from mindsay_sdk import Client

# Create mindsay client. This line will ask for your password and email code.
client = Client("your.name@mindsay.com")

# Define current environment for next operations
client.set_current_instance(1)
client.set_current_experiment(1)
client.set_current_language("fr_FR")

user_nodes = client.get_user_nodes()
print(user_nodes)
```
```
[{'name': 'Main',
  'record_id': 1,
  'service_record_id': None,
  'exploring': None,
  'display_name': '/Main',
  'resource_url': '/user_nodes/1'},
 {'name': 'After Itineraire',
  'record_id': 2,
  'service_record_id': 1,
  'exploring': None,
  'display_name': 'Itineraire/After Itineraire',
  'resource_url': '/user_nodes/2'},
 {'name': 'After Orientation',
  'record_id': 3,
  'service_record_id': 2,
  'exploring': None,
  'display_name': 'Orientation/After Orientation',
  'resource_url': '/user_nodes/3'}]
```
More examples can be found in the `examples/` folder.

# Development

Clone the repository and run in your virtual environment:
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```
