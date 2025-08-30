from json import load

from py2md.classes import MDHeading, MDReport, MDTable

from .specimenresult import SpecimenResult
from .statistics import Statistics


class BatchResult():
    name: str = None
    nomthick: float = None
    emodlabel: str = None
    emodunit: str = None
    lunit: str = None
    sunit: str = None
    dunit: str = None
    eunit: str = None
    specresults: dict[str, SpecimenResult] = None
    _emodstats: Statistics = None
    _stressstats: Statistics = None
    _normemodstats: Statistics = None
    _normstressstats: Statistics = None
    _strainstats: Statistics = None

    def __init__(self, name: str, nomthick: float) -> None:
        self.name = name
        self.nomthick = nomthick
        self.specresults = {}

    def add_specimen_result(self, specresult: SpecimenResult) -> None:
        self.specresults[specresult.label] = specresult

    def normalise_stress(self, nomthick: float) -> None:
        for specresult in self.specresults.values():
            specresult.normalise_stress(nomthick)

    def trim_max_load(self) -> None:
        for specresult in self.specresults.values():
            specresult.trim_max_load()

    def trim_max_stress(self) -> None:
        for specresult in self.specresults.values():
            specresult.trim_max_stress()

    def calc_emod_load(self, lf1: float, lf2: float) -> None:
        for specresult in self.specresults.values():
            specresult.calc_emod_load(lf1, lf2)

    def calc_emod_strain(self, strn1: float, strn2: float) -> None:
        for specresult in self.specresults.values():
            specresult.calc_emod_strain(strn1, strn2)

    def plot_load_deflection(self, ax=None, figsize=(10, 6)):
        for specresult in self.specresults.values():
            ax = specresult.plot_load_deflection(ax=ax, figsize=figsize)
        ax.set_xlabel(f'Deflection [{self.dunit:s}]')
        ax.set_ylabel(f'Load [{self.lunit:s}]')
        ax.legend()
        return ax

    def plot_stress_strain(self, ax=None, figsize=(10, 6)):
        for specresult in self.specresults.values():
            ax = specresult.plot_stress_strain(ax=ax, figsize=figsize)
        ax.set_xlabel(f'Strain [{self.eunit:s}]')
        ax.set_ylabel(f'Stress [{self.sunit:s}]')
        ax.legend()
        return ax

    def plot_normalised_stress_strain(self, ax=None, figsize=(10, 6)):
        for specresult in self.specresults.values():
            ax = specresult.plot_normalised_stress_strain(ax=ax, figsize=figsize)
        ax.set_xlabel(f'Strain [{self.eunit:s}]')
        ax.set_ylabel(f'Normalised Stress [{self.sunit:s}]')
        ax.legend()
        return ax

    def plot_stress_deflection(self, ax=None, figsize=(10, 6)):
        for specresult in self.specresults.values():
            ax = specresult.plot_stress_deflection(ax=ax, figsize=figsize)
        ax.set_xlabel(f'Deflection [{self.dunit:s}]')
        ax.set_ylabel(f'Stress [{self.sunit:s}]')
        ax.legend()
        return ax

    def plot_normalised_stress_deflection(self, ax=None, figsize=(10, 6)):
        for specresult in self.specresults.values():
            ax = specresult.plot_normalised_stress_deflection(ax=ax, figsize=figsize)
        ax.set_xlabel(f'Deflection [{self.dunit:s}]')
        ax.set_ylabel(f'Normalised Stress [{self.sunit:s}]')
        ax.legend()
        return ax

    @property
    def emodstats(self) -> Statistics:
        if self._emodstats is None:
            emod = [sr.emod for sr in self.specresults.values()]
            self._emodstats = Statistics(emod)
        return self._emodstats

    @property
    def stressstats(self) -> Statistics:
        if self._stressstats is None:
            stress = [sr.maxstress for sr in self.specresults.values()]
            self._stressstats = Statistics(stress)
        return self._stressstats

    @property
    def normemodstats(self) -> Statistics:
        if self._normemodstats is None:
            normemod = [sr.normemod for sr in self.specresults.values()]
            self._normemodstats = Statistics(normemod)
        return self._normemodstats

    @property
    def normstressstats(self) -> Statistics:
        if self._normstressstats is None:
            normstress = [sr.maxnormstress for sr in self.specresults.values()]
            self._normstressstats = Statistics(normstress)
        return self._normstressstats

    @property
    def strainstats(self) -> Statistics:
        if self._strainstats is None:
            strain = [sr.maxstress/sr.emod for sr in self.specresults.values()]
            self._strainstats = Statistics(strain)
        return self._strainstats

    def to_mdobj(self) -> MDReport:
        report = MDReport()
        heading = MDHeading(f'{self.name:s} Results', 1)
        report.add_object(heading)
        table = MDTable()
        table.add_column('Label', 's', '<')
        table.add_column('Width', '.3f', '')
        table.add_column('Thickness', '.3f', '')
        table.add_column('Max Load', '.0f', '')
        table.add_column('Max Stress', '.1f', '')
        table.add_column('Max Norm Stress', '.1f', '')
        if self.emodlabel is not None:
            table.add_column(self.emodlabel, '.0f', '')
            table.add_column('Elastic Modulus', '.0f', '')
            table.add_column('Norm Elastic Modulus', '.0f', '')
        for sr in self.specresults.values():
            row = [sr.label, sr.width, sr.thick, sr.maxload,
                   sr.maxstress, sr.maxnormstress]
            if self.emodlabel is not None:
                row = row + [sr.emodgiven, sr.emod, sr.normemod]
            table.add_row(row)
        report.add_object(table)
        table = MDTable()
        table.add_column('Parameter', 's', '<')
        table.add_column('Mean Value', '.1f')
        table.add_column('Standard Deviation', '.2f')
        table.add_column('B Value', '.1f')
        table.add_column('A Value', '.1f')
        if self.emodlabel is not None:
            row = [
                f'Elastic Modulus [{self.emodunit:s}]',
                self.emodstats.mean,
                self.emodstats.std,
                self.emodstats.B,
                self.emodstats.A,
            ]
            table.add_row(row)
        row = [
            f'Strength [{self.sunit:s}]',
            self.stressstats.mean,
            self.stressstats.std,
            self.stressstats.B,
            self.stressstats.A,
        ]
        table.add_row(row)
        if self.emodlabel is not None:
            row = [
                f'Normalised Elastic Modulus [{self.emodunit:s}]',
                self.normemodstats.mean,
                self.normemodstats.std,
                self.normemodstats.B,
                self.normemodstats.A,
            ]
            table.add_row(row)
        row = [
            f'Normalised Strength [{self.sunit:s}]',
            self.normstressstats.mean,
            self.normstressstats.std,
            self.normstressstats.B,
            self.normstressstats.A,
        ]
        table.add_row(row)
        if self.emodlabel is not None:
            row = [
                'Failure Strain [μS]',
                self.strainstats.mean*1e6,
                self.strainstats.std*1e6,
                self.strainstats.B*1e6,
                self.strainstats.A*1e6,
            ]
            table.add_row(row)
        report.add_object(table)
        return report

    def __str__(self) -> str:
        return self.to_mdobj().__str__()

    def _repr_markdown_(self):
        return self.to_mdobj()._repr_markdown_()


