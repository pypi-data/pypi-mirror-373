from collections.abc import Iterable
from json import load
from typing import TYPE_CHECKING, Any

from numpy import (absolute, argmax, asarray, concatenate, exp, full, log,
                   mean, median, round, sqrt, std, zeros)
from py2md.classes import MDReport, MDTable
from scipy.stats import (PermutationMethod, anderson, anderson_ksamp,
                         goodness_of_fit, levene)
from scipy.stats.distributions import lognorm, norm, t, weibull_min
from toleranceinterval.hk import HansonKoopmans

from ..tools.stats import (a_value_lognormal, a_value_normal,
                           b_value_lognormal, b_value_normal, k_factor_normal,
                           k_factor_weibull)

if TYPE_CHECKING:
    from numpy.typing import NDArray


class Sample():
    name: str = None
    _data: 'NDArray' = None
    _valid: 'NDArray' = None
    _numcoupon: int = None
    _normstats: 'NormalStatistics' = None
    _lognormstats: 'LogNormalStatistics' = None
    _weibullstats: 'WeibullStatistics' = None
    _nonparamstats: 'NonParametricStatistics' = None

    def get_valid_data(self) -> 'NDArray':
        return self.data[self.valid]

    def mnr_test(self, alpha: float=0.05) -> None:
        mnr_max = float('inf')
        gcrit = 0.0
        ind_max = None
        while mnr_max > gcrit:
            if ind_max is not None:
                self.valid[ind_max] = False
            data = self.get_valid_data()
            n = len(data)
            tval = t.ppf(1-alpha/2/n, n-2)
            tval2 = tval**2
            gcrit = (n - 1)*(tval2/n/(n - 2 + tval2))**0.5
            mean_x = mean(data)
            std_x = std(data, ddof=1)
            mnr_vals = zeros(self.data.shape)
            mnr_vals[self.valid] = absolute(data - mean_x)/std_x
            ind_max = argmax(mnr_vals)
            mnr_max = mnr_vals[ind_max]

    @property
    def data(self) -> 'NDArray':
        return self._data

    @property
    def valid(self) -> 'NDArray':
        if self._valid is None:
            self._valid = full(self.data.shape, True, dtype=bool)
        return self._valid

    @property
    def numcoupon(self) -> int:
        if self._numcoupon is None:
            self._numcoupon = self.data.size
        return self._numcoupon

    @property
    def normstats(self) -> 'NormalStatistics':
        if self._normstats is None:
            self._normstats = NormalStatistics(self.data)
        return self._normstats

    @property
    def lognormstats(self) -> 'LogNormalStatistics':
        if self._lognormstats is None:
            self._lognormstats = LogNormalStatistics(self.data)
        return self._lognormstats

    @property
    def weibullstats(self) -> 'WeibullStatistics':
        if self._weibullstats is None:
            self._weibullstats = WeibullStatistics(self.data)
        return self._weibullstats

    @property
    def nonparamstats(self) -> 'NonParametricStatistics':
        if self._nonparamstats is None:
            self._nonparamstats = NonParametricStatistics()
            self._nonparamstats.set_data(self.data)
        return self._nonparamstats


class DataSet(Sample):
    _labels: list[str] = None

    def __init__(self, name: str, data: 'NDArray') -> None:
        self.name = name
        self._data = asarray(data).reshape(-1)
        self.mnr_test()

    def set_labels(self, labels: list[str]) -> None:
        numlbl = len(labels)
        n = self.data.size
        if n != numlbl:
            raise ValueError('The length of labels is not the same as data.')
        self._labels = labels

    @property
    def labels(self) -> list[str]:
        if self._labels is None:
            self._labels = [str(i+1) for i in range(self.data.size)]
        return self._labels


