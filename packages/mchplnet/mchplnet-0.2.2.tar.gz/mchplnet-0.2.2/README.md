<p align="center">
  <img src="https://raw.githubusercontent.com/X2Cscope/pyx2cscope/refs/heads/main/doc/images/pyx2cscope_logo.png" alt="PyX2CScope Logo" width="250">
</p>

# mchplnet
- mchplnet is the Python implementation of the LNet protocol.
- It implements multiple LNet services to communicate to embedded systems/microcontrollers.
- Currently only pyserial interface is supported. 
- It is recommended to use the pyx2cscope package, which offers a higher-level interface.

## Getting Started
1. Navigate to the Examples directory in the mchplnet project to explore the available examples or create a new .py file based on your requirements.
2. Import the necessary classes:
```
from mchplnet.interfaces.factory import InterfaceFactory
from mchplnet.interfaces.factory import InterfaceType as IType
from mchplnet.lnet import LNet
```
3. Create an interface according to your requirements and initialize the LNet with the interface:
```
interface = InterfaceFactory.get_interface(IType.SERIAL, port="COM8", baudrate=115200)
l_net = mchplnet.LNet(interface))
```
4. Use the appropriate functions, such as get_ram, to interact with variables by specifying their address and size:

```
var_address = 0x00000000
var_size = 4 
var_value = l_net.get_ram(var_address, var_size) 
logging.debug(var_value)
```
5. To modify the value of a variable, use the put_ram function:

```
var_newValue = 500
l_net.put_ram(var_address, var_size, var_newValue)
```

## Contribute
If you discover a bug or have an idea for an improvement, we encourage you to contribute! You can do so by following these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make the necessary changes and commit them. 
4. Push your changes to your forked repository. 
5. Open a pull request on the main repository, describing your changes.

We appreciate your contribution!



-------------------------------------------------------------------



