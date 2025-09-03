from typing import Callable, Union, Awaitable, List
from acex.config_map import ConfigMap
from .compiled_logical_node import CompiledLogicalNode

import os
import importlib.util
import sys
from pathlib import Path
import inspect


class ConfigCompiler: 
    """
    This class enriches logical nodes with
    configuration from ConfigMaps.

    compile() is being run as the entrypoint
    1. Selects a logical node as self.ln, instancitating a CompiledLogicalNode
    2. Discovers processors and registers with CompiledLogicalNode.register()
    3. Discovers all ConfigMaps and registers those with matching ConfigMap.Filter.
    4. Runs all processors with CompiledLogicalNode.compile()
    """


    def __init__(self):
        self.ln = None
        self.config_map_paths = []
        self.config_maps = []

    def add_config_map_path(self, dir_path: str):
        self.config_map_paths.append(dir_path)
        self._find_and_register_config_maps(dir_path)

    def add_config_map(self, config_map: ConfigMap):
        """
        Adds a ConfigMap to the compiler.
        """
        self.config_maps.append(config_map)

    def _find_and_register_config_maps(self, dir_path: str):
        """
        Finds all ConfigMaps in the given directory and subdirectories and registers them.
        """
        py_files = self._find_python_files_in_dir(dir_path)
        for file_path in py_files:
            module_name = Path(file_path).stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            try:
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
            except Exception as e:
                print(f"Failed to import {file_path}: {e}")
                continue
            # Hitta alla variabler som är instanser av ConfigMap (men inte klasser)
            for name, obj in module.__dict__.items():
                if isinstance(obj, ConfigMap) and not isinstance(obj, type):
                    self.add_config_map(obj)
                    print(f"Registered ConfigMap instance: '{name}' from {file_path}")

    def _find_python_files_in_dir(self, dir_path: str) -> list:
        """
        Recursively finds all .py files in the given directory and subdirectories.
        """
        py_files = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))
        return py_files


    def _find_processors_for_ln(self):
        """
        Finds all processors that match the logical node's filters.
        This method should be implemented to discover and register processors.
        """
        for config_map in self.config_maps:
            if self.ln.check_config_map_filter(config_map):
                self.ln.register(config_map.compile)


    async def compile(self, logical_node: dict) -> dict:

        self.ln = CompiledLogicalNode(logical_node)
        self._find_processors_for_ln()
        await self.ln.compile()
        return self.ln.response