class Batch(Sample):
    datasets: list[DataSet] = None
    _numdataset: int = None

    def __init__(self, name: str, datasets: list[DataSet]) -> None:
        self.name = name
        self.datasets = datasets
        self.mnr_test()

    @property
    def numdataset(self) -> int:
        if self._numdataset is None:
            self._numdataset = len(self.datasets)
        return self._numdataset

    @property
    def data(self) -> 'NDArray':
        if self._data is None:
            self._data = concatenate([ds.data for ds in self.datasets])
        return self._data

    @property
    def valid(self) -> 'NDArray':
        if self._valid is None:
            self._valid = concatenate([ds.valid for ds in self.datasets])
        return self._valid

    def mnr_test(self, alpha: float=0.05) -> None:

        for ds in self.datasets:
            ds.mnr_test(alpha=alpha)

        super().mnr_test(alpha=alpha)


class Pool(Batch):
    metadata: dict[str, str] = None
    batches: list[Batch] = None
    _datasets: list[DataSet] = None
    _numbatch: int = None
    _adkresult: Any = None
    _levenetest: 'LeveneTest' = None
    _anovastats: 'ANOVAStatistics' = None

    def __init__(self, metadata: dict[str, str], batches: list[Batch]) -> None:
        self.metadata = metadata
        self.batches = batches
        self.mnr_test()

    @property
    def datasets(self) -> list[DataSet]:
        if self._datasets is None:
            self._datasets = []
            for batch in self.batches:
                self._datasets += batch.datasets
        return self._datasets

    @property
    def numbatch(self) -> int:
        if self._numbatch is None:
            self._numbatch = len(self.batches)
        return self._numbatch

    @property
    def numcoupon(self) -> int:
        if self._numcoupon is None:
            self._numcoupon = sum([ds.numcoupon for ds in self.datasets])
        return self._numcoupon

    @property
    def adk_result(self):
        samples = [ds.get_valid_data() for ds in self.datasets]

        return anderson_ksamp(samples, midrank=True, method=PermutationMethod())

    @property
    def levenetest(self) -> 'LeveneTest':
        if self._levenetest is None:
            samples = [ds.data for ds in self.datasets]
            self._levenetest = LeveneTest(samples)
        return self._levenetest

    @property
    def anovastats(self) -> 'ANOVAStatistics':
        if self._anovastats is None:
            samples = [ds.data for ds in self.datasets]
            self._anovastats = ANOVAStatistics(samples)
        return self._anovastats

    def to_mdobj(self) -> MDReport:

        report = MDReport()

        table = MDTable()
        table.add_column('Pool Information', 's', '<')
        table.add_column('Value', 's', '>')
        for key, val in self.metadata.items():
            table.add_row([str(key), str(val)])
        table.add_row(['Number of Specimens', f'{self.numcoupon:d}'])
        table.add_row(['Number of Batches', f'{self.numbatch:d}'])
        table.add_row(['Number of Data Sets', f'{self.numdataset:d}'])
        table.add_row(['Minimum Value', f'{self.data.min():g}'])
        table.add_row(['Maximum Value', f'{self.data.max():g}'])
        report.add_object(table)

        table = MDTable()
        table.add_column('Batch ID', 's')
        table.add_column('Data Set ID', 's')
        table.add_column('Coupon ID', 's')
        table.add_column('Data Values', 'g')
        table.add_column('Before Pooling', 's')
        table.add_column('After Pooling', 's')
        c = 0
        for batch in self.batches:
            for dataset in batch.datasets:
                for k in range(dataset.data.size):
                    if not dataset.valid[k]:
                        dsvalid = 'X'
                        plvalid = ''
                    else:
                        dsvalid = ''
                        if not self.valid[c]:
                            plvalid = 'X'
                        else:
                            plvalid = ''
                    row = [batch.name, dataset.name, dataset.labels[k],
                           dataset.data[k], dsvalid, plvalid]
                    c += 1
                    table.add_row(row)
        report.add_object(table)

        adk_result = self.adk_result

        table = MDTable()
        table.add_column('Anderson k-Sample Test', 's', '<')
        table.add_column('Value', 's', '>')
        table.add_row(['ADK Statistic', f'{adk_result.statistic:g}'])
        sig = asarray([0.25, 0.1, 0.05, 0.025, 0.01, 0.005, 0.001])
        for s, c in zip(sig, adk_result.critical_values):
            table.add_row([f'AD Critical (&alpha; = {s:.3f})', f'{c:g}'])
        table.add_row(['ADK p-value', f'{adk_result.pvalue:g}'])
        report.add_object(table)

        report.add_object(self.normstats.table)
        report.add_object(self.lognormstats.table)
        report.add_object(self.weibullstats.table)
        report.add_object(self.nonparamstats.table)
        report.add_object(self.levenetest.table)
        report.add_object(self.anovastats.table)

        return report

    def _repr_markdown_(self) -> str:
        return self.to_mdobj()._repr_markdown_()

    def __str__(self) -> str:
        return self.to_mdobj().__str__()


