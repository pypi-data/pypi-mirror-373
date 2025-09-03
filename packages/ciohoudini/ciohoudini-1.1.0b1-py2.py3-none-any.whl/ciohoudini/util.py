"""
Houdini Conductor Path Utilities

This module provides utility functions for path manipulation in the context of Conductor
submissions for Houdini. It includes functions to prepare, clean, strip, and resolve file
paths, ensuring consistency and compatibility across different platforms.

Dependencies:
- ciopath.gpath: Custom path handling library for platform-independent paths
- os: Standard library for OS interactions
- re: Standard library for regular expressions
- ciocore.loggeria: Custom logging for Conductor
"""
import hou
import functools
from ciopath.gpath import Path

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

def prepare_path(current_path):
    """
    Prepares a file path by expanding environment variables, normalizing slashes, removing
    drive letters, and quoting the result.

    Args:
        current_path (str): The file path to prepare.

    Returns:
        str: The prepared file path, quoted and normalized, or the original path on error.
    """
    try:
        if not current_path:
            return f'"{current_path}"'
        # Use ciopath.Path to normalize the path and expand environment variables
        path_obj = Path(current_path)
        # Get forward-slash path without drive letter
        normalized_path = path_obj.fslash(with_drive=False)
        # Quote the path
        return f'"{normalized_path}"'
    except Exception as e:
        logger.error(f"Error preparing path: {current_path}, {e}")
        return f'"{current_path}"'

def clean_path(current_path):
    """
    Prepares a file path by expanding environment variables, normalizing slashes, removing
    drive letters, and quoting the result.

    Args:
        current_path (str): The file path to prepare.

    Returns:
        str: The prepared file path, quoted and normalized, or the original path on error.
    """
    try:
        if not current_path:
            return f'{current_path}'
        # Use ciopath.Path to normalize the path and expand environment variables
        path_obj = Path(current_path)
        # Get forward-slash path without drive letter
        normalized_path = path_obj.fslash(with_drive=False)
        # Quote the path
        return f'{normalized_path}'
    except Exception as e:
        logger.error(f"Error preparing path: {current_path}, {e}")
        return f'{current_path}'

def clean_and_strip_path(current_path):
    """
    Cleans and normalizes a path by resolving it to an absolute path and stripping
    drive letters. Converts backslashes to forward slashes for consistency.

    Args:
        current_path (str): The path string to clean and normalize.

    Returns:
        str: The cleaned and normalized path, or the original path on error.
    """
    cleaned_path = current_path
    try:
        if current_path:
            # Use ciopath.Path to resolve and normalize the path
            path_obj = Path(current_path)
            # Check if the path exists to mimic pathlib's resolve(strict=True)
            if not path_obj.stat():
                raise ValueError(f"Path does not exist: {current_path}")
            # Get forward-slash path without drive letter
            cleaned_path = path_obj.fslash(with_drive=False)
    except Exception as e:
        logger.debug(f"Unable to clean and strip path: {current_path} error: {e}")
    return cleaned_path

def resolve_path(filepath):
    """
    Resolves a file path to its absolute form, ensuring the path exists, and converts
    backslashes to forward slashes.

    Args:
        filepath (str): The file path to resolve.

    Returns:
        str: The resolved file path, or the original path on error.
    """
    try:
        # Use ciopath.Path to resolve and normalize the path
        path_obj = Path(filepath)
        # Check if the path exists to mimic pathlib's resolve(strict=True)
        if not path_obj.stat():
            raise ValueError(f"Path does not exist: {filepath}")
        # Get forward-slash path with drive letter (if any)
        resolved_path = path_obj.fslash(with_drive=True)
        return resolved_path
    except Exception as e:
        logger.debug(f"Unable to resolve path: {filepath} error: {e}")
        return filepath

def log_error(msg, e):
    """
    Logs an error message and then raises a hou.NodeError, chaining the original exception.

    Args:
        msg (str): The custom error message to log and include in the NodeError.
        e (Exception): The original exception that was caught.
    """
    # Log the detailed error message including the type and message of the original exception
    logger.error(f"{msg} - Caused by: {type(e).__name__}: {e}")
    # Raise a Houdini-specific error, passing the custom message and the original exception
    # This allows Houdini to potentially display more context about the error.
    raise hou.NodeError(msg, e)


