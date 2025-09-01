import os
import shutil
from . import tfp
from hawc2models import IEA22MW
import pytest


def test_versions():
    f = tfp / 'tmp/IEA-22-280-RWT-Monopile'

    if f.exists():
        shutil.rmtree(f)
    IEA22MW(folder=f)  # newest version
    shutil.rmtree(f)
    IEA22MW(folder=f, version='refs/tags/v1.0.1')  # specific tag
    shutil.rmtree(f)
    IEA22MW(folder=f, version='3afe3f648a36f26394b054dc9fa18b33c914325c')  # specific commit

    IEA22MW(folder=f, version='3afe3f648a36f26394b054dc9fa18b33c914325c',
            known_hash='a6c085d8d2e9a12be506ed6541cd5191d1d31d74b9908528d931929cf85c77de')  # specific commit
    shutil.rmtree(f)
    with pytest.raises(ValueError, match='SHA256 hash of downloaded file'):
        IEA22MW(folder=f, version='3afe3f648a36f26394b054dc9fa18b33c914325c',
                known_hash='wrong_hash_a6c085d8d2e9a12be506ed6541cd5191d1d31d74b9908528d931929cf85c77de')