def dataset_from_dict(datasetname: str, datasetata: dict[str, float]) -> DataSet:

    coupondict: dict[str, Any] = datasetata['coupons']

    labels = []
    data = []
    for couponlbl, couponval in coupondict.items():
        labels.append(couponlbl)
        data.append(couponval)

    data = asarray(data)

    ds = DataSet(datasetname, data)
    ds.set_labels(labels)

    return ds


def batch_from_dict(batchname: str, batchdata: dict[str, Any]) -> Batch:

    datasetdict: dict[str, Any] = batchdata['datasets']

    datasets = []
    for datasetname, datasetdata in datasetdict.items():
        dataset = dataset_from_dict(datasetname, datasetdata)
        datasets.append(dataset)

    return Batch(batchname, datasets)


def pool_from_dict(pooldata: dict[str, dict[str, Any]]) -> Pool:

    metadata = {}
    batchdict = {}
    for key, val in pooldata.items():
        if key != 'batches':
            metadata[key] = val
        else:
            batchdict = val

    batches = []
    for batchname, batchdata in batchdict.items():
        batch = batch_from_dict(batchname, batchdata)
        batches.append(batch)

    return Pool(metadata, batches)


def pool_from_json(jsonfilepath):
    jsondata = {}
    with open(jsonfilepath, 'rt') as jsonfile:
        jsondata = load(jsonfile)
    return pool_from_dict(jsondata)


class NormalStatistics():
    data: 'NDArray' = None
    _xnum: int = None
    _xmax: float = None
    _xmin: float = None
    _ad = None
    _ads: float = None
    _osl: float = None
    _pdf_fitted: float = None
    _var: float = None
    _cov: float = None
    _bvalue: float = None
    _avalue: float = None

    def __init__(self, data: 'NDArray') -> None:
        self.data = data

    @property
    def xnum(self) -> int:
        if self._xnum is None:
            self._xnum = self.data.size
        return self._xnum

    @property
    def xmin(self) -> float:
        if self._xmin is None:
            self._xmin = self.data.min()
        return self._xmin

    @property
    def xmax(self) -> float:
        if self._xmax is None:
            self._xmax = self.data.max()
        return self._xmax

    @property
    def ad(self):
        if self._ad is None:
            self._ad = anderson(self.data, dist='norm')
        return self._ad

    @property
    def ads(self) -> float:
        if self._ads is None:
            self._ads = (1 + 4/self.xnum - 25/self.xnum**2)*self.ad.statistic # CMH-17 8.3.6.5.1.2(d)
        return self._ads

    @property
    def osl(self) -> float:
        if self._osl is None:
            self._osl = 1/(1 + exp(-0.48 + 0.78*log(self.ads) + 4.58*self.ads)) # CMH-17 8.3.6.5.1.2(c)
        return self._osl

    @property
    def mean(self) -> float:
        return self.ad.fit_result.params.loc

    @property
    def stdev(self) -> float:
        return self.ad.fit_result.params.scale

    @property
    def pdf_fitted(self):
        if self._pdf_fitted is None:
            self._pdf_fitted = norm(self.mean, self.stdev)
        return self._pdf_fitted

    @property
    def var(self) -> float:
        if self._var is None:
            self._var = self.stdev**2
        return self._var

    @property
    def cov(self) -> float:
        if self._cov is None:
            self._cov = self.stdev/self.mean
        return self._cov

    @property
    def bvalue(self) -> float:
        if self._bvalue is None:
            self._bvalue = b_value_normal(self.mean, self.stdev, self.xnum)
        return self._bvalue

    @property
    def avalue(self) -> float:
        if self._avalue is None:
            self._avalue = a_value_normal(self.mean, self.stdev, self.xnum)
        return self._avalue

    @property
    def table(self) -> MDTable:
        table = MDTable()
        table.add_column('Normal Distribution Statistics', 's', '<')
        table.add_column('Value', 's', '>')
        table.add_row(['Observed Significance Level (OSL)', f'{self.osl:g}'])
        table.add_row(['Mean', f'{self.mean:g}'])
        table.add_row(['Standard Deviation', f'{self.stdev:g}'])
        table.add_row(['Coefficient of Variation (%)', f'{self.cov*100:g}%'])
        table.add_row(['B-Basis Value', f'{self.bvalue:g}'])
        table.add_row(['A-Basis Value', f'{self.avalue:g}'])
        return table

    def _repr_markdown_(self) -> str:
        return self.table._repr_markdown_()


