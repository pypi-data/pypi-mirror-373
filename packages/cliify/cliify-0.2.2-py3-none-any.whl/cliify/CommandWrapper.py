from typing import Dict, Any, List, Callable, get_type_hints, Optional, Union
import inspect
import ast
import re
from cliify.splitHelper import splitWithEscapes
import yaml
from termcolor import colored


regExEval = re.compile(r'\$\((.*?)\)')
regCmdParams = re.compile(r'\s*?(\S*)\s(.*)')

regHexStr = re.compile(r"(0x[0-9a-f]*\s)+", re.IGNORECASE)

def evalaluate_for_expressions(value: str) -> str:

    #get all the expressions
    expressions = regExEval.findall(value)

    #if there are no expressions, return the value as is
    if not expressions:
        return value
    
    #iterate over all the expressions
    for expression in expressions:
        #evaluate the expression

        try:
            value = value.replace(f"$({expression})", str(eval(expression)))
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {expression}") from e
        
    return value


def _parse_args(args_str: str, allow_eval: bool = False) -> tuple[list, dict]:
    """Parse a command string into positional and keyword arguments.
    
    Returns:
        tuple: (positional_args, keyword_args)
    """
    pos_args = []
    kw_args = {}
    
    if not args_str.strip():
        return pos_args, kw_args
        
    args_parts = splitWithEscapes(args_str.strip(), ',')
    args_parts = [part.strip() for part in args_parts]
    
    for part in args_parts:


        if ': ' in part:
            # This is a keyword argument
            split_vals = splitWithEscapes(part, ':', maxsplit=1)
            key = split_vals[0]
            value = split_vals[1]
            
            if allow_eval:
                value = evalaluate_for_expressions(value)
            
            kw_args[key] = value
        else:
            # This is a positional argument
            value = part.strip()
            if allow_eval:
                value = evalaluate_for_expressions(value)
            pos_args.append(value)
    
    return pos_args, kw_args


def _get_subparser_items(obj, subparser_name: str) -> Dict[str, Any]:
    """Helper function to get items from a subparser, whether it's a dict or list."""
    if not hasattr(obj, subparser_name):
        return {}
        
    subparser = getattr(obj, subparser_name)
    
    # If it's a dictionary, return as is
    if isinstance(subparser, dict):
        return subparser
        
    # If it's a list/array, convert to dict using name property
    if isinstance(subparser, (list, tuple)):
        result = {}
        for item in subparser:
            if not hasattr(item, 'name'):
                raise ValueError(
                    f"Items in subparser array '{subparser_name}' must have a 'name' property. "
                    "Either add a name property to your objects or use a dictionary instead."
                )
            result[item.name] = item
        return result
        
    # If it's a single object, treat it like a one-item dict
    if hasattr(subparser, 'name'):
        return {subparser.name: subparser}
        
    raise ValueError(
        f"Subparser '{subparser_name}' must be either:\n"
        "1. A dictionary mapping names to objects\n"
        "2. An array of objects with 'name' properties\n"
        "3. A single object with a 'name' property"
    )

