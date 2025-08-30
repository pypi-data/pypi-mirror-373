import pytest
from typing import Dict, Any
from cliify import commandParser, command

# Test fixtures and helper classes



@commandParser
class DeviceBase:
    def __init__(self, name: str):
        self.name = name
        
    @command(help="Simple test command")
    def test_command(self, arg1: int, arg2: str = "default"):
        return f"Received {arg1} and {arg2}"

@commandParser
class DeviceSub(DeviceBase):
    def __init__(self, name: str):
        super().__init__(name)
        
    @command(help="Sub command")
    def sub_command(self, arg1: int):
        return f"Sub command received {arg1}"   

@commandParser
class DeviceComplex:
    def __init__(self, name: str):
        self.name = name
        self.data = {}
        
    @command(help="Store data with label")
    def store_data(self, label: str = None, data: bytes = None):
        self.data[label] = data
        return len(data)

@commandParser(subparsers=['devices'])
class InterfaceBase:
    def __init__(self, name: str):
        self.name = name
        self.devices: Dict[str, DeviceBase] = {}

    def get_completions(self):
        return [0,1738]
        
    @command(help="Add two numbers", completions={'a': [1, 2, 3, 4, 5], 'b': lambda self: self.get_completions()})
    def add_numbers(self, a: int, b: int):
        return a + b
    
    @command(help="Subtract two numbers", completions={'a': lambda self: self.get_completions()})
    def sub_numbers(self, a: int, b: int):
        return a - b
    
    def add_device(self, device):
        self.devices[device.name] = device

@commandParser(allow_eval=True, subparsers=['interfaces', 'mainInterface', 'extraInterfaces'])
class SessionBase:
    def __init__(self):

        self.interfaces: Dict[str, InterfaceBase] = {}

        self.mainInterface = InterfaceBase('main')
    
    def add_interface(self, interface):
        self.interfaces[interface.name] = interface

@pytest.fixture
def setup_session():
    session = SessionBase()
    interface = InterfaceBase('test_interface')
    device = DeviceBase('test_device')
    interface.add_device(device)
    session.add_interface(interface)
    return session

def test_simple_command():
    device = DeviceBase('test')
    result = device.parseCommand("test_command arg1: 42")
    assert result == "Received 42 and default"
    
    result = device.parseCommand("test_command arg1: 42, arg2: custom")
    assert result == "Received 42 and custom"


def test_complex_device():
    device = DeviceComplex('test')
    result = device.parseCommand("store_data label: test, data: b'hello'")
    assert result == 5
    assert device.data['test'] == b'hello'


def test_single_subparser():

    session = SessionBase()

    result = session.parseCommand("mainInterface.add_numbers a: 2, b: 3")
    assert result == 5



def test_nested_commands_with_include_name():
    @commandParser(subparsers=['devices'], include_subparser_name=True)
    class InterfaceWithNames:
        def __init__(self, name: str):
            self.name = name
            self.devices: Dict[str, DeviceBase] = {}
            
        def add_device(self, device):
            self.devices[device.name] = device
            
    interface = InterfaceWithNames('test_interface')
    device = DeviceBase('test_device')
    interface.add_device(device)
    
    # With include_subparser_name=True, we need to include 'devices' in the path
    result = interface.parseCommand("devices.test_device.test_command arg1: 42")
    assert result == "Received 42 and default"

def test_bytes_conversion_2():

    @commandParser
    class DeviceBytesProcessor:
        def __init__(self, name: str):
            self.name = name
            self.data = {}
            
        @command
        def handleBytes(self, data: bytes):
            return data
    
    device = DeviceBytesProcessor('test')
    result = device.parseCommand("handleBytes data: b'hello'")
    assert result == b'hello'

    result = device.parseCommand("handleBytes data: [0x01 ,0x02 ,0x03]")
    assert result == b'\x01\x02\x03'

    result = device.parseCommand("handleBytes data: 0x01 0x02 0x03")
    assert result == b'\x01\x02\x03'

    result = device.parseCommand("handleBytes data: hello world")
    assert result == b'hello world'



def test_nested_commands_without_include_name():
    @commandParser(subparsers=['devices'])  # Default is include_subparser_name=False
    class InterfaceWithoutNames:
        def __init__(self, name: str):
            self.name = name
            self.devices: Dict[str, DeviceBase] = {}
            
        def add_device(self, device):
            self.devices[device.name] = device
            
    interface = InterfaceWithoutNames('test_interface')
    device = DeviceBase('test_device')
    interface.add_device(device)
    
    # Without include_subparser_name=True, we can skip 'devices' in the path
    result = interface.parseCommand("test_device.test_command arg1: 42")
    assert result == "Received 42 and default"