class LogNormalStatistics(NormalStatistics):
    _logdata: 'NDArray' = None
    _mean: float = None
    _stdev: float = None

    @property
    def logdata(self) -> 'NDArray':
        if self._logdata is None:
            self._logdata = log(self.data)
        return self._logdata

    @property
    def ad(self):
        if self._ad is None:
            self._ad = anderson(self.logdata, dist='norm')
        return self._ad

    @property
    def logmean(self) -> float:
        return self.ad.fit_result.params.loc

    @property
    def logstdev(self) -> float:
        return self.ad.fit_result.params.scale

    @property
    def mean(self) -> float:
        if self._mean is None:
            self._mean = exp(self.logmean)
        return self._mean

    @property
    def stdev(self) -> float:
        if self._stdev is None:
            self._stdev = exp(self.logstdev)
        return self._stdev

    @property
    def pdf_fitted(self):
        if self._pdf_fitted is None:
            self._pdf_fitted = lognorm(self.logstdev, loc=0.0, scale=self.mean)
        return self._pdf_fitted

    @property
    def bvalue(self) -> float:
        if self._bvalue is None:
            self._bvalue = b_value_lognormal(self.mean, self.stdev, self.xnum)
        return self._bvalue

    @property
    def avalue(self) -> float:
        if self._avalue is None:
            self._avalue = a_value_lognormal(self.mean, self.stdev, self.xnum)
        return self._avalue

    @property
    def table(self) -> MDTable:
        table = MDTable()
        table.add_column('Log Normal Distribution Statistics', 's', '<')
        table.add_column('Value', 's', '>')
        table.add_row(['Observed Significance Level (OSL)', f'{self.osl:g}'])
        table.add_row(['Log Mean', f'{self.logmean:g}'])
        table.add_row(['Log Standard Deviation', f'{self.logstdev:g}'])
        table.add_row(['B-Basis Value', f'{self.bvalue:g}'])
        table.add_row(['A-Basis Value', f'{self.avalue:g}'])
        return table


