from pathlib import Path
import shutil
import glob

from hawc2models.utils import download
from hawc2models.reference_models._reference_model import ReferenceModel
from wetb.hawc2.htc_file import HTCFile


class DTU10MW(HTCFile, ReferenceModel):
    def __init__(self, folder='DTU_10MW_RWT', version=None, known_hash=None):
        folder = Path(folder)
        if not folder.exists():
            version = version or 'master'
            f_lst = download(
                f'https://gitlab.windenergy.dtu.dk/rwts/dtu-10mw-rwt/-/archive/{version}/dtu-10mw-rwt-{version}.zip',
                known_hash=known_hash,
                unzip=True)
            cache_dir = glob.glob(f_lst[0][:f_lst[0].index('.zip.unzip')] +
                                  '.zip.unzip/dtu-10mw-rwt-*/aeroelastic_models/hawc2')[0]
            shutil.copytree(cache_dir, folder, dirs_exist_ok=True)
        HTCFile.__init__(self, folder / 'htc/DTU_10MW_RWT_wind_steps.htc')

        self.set_name('dtu_10mw_rwt')