def test_inheritance_support():
    @commandParser
    class BaseDevice:
        def __init__(self, name: str):
            self.name = name
            
        @command()
        def base_command(self, arg: int) -> str:
            return f"Base {arg}"
    
    @commandParser
    class DerivedDevice(BaseDevice):
        @command()
        def derived_command(self, arg: int) -> str:
            return f"Derived {arg}"
    
    device = DerivedDevice('test')
    
    # Should be able to call both base and derived commands
    result = device.parseCommand("base_command 42")
    assert result == "Base 42"
    
    result = device.parseCommand("derived_command 43")
    assert result == "Derived 43"

def test_subparser_inheritance():
    @commandParser
    class BaseDevice:
        def __init__(self, name: str):
            self.name = name
            
        @command()
        def base_command(self, arg: int) -> str:
            return f"Base {arg}"
    
    @commandParser
    class DerivedDevice(BaseDevice):
        def __init__(self, name: str):
            super().__init__(name)

            
        @command()
        def derived_command(self, arg: int) -> str:
            return f"Derived {arg}"

    @commandParser(subparsers=['devices'])
    class Interface:
        def __init__(self):
            self.devices = {
                'dev1': DerivedDevice('dev1')
            }
    
    interface = Interface()
    
    # Test accessing base command through inheritance
    result = interface.parseCommand("dev1.base_command 42")
    assert result == "Base 42"
    
    # Test accessing derived command
    result = interface.parseCommand("dev1.derived_command 43")
    assert result == "Derived 43"
    
    # Test accessing nested subdevice
    result = interface.parseCommand("dev1.base_command 44")
    assert result == "Base 44"

def test_dynamic_subparser_modification():
    @commandParser(subparsers=['subdevices'])
    class DynamicDevice:
        def __init__(self, name: str):
            self.name = name
            self.subdevices = {}
            
        @command()
        def add_subdevice(self, name: str) -> str:
            self.subdevices[name] = DynamicDevice(name)
            return f"Added {name}"
            
        @command()
        def echo(self, msg: str) -> str:
            return f"{self.name}: {msg}"
    
    device = DynamicDevice('root')
    
    # Add a subdevice
    result = device.parseCommand("add_subdevice test")
    assert result == "Added test"
    
    # Should be able to use the newly added subdevice
    result = device.parseCommand("test.echo hello")
    assert result == "test: hello"

def test_override_command():
    @commandParser
    class BaseDevice:
        def __init__(self, name: str):
            self.name = name
            
        @command()
        def echo(self, msg: str) -> str:
            return f"Base: {msg}"
    
    @commandParser
    class DerivedDevice(BaseDevice):
        @command()
        def echo(self, msg: str) -> str:
            return f"Derived: {msg}"
    
    device = DerivedDevice('test')
    
    # Should use the overridden command
    result = device.parseCommand("echo hello")
    assert result == "Derived: hello"

def test_sub_class_command_with_inheritance():

    @commandParser(subparsers=['devices'])
    class InterfaceWithSub:
        def __init__(self, name: str):
            self.name = name
            self.devices: Dict[str, DeviceBase] = {}
            
        def add_device(self, device):
            self.devices[device.name] = device

    device = DeviceSub('test')
    interface = InterfaceWithSub('test_interface')

    interface.add_device(device)

    result = interface.parseCommand("test.test_command arg1: 42")
    assert result == "Received 42 and default"


def test_eval_expression(setup_session):
    session = setup_session
    result = session.parseCommand("test_interface.add_numbers a: $(2 * 3), b: $(5 + 5)")
    assert result == 16

def test_completion_tree(setup_session):
    session = setup_session
    tree = session.getCompletionTree()
    
    # Verify structure

    assert 'test_interface' in tree
    assert 'test_device' in tree['test_interface']
    assert 'add_numbers' in tree['test_interface']
    assert {'a'  :[1,2,3,4,5], 'b':[0,1738]} == tree['test_interface']['add_numbers']

def test_completions(setup_session):
    session = setup_session
    
    # Test root level completion
    completions = session.getCompletions("")
    assert 'test_interface' in completions
    
    # Test nested completion
    completions = session.getCompletions("test_interface.")
    assert 'test_device' in completions
    assert 'add_numbers ' in completions
    
    # Test command parameter completion
    completions = session.getCompletions("test_interface.add_numbers ")
    assert '5' in completions
    assert 'a' in completions
    assert 'b' in completions

    # Test positional lambda completion
    completions = session.getCompletions("test_interface.sub_numbers ")
    assert '1738' in completions
    assert 'a' in completions

    # Test command with some parameters
    completions = session.getCompletions("test_interface.add_numbers a: 5 , ")
    assert 'b' in completions
    assert '1738' in completions
    assert 'a' not in completions

    #Test args 
    completions = session.getCompletions("test_interface.add_numbers a:")
    assert [1,2,3,4,5] == completions

    # Test with weird spacing
    completions = session.getCompletions("test_interface.add_numbers a:5,")
    assert 'b' in completions
    assert 'a' not in completions

