from pathlib import Path
import shutil


from hawc2models.utils import download
from hawc2models.reference_models._reference_model import ReferenceModel
from wetb.hawc2.htc_file import HTCFile
import glob


class IEA22MW(HTCFile, ReferenceModel):
    def __init__(self, folder='IEA-22-280-RWT-Monopile', version=None, known_hash=None):
        """
        Parameters
        ----------
        folder : str or Path
            destination folder
        version : str or None
            Specific version or None (lastest commit)
            The version string can be either a tag, e.g. 'refs/tags/v1.0.1'
            or commit, e.g. '3afe3f648a36f26394b054dc9fa18b33c914325c'
        known_hash : str or None
            If None, no checks are made and the downloaded hash is printed
            If str and the cache folder already exists locally, its hash will be compared to
            *known_hash*. If they are not the same, this is interpreted as the file
            needing to be updated and it will be downloaded again.
            If the hash of the downloaded file does not match *known_hash*, an error will be raised

        Returns
        -------
        HTCFile object
        """
        folder = Path(folder)
        if not folder.exists():
            if version is None:
                version = 'refs/heads/main'

            f_lst = download(f'https://github.com/IEAWindSystems/IEA-22-280-RWT/archive/{version}.zip',
                             unzip=True, known_hash=known_hash)
            cache_dir = glob.glob(f_lst[0][:f_lst[0].index('.zip.unzip')] +
                                  '.zip.unzip/IEA-22-280-RWT-*/HAWC2/IEA-22-280-RWT-Monopile')[0]
            shutil.copytree(cache_dir, folder, dirs_exist_ok=True)
            shutil.rmtree(folder / 'htc/_master')
            shutil.rmtree(folder / 'htc/DLC')
        HTCFile.__init__(self, folder / 'htc/iea_22mw_rwt_steps.htc')

        self.set_name('iea_22mw_rwt')

    def make_onshore(self):
        ReferenceModel.make_onshore(self)
        self.new_htc_structure.get_subsection_by_name('monopile').delete()
        base = self.new_htc_structure.orientation.base
        base.mbdy = 'tower'
        base.inipos = [0, 0, 0]
        self.new_htc_structure.orientation.get_subsection_by_name('monopile', field='mbdy1').delete()
        self.new_htc_structure.constraint.fix0.mbdy = 'tower'
        self.new_htc_structure.constraint.get_subsection_by_name('monopile', field='mbdy1').delete()
