import json

from datetime import datetime

from .factory import SBOMConverterFactory
from ..tests.test_utility import (
    create_example_sbom,
    create_massive_sbom,
    create_example_cyclonedx_dict,
    create_example_cyclonedx_object,
)

from cyclonedx.output.json import JsonV1Dot5


def clean_dict(d):
    """Recursively removes 'bom-ref' keys from a dictionary."""
    if isinstance(d, dict):
        return {k: clean_dict(v) for k, v in d.items() if k not in ["bom-ref", "ref", "serialNumber", "$schema", "properties", "dependencies", "affects", "timestamp"]}
    elif isinstance(d, list):
        return sorted((clean_dict(item) for item in d), key=lambda x: sorted(x.items()))
    return d


def compare_dicts_recursive(dict1, dict2):
    """Compares two dictionaries after recursively removing 'bom-ref' keys."""
    assert clean_dict(dict1) == clean_dict(dict2)


def test_from_cyclonedx_dict():

    sbom = create_example_cyclonedx_dict()

    ossbom = SBOMConverterFactory.from_cyclonedx_dict(sbom)
    new_sbom = SBOMConverterFactory.to_cyclonedx_dict(ossbom)

    compare_dicts_recursive(sbom, new_sbom)


def test_from_cyclonedx():

    sbom = create_example_cyclonedx_object()

    ossbom = SBOMConverterFactory.from_cyclonedx(sbom)
    new_sbom = SBOMConverterFactory.to_cyclonedx(ossbom)

    json_sbom = SBOMConverterFactory.to_cyclonedx_dict(ossbom)

    my_json_outputter: 'JsonOutputter' = JsonV1Dot5(new_sbom)
    cdx_json = my_json_outputter.output_as_string()
    json_new_sbom = json.loads(cdx_json)

    # Recursively Compare json while ignoring bom-ref
    compare_dicts_recursive(json_sbom, json_new_sbom)


def test_to_cyclonedx_dict():

    sbom = create_example_sbom()

    cdx_dict = SBOMConverterFactory.to_cyclonedx_dict(sbom)
    from pprint import pprint
    pprint(cdx_dict)
    new_sbom = SBOMConverterFactory.from_cyclonedx_dict(cdx_dict)

    assert str(sbom.to_dict()) == str(new_sbom.to_dict())


def test_to_cyclonedx():

    sbom = create_example_sbom()
    cdx = SBOMConverterFactory.to_cyclonedx(sbom)
    new_sbom = SBOMConverterFactory.from_cyclonedx(cdx)

    assert sbom.to_dict() == new_sbom.to_dict()


def test_to_minibom():
    
    sbom = create_example_sbom()

    sbom_dict = SBOMConverterFactory.to_minibom(sbom)
    new_sbom = SBOMConverterFactory.from_minibom(sbom_dict)

    assert sbom.to_dict() == new_sbom.to_dict()


def test_from_minibom():

    sbom = create_example_sbom()

    sbom_dict = SBOMConverterFactory.to_minibom(sbom)
    new_sbom = SBOMConverterFactory.from_minibom(sbom_dict)

    assert sbom.to_dict() == new_sbom.to_dict()


def test_massive_sbom():
    # This SBOM should be processed within 5 seconds AND the max size of the
    # OSSBOM JSON object should be less than 400kb

    sbom = create_massive_sbom()

    start_time = datetime.now()
    sbom_dict = SBOMConverterFactory.to_minibom(sbom)

    end_time = datetime.now()

    assert (end_time - start_time).seconds < 2

    max_size = 400 * 1024
    assert (len(str(sbom_dict)) < max_size)


def test_from_cyclonedx_dict_invalid_json_raises():
    """Test that from_cyclonedx_dict raises an exception for invalid CycloneDX JSON."""
    invalid_sbom = {"not": "a valid cyclonedx sbom"}

    try:
        SBOMConverterFactory.from_cyclonedx_dict(invalid_sbom)
        assert False, "Expected exception was not raised"
    except Exception as e:
        assert "Invalid CycloneDX JSON" in str(e)


def test_to_cyclonedx_with_component_metadata():
    """Test that component metadata is preserved when converting to CycloneDX."""
    from ..model.ossbom import OSSBOM
    from ..model.component import Component
    from ..model.dependency_env import DependencyEnv

    sbom = OSSBOM(name="Metadata Test SBOM")
    comp = Component(
        name="meta-pkg",
        version="1.0.0",
        source={"pypi"},
        env={DependencyEnv.DEV},
        type="library",
        metadata={"license": "MIT", "homepage": "https://example.com"}
    )
    sbom.add_components([comp])

    cdx = SBOMConverterFactory.to_cyclonedx(sbom)

    cdx_components = list(cdx.components)
    assert len(cdx_components) == 1
    props = {p.name: p.value for p in cdx_components[0].properties}
    assert props.get("license") == "MIT"
    assert props.get("homepage") == "https://example.com"


def test_cyclonedx_roundtrip_preserves_qualifiers_subpath_namespace():
    """Test that a PURL with path qualifier, subpath, and namespace survives a CycloneDX round-trip."""
    from ..model.ossbom import OSSBOM
    from ..model.component import Component
    from ..model.dependency_env import DependencyEnv

    sbom = OSSBOM(name="Purl Roundtrip Test")
    comp = Component(
        name="repo",
        version="main",
        source={"github"},
        env={DependencyEnv.DEV},
        type="github",
        namespace="myorg",
        qualifiers={"path": "examples/ex1"},
        subpath="sub/dir",
    )
    sbom.add_components([comp])

    # Round-trip via CycloneDX object
    cdx = SBOMConverterFactory.to_cyclonedx(sbom)
    restored_sbom = SBOMConverterFactory.from_cyclonedx(cdx)

    components = list(restored_sbom.get_components())
    assert len(components) == 1
    restored = components[0]

    assert restored.namespace == "myorg"
    assert restored.qualifiers == {"path": "examples/ex1"}
    assert restored.subpath == "sub/dir"
    assert str(restored.get_purl()) == "pkg:github/myorg/repo@main?path=examples/ex1#sub/dir"