class CommandWrapper:
    """Base wrapper for command functionality."""
    
    def __init__(self, obj, name="", parent=None, allow_eval=False, include_subparser_name=False, 
                 validate_options=False, flat=False, default_help=True):
        self._obj = obj
        self._name = name
        self._parent = parent
        self._allow_eval = allow_eval
        self._include_subparser_name = include_subparser_name
        self._validate_options = validate_options
        self._flat = flat
        self._tree_cache = None
        self._commands = self._get_commands_for_obj(obj)
        self._default_help = default_help
        # Store subparser objects for flat mode
        self._subparser_objects = self._get_subparser_objects(obj) if flat else {}

    def _get_commands_for_obj(self, obj: Any) -> dict:
        """Get all command methods for an object."""
        commands = {}
        for name, member in inspect.getmembers(obj):
            if hasattr(member, '_is_command'):
                if member._when and not member._when(obj):
                    continue
                commands[name] = member
                
        # If flat mode is enabled, include commands from subparsers
        if hasattr(self, '_flat') and self._flat:
            subparser_commands = self._get_flat_commands(obj)
            # Add subparser commands, but don't override existing commands
            for name, cmd in subparser_commands.items():
                if name not in commands:
                    commands[name] = cmd
                    
        return commands
    
    def _get_flat_commands(self, obj: Any) -> dict:
        """Get all commands from subparsers when in flat mode."""
        flat_commands = {}
        
        for subparser_name in getattr(obj.__class__, '_subparsers', []):
            try:
                subparser_items = _get_subparser_items(obj, subparser_name)
                
                for subparser_key, subparser_obj in subparser_items.items():
                    # Get all commands from this subparser
                    for name, member in inspect.getmembers(subparser_obj):
                        if hasattr(member, '_is_command'):
                            if member._when and not member._when(subparser_obj):
                                continue
                            # Store the command and its parent object for execution
                            flat_commands[name] = member
                            # Keep track of subparser objects for command execution
                            if not hasattr(self, '_subparser_objects'):
                                self._subparser_objects = {}
                            if name not in self._subparser_objects:
                                self._subparser_objects[name] = subparser_obj
            except ValueError:
                pass
                
        return flat_commands
    
    def _get_subparser_objects(self, obj: Any) -> dict:
        """Get all subparser objects for flat mode."""
        subparser_objects = {}
        
        for subparser_name in getattr(obj.__class__, '_subparsers', []):
            try:
                subparser_items = _get_subparser_items(obj, subparser_name)
                
                for subparser_key, subparser_obj in subparser_items.items():
                    # Get all commands from this subparser
                    for name, member in inspect.getmembers(subparser_obj):
                        if hasattr(member, '_is_command'):
                            if member._when and not member._when(subparser_obj):
                                continue
                            # Store the subparser object for this command
                            subparser_objects[name] = subparser_obj
            except ValueError:
                pass
                
        return subparser_objects
        
    def _get_subparsers_for_obj(self, obj: Any) -> dict:
        """Get all subparsers for an object."""
        subparsers = {}
        
        for subparser_name in getattr(obj.__class__, '_subparsers', []):
            try:
                subparser_items = _get_subparser_items(obj, subparser_name)
                subparsers[subparser_name] = subparser_items
            except ValueError as e:
                # Re-raise with more context
                raise ValueError(f"Error in subparser '{subparser_name}': {str(e)}") from e
                    
        return subparsers

    def _get_completion_info_for_path(self, path: str) -> tuple[Any, dict, dict]:
        """Get completion information for a given path."""
        if not path:
            return self._obj, self._get_commands_for_obj(self._obj), self._get_subparsers_for_obj(self._obj)
            
        try:
            current_obj = self._obj
            parts = path.split('.')
            
            for i, part in enumerate(parts):
                found = False
                
                subparsers = self._get_subparsers_for_obj(current_obj)
                for subparser_name, subparser_dict in subparsers.items():
                    if self._include_subparser_name:
                        if part == subparser_name:
                            if i + 1 >= len(parts):
                                return current_obj, {}, subparser_dict
                            next_part = parts[i + 1]
                            if next_part in subparser_dict:
                                current_obj = subparser_dict[next_part]
                                i += 1
                                found = True
                                break
                    elif part in subparser_dict:
                        current_obj = subparser_dict[part]
                        found = True
                        break
                        
                if not found:
                    if hasattr(current_obj, part):
                        current_obj = getattr(current_obj, part)
                    
            return current_obj, self._get_commands_for_obj(current_obj), self._get_subparsers_for_obj(current_obj)
            
        except (AttributeError, KeyError):
            return None, {}, {}

    def _resolve_completions(self, method: Callable, target_obj: Any) -> Dict:
        """Resolve completion functions to their actual values."""
        if not hasattr(method, '_completions'):
            return {}
            
        completions = method._completions.copy()
        for param, completion in completions.items():
            if isinstance(completion, str):
                # If it's a string, treat it as a method name
                if hasattr(target_obj, completion):
                    method = getattr(target_obj, completion)
                    if callable(method):
                        completions[param] = method()
            elif callable(completion) and not isinstance(completion, (list, tuple)):
                # If it's a callable (but not a list/tuple), call it with the target object
                completions[param] = completion(target_obj)
        return completions
    


    def _find_target(self, path: str) -> tuple[Any, str, Any]:
        """Traverse the object hierarchy to find the target object and method."""
        parts = path.split('.')

            
        current_obj = self._obj
        i = 0
        
        while i < len(parts) - 1:
            part = parts[i]
            found = False
            
            if hasattr(current_obj.__class__, '_subparsers'):
                for subparser_name in current_obj.__class__._subparsers:
                    if hasattr(current_obj, subparser_name):
                        subparser_obj = getattr(current_obj, subparser_name)
                        if isinstance(subparser_obj, dict):
                            if self._include_subparser_name:
                                if part == subparser_name:
                                    if i + 1 >= len(parts) - 1:
                                        raise ValueError(f"Incomplete path after {part}")
                                    next_part = parts[i + 1]
                                    if next_part in subparser_obj:
                                        current_obj = subparser_obj[next_part]
                                        i += 2
                                        found = True
                                        break
                            elif part in subparser_obj:
                                current_obj = subparser_obj[part]
                                i += 1
                                found = True
                                break
            
            if not found:
                if hasattr(current_obj.__class__, '_subparsers'):
                    for subparser_name in current_obj.__class__._subparsers:
                        if hasattr(current_obj, subparser_name):
                            subparser_obj = getattr(current_obj, subparser_name)
                            if isinstance(subparser_obj, dict) and part in subparser_obj:
                                current_obj = subparser_obj[part]
                                i += 1
                                found = True
                                break
                
                if not found:
                    if not hasattr(current_obj, part):
                        raise ValueError(f"Invalid path component: {part}")
                    current_obj = getattr(current_obj, part)
                    i += 1

        method_name = parts[-1]

        if self._flat and current_obj == self._obj:

            if not hasattr(current_obj, method_name):
                # method not found, check subparsers
                for subparser_name in current_obj.__class__._subparsers:
                    sub = getattr(current_obj, subparser_name)
                    #check for method in subparser
                    if hasattr(sub, method_name):
                        method = getattr(sub, method_name)
                        if hasattr(method, '_is_command'):
                            return sub, method_name, method



        if not hasattr(current_obj, method_name):
            raise ValueError(f"Method not found: {method_name}")
            
        method = getattr(current_obj, method_name)
        if not hasattr(method, '_is_command'):
            raise ValueError(f"Not a command: {method_name}")
            
        return current_obj, method_name, method

    def _convert_type(self, value: str, type_hint: type, param_name: str = None, 
                     target_obj: Any = None, method: Callable = None) -> Any:
        """Convert a string value to the specified type."""

        # Handle special cases for Optional types
        if hasattr(type_hint, '__origin__'):
            # Handle Optional types
            if type_hint.__origin__ == Union:
                if len(type_hint.__args__) == 2 and type_hint.__args__[1] is type(None):
                    type_hint = type_hint.__args__[0]
                else:
                    raise ValueError(f"Unsupported type hint: {type_hint}")

        #support multiple types 
        validInt = False
        hints=[]
        strHints = str(type_hint).split('|')
        for strHint in strHints:
            hints.append(strHint.strip().replace('typing.','').replace('builtins.',''))

        # First check if we have completions for this parameter
        if param_name and method and target_obj and self._validate_options:
            completions = self._resolve_completions(method, target_obj)
            if param_name in completions:
                valid_values = completions[param_name]
                if isinstance(valid_values, (list, tuple)):
                    try:
                        idx = valid_values.index(type_hint(value))
                        return valid_values[idx]
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid value for {param_name}. Must be one of: {valid_values}")

        if 'int' in hints:
            try:
                test = int(value)
                validInt = True
            except:
                validInt = False     

                    

        if 'bool' in hints:
            if value.lower() in ['true', '1', 'yes', 'on']:
                return True
            elif value.lower() in ['false', '0', 'no', 'off']:
                return False
            else:
                raise ValueError(f"Invalid boolean value: {value}")
        elif 'int' in hints and validInt:
            return int(value)
        if 'bytes' in hints:
            if value.startswith("b'") and value.endswith("'"):
                return value[2:-1].encode('utf-8')
            elif value.startswith('b"') and value.endswith('"'):
                return value[2:-1].encode('utf-8')
            elif value.startswith('[') and value.endswith(']'):
                return bytes(yaml.safe_load(value))
            else: 
                match = regHexStr.match(value)  
                if match:
                    value = value.replace('0x', '').replace(' ', '')
                    return bytes.fromhex(value)
                return value.encode('utf-8')
        elif 'str' in hints:
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                return value[1:-1]
            return value
        elif 'list' in hints:
            if value.startswith('[') and value.endswith(']'):
                return yaml.safe_load(value)
            else: 
                return yaml.safe_load(f"[{value}]")

        return type_hint(value)

    def getCompletionTree(self, base_path: str = "") -> Dict:
        """Get the complete command tree for autocompletion starting from given path."""
        tree = {} # Always include help command
        
        # Get completion info for the base path
        current_obj, commands, subparsers = self._get_completion_info_for_path(base_path)
        if current_obj is None:
            return tree
            
        # Add commands to tree
        for name, method in commands.items():
            completions = {}
            # Get method signature to get all parameters
            sig = inspect.signature(method)
            params = [p for p in sig.parameters if p != 'self']
            
            # Initialize all parameters with empty lists
            for param in params:
                completions[param] = []
                
            # Override with actual completions if defined
            if hasattr(method, '_completions'):
                # For flat mode, we need to use the correct target object
                target_obj = self._subparser_objects.get(name, current_obj) if self._flat else current_obj
                resolved_completions = self._resolve_completions(method, target_obj)
                completions.update(resolved_completions)
                
            tree[name] = completions
            
        # Add subparsers to tree (skip in flat mode since commands are already flattened)
        if not self._flat:
            if self._include_subparser_name:
                for subparser_name, subparser_dict in subparsers.items():
                    subtree = {}
                    for key, value in subparser_dict.items():
                        # Recursively get completion tree for subparser items
                        new_path = f"{base_path}.{subparser_name}.{key}" if base_path else f"{subparser_name}.{key}"
                        subtree[key] = self.getCompletionTree(new_path)
                    tree[subparser_name] = subtree
            else:
                for subparser_dict in subparsers.values():
                    for key, value in subparser_dict.items():
                        # Recursively get completion tree
                        new_path = f"{base_path}.{key}" if base_path else key
                        tree[key] = self.getCompletionTree(new_path)
                    
        return tree
    
    def getCompletions(self, partial_cmd: str, force_strings=False, use_cache=False) -> List[str]:
        """Get possible completions for a partial command."""
        
        # Initialize state tracking
        state = 'command'  # Can be 'command', 'arg', or 'value'
        positional_arg = 0  # Track which positional argument we're on
        current_tree = None
        completions = []
        used_keywords = []
        
        # Get or create completion tree
        if use_cache and hasattr(self, '_tree_cache'):
            tree = self._tree_cache
        else:
            tree = self.getCompletionTree()
            self._tree_cache = tree
        
        # Handle empty command
        if not partial_cmd:
            return list(tree.keys())
            
        # Determine state and position
        cmd_split = partial_cmd.split(' ', maxsplit=1)
        if len(cmd_split) > 1:
            state = 'arg'
            arg_split = splitWithEscapes(cmd_split[1], ',')

            if len(arg_split) > 0:
                # If last argument contains :, we're completing a value
                if ':' in arg_split[-1]:
                    state = 'value'
                    
                # Count positional arguments (those without :)
                for arg in arg_split[:-1]:  # Don't count current argument
                    kv = splitWithEscapes(arg, ':')
                    if len(kv) == 1:
                        positional_arg += 1
                    else:
                        used_keywords.append(kv[0].strip())
                        
            # Navigate to command in tree
            cmd_parts = cmd_split[0].split('.')
            current_tree = tree
            for part in cmd_parts:
                if part not in current_tree:
                    return []
                current_tree = current_tree[part]
                
            if not isinstance(current_tree, dict):
                return []
                
            # Handle each state
            if state == 'value':
                # Get the parameter name before the colon
                param_name = splitWithEscapes(arg_split[-1], ':')[0].strip()
                if param_name in current_tree:
                    return current_tree[param_name]
                return []
                
            elif state == 'arg':
                param_names = list(current_tree.keys())

                for idx, param in enumerate(param_names):
                    if param in used_keywords and idx >= positional_arg:
                        positional_arg += 1
                
                # Get completions for current positional argument if available
                if positional_arg < len(param_names):
                    current_pos_param = param_names[positional_arg]
                    if current_pos_param in current_tree:
                        pos_completions = current_tree[current_pos_param]
                        if isinstance(pos_completions, (list, tuple)):
                            completions.extend(str(c) for c in pos_completions)
                
                # add keywords for all used positional arguments to used_keywords
                for i in range(positional_arg):
                    used_keywords.append(param_names[i])
                # Add all unused parameter names
                
                remaining_params = [p for p in param_names if p not in used_keywords]
                completions.extend(remaining_params)
                
        else:
            # Handle command completion
            parts = partial_cmd.split('.')
            current_tree = tree
            
            # Navigate through all but the last part
            for part in parts[:-1]:
                if part not in current_tree:
                    return []
                current_tree = current_tree[part]
                    
            # Get completions that match the last part
            current_part = parts[-1]
            for name, value in current_tree.items():
                if name.startswith(current_part):
                    suffix = ' ' if isinstance(value, dict) and all(isinstance(v, list) for v in value.values()) else ''
                    completions.append(name + suffix)
        
        if force_strings:
            return [f'"{c}"' for c in completions]
            
        return completions

    def getPathCompletions(self, partial_cmd: str) -> List[str]:
        """Get possible completions for a partial command path."""
        if not partial_cmd:
            return list(self._commands.keys())
            
        parts = partial_cmd.split('.')
        current_tree = self._commands
        
        # Navigate through all but the last part
        for part in parts[:-1]:
            if part not in current_tree:
                return []
            current_tree = self._get_subparsers_for_obj(current_tree[part])
            
        # Get completions that match the last part
        current_part = parts[-1]
        completions = []
        
        for name, value in current_tree.items():
            if name.startswith(current_part):
                completions.append(name)
                
        return completions

    def parseCommand(self, cmd_str: str) -> Any:
        """Parse and execute a command string."""
        # Split on first space to separate command path from arguments
        cmd_parts = cmd_str.split(" ", 1)
        cmd_path = cmd_parts[0]

        if cmd_path == 'help' and self._default_help:
            if len(cmd_parts) == 1:
                print(colored("Available commands:\n", color='yellow'))
                for cmd in self._commands:
                    helpText = getattr(self._commands[cmd], '_help', "")
                    print(colored(f"{cmd}: {helpText}", color='yellow'))
                return True

            print(colored(self.getHelp(cmd_parts[1]), color='yellow'))
            return True
        
        args_str = cmd_parts[1] if len(cmd_parts) > 1 else ""
        
        # Handle flat mode for simple commands
        if self._flat and '.' not in cmd_path and cmd_path in self._subparser_objects:
            target_obj = self._subparser_objects[cmd_path]
            method_name = cmd_path
            method = getattr(target_obj, method_name)
        else:
            # Find the target object and method using the regular path
            target_obj, method_name, method = self._find_target(cmd_path)
        
        # Parse arguments
        pos_args, kw_args = _parse_args(args_str, self._allow_eval)
        
        # Get method signature and type hints
        sig = inspect.signature(method)
        type_hints = get_type_hints(method)
        
        # Process arguments
        processed_args = []
        param_items = list(sig.parameters.items())
        
        # Handle positional arguments first
        pos_idx = 0
        for param_name, param in param_items:
            if param_name == 'self':
                continue
                
            if pos_idx < len(pos_args) and param_name not in kw_args:
                value = pos_args[pos_idx]
                if param_name in type_hints:
                    type_hint = type_hints[param_name]
                    value = self._convert_type(value, type_hint, param_name, target_obj, method)
                processed_args.append(value)
                pos_idx += 1
                continue
            
            # Handle as keyword argument if provided
            if param_name in kw_args:
                value = kw_args[param_name]
                if param_name in type_hints:
                    type_hint = type_hints[param_name]
                    value = self._convert_type(value, type_hint, param_name, target_obj, method)
                processed_args.append(value)
            elif param.default == inspect.Parameter.empty:
                raise ValueError(f"Missing required argument: {param_name}")
            else:
                processed_args.append(param.default)
        
        # Verify we used all positional arguments
        if pos_idx < len(pos_args):
            raise ValueError(f"Too many positional arguments provided")
            
        # Call the method
        return method.__get__(target_obj, target_obj.__class__)(*processed_args)
    
    def getHelp(self, cmd_path: str) -> str:
        """
        Get help text for a command at the given path.
        
        Args:
            cmd_path: The dot-separated path to the command
            
        Returns:
            The help string for the command
            
        Raises:
            ValueError: If the path is invalid or doesn't point to a command
        """
        try:
            cmd_path = cmd_path.strip()
            
            # Handle flat mode for simple commands
            if self._flat and '.' not in cmd_path and cmd_path in self._subparser_objects:
                target_obj = self._subparser_objects[cmd_path]
                method_name = cmd_path
                method = getattr(target_obj, method_name)
            else:
                # Find the target object and method using the regular path
                target_obj, method_name, method = self._find_target(cmd_path)
            
            # Return the help text, defaulting to empty string if none exists
            return getattr(method, '_help', "") + "\n\n" or ""
        except ValueError as e:
            raise ValueError(f"Invalid command path: {cmd_path}") from e                            

