"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Reflection utilities for dynamic code inspection and manipulation.
"""

import importlib
import inspect
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

from ..config.logging_setup import get_logger

logger = get_logger("xsystem.runtime.reflection")


class ReflectionUtils:
    """
    Comprehensive reflection utilities for dynamic code inspection,
    module loading, and runtime introspection.
    """

    @staticmethod
    def get_class_info(cls: Type) -> Dict[str, Any]:
        """
        Get comprehensive information about a class.

        Args:
            cls: Class to inspect

        Returns:
            Dictionary with class information
        """
        return {
            'name': cls.__name__,
            'module': cls.__module__,
            'qualname': getattr(cls, '__qualname__', cls.__name__),
            'bases': [base.__name__ for base in cls.__bases__],
            'mro': [c.__name__ for c in cls.__mro__],
            'doc': cls.__doc__,
            'attributes': [name for name in dir(cls) if not name.startswith('_')],
            'methods': [name for name, obj in inspect.getmembers(cls, inspect.ismethod)],
            'functions': [name for name, obj in inspect.getmembers(cls, inspect.isfunction)],
            'properties': [name for name, obj in inspect.getmembers(cls, lambda x: isinstance(x, property))],
            'is_abstract': inspect.isabstract(cls),
            'file': inspect.getfile(cls) if hasattr(cls, '__file__') else None,
            'source_lines': ReflectionUtils._get_source_lines(cls),
        }

    @staticmethod
    def get_function_info(func: Callable) -> Dict[str, Any]:
        """
        Get comprehensive information about a function.

        Args:
            func: Function to inspect

        Returns:
            Dictionary with function information
        """
        signature = inspect.signature(func)
        
        return {
            'name': func.__name__,
            'module': func.__module__,
            'qualname': getattr(func, '__qualname__', func.__name__),
            'doc': func.__doc__,
            'signature': str(signature),
            'parameters': {
                name: {
                    'annotation': str(param.annotation) if param.annotation != param.empty else None,
                    'default': str(param.default) if param.default != param.empty else None,
                    'kind': str(param.kind),
                } for name, param in signature.parameters.items()
            },
            'return_annotation': str(signature.return_annotation) if signature.return_annotation != signature.empty else None,
            'is_coroutine': inspect.iscoroutinefunction(func),
            'is_generator': inspect.isgeneratorfunction(func),
            'is_builtin': inspect.isbuiltin(func),
            'file': inspect.getfile(func) if hasattr(func, '__file__') else None,
            'source_lines': ReflectionUtils._get_source_lines(func),
        }

    @staticmethod
    def get_module_info(module: Any) -> Dict[str, Any]:
        """
        Get comprehensive information about a module.

        Args:
            module: Module to inspect

        Returns:
            Dictionary with module information
        """
        return {
            'name': module.__name__,
            'file': getattr(module, '__file__', None),
            'package': getattr(module, '__package__', None),
            'doc': module.__doc__,
            'version': getattr(module, '__version__', None),
            'author': getattr(module, '__author__', None),
            'classes': [name for name, obj in inspect.getmembers(module, inspect.isclass)],
            'functions': [name for name, obj in inspect.getmembers(module, inspect.isfunction)],
            'constants': [name for name in dir(module) if name.isupper() and not name.startswith('_')],
            'all': getattr(module, '__all__', None),
            'loader': str(getattr(module, '__loader__', None)),
            'spec': str(getattr(module, '__spec__', None)),
        }

    @staticmethod
    def _get_source_lines(obj: Any) -> Optional[Dict[str, Any]]:
        """Get source lines for an object."""
        try:
            source_lines, start_line = inspect.getsourcelines(obj)
            return {
                'start_line': start_line,
                'line_count': len(source_lines),
                'source': ''.join(source_lines),
            }
        except (OSError, TypeError):
            return None

    @staticmethod
    def import_module(module_name: str, package: Optional[str] = None) -> Any:
        """
        Dynamically import a module.

        Args:
            module_name: Name of module to import
            package: Package for relative imports

        Returns:
            Imported module

        Raises:
            ImportError: If module cannot be imported
        """
        try:
            return importlib.import_module(module_name, package)
        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}")
            raise

    @staticmethod
    def reload_module(module: Any) -> Any:
        """
        Reload a module.

        Args:
            module: Module to reload

        Returns:
            Reloaded module
        """
        try:
            return importlib.reload(module)
        except Exception as e:
            logger.error(f"Failed to reload module {module}: {e}")
            raise

    @staticmethod
    def get_class_from_string(class_path: str) -> Type:
        """
        Get class from string path.

        Args:
            class_path: Dot-separated path to class (e.g., 'module.Class')

        Returns:
            Class object

        Raises:
            ImportError: If class cannot be imported
            AttributeError: If class not found in module
        """
        parts = class_path.split('.')
        module_path = '.'.join(parts[:-1])
        class_name = parts[-1]
        
        module = ReflectionUtils.import_module(module_path)
        return getattr(module, class_name)

    @staticmethod
    def get_function_from_string(func_path: str) -> Callable:
        """
        Get function from string path.

        Args:
            func_path: Dot-separated path to function (e.g., 'module.function')

        Returns:
            Function object

        Raises:
            ImportError: If function cannot be imported
            AttributeError: If function not found in module
        """
        parts = func_path.split('.')
        module_path = '.'.join(parts[:-1])
        func_name = parts[-1]
        
        module = ReflectionUtils.import_module(module_path)
        return getattr(module, func_name)

    @staticmethod
    def instantiate_class(class_path: str, *args: Any, **kwargs: Any) -> Any:
        """
        Instantiate class from string path.

        Args:
            class_path: Dot-separated path to class
            *args: Positional arguments for constructor
            **kwargs: Keyword arguments for constructor

        Returns:
            Class instance
        """
        cls = ReflectionUtils.get_class_from_string(class_path)
        return cls(*args, **kwargs)

    @staticmethod
    def call_function(func_path: str, *args: Any, **kwargs: Any) -> Any:
        """
        Call function from string path.

        Args:
            func_path: Dot-separated path to function
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result
        """
        func = ReflectionUtils.get_function_from_string(func_path)
        return func(*args, **kwargs)

    @staticmethod
    def find_classes_in_module(module: Any, base_class: Optional[Type] = None) -> List[Type]:
        """
        Find all classes in a module, optionally filtered by base class.

        Args:
            module: Module to search
            base_class: Optional base class to filter by

        Returns:
            List of class objects
        """
        classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:  # Only classes defined in this module
                if base_class is None or issubclass(obj, base_class):
                    classes.append(obj)
        return classes

    @staticmethod
    def find_functions_in_module(module: Any, decorator: Optional[Any] = None) -> List[Callable]:
        """
        Find all functions in a module, optionally filtered by decorator.

        Args:
            module: Module to search
            decorator: Optional decorator to filter by

        Returns:
            List of function objects
        """
        functions = []
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__ == module.__name__:  # Only functions defined in this module
                if decorator is None or hasattr(obj, decorator.__name__):
                    functions.append(obj)
        return functions

    @staticmethod
    def get_all_subclasses(cls: Type) -> List[Type]:
        """
        Get all subclasses of a class recursively.

        Args:
            cls: Base class

        Returns:
            List of all subclasses
        """
        subclasses = []
        for subclass in cls.__subclasses__():
            subclasses.append(subclass)
            subclasses.extend(ReflectionUtils.get_all_subclasses(subclass))
        return subclasses

    @staticmethod
    def is_instance_of(obj: Any, class_path: str) -> bool:
        """
        Check if object is instance of class specified by string path.

        Args:
            obj: Object to check
            class_path: Dot-separated path to class

        Returns:
            True if obj is instance of class
        """
        try:
            cls = ReflectionUtils.get_class_from_string(class_path)
            return isinstance(obj, cls)
        except (ImportError, AttributeError):
            return False

    @staticmethod
    def get_method_resolution_order(cls: Type) -> List[str]:
        """
        Get method resolution order for a class.

        Args:
            cls: Class to inspect

        Returns:
            List of class names in MRO order
        """
        return [c.__name__ for c in cls.__mro__]

    @staticmethod
    def get_object_memory_size(obj: Any) -> int:
        """
        Get approximate memory size of an object.

        Args:
            obj: Object to measure

        Returns:
            Size in bytes
        """
        return sys.getsizeof(obj)

    @staticmethod
    def get_module_dependencies(module_name: str) -> List[str]:
        """
        Get list of modules that a module depends on.

        Args:
            module_name: Name of module to analyze

        Returns:
            List of dependency module names
        """
        dependencies = []
        try:
            module = ReflectionUtils.import_module(module_name)
            if hasattr(module, '__file__') and module.__file__:
                # Read source file and extract imports
                source_file = Path(module.__file__)
                if source_file.exists():
                    content = source_file.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith('import ') or line.startswith('from '):
                            # Extract module name from import statement
                            if line.startswith('import '):
                                module_part = line[7:].split()[0].split('.')[0]
                            elif line.startswith('from '):
                                module_part = line[5:].split()[0].split('.')[0]
                            
                            if module_part and module_part not in dependencies:
                                dependencies.append(module_part)
                                
        except Exception as e:
            logger.warning(f"Could not analyze dependencies for {module_name}: {e}")
            
        return dependencies

    @staticmethod
    def get_runtime_info() -> Dict[str, Any]:
        """
        Get comprehensive runtime reflection information.

        Returns:
            Dictionary with runtime information
        """
        return {
            'loaded_modules': list(sys.modules.keys()),
            'module_count': len(sys.modules),
            'python_path': sys.path,
            'builtin_modules': list(sys.builtin_module_names),
            'current_frame_info': ReflectionUtils._get_current_frame_info(),
        }

    @staticmethod
    def _get_current_frame_info() -> Dict[str, Any]:
        """Get information about the current execution frame."""
        frame = inspect.currentframe()
        if frame and frame.f_back:
            frame = frame.f_back  # Go up one frame to get caller info
            return {
                'filename': frame.f_code.co_filename,
                'function': frame.f_code.co_name,
                'line_number': frame.f_lineno,
                'local_vars': list(frame.f_locals.keys()),
                'global_vars': list(frame.f_globals.keys()),
            }
        return {}
