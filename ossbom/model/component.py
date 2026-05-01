from packageurl import PackageURL
from typing import Set

from .base import Serializable
from .dependency_env import DependencyEnv


class Component(Serializable):
    def __init__(self,
                 name: str,
                 version: str,
                 source: Set[str] | None = None,
                 env: Set[DependencyEnv] | None = None,
                 type: str = "library",
                 location: list | None = None,
                 metadata: dict | None = None,
                 qualifiers: dict | None = None,
                 subpath: str | None = None,
                 namespace: str | None = None) -> None:

        self.name = name
        self.version = version
        self.source = source if source else set()
        self.env = env if env else set()
        self.type = type
        self.location = location if location else []
        self.metadata = metadata if metadata else {}
        self.qualifiers = dict(qualifiers) if qualifiers else {}
        self.subpath = subpath
        self.namespace = namespace

    @classmethod
    def create(cls,
               name: str,
               version: str,
               source: str | None = None,
               env: str | None = None,
               type: str = "library",
               location: list | None = None,
               metadata: dict | None = None,
               qualifiers: dict | None = None,
               subpath: str | None = None,
               namespace: str | None = None
               ):

        source = {source} if source else set()
        env = {DependencyEnv(env)} if env else set()
        location = location if location else []
        metadata = metadata if metadata else {}

        return cls(name, version, source, env, type, location, metadata, qualifiers, subpath, namespace)

    def __hash__(self):
        return hash(self.get_purl().to_string())

    def __eq__(self, other):
        if not isinstance(other, Component):
            return NotImplemented
        return (
            self.name == other.name
            and self.version == other.version
            and self.type == other.type
            and self.namespace == other.namespace
            and (self.qualifiers or {}) == (other.qualifiers or {})
            and self.subpath == other.subpath
        )

    def add_source(self, source):
        self.source.add(source)

    def add_env(self, env):
        self.env.add(env)

    def get_type(self):
        return self.type

    def add_location(self, location):
        self.location.append(location)

    def get_purl(self):
        return PackageURL(
            name=self.name,
            namespace=self.namespace,
            version=self.version,
            type=self.type,
            qualifiers=self.qualifiers or None,
            subpath=self.subpath,
        )

    def __repr__(self):
        return f"{self.get_purl().to_string()} Source:({', '.join([s for s in self.source])}) Env:({', '.join([t.value for t in self.env])})"

    def to_dict(self):
        data = {
            "name": self.name,
            "version": self.version,
            "source": list(self.source) if self.source else [],
            "env": [t.value for t in self.env] if self.env else [],
            "type": self.type,
            "location": self.location,
            "metadata": self.metadata,
        }
        if self.namespace:
            data["namespace"] = self.namespace
        if self.qualifiers:
            data["qualifiers"] = dict(self.qualifiers)
        if self.subpath:
            data["subpath"] = self.subpath
        return data

    @classmethod
    def from_dict(cls, data):
        name = data['name']  # Not optional
        version = data['version']  # Not optional
        type = data.get("type", "library")
        env = set(DependencyEnv(e) for e in data.get('env', []))
        source = set(data.get('source', []))
        location = data.get('location', [])
        metadata = data.get('metadata', {})
        qualifiers = data.get('qualifiers') or {}
        subpath = data.get('subpath')
        namespace = data.get('namespace')

        return Component(name, version, source, env, type, location, metadata, qualifiers, subpath, namespace)

    @staticmethod
    def get_hash(
        name,
        version,
        type,
        qualifiers: dict | None = None,
        subpath: str | None = None,
        namespace: str | None = None,
    ):
        return hash(PackageURL(
            name=name,
            namespace=namespace,
            version=version,
            type=type,
            qualifiers=qualifiers or None,
            subpath=subpath,
        ).to_string())
