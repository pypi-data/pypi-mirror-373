import ast
import inspect
import sys
import textwrap
import types
from abc import ABCMeta
from functools import lru_cache
from functools import wraps
from typing import Mapping

from python_sdk_remote.mini_logger import MiniLogger

from .logger_local import Logger


def log_function_decorator(logger: Logger) -> callable:
    def decorator(func: callable) -> callable:
        return log_function(func, logger)

    return decorator


def log_function(func: callable, logger: Logger) -> callable:
    """Wrap a function with loggger.start, logger.end and logger.error in case of exception."""

    # This is called a lot of times, so we have to make sure it's very efficient:
    @wraps(func)
    def wrapper(*args, **kwargs) -> any:
        # Obtain the module name of the wrapped function
        function_module = getattr(func, '__module__', None) or func.__globals__.get('__name__', 'unknown_module')

        signature = inspect.signature(func)
        arg_names = [param.name for param in signature.parameters.values()]
        if len(args) + len(kwargs) == len(arg_names) + 1:  # staticmethod called with class instance
            args = args[1:]

        kwargs_updated = {**dict(zip(arg_names, args)), **kwargs.copy()}
        # if it has __wrapped__, func = func.__wrapped__  (for functools.wraps)
        real_func = func.__dict__.get("__wrapped__", func)
        filename = inspect.getfile(real_func) if not isinstance(real_func, staticmethod) else inspect.getfile(
            real_func.__func__)
        extra_kwargs = {"function_name": real_func.__name__,
                        "class_name": real_func.__qualname__.split(".")[0],
                        "filename": filename,
                        "path": f"{function_module}.{real_func.__qualname__}"}
        kwargs_updated["extra_kwargs"] = extra_kwargs

        logger.start(object=kwargs_updated)
        result = None
        try:
            # TODO: add warning if the typing doesn't match (and not None)
            result = func(*args, **kwargs)
        except Exception as exception:
            # Use traceback to capture frame information
            # Use sys.exc_info() to get exception information
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # Extract the frame information from the traceback
            frame = (exc_traceback.tb_next or exc_traceback).tb_frame
            # Get the local variables
            locals_before_exception = frame.f_locals

            # use logger.exception if the caller is a test
            logger.error(object={"exception": exception,
                                 "locals_before_exception": locals_before_exception,
                                 "extra_kwargs": kwargs_updated})
            raise exception

        finally:
            result_dict = {"extra_kwargs": kwargs_updated}
            return_variables = get_return_variables(func)
            if isinstance(result, tuple) and len(return_variables) > 1:
                if len(return_variables) != len(result):
                    MiniLogger.warning(
                        f"Number of return variables ({len(return_variables)}) does not match the number of "
                        f"returned values ({len(result)}) in function {extra_kwargs['path']}")
                    result_dict["result"] = result
                else:
                    for var, value in zip(return_variables, result):
                        result_dict[var] = value
            elif return_variables:
                result_dict[return_variables[0]] = result
            else:
                result_dict["result"] = result

            logger.end(object=result_dict)
        return result

    return wrapper


class MetaLogger(type):
    @classmethod
    def __prepare__(metacls, name, bases, **kwargs) -> Mapping[str, object]:
        """This method is called before the class is created. It is used to create the class namespace."""
        return super().__prepare__(name, bases, **kwargs)

    def __new__(cls, name, bases, dct, **kwargs) -> type:
        # kwargs may be empty if the class is not instantiated with the metaclass
        cls.logger: Logger = None  # noqa add logger to the namespace (for typing)
        if not kwargs:
            if not bases:
                raise ValueError("Please provide a logger object to the MetaLogger metaclass")
            if any(base.__name__ == "ABC" for base in bases):
                return super().__new__(cls, name, bases, dct)
            kwargs = {"object": {'bases': bases}}
        kwargs['object']['class'] = name
        kwargs['is_meta_logger'] = True
        logger = Logger.create_logger(**kwargs)
        dct['logger'] = logger

        for key, function in dct.items():
            if callable(function) and (not key.endswith("__") or key == "__init__"):  # Exclude magic methods
                dct[key] = log_function(function, logger)

        # Add __repr__ to the class namespace, even if explicitly defined in the class
        # because otherwise logger.start in init will fail (if __repr__ is already defined)
        def __repr__(self):
            # get init arguments
            # TODO: avoid recursive `self` repr in inheritance
            args = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
            return f"{self.__class__.__name__}({args})"

        dct["__repr__"] = __repr__
        return super().__new__(cls, name, bases, dct)


def module_wrapper(logger: Logger) -> None:
    """Wrap all functions in a module with log_function.
    Example:
    import sys
    def foo(): 1/0
    def bar(): return 1
    logger = ...
    module_wrapper(logger)
    """
    # Get the module of the caller
    module = sys.modules[inspect.stack()[1].frame.f_globals["__name__"]]
    for name, function in vars(module).items():
        if isinstance(function, types.FunctionType) and function.__module__ == module.__name__:
            setattr(module, name, log_function(function, logger))


class ReturnVisitor(ast.NodeVisitor):
    def __init__(self):
        self.returns = []

    def visit_Return(self, node):
        # Ignore return None and `return`
        if not (isinstance(node.value, ast.Constant) and node.value.value is None) and node.value is not None:
            self.returns.append(node)
        self.generic_visit(node)


@lru_cache(maxsize=128)
def get_return_variables(func: callable) -> tuple:
    """Returns the last meaningful return statement of the function, if exists."""
    # TODO: do we need first/last? (for multiple returns)
    # print(f"get_return_variables: {func.__name__}")
    try:
        source_code = inspect.getsource(func)
        # print(f"get_return_variables: {func.__name__} success.")
    except Exception:
        print(f"logger-local branch=2614 package={__package__} version={__version__} get_return_variables({func.__name__}) failed. TODO Please make sure this function has returns a type i.e. `-> None`")  # noqa E501
        return ("result",)

    # source_code doesn't include class definition, so the indentation is wrong
    source_code = 'if 1:\n' + textwrap.indent(source_code, prefix=' ')
    tree = ast.parse(source_code)
    visitor = ReturnVisitor()
    visitor.visit(tree)

    if not visitor.returns:
        return ("result",)

    node = visitor.returns[-1].value
    try:
        if isinstance(node, ast.Name):
            vars = (node.id,)
        elif isinstance(node, (ast.Tuple, ast.List)):
            vars = tuple(ast.unparse(elt) for elt in node.elts)  # noqa
        else:
            vars = (ast.unparse(node),)
            MiniLogger.warning(f"Invalid return statement: {vars[0]} (not a variable)")

    except Exception:
        MiniLogger.warning(f"Invalid return statement: {ast.dump(node)} (unable to parse)")
        vars = ("result",)
    return vars


class ABCMetaLogger(MetaLogger, ABCMeta):
    """When using abstract class, use this class to avoid conflicts with MetaLogger.
    Example:
    from abc import ABC
    class AbstractClass(ABC, metaclass=ABCMetaLogger):
        pass
    """

    def __new__(cls, name, bases, dct, **kwargs) -> type:
        cls.logger = None  # add logger to the namespace (for typing)
        return super().__new__(cls, name, bases, dct, **kwargs)
