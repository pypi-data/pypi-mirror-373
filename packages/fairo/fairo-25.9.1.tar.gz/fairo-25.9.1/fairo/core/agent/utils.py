import functools
import hashlib
import json
import os
import pickle
from pathlib import Path
from typing import Any, Callable, Dict, List, TypeVar, Union

T = TypeVar('T')


def truncate_long_message(content: str, max_lines: int = 100) -> str:
    """
    Simple function to truncate long messages to a maximum number of lines.
    Adds a summary line indicating how many lines were truncated.
    
    Args:
        content: The message content to truncate
        max_lines: Maximum number of lines to keep
        
    Returns:
        Truncated message with summary
    """
    lines = content.split('\n')
    
    # If content is already shorter than max_lines, return unchanged
    if len(lines) <= max_lines:
        return content
    
    # Keep the first max_lines and add a summary
    truncated_content = lines[:max_lines]
    truncated_content.append(f"\n[...{len(lines) - max_lines} more lines truncated...]")
    
    return '\n'.join(truncated_content)


def summarize_with_llm(content: str, llm, prompt: str = None) -> str:
    """
    Generate an AI summary of content using the provided LLM and custom prompt.
    
    Args:
        content: The content to summarize
        llm: The LLM instance to use for summarization
        prompt: Custom prompt to use for summarization, if None uses default
        
    Returns:
        AI-generated summary of the content
    """
    from langchain.schema import HumanMessage, SystemMessage
    
    # Use custom prompt or default
    if prompt is None:
        prompt = f"Please provide a brief summary (3-5 sentences) of the following content:\n\n{content}"
    else:
        # Insert content into custom prompt if it has a placeholder
        if "{content}" in prompt:
            prompt = prompt.format(content=content)
        else:
            prompt = f"{prompt}\n\n{content}"
    
    # Create messages for LLM
    messages = [
        SystemMessage(content="You are a helpful assistant that provides concise summaries."),
        HumanMessage(content=prompt)
    ]
    
    # Get summary from LLM
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        # If summarization fails, return a basic message
        return f"[Content was truncated. Unable to generate summary: {str(e)}]"


def disk_cache(cache_dir: str = '.cache'):
    """
    Cache function results on disk based on hash of input arguments.
    For file paths, it uses file metadata (modification time) for hashing.

    Args:
        cache_dir: Directory to store cached results

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache directory if it doesn't exist
            Path(cache_dir).mkdir(exist_ok=True)

            # Create a unique key based on function name and arguments
            key_parts = [func.__name__]

            # Process args
            for arg in args:
                if isinstance(arg, str) and os.path.isfile(arg):
                    # For files, use path and modification time
                    mtime = os.path.getmtime(arg)
                    key_parts.append(f"{arg}:{mtime}")
                else:
                    # For other arguments
                    key_parts.append(str(arg))

            # Process kwargs
            for k, v in sorted(kwargs.items()):
                if isinstance(v, str) and os.path.isfile(v):
                    # For files, use path and modification time
                    mtime = os.path.getmtime(v)
                    key_parts.append(f"{k}:{v}:{mtime}")
                else:
                    # For other arguments
                    key_parts.append(f"{k}:{v}")

            # Create hash from key parts
            cache_key = hashlib.md5(json.dumps(key_parts).encode()).hexdigest()
            cache_file = os.path.join(cache_dir, cache_key)

            # Check if result is already cached
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)

            # Call the function and cache the result
            result = func(*args, **kwargs)
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)

            return result

        return wrapper

    return decorator


def truncate_content(content, n_lines=5):
    lines = content.split('\n')
    if len(lines) > n_lines:
        truncated = '\n'.join(lines[:n_lines])
        return f"{truncated}\n... [truncated {len(lines) - n_lines} more lines]"
    return content


def truncate_obj_content(obj, n_lines):
    """
    Recursively traverse a Python object and truncate any strings to the specified max_length.

    Args:
        obj: The object to traverse (dict, list, tuple, set, or primitive type)
        max_length: Maximum length to allow for strings

    Returns:
        A copy of the object with all content truncated to n_lines
    """
    if isinstance(obj, str):
        return truncate_content(obj, n_lines)
    elif isinstance(obj, dict):
        return {k: truncate_obj_content(v, n_lines) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [truncate_obj_content(item, n_lines) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(truncate_obj_content(item, n_lines) for item in obj)
    elif isinstance(obj, set):
        return {truncate_obj_content(item, n_lines) for item in obj}
    else:
        # For numbers, booleans, None, etc., return as is
        return obj
