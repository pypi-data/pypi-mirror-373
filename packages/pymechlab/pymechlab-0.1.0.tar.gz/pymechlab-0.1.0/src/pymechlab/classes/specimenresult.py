from matplotlib.pyplot import figure
from numpy import interp


class SpecimenResult():
    label: str = None
    width: float = None
    thick: float = None
    nomthick: float = None
    load: list[float] = None
    maxload: float = None
    deflection: list[float] = None
    strain: list[float] = None
    stress: list[float] = None
    maxstress: float = None
    normstress: list[float] = None
    maxnormstress: float = None
    emodgiven: float = None
    emod: float = None
    normemod: float = None

    def __init__(self, label: str, width: float, thick: float) -> None:
        self.label = label
        self.width = width
        self.thick = thick

    def set_emod_given(self, emod: float):
        self.emodgiven = emod

    def set_load(self, load: list[float]) -> None:
        self.load = load
        self.maxload = max(load)

    def set_deflection(self, deflection: list[float]) -> None:
        self.deflection = deflection

    def set_strain(self, strain: list[float]) -> None:
        self.strain = strain

    def set_stress(self, stress: list[float]) -> None:
        self.stress = stress
        self.maxstress = max(stress)

    def normalise_stress(self, nomthick: float) -> None:
        self.nomthick = nomthick
        self.normstress = [sti*self.thick/nomthick for sti in self.stress]
        self.maxnormstress = max(self.normstress)

    def trim_max_load(self) -> None:
        indmax = self.load.index(self.maxload)
        self.set_load(self.load[0:indmax+1])
        if self.deflection is not None:
            self.set_deflection(self.deflection[0:indmax+1])
        if self.strain is not None:
            self.set_strain(self.strain[0:indmax+1])
        if self.stress is not None:
            self.set_stress(self.stress[0:indmax+1])
            self.normalise_stress(self.nomthick)

    def trim_max_stress(self) -> None:
        indmax = self.stress.index(self.maxstress)
        self.set_stress(self.stress[0:indmax+1])
        self.normalise_stress(self.nomthick)
        if self.load is not None:
            self.set_load(self.load[0:indmax+1])
        if self.deflection is not None:
            self.set_deflection(self.deflection[0:indmax+1])
        if self.strain is not None:
            self.set_strain(self.strain[0:indmax+1])

    def plot_load_deflection(self, ax=None, figsize=(10, 6)):
        if ax is None:
            fig = figure(figsize=figsize)
            ax = fig.gca()
            ax.grid(True)
        ax.plot(self.deflection, self.load, label=self.label)
        return ax

    def plot_stress_strain(self, ax=None, figsize=(10, 6)):
        if ax is None:
            fig = figure(figsize=figsize)
            ax = fig.gca()
            ax.grid(True)
        ax.plot(self.strain, self.stress, label=self.label)
        return ax

    def plot_normalised_stress_strain(self, ax=None, figsize=(10, 6)):
        if ax is None:
            fig = figure(figsize=figsize)
            ax = fig.gca()
            ax.grid(True)
        ax.plot(self.strain, self.normstress, label=self.label)
        return ax

    def plot_stress_deflection(self, ax=None, figsize=(10, 6)):
        if ax is None:
            fig = figure(figsize=figsize)
            ax = fig.gca()
            ax.grid(True)
        ax.plot(self.deflection, self.stress, label=self.label)
        return ax

    def plot_normalised_stress_deflection(self, ax=None, figsize=(10, 6)):
        if ax is None:
            fig = figure(figsize=figsize)
            ax = fig.gca()
            ax.grid(True)
        ax.plot(self.deflection, self.normstress, label=self.label)
        return ax

    def calc_emod_load(self, lf1: float, lf2: float) -> None:
        load1 = self.maxload*lf1
        load2 = self.maxload*lf2
        strn1 = interp(load1, self.load, self.strain)
        strn2 = interp(load2, self.load, self.strain)
        strs1 = interp(load1, self.load, self.stress)
        strs2 = interp(load2, self.load, self.stress)
        nrmstrs1 = interp(load1, self.load, self.normstress)
        nrmstrs2 = interp(load2, self.load, self.normstress)
        self.emod = (strs2-strs1)/(strn2-strn1)
        self.normemod = (nrmstrs2-nrmstrs1)/(strn2-strn1)

    def calc_emod_strain(self, strn1: float, strn2: float) -> None:
        strs1 = interp(strn1, self.strain, self.stress)
        strs2 = interp(strn2, self.strain, self.stress)
        nrmstrs1 = interp(strn1, self.strain, self.normstress)
        nrmstrs2 = interp(strn2, self.strain, self.normstress)
        self.emod = (strs2-strs1)/(strn2-strn1)
        self.normemod = (nrmstrs2-nrmstrs1)/(strn2-strn1)