def command(*args, help: str = None, completions: Dict[str, Union[List, Callable, str]] = None, when: Callable = None):
    """
    Decorator to mark a method as a command.
    Can be used with or without parameters.
    """
    def decorator(func):
        func._is_command = True
        func._help = help or inspect.getdoc(func) or ""
        func._completions = completions or {}
        func._when = when
        return func

    # Handle no-parentheses usage
    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])
        
    return decorator

def invalidatesTree(func):
    """Decorator that invalidates the completion tree cache when the method is called."""
    def wrapper(self, *args, **kwargs):
        # Clear the tree cache
        if hasattr(self, '_tree_cache'):
            self._tree_cache = None
        # Call the original function
        return func(self, *args, **kwargs)
    return wrapper


def commandParser(cls=None, /, *, allow_eval: bool = False, subparsers: Optional[List[str]] = None, 
                  include_subparser_name: bool = False, flat: bool = False, default_help: bool = True):
    """Class decorator to enable command parsing functionality."""
    def wrap(cls):
        # Add subparsers list as a class attribute
        cls._subparsers = subparsers or []
        cls._include_subparser_name = include_subparser_name
        cls._allow_eval = allow_eval  # Add this to store at class level
        cls._flat = flat  # Store the flat setting
        cls._default_help = default_help  # Store the include_help setting
        
        original_init = cls.__init__
        
        def __init__(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self._wrapper = CommandWrapper(
                self, 
                allow_eval=allow_eval, 
                include_subparser_name=include_subparser_name,
                flat=flat,
                default_help=default_help
            )

        if default_help and not hasattr(cls, 'help'):

            @command(completions={'cmd_path': ['$path']})
            def help(self, cmd_path: str = "") -> str:
                """Get help text for a command."""
                helpStr = self._wrapper.getHelp(cmd_path)
                print(colored(helpStr, 'yellow'))
            
        def parseCommand(self, cmd_str: str) -> Any:
            return self._wrapper.parseCommand(cmd_str)
            
        def getCompletionTree(self) -> Dict:
            return self._wrapper.getCompletionTree()
            
        def getCompletions(self, partial_cmd: str) -> List[str]:
            return self._wrapper.getCompletions(partial_cmd)
        
        def getPathCompletions(self, partial_cmd: str) -> List[str]:
            return self._wrapper.getPathCompletions(partial_cmd)
        
        def getHelp(self, cmd_path: str) -> str:
            return self._wrapper.getHelp(cmd_path)
            
        cls.getHelp = getHelp
        cls.__init__ = __init__
        cls.parseCommand = parseCommand
        cls.getCompletionTree = getCompletionTree
        cls.getCompletions = getCompletions
        cls.getPathCompletions = getPathCompletions
        
        return cls
        
    if cls is None:
        return wrap
        
    return wrap(cls)