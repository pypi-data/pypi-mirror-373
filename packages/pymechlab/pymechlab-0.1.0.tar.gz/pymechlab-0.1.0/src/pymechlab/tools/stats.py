from typing import TYPE_CHECKING

from numpy import (asarray, concatenate, cumsum, exp, log, mean, sqrt, square,
                   std, unique, zeros)
from scipy.stats.distributions import nct, norm, t

if TYPE_CHECKING:
    from numpy.typing import NDArray

def k_factor_normal(n: int, p: float, conf: float=0.95, r: int=1) -> float:
    z = norm.ppf(p)
    nct_pdf = nct(df=n-r, nc=z*sqrt(n))
    t = nct_pdf.ppf(conf)
    return t / sqrt(n)

def b_value_normal(mean: float, stdev: float, n: int, r: int=1) -> float:
    kb = k_factor_normal(n, 0.90, r=r)
    return mean - kb*stdev

def a_value_normal(mean: float, stdev: float, n: int, r: int=1) -> float:
    ka = k_factor_normal(n, 0.99, r=r)
    return mean - ka*stdev

def b_value_lognormal(mean: float, stdev: float, n: int, r: int=1) -> float:
    logmean = log(mean)
    logstdev = log(stdev)
    kb = k_factor_normal(n, 0.90, r=r)
    return exp(logmean - kb*logstdev)

def a_value_lognormal(mean: float, stdev: float, n: int, r: int=1) -> float:
    logmean = log(mean)
    logstdev = log(stdev)
    ka = k_factor_normal(n, 0.99, r=r)
    return exp(logmean - ka*logstdev)

def k_factor_weibull(n: int, p: float, conf: float=0.95, r: int=1) -> float:
    lamda = log(-log(p))
    nct_pdf = nct(df=n-r, nc=-sqrt(n)*lamda)
    t = nct_pdf.ppf(conf)
    return t / sqrt(n-1)

def V_factor_weibull(n: int, p: float, conf: float=0.95, r: int=1) -> float:
    lamda = log(-log(p))
    nct_pdf = nct(df=n-r, nc=-sqrt(n)*lamda)
    t = nct_pdf.ppf(conf)
    return t

def mnr_crit(n: int, alpha: float=0.05) -> float:
    tval = t.ppf(1-alpha/2/n, n-2)
    tval2 = square(tval)
    return (n - 1)/sqrt(n)*sqrt(tval2/(n - 2 + tval2))

def grubbs_test(x, alpha: float=0.05):
   n = len(x)
   mean_x = mean(x)
   sd_x = std(x, ddof=1)
   numerator = max(abs(x-mean_x))
   g_calculated = numerator/sd_x
   print("Grubbs Calculated Value:", g_calculated)
   t_value_1 = t.ppf(1 - alpha / (2 * n), n - 2)
   g_critical = ((n - 1) * sqrt(square(t_value_1))) / (sqrt(n) * sqrt(n - 2 + square(t_value_1)))
   print("Grubbs Critical Value:", g_critical)
   if g_critical > g_calculated:
      print("We can see from the Grubbs test that the calculated value is less than the crucial value. Recognize the null hypothesis and draw the conclusion that there are no outliers\n")
   else:
      print("We see from the Grubbs test that the estimated value exceeds the critical value. Reject the null theory and draw the conclusion that there are outliers\n")

