from collections import OrderedDict
from pathlib import Path
from typing import List

from dataclasses import dataclass, field
import tomlkit

@dataclass(order=True)
class Config:
    project_module_dirs: List[str] = field(default_factory=list)
    third_party_module_dirs: List[str] = field(default_factory=list)
    include_modules: List[str] = field(default_factory=list)
    exclude_modules: List[str] = field(default_factory=list)

def read_config(path):
    with open(path) as config_file:
        config = tomlkit.load(config_file)

    return Config(**config.unwrap())
