import json
import pytest


@pytest.fixture()
def cluster_definition():
    return {
        "name": "cluster_definition",
        "namespace": "meta.physical",
        "metatype": "noun",
        "attributes": {
            "id": {
                "type": "integer",
                "required": True,
                "description": "The unique identifier for the command",
            },
            "name": {
                "description": "The name of the cluster",
                "required": True,
                "type": "string",
            },
            "type": {
                "description": "The cluster type. [Presto, Hive, etc.]",
                "required": True,
                "type": "string",
            },
            "location": {
                "description": "",
                "required": True,
                "type": "enum",
                "definition": ["a", "b"],
            },
        },
    }


@pytest.fixture()
def cluster_definition_json(cluster_definition):
    return json.dumps(cluster_definition)


@pytest.fixture()
def sub_definition():
    return {
        "name": "sub_definition",
        "namespace": "meta.physical",
        "metatype": "noun",
        "attributes": {
            "id": {
                "type": "integer",
                "required": True,
                "description": "The unique identifier for the command",
            },
            "name": {
                "description": "The name of the cluster",
                "required": True,
                "type": "string",
            },
            "type": {
                "description": "The cluster type. [Presto, Hive, etc.]",
                "required": True,
                "type": "string",
            },
            "location": {
                "description": "",
                "required": True,
                "type": "enum",
                "definition": ["a", "b"],
            },
        },
    }


@pytest.fixture()
def sub_definition_json(sub_definition):
    return json.dumps(sub_definition)


@pytest.fixture()
def cluster_definition_rel():
    return {
        "name": "cluster_definition_rel",
        "namespace": "meta.physical",
        "metatype": "relationship",
        "ref_from": "meta.physical.cluster_definition",
        "ref_to": "meta.physical.sub_definition",
        "attributes": {
            "id": {
                "type": "integer",
                "required": True,
                "description": "The unique identifier for the command",
            },
            "name": {
                "description": "The name of the cluster",
                "required": True,
                "type": "string",
            },
            "type": {
                "description": "The cluster type. [Presto, Hive, etc.]",
                "required": True,
                "type": "string",
            },
            "location": {
                "description": "",
                "required": True,
                "type": "enum",
                "definition": ["a", "b"],
            },
        },
    }
