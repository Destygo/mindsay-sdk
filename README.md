<img src="https://www.mindsay.com/wp-content/uploads/2019/09/Mindsay-Logo.png"
	align="right" width="496" height="108">

# mindsay-sdk

The mindsay-sdk is a Mindsay python client that makes it easy to interact with the Mindsay chatbot building platform.
It requires an account on the Mindsay platform.

## Installation
`pip install -e git+https://github.com/Destygo/mindsay-sdk#egg=mindsay_sdk`

## Usage
```python
from mindsay_sdk import Client

# Create mindsay client. This line will ask for your password and email code.
client = Client('your.name@mindsay.com')

# Define current environment for next operations
client.set_current_instance(1)
client.set_current_experiment(1)
client.set_current_language('fr_FR')

...
```
