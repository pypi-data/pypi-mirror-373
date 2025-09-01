from hawc2models.reference_models._reference_model import ReferenceModel
from hawc2models.utils import get_all_subclasses, delete_download_cache
import pytest
from tests import tfp, npt
import shutil
from hawc2models import version


@pytest.mark.parametrize('model_cls', get_all_subclasses(ReferenceModel))
def test_reference_models(model_cls):

    tmp_folder = tfp / 'tmp'
    tmp_folder.mkdir(exist_ok=True)
    htc: ReferenceModel = model_cls(str(tmp_folder / model_cls.__name__))
    htc.strip()

    htc.add_standard_output()

    htc.set_fixed_pitch_rotorspeed(pitch=2.5, rotor_speed=0.6)
    for b in [1, 2, 3]:
        r = htc.get_pitch_relative(blade_nr=b)
        npt.assert_array_equal(r.body2_eulerang.values, [0, 0, -2.5])
    shaft_rot = htc.new_htc_structure.constraint.get_subsection_by_name('shaft_rot')
    assert shaft_rot.name_ == 'bearing3'
    npt.assert_equal(shaft_rot.omegas[0], 0.6)

    htc.set_tilt_cone_yaw(4, 5, 6)

    htc.save()

    htc.make_onshore()
    shutil.rmtree(tmp_folder)


def test_delete_download_cache():
    delete_download_cache()


def test_version():
    assert version.__version__.startswith(".".join(map(str, version.__version_tuple__[:3])))
