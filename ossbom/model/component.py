from packageurl import PackageURL
from typing import Set

from .base import Serializable
from .dependency_env import DependencyEnv


class Component(Serializable):
    def __init__(self,
                 name: str,
                 version: str,
                 source: Set[str] = set(),
                 env: Set[DependencyEnv] = set(),
                 type: str = "library") -> None:

        self.name = name
        self.version = version
        self.source = source
        self.env = env
        self.type = type

    @classmethod
    def create(cls,
               name: str,
               version: str,
               source: str = None,
               env: str = None,
               type: str = "library"
               ):

        if source:
            source = {source}
        else:
            source = set()

        if env:
            env = {DependencyEnv(env)}
        return cls(name, version, source, env, type)

    def __hash__(self):
        # Hash based on the name and version concatenated
        return hash(self.get_purl().to_string())

    def __eq__(self, other):
        # Equality based on name and version
        if not isinstance(other, Component):
            return NotImplemented
        return self.name == other.name and self.version == other.version

    def add_source(self, source):
        self.source.add(source)

    def add_env(self, env):
        self.env.add(env)

    def get_type(self):
        return self.type

    def get_purl(self):
        return PackageURL(name=self.name, version=self.version, type=self.type)

    def __repr__(self):
        return f"pkg:{self.type}/{self.name}@{self.version} Source:({', '.join([s for s in self.source])}) Env:({', '.join([t.value for t in self.env])})"

    def to_dict(self):
        return {
            "name": self.name,
            "version": self.version,
            "source": list(self.source) if self.source else [],
            "env": [t.value for t in self.env] if self.env else [],
            "type": self.type
        }

    @classmethod
    def from_dict(cls, data):
        name = data['name']  # Not optional
        version = data['version']  # Not optional
        type = data.get("type", "library")
        env = set(DependencyEnv(e) for e in data.get('env', []))
        source = set(data.get('source', []))

        return Component(name, version, source, env, type)

    @staticmethod
    def get_hash(name, version, type):
        return hash(PackageURL(name=name, version=version, type=type).to_string())