def adk_ksample(samples: tuple['NDArray'], display=False) -> float:

    samples = tuple([asarray(sample) for sample in samples])

    k = len(samples)

    if display:
        print(f'k = {k:d}')

    x = concatenate(samples)

    if display:
        print(f'x = {x}\n')

    n = x.size

    if display:
        print(f'n = {n:d}')

    zj, hj = unique(x, return_counts=True)

    if display:
        print(f'zj = {zj}\n')
        print(f'hj = {hj}\n')

    l = zj.size

    if display:
        print(f'l = {l:d}')

    Hj = cumsum(hj) - hj/2

    if display:
        print(f'Hj = {Hj}\n')

    ni = zeros(k)
    Fij = zeros((k, l))

    for i in range(k):
        zi = samples[i]
        zi = zi.reshape(1, -1)
        f_lt = zj.reshape(-1, 1) > zi
        f_eq = zj.reshape(-1, 1) == zi
        Fij[i] = f_eq.sum(axis=1)/2 + f_lt.sum(axis=1)
        ni[i] = zi.size

    if display:
        print(f'hj = \n{hj}\n')
        print(f'Fij = \n{Fij}\n')
        print(f'ni = {ni}\n')

    Hij = ni.reshape(-1, 1)@Hj.reshape(1, -1)

    if display:
        print(f'Hij = \n{Hij}\n')

    nij = (n*Fij - Hij)**2

    if display:
        print(f'nij = \n{nij}\n')

    dij = hj/(Hj*(n - Hj) - n*hj/4)

    if display:
        print(f'dij = {dij}\n')

    Dij = dij.reshape(1, -1).repeat(k, axis=0)

    if display:
        print(f'Dij = \n{Dij}\n')

    Lij = Dij*nij

    if display:
        print(f'Lij = \n{Lij}\n')

    Li = Lij.sum(axis=1)

    if display:
        print(f'Li = \n{Li}\n')

    li = Li/ni

    if display:
        print(f'li = \n{li}\n')

    l = li.sum()

    if display:
        print(f'l = {l}\n')

    adk = (n-1)/n**2/(k-1)*l

    if display:
        print(f'adk = {adk}\n')

    return adk

def adc_ksample(samples: tuple['NDArray'], display=False) -> float:
    arr = concatenate(samples)

    n=arr.size

    nvaluearr = asarray([len(sample) for sample in samples])

    k = len(samples)

    #S
    S = 0
    for x in nvaluearr:
        S = S + 1/x

    #T
    T = 0
    for t in range(1,n):
        T = T + 1/t

    #g
    G = 0
    for i in range(1, n-1):
        for j in range(i+1, n):
            G = G+1/((n-i)*j)

    #ABC
    A = (4 * G - 6) * (k - 1) + (10 - 6 * G) * S
    B = (2 * G - 4) * k * k + 8 * T * k + (2 * G - 14 * T - 4) * S - 8 * T + 4 * G - 6
    C = (6 * T + 2 * G - 2) * k * k + (4 * T - 4 * G + 6) * k + (2 * T - 6) * S + 4 * T
    D = (2 * T + 6) * k * k - 4 * T * k

    #ADC
    Var_ADK = ((A * n ** 3) + (B * n ** 2) + (C * n) + D)/((n - 1)*(n - 2)*(n - 3)*((k - 1) ** 2))
    ADC_2_5 = 1 + sqrt(Var_ADK) * (1.96 + 1.149 / sqrt(k - 1) - 0.391 / (k - 1))
    ADC_5_0 = 1 + sqrt(Var_ADK) * (1.645 + 0.678 / sqrt(k - 1) - 0.362 / (k - 1))
    ADC_10_0 = 1 + sqrt(Var_ADK) * (1.281 + 0.25 / sqrt(k - 1) - 0.305 / (k - 1))
    ADC_25_0 = 1 + sqrt(Var_ADK) * (0.675 - 0.245 / sqrt(k - 1) - 0.105 / (k - 1))

    if display:
        print(f'Var_ADK = {Var_ADK}\n')
        print(f'Var_ADK*(k-1)**2 = {Var_ADK*(k-1)**2}\n')
        print(f'sqrt(Var_ADK*(k-1)**2) = {sqrt(Var_ADK*(k-1)**2)}\n')
        print(f'ADC(α=0.250) = {ADC_25_0}\n')
        print(f'ADC(α=0.100) = {ADC_10_0}\n')
        print(f'ADC(α=0.050) = {ADC_5_0}\n')
        print(f'ADC(α=0.025) = {ADC_2_5}\n')

    return ADC_2_5, ADC_5_0, ADC_10_0, ADC_25_0