class WeibullStatistics():
    data: 'NDArray' = None
    _xnum: int = None
    _xmax: float = None
    _xmin: float = None
    _params: tuple[float, float, float] = None
    _ad = None
    _ads: float = None
    _osl: float = None
    _pdf_fitted: float = None
    _var: float = None
    _cov: float = None
    _bvalue: float = None
    _avalue: float = None

    def __init__(self, data: 'NDArray') -> None:
        self.data = data

    @property
    def xnum(self) -> int:
        if self._xnum is None:
            self._xnum = self.data.size
        return self._xnum

    @property
    def xmin(self) -> float:
        if self._xmin is None:
            self._xmin = self.data.min()
        return self._xmin

    @property
    def xmax(self) -> float:
        if self._xmax is None:
            self._xmax = self.data.max()
        return self._xmax

    @property
    def params(self) -> tuple[float, float, float]:
        if self._params is None:
            self._params = weibull_min.fit(self.data, floc=0.0)
        return self._params

    @property
    def c(self) -> float:
        return self.params[0]

    @property
    def loc(self) -> float:
        return self.params[1]

    @property
    def scale(self) -> float:
        return self.params[2]

    @property
    def pdf_fitted(self):
        if self._pdf_fitted is None:
            self._pdf_fitted = weibull_min(*self.params)
        return self._pdf_fitted

    @property
    def ad(self):
        if self._ad is None:
            self._ad = goodness_of_fit(weibull_min, self.data,
                                       known_params={'c': self.c,
                                                     'loc': self.loc,
                                                     'scale': self.scale},
                                       statistic='ad')
        return self._ad

    @property
    def ads(self) -> float:
        if self._ads is None:
            self._ads = (1 + 0.2/sqrt(self.xnum))*self.ad.statistic # CMH-17 8.3.6.5.2.2(d)
        return self._ads

    @property
    def osl(self) -> float:
        if self._osl is None:
            self._osl = 1/(1 + exp(-0.1 + 1.24*log(self.ads) + 4.48*self.ads)) # CMH-17 8.3.6.5.2.2(c)
        return self._osl

    @property
    def bvalue(self) -> float:
        if self._bvalue is None:
            kb = k_factor_weibull(self.xnum, 0.90)
            self._bvalue = self.scale*exp(-kb/self.c)
        return self._bvalue

    @property
    def avalue(self) -> float:
        if self._avalue is None:
            ka = k_factor_weibull(self.xnum, 0.99)
            self._avalue = self.scale*exp(-ka/self.c)
        return self._avalue

    @property
    def table(self) -> MDTable:
        table = MDTable()
        table.add_column('Two Param Weibull Distribution Statistics', 's', '<')
        table.add_column('Value', 's', '>')
        table.add_row(['Observed Significance Level (OSL)', f'{self.osl:g}'])
        table.add_row(['Scale Parameter', f'{self.scale:g}'])
        table.add_row(['Shape Parameter', f'{self.c:g}'])
        table.add_row(['B-Basis Value', f'{self.bvalue:g}'])
        table.add_row(['A-Basis Value', f'{self.avalue:g}'])
        return table

    def _repr_markdown_(self) -> str:
        return self.table._repr_markdown_()


