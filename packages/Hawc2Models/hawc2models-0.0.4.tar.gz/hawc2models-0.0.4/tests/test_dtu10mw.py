import os
import shutil
from . import tfp
from hawc2models import DTU10MW
import pytest


def test_versions():
    f = tfp / 'tmp/DTU10MW_RWT'

    if f.exists():
        shutil.rmtree(f)
    DTU10MW(folder=f)  # newest version
    shutil.rmtree(f)
    # no tags at the moment
    # DTU10MW(folder=f, version='refs/tags/v1.0.1')  # specific tag
    # DTU10MW.rmtree(f)
    DTU10MW(folder=f, version='5e242c07eb6bd5b96f6803d2c2170e7f91a879b4')  # specific commit
    shutil.rmtree(f)
    DTU10MW(folder=f, version='5e242c07eb6bd5b96f6803d2c2170e7f91a879b4',
            known_hash='1dbe19521e49e4926e65e8071b90a0c1c2b8e5778516a128f9b56eaac6db87ee')  # specific commit
    shutil.rmtree(f)
    with pytest.raises(ValueError, match='SHA256 hash of downloaded file'):
        DTU10MW(folder=f, version='5e242c07eb6bd5b96f6803d2c2170e7f91a879b4',
                known_hash='wrong_hash_1dbe19521e49e4926e65e8071b90a0c1c2b8e5778516a128f9b56eaac6db87ee')
