from __future__ import annotations

import importlib.metadata

import cditools as m


def test_version():
    assert importlib.metadata.version("cditools") == m.__version__