class ANOVAStatistics():
    samples: Iterable['NDArray'] = None
    _k: int = None
    _ni: 'NDArray' = None
    _meani: 'NDArray' = None
    _data: 'NDArray' = None
    _n: int = None
    _mean: float = None
    _ssb: float = None
    _sst: float = None
    _sse: float = None
    _msb: float = None
    _mse: float = None
    _f: float = None
    _ns: float = None
    _np: float = None
    _s: float = None
    _u: float = None
    _w: float = None
    _k0b: float = None
    _k1b: float = None
    _tb: float = None
    _bvalue: float = None
    _k0a: float = None
    _k1a: float = None
    _ta: float = None
    _avalue: float = None

    def __init__(self, samples: Iterable['NDArray']) -> None:
        self.samples = samples

    @property
    def k(self) -> int:
        if self._k is None:
            self._k = len(self.samples)
        return self._k

    @property
    def ni(self) -> int:
        if self._ni is None:
            self._ni = asarray([len(sample) for sample in self.samples], dtype=int)
        return self._ni

    @property
    def meani(self) -> float:
        if self._meani is None:
            self._meani = asarray([sample.mean() for sample in self.samples])
        return self._meani

    @property
    def data(self) -> 'NDArray':
        if self._data is None:
            self._data = concatenate(self.samples)
        return self._data

    @property
    def n(self) -> int:
        if self._n is None:
            self._n = self.data.size
        return self._n

    @property
    def mean(self) -> float:
        if self._mean is None:
            self._mean = self.data.mean()
        return self._mean

    @property
    def ssb(self) -> float:
        if self._ssb is None:
            self._ssb = (self.ni*self.meani**2).sum() - self.n*self.mean**2
        return self._ssb

    @property
    def sst(self) -> float:
        if self._sst is None:
            self._sst = sum([(sample**2).sum() for sample in self.samples])  - self.n*self.mean**2
        return self._sst

    @property
    def sse(self) -> float:
        if self._sse is None:
            self._sse = self.sst - self.ssb
        return self._sse

    @property
    def msb(self) -> float:
        if self._msb is None:
            self._msb = self.ssb/(self.k - 1)
        return self._msb

    @property
    def mse(self) -> float:
        if self._mse is None:
            self._mse = self.sse/(self.n - self.k)
        return self._mse

    @property
    def f(self) -> float:
        if self._f is None:
            self._f = self.msb/self.mse
        return self._f

    @property
    def ns(self) -> float:
        if self._ns is None:
            self._ns = float((self.ni**2).sum()/self.n)
        return self._ns

    @property
    def np(self) -> float:
        if self._np is None:
            self._np = (self.n - self.ns)/(self.k - 1)
        return self._np

    @property
    def s(self) -> float:
        if self._s is None:
            self._s = sqrt(self.msb/self.np + (self.np - 1)/self.np*self.mse)
        return self._s

    @property
    def u(self) -> float:
        if self._u is None:
            self._u = max([self.f, 1.0])
        return self._u

    @property
    def w(self) -> float:
        if self._w is None:
            self._w = sqrt(self.u / (self.u + self.np - 1))
        return self._w

    @property
    def k0b(self) -> float:
        if self._k0b is None:
            self._k0b = k_factor_normal(self.n, 0.90)
        return self._k0b

    @property
    def k1b(self) -> float:
        if self._k1b is None:
            self._k1b = k_factor_normal(self.k, 0.90)
        return self._k1b

    @property
    def tb(self) -> float:
        if self._tb is None:
            self._tb = (self.k0b - self.k1b / sqrt(self.np) + (self.k1b - self.k0b) * self.w) / (1 - 1 / sqrt(self.np))
        return self._tb

    @property
    def bvalue(self) -> float:
        if self._bvalue is None:
            self._bvalue = self.mean - self.tb*self.s
        return self._bvalue

    @property
    def k0a(self) -> float:
        if self._k0a is None:
            self._k0a = k_factor_normal(self.n, 0.99)
        return self._k0a

    @property
    def k1a(self) -> float:
        if self._k1a is None:
            self._k1a = k_factor_normal(self.k, 0.99)
        return self._k1a

    @property
    def ta(self) -> float:
        if self._ta is None:
            self._ta = (self.k0a - self.k1a / sqrt(self.np) + (self.k1a - self.k0a) * self.w) / (1 - 1 / sqrt(self.np))
        return self._ta

    @property
    def avalue(self) -> float:
        if self._avalue is None:
            self._avalue = self.mean - self.ta*self.s
        return self._avalue

    @property
    def table(self) -> MDTable:
        table = MDTable()
        table.add_column('ANOVA Statistics', 's', '<')
        table.add_column('Value', 's', '>')
        table.add_row(['Sample Between-batch Mean Sq. (MSB)', f'{self.msb:g}'])
        table.add_row(['Error Mean Square (MSE)', f'{self.mse:g}'])
        table.add_row(['Estimate of Pop. Std. Deviation(s)', f'{self.s:g}'])
        table.add_row(['B-Basis Tolerance Limit Factor (T<sub>B</sub>)', f'{self.tb:g}'])
        table.add_row(['A-Basis Tolerance Limit Factor (T<sub>A</sub>)', f'{self.ta:g}'])
        table.add_row(['B-Basis Value', f'{self.bvalue:g}'])
        table.add_row(['A-Basis Value', f'{self.avalue:g}'])
        return table

    def _repr_markdown_(self) -> str:
        return self.table._repr_markdown_()