def batch_from_json(jsonfilepath: str):
    with open(jsonfilepath, 'rt') as jsonfile:
        batchdict = load(jsonfile)
    name = batchdict['name']
    nomthick = batchdict['nomthick']
    batch = BatchResult(name, nomthick)
    if 'metainfo' in batchdict:
        if 'emod' in batchdict['metainfo']:
            emodmeta = batchdict['metainfo']['emod']
            batch.emodlabel = emodmeta['value']
            batch.emodunit = emodmeta['unit']
    if 'testinfo' in batchdict:
        if 'load' in batchdict['testinfo']:
            loadmeta = batchdict['testinfo']['load']
            batch.lunit = loadmeta['unit']
        if 'deflection' in batchdict['testinfo']:
            deflmeta = batchdict['testinfo']['deflection']
            batch.dunit = deflmeta['unit']
        if 'stress' in batchdict['testinfo']:
            stressmeta = batchdict['testinfo']['stress']
            batch.sunit = stressmeta['unit']
        if 'strain' in batchdict['testinfo']:
            strainmeta = batchdict['testinfo']['strain']
            batch.eunit = strainmeta['unit']
    for speclabel in batchdict['specimens']:
        specdict = batchdict['specimens'][speclabel]
        active = True
        if 'active' in specdict:
            active = specdict['active']
        if active:
            width = specdict['width']
            thick = specdict['thick']
            specres = SpecimenResult(speclabel, width, thick)
            batch.add_specimen_result(specres)
            if batch.emodlabel is not None:
                emod = specdict['meta'][batch.emodlabel]['value']
                specres.set_emod_given(emod)
            if batch.lunit is not None:
                loaddata = specdict['test'][loadmeta['value']]['data']
                specres.set_load(loaddata)
            if batch.dunit is not None:
                defldata = specdict['test'][deflmeta['value']]['data']
                specres.set_deflection(defldata)
            if batch.sunit is not None:
                stressdata = specdict['test'][stressmeta['value']]['data']
                specres.set_stress(stressdata)
            if batch.eunit is not None:
                straindata = specdict['test'][strainmeta['value']]['data']
                specres.set_strain(straindata)
    batch.normalise_stress(batch.nomthick)
    return batch