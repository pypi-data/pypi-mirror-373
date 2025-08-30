"""Dynamic UDTF file loading utility."""

import ast
import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import List, Set, Tuple, Union

logger = logging.getLogger(__name__)


class UDTFLoaderError(Exception):
    pass


class UDTFFileValidationError(UDTFLoaderError):
    pass


class UDTFImportError(UDTFLoaderError):
    pass


def parse_udtf_paths(udtf_files_input: Union[str, List[str], None]) -> List[Path]:
    if not udtf_files_input:
        return []

    if isinstance(udtf_files_input, str):
        if not udtf_files_input.strip():
            return []
        paths = [p.strip() for p in udtf_files_input.split(':') if p.strip()]
    else:
        paths = [str(p) for p in udtf_files_input]
    
    discovered_files = []
    
    for path_str in paths:
        path = Path(path_str).resolve()
        
        if not path.exists():
            raise UDTFLoaderError(f"UDTF path does not exist: {path}")
        
        if path.is_file():
            if path.suffix == '.py':
                discovered_files.append(path)
            else:
                logger.warning(f"Ignoring non-Python file: {path}")
        elif path.is_dir():
            py_files = list(path.rglob('*.py'))
            discovered_files.extend(py_files)
            logger.info(f"Found {len(py_files)} Python files in directory: {path}")
        else:
            raise UDTFLoaderError(f"Invalid path type: {path}")
    
    return discovered_files


def validate_python_file(file_path: Path) -> None:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        ast.parse(content, filename=str(file_path))
        
    except SyntaxError as e:
        raise UDTFFileValidationError(
            f"Syntax error in {file_path}:{e.lineno}: {e.msg}"
        ) from e
    except UnicodeDecodeError as e:
        raise UDTFFileValidationError(
            f"Encoding error in {file_path}: {e}"
        ) from e
    except Exception as e:
        raise UDTFFileValidationError(
            f"Failed to validate {file_path}: {e}"
        ) from e


def import_udtf_module(file_path: Path, loaded_modules: Set[str]) -> str:
    try:
        module_name = f"udtf_module_{abs(hash(str(file_path)))}"

        counter = 0
        original_name = module_name
        while module_name in loaded_modules or module_name in sys.modules:
            counter += 1
            module_name = f"{original_name}_{counter}"

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise UDTFImportError(f"Could not create module spec for {file_path}")
        
        module = importlib.util.module_from_spec(spec)

        sys.modules[module_name] = module
        loaded_modules.add(module_name)

        spec.loader.exec_module(module)
        
        logger.info(f"Successfully imported UDTF module: {file_path} as {module_name}")
        return module_name
        
    except ImportError as e:
        raise UDTFImportError(
            f"Import error in {file_path}: {e}"
        ) from e
    except Exception as e:
        if module_name in sys.modules:
            del sys.modules[module_name]
        if module_name in loaded_modules:
            loaded_modules.remove(module_name)
        
        raise UDTFImportError(
            f"Failed to import {file_path}: {e}"
        ) from e


def load_udtf_files(udtf_files_input: Union[str, List[str], None]) -> Tuple[List[str], List[str]]:
    if not udtf_files_input:
        logger.info("No UDTF files specified")
        return [], []
    
    loaded_modules = set()
    successful_modules = []
    error_messages = []
    
    try:
        file_paths = parse_udtf_paths(udtf_files_input)
        
        if not file_paths:
            logger.info("No Python files found in specified UDTF paths")
            return [], []
        
        logger.info(f"Loading {len(file_paths)} UDTF files...")
        
        for file_path in file_paths:
            try:
                validate_python_file(file_path)

                module_name = import_udtf_module(file_path, loaded_modules)
                successful_modules.append(module_name)
                
            except (UDTFFileValidationError, UDTFImportError) as e:
                error_msg = f"Failed to load UDTF file {file_path}: {e}"
                logger.error(error_msg)
                error_messages.append(error_msg)
                
            except Exception as e:
                error_msg = f"Unexpected error loading UDTF file {file_path}: {e}"
                logger.error(error_msg)
                error_messages.append(error_msg)
        
        if successful_modules:
            logger.info(f"Successfully loaded {len(successful_modules)} UDTF modules")
        
        if error_messages:
            logger.warning(f"Failed to load {len(error_messages)} UDTF files")
            
    except UDTFLoaderError as e:
        error_msg = f"UDTF loading failed: {e}"
        logger.error(error_msg)
        error_messages.append(error_msg)
    
    return successful_modules, error_messages