def f_crit_calc(ndf: int, ddf: int) -> float:
    z = 1.645
    if ndf == 1:
        fval = (1.959964 + 2.372272 / ddf + 2.8225 / ddf ** 2 + 2.5555852 / ddf ** 3 + 1.589536 / ddf ** 4) ** 2
    elif ddf == 1:
        fval = (0.06270671 + 0.01573832 / ndf + 0.00200073 / ndf ** 2 - 0.00243852 / ndf ** 3 - 0.00064811 / ndf ** 4) ** -2
    else:
        delta = 0.5 * (1 / (ddf - 1) - 1 / (ndf - 1))
        sigma2 = 0.5 * (1 / (ddf - 1) + 1 / (ndf - 1))
        fval = exp(2 * delta * (1 + (z ** 2 - 1) / 3 - 4 * sigma2 / 3) + 2 * z * sigma2 ** 0.5 * sqrt(1 + sigma2 * (z ** 2 - 3) / 6))

    return fval


class LeveneTest():
    samples: Iterable['NDArray'] = None
    _k: int = None
    _ni: 'NDArray' = None
    _mediani: 'NDArray' = None
    _data: 'NDArray' = None
    _n: int = None
    _fcrit: float = None
    _fcalc: float = None
    _pcalc: float = None

    def __init__(self, samples: Iterable['NDArray']) -> None:
        self.samples = samples

    @property
    def k(self) -> int:
        if self._k is None:
            self._k = len(self.samples)
        return self._k

    @property
    def ni(self) -> int:
        if self._ni is None:
            self._ni = asarray([len(sample) for sample in self.samples], dtype=int)
        return self._ni

    @property
    def mediani(self) -> float:
        if self._mediani is None:
            self._mediani = asarray([median(sample) for sample in self.samples])
        return self._mediani

    @property
    def data(self) -> 'NDArray':
        if self._data is None:
            self._data = concatenate(self.samples)
        return self._data

    @property
    def n(self) -> int:
        if self._n is None:
            self._n = self.data.size
        return self._n

    @property
    def fcrit(self) -> float:
        if self._fcrit is None:
            self._fcrit = f_crit_calc(self.k - 1, self.n - self.k)
        return self._fcrit

    @property
    def fcalc(self) -> float:
        if self._fcalc is None:
            self._fcalc, self._pval = levene(*self.samples)
        return self._fcalc

    @property
    def pcalc(self) -> float:
        if self._pcalc is None:
            self._fcalc, self._pcalc = levene(*self.samples)
        return self._pcalc

    @property
    def table(self) -> MDTable:
        table = MDTable()
        table.add_column('Parameter', 's', '<')
        table.add_column('Value', 's', '>')
        table.add_row(['Fcalc', f'{self.fcalc:g}'])
        table.add_row(['pcalc', f'{self.pcalc:g}'])
        table.add_row(['Fcrit', f'{self.fcrit:g}'])
        return table

    def _repr_markdown_(self) -> str:
        return self.table._repr_markdown_()

hk_b_rank = {
    2: 2,
    3: 3,
    4: 4,
    5: 4,
    6: 5,
    7: 5,
    8: 6,
    9: 6,
    10: 6,
    11: 7,
    12: 7,
    13: 7,
    14: 8,
    15: 8,
    16: 8,
    17: 8,
    18: 9,
    19: 9,
    20: 10,
    21: 10,
    22: 10,
    23: 11,
    24: 11,
    25: 11,
    26: 11,
    27: 11,
    28: 12
}