def test_invalid_commands(setup_session):
    session = setup_session
    
    # Test invalid command path
    with pytest.raises(ValueError):
        session.parseCommand("invalid.path")
    
    # Test missing required argument
    with pytest.raises(ValueError):
        session.parseCommand("interfaces.test_interface.add_numbers")
    
    # Test invalid argument type
    with pytest.raises(ValueError):
        session.parseCommand("interfaces.test_interface.add_numbers a: invalid, b: 5")

def test_eval_security():
    # Test that eval is disabled by default
    interface = InterfaceBase('test')
    
    # Should not evaluate expression without allow_eval=True and raise exception

    try :
        result = interface.parseCommand("add_numbers a: $(2 * 3), b: 5")
        assert False
    except Exception as e:
        assert True 


def test_type_exceptions():
    device = DeviceBase('test')
    
    # should raise exception for invalid type
    try:
        result = device.parseCommand("test_command arg1: '42'")
        assert False
    except Exception as e:
        assert True


def test_bytes_conversion():
    device = DeviceComplex('test')
    
    # Test bytes conversion
    result = device.parseCommand("store_data label: test, data: b'hello'")
    assert isinstance(device.data['test'], bytes)
    assert device.data['test'] == b'hello'

    # Test hex conversion
    result = device.parseCommand("store_data label: test, data: 0x01 0x02 0x03")
    assert isinstance(device.data['test'], bytes)
    assert device.data['test'] == b'\x01\x02\x03'
    
def test_positional_arguments():
    device = DeviceBase('test')
    # Test with only positional arguments
    result = device.parseCommand("test_command 42")
    assert result == "Received 42 and default"
    
    # Test with both positional and keyword arguments
    result = device.parseCommand("test_command 42, arg2: custom")
    assert result == "Received 42 and custom"
    
    # Test with all arguments as positional
    result = device.parseCommand("test_command 42, custom")
    assert result == "Received 42 and custom"

def test_complex_device_positional():
    device = DeviceComplex('test')
    # Test with positional arguments
    result = device.parseCommand("store_data test, b'hello'")
    assert result == 5
    assert device.data['test'] == b'hello'
    
    # Test with mixed positional and keyword arguments
    result = device.parseCommand("store_data test, data: b'world'")
    assert result == 5
    assert device.data['test'] == b'world'

def test_invalid_positional_arguments():
    device = DeviceBase('test')
    
    # Test too many positional arguments
    with pytest.raises(ValueError, match="Too many positional arguments provided"):
        device.parseCommand("test_command 42, custom, extra")
    
    # Test missing required argument
    with pytest.raises(ValueError, match="Missing required argument"):
        device.parseCommand("test_command")
    
    # Test invalid type for positional argument
    with pytest.raises(ValueError):
        device.parseCommand("test_command invalid")



def test_complex_strings():

    @commandParser
    class DeviceStringProcessor:
        def __init__(self, name: str):
            self.name = name
            self.data = {}
            
        @command
        def handleString(self, cmd: str):
            return cmd
    
    device = DeviceStringProcessor('test')
    result = device.parseCommand('handleString main(1,"Hello World")')
    assert result == 'main(1,"Hello World")'

    result = device.parseCommand('handleString strcpy(argv[0],buf)')
    assert result == 'strcpy(argv[0],buf)'

@commandParser
class mySubParser:
    def __init__(self, name: str):
        self.name = name
        
    @command(help="Sub command")
    def sub_command(self, arg1: int):
        return f"Sub command received {arg1}"


@commandParser(collapsed=True, subparsers=['device'])
class CollapsedParser:
    def __init__(self, name: str):
        self.name = name
        self.device = mySubParser('test_device')

def test_collapsed_subparser():


    parser = CollapsedParser('test_interface')
    # Test accessing the subparser directly
    result = parser.parseCommand("sub_command arg1: 42")
    assert result == "Sub command received 42"

def test_collapsed_completions():
    parser = CollapsedParser('test_interface')
    
    # Test root level completion
    completions = parser.getCompletions("")
    assert 'sub_command' in completions
    
    # Test command parameter completion
    completions = parser.getCompletions("sub_command ")
    assert 'arg1' in completions

    # Test with some parameters
    completions = parser.getCompletions("sub_command arg1: 42, ")
    assert 'arg1' not in completions



if __name__ == '__main__':
    pytest.main([__file__])