def rop_error_handler_original(error_message=None):
    """
    Decorator to handle errors in ROP utility functions within Houdini.

    Wraps a function to catch and handle exceptions, logging errors and converting
    non-hou.NodeError exceptions into hou.NodeError. Includes node path in error
    messages when available, or indicates if the node is None or invalid. An optional
    custom error message can be provided to customize the error output.

    Args:
        error_message (str, optional): Custom error message to include in the exception.
        func (callable): The function to decorate, typically operating on hou.Node objects.

    Returns:
        callable: The wrapped function with error handling.

    Raises:
        hou.NodeError: If the decorated function raises a hou.NodeError or another exception.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except hou.NodeError:
                raise  # Re-raise Houdini-specific node errors unchanged
            except Exception as e:
                node_path_info = ""
                if args:
                    if args[0] is None:
                        node_path_info = " for node 'None' (node not found)"
                    elif isinstance(args[0], hou.Node):
                        try:
                            node_path_info = f" for node '{args[0].path()}'"
                        except AttributeError:
                            node_path_info = " for node with invalid path"
                    else:
                        node_path_info = f" for invalid argument type '{type(args[0]).__name__}'"

                # Use custom error message if provided, otherwise default to function name
                base_msg = error_message if error_message else f"Failed in '{func.__name__}'"
                err_msg = f"{node_path_info} ({base_msg}): {str(e)}"
                logger.error(err_msg)
                raise hou.NodeError(err_msg) from e
        return wrapper
    return decorator


def node_error_handler(error_message=None, warning_only=False):
    """
    Decorator to handle errors in ROP utility functions within Houdini.

    Wraps a function to catch and handle exceptions, logging errors and converting
    non-hou.NodeError exceptions into hou.NodeError. Includes node path in error
    messages when available, or indicates if the node is None or invalid. An optional
    custom error message can be provided to customize the error output. If warning_only
    is True, logs errors as debug messages and does not raise an exception.

    Args:
        error_message (str, optional): Custom error message to include in the exception.
        warning_only (bool, optional): If True, log as debug and do not raise exception.
        func (callable): The function to decorate, typically operating on hou.Node objects.

    Returns:
        callable: The wrapped function with error handling.

    Raises:
        hou.NodeError: If the decorated function raises a hou.NodeError or another exception,
            unless warning_only is True.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except hou.NodeError:
                if warning_only:
                    logger.debug(f"Houdini NodeError in '{func.__name__}': {str(e)}")
                    return None
                raise
            except Exception as e:
                node_path_info = ""
                if args:
                    if args[0] is None:
                        node_path_info = " for node 'None' (node not found)"
                    elif isinstance(args[0], hou.Node):
                        try:
                            node_path_info = f" for node '{args[0].path()}'"
                        except AttributeError:
                            node_path_info = " for node with invalid path"
                    else:
                        node_path_info = f" for invalid argument type '{type(args[0]).__name__}'"

                base_msg = error_message if error_message else f"Failed in '{func.__name__}'"
                err_msg = f"{node_path_info} ({base_msg}): {str(e)}"
                if warning_only:
                    logger.debug(err_msg)
                    return None
                else:
                    logger.error(err_msg)
                    raise hou.NodeError(err_msg) from e
        return wrapper
    return decorator