class NonParametricStatistics():
    data: 'NDArray' = None
    _n: int = None
    _bmethod: str = None
    _amethod: str = None
    _brank: int = None
    _arank: int = None
    _bfactor: float = None
    _afactor: float = None
    _bvalue: float = None
    _avalue: float = None

    def set_data(self, data: 'NDArray') -> None:
        self.data = data.copy()
        self.data.sort()

    def set_data_size(self, n: int) -> None:
        self._n = n

    @property
    def n(self) -> int:
        if self._n is None:
            self._n = self.data.size
        return self._n

    @property
    def bmethod(self) -> str:
        if self._bmethod is None:
            if self.n > 28:
                self._bmethod = 'Non-Param'
            else:
                self._bmethod = 'Hans-Koop'
        return self._bmethod

    @property
    def amethod(self) -> str:
        if self._amethod is None:
            if self.n > 298:
                self._amethod = 'Non-Param'
            else:
                self._amethod = 'Hans-Koop'
        return self._amethod

    @property
    def brank(self) -> int:
        if self._brank is None:
            if self.n > 28:
                if self.n < 46:
                    self._brank = 1
                elif self.n < 61:
                    self._brank = 2
                elif self.n < 76:
                    self._brank = 3
                elif self.n < 89:
                    self._brank = 4
                elif self._n < 103:
                    self._brank = 5
                else:
                    self._brank = int(round(0.1*self.n - 1.645*sqrt(0.09*self.n) + 0.23))
            elif self.n < 2:
                raise ValueError('NonParametricStatistics data size < 2.')
            else:
                self._brank = hk_b_rank[self.n]
        return self._brank

    @property
    def arank(self) -> int:
        if self._arank is None:
            if self.n > 298:
                self._arank = int(round(0.01*self.n - 1.645*sqrt(0.0099*self.n) + 0.29 + 19.1/self.n))
            elif self.n < 2:
                raise ValueError('NonParametricStatistics data size < 2.')
            else:
                self._arank = self.n
        return self._arank

    @property
    def bfactor(self) -> float:
        if self._bfactor is None:
            if self.n > 28:
                hkb = HansonKoopmans(0.10, 0.95, self.n, self.brank)
            else:
                hkb = HansonKoopmans(0.10, 0.95, self.n, self.brank-1)
            if hasattr(hkb, 'b'):
                self._bfactor = float(hkb.b)
            else:
                self._bfactor = 1.0
        return self._bfactor

    @property
    def afactor(self) -> float:
        if self._afactor is None:
            hka = HansonKoopmans(0.01, 0.95, self.n, self.arank-1)
            if hasattr(hka, 'b'):
                self._afactor = float(hka.b)
            else:
                self._afactor = 1.0
        return self._afactor

    @property
    def bvalue(self) -> float:
        if self._bvalue is None:
            if self.data is None:
                raise ValueError('No data provided to calculated b value.')
            else:
                if self.n > 28:
                    self._bvalue = self.data[self.brank]*(self.data[0]/self.data[self.brank])**self.bfactor
                else:
                    self._bvalue = self.data[self.brank-1]*(self.data[0]/self.data[self.brank-1])**self.bfactor
        return self._bvalue

    @property
    def avalue(self) -> float:
        if self._avalue is None:
            if self.data is None:
                raise ValueError('No data provided to calculated b value.')
            else:
                self._avalue = self.data[self.arank-1]*(self.data[0]/self.data[self.arank-1])**self.afactor
        return self._avalue

    @property
    def table(self) -> MDTable:
        table = MDTable()
        table.add_column('Non-Parametric Statistics', 's', '<')
        table.add_column('Value', 's', '>')
        table.add_row(['B-Basis Method', f'{self.bmethod:s}'])
        table.add_row(['A-Basis Method', f'{self.amethod:s}'])
        table.add_row(['B-Basis Rank', f'{self.brank:d}'])
        if self.n > 298:
            table.add_row(['A-Basis Rank', f'{self.arank:d}'])
        else:
            table.add_row(['A-Basis Rank', 'N/A'])
        if self.bmethod == 'Hans-Koop':
            table.add_row(['B-Basis Hans-Koop k Factor', f'{self.bfactor:g}'])
        else:
            table.add_row(['B-Basis Hans-Koop k Factor', 'N/A'])
        if self.amethod == 'Hans-Koop':
            table.add_row(['A-Basis Hans-Koop k Factor', f'{self.afactor:g}'])
        else:
            table.add_row(['A-Basis Hans-Koop k Factor', 'N/A'])
        if self.data is not None:
            table.add_row(['B-Basis Value', f'{self.bvalue:g}'])
            table.add_row(['A-Basis Value', f'{self.avalue:g}'])
        return table