def generic_error_handler(error_message=None, warning_only=False):
    """
    Generic error handler decorator, adaptable for Houdini and other contexts.

    Wraps a function to catch and handle exceptions. It logs errors and,
    unless warning_only is True, raises hou.NodeError (or a more generic
    custom error if not in a Houdini context where hou.NodeError is appropriate).
    Attempts to include context about the first argument if it's a hou.Node.
    The 'error_message' parameter is intended to be added as a note to the
    exception for better user readability.

    Args:
        error_message (str, optional): Custom message to be added as a note
                                       to the exception.
        warning_only (bool, optional): If True, logs the error as debug and
                                       returns None instead of raising.

    Returns:
        callable: The wrapped function with error handling.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except hou.NodeError as e_node_error:  # Caught existing hou.NodeError
                if warning_only:
                    logger.debug(f"Suppressed Houdini NodeError in '{func.__name__}': {str(e_node_error)}")
                    return None

                # Attempt to add the decorator's error_message as a note
                if error_message:
                    try:
                        if hasattr(e_node_error, 'add_note'):
                            e_node_error.add_note(error_message)
                        else:  # Fallback: append to the existing message
                            current_msg = e_node_error.args[0] if e_node_error.args else str(e_node_error)
                            e_node_error.args = (f"{current_msg}\nNote (from decorator): {error_message}",) + e_node_error.args[
                                                                                                              1:]
                    except Exception as note_ex:
                        logger.warning(f"Could not add/append note to existing hou.NodeError: {note_ex}")
                raise  # Re-raise the (potentially modified) hou.NodeError
            except Exception as e_general:  # Caught a general Exception
                context_info = ""
                if args:  # Check if there are any positional arguments
                    first_arg = args[0]
                    if isinstance(first_arg, hou.Node):
                        try:
                            context_info = f" for node '{first_arg.path()}'"
                        except hou.ObjectWasDeleted:
                            context_info = " for a deleted Houdini node"
                        except AttributeError:  # path() might fail or node is not fully formed
                            context_info = " for a Houdini node (path retrieval failed)"
                        except Exception as path_ex:  # Catch any other error during path access
                            logger.debug(f"Minor error getting path for {first_arg}: {path_ex}")
                            context_info = " for a Houdini node (path retrieval issue)"
                    elif first_arg is None:
                        context_info = " (first argument was None)"
                    else:
                        # For non-Node types, just mention the type of the first argument
                        context_info = f" (first argument type: '{type(first_arg).__name__}')"
                # If no args, context_info remains an empty string

                # Main message for the new hou.NodeError
                base_msg = f"Operation failed in '{func.__name__}'"
                main_exception_content = f"{base_msg}{context_info}: {str(e_general)}"

                new_hne = hou.NodeError(main_exception_content)

                # Add the decorator's 'error_message' as a note
                if error_message:
                    try:
                        if hasattr(new_hne, 'add_note'):
                            new_hne.add_note(error_message)
                        else:  # Fallback: append to the new message
                            current_msg = new_hne.args[0] if new_hne.args else ""
                            new_hne.args = (f"{current_msg}\nNote: {error_message}",) + new_hne.args[1:]
                    except Exception as note_ex:
                        logger.warning(f"Could not add/append note to new hou.NodeError: {note_ex}")

                if warning_only:
                    # str(new_hne) will include the note if appended or if add_note worked and Python/Houdini displays it
                    logger.debug(str(new_hne))
                    return None
                else:
                    logger.error(str(new_hne))
                    raise new_hne from e_general

        return wrapper

    return decorator

def rop_error_handler(error_message=None, warning_only=False):
    """
    Decorator to handle errors in utility functions, suitable for both node-based and non-node-based functions.

    Wraps a function to catch and handle exceptions, logging errors and converting non-hou.NodeError exceptions
    into hou.NodeError for Houdini compatibility. If a hou.Node is provided as an argument, includes node path
    information in the error message. Supports custom error messages and a warning-only mode where errors are
    logged but not raised.

    Args:
        error_message (str, optional): Custom error message to include in the exception.
        warning_only (bool, optional): If True, log errors as debug messages and return None instead of raising.

    Returns:
        callable: The wrapped function with error handling.

    Raises:
        hou.NodeError: If the decorated function raises an exception, unless warning_only is True.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except hou.NodeError as e:
                if warning_only:
                    logger.debug(f"Houdini NodeError in '{func.__name__}': {str(e)}")
                    return None
                raise
            except Exception as e:
                # Check for a node in the arguments
                node_path_info = ""
                for arg in args:
                    if isinstance(arg, hou.Node):
                        try:
                            node_path_info = f" for node '{arg.path()}'"
                        except AttributeError:
                            node_path_info = " for node with invalid path"
                        break
                    elif arg is None and func.__name__ in ["get_node_type", "get_default_task_template",
                                                           "get_generator_task_template"]:
                        node_path_info = " for node 'None' (node not found)"
                        break

                # Use custom error message if provided, otherwise default to function name
                base_msg = error_message if error_message else f"Failed in '{func.__name__}'"
                err_msg = f"{base_msg}{node_path_info}: {str(e)}"

                if warning_only:
                    logger.debug(err_msg)
                    return None
                else:
                    logger.error(err_msg)
                    raise hou.NodeError(err_msg) from e

        return wrapper

    return decorator