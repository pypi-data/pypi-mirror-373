import statistics
import inspect

import numpy as np




def three_phase_linear(t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0   # due to the imposed preprocessing, y0==0 always.
    return np.piecewise(
        t, [t<=tlag, (t>tlag) & (t<=tmax), t>tmax],
        [lambda t: y0, lambda t: y0+mu*(t-tlag), lambda t: y0+mu*(tmax-tlag)])

def four_phase_linear (t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0   # due to the imposed preprocessing, y0==0 always.
    return np.piecewise(
        t, [t<=tlag, (t>tlag) & (t<=tmax), (t>tmax) & (t<=tdeath), t>tdeath], 
        [lambda t: y0, lambda t: y0+mu*(t-tlag), lambda t: y0+mu*(tmax-tlag), lambda t: y0+mu*(tmax-tlag)-mudeath*(t-tdeath)])

def gompertz          (t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0   # due to the imposed preprocessing, y0==0 always.
    # rewritten with biologial parameters by ZWIETERING et al, 1990 (doi 10.1128/aem.56.6.1875-1881.1990).
    return (ymax * np.exp(-np.exp((mu * np.e / ymax) * (tlag - t) + 1))) + y0

def logistic          (t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0   # due to the imposed preprocessing, y0==0 always.
    # rewritten with biologial parameters by ZWIETERING et al, 1990 (doi 10.1128/aem.56.6.1875-1881.1990).
    return (ymax / (1 + np.exp(4*mu / ymax * (tlag - t) +2))) + y0

def richards          (t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0   # due to the imposed preprocessing, y0==0 always.
    # rewritten with biologial parameters by ZWIETERING et al, 1990 (doi 10.1128/aem.56.6.1875-1881.1990).
    shape = 0.1    # should be variable but keep it fixed for the moment.
    return (ymax * np.power((1+ shape * np.exp(1+ shape) * np.exp(mu / ymax * np.power(1+ shape, 1+ 1/shape) * (tlag - t))), -1/shape)) + y0

def baranyi           (t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0   # due to the imposed preprocessing, y0==0 always.
    # rewritten with biologial parameters by PERNI et al, 2005 (doi 10.1016/j.fm.2004.11.014).
    A = t + 1/mu *np.log(np.exp(-mu *t) + np.exp(-tlag *mu) - np.exp(-mu*t -tlag*mu))
    return y0 + mu*A -np.log(1 + (np.exp(mu*A) -1) / np.exp(ymax - y0))

def baranyi_nolag     (t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0   # due to the imposed preprocessing, y0==0 always.
    # So it's a 'baranyi' with 'tlag'==0. This means that 'A' == 't'.
    return y0 + mu*t -np.log(1 + (np.exp(mu*t) -1) / np.exp(ymax - y0))

def baranyi_nostat    (t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0   # due to the imposed preprocessing, y0==0 always.
    # So it's a 'baranyi' with 'ymax'==+inf. 
    A = t + 1/mu *np.log(np.exp(-mu *t) + np.exp(-tlag *mu) - np.exp(-mu*t -tlag*mu))
    return y0 + mu*A 

def baranyi_wlind     (t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0  # due to the imposed preprocessing, y0==0 always.
    if mudeath <0: mudeath = -mudeath   # force positive mu
    y_growth = baranyi(t, y0, tlag, mu, ymax, tmax, tdeath, mudeath)
    y_tdeath = baranyi(tdeath, y0, tlag, mu, ymax, tmax, tdeath, mudeath)
    y_decay = y_tdeath - mudeath * (t - tdeath)
    y = np.where(t < tdeath, y_growth, y_decay)
    return y

def baranyi_wexpd     (t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0  # due to the imposed preprocessing, y0==0 always.
    if mudeath <0: mudeath = -mudeath   # force positive mu
    y_growth = baranyi(t, y0, tlag, mu, ymax, tmax, tdeath, mudeath)
    y_tdeath = baranyi(tdeath, y0, tlag, mu, ymax, tmax, tdeath, mudeath)
    y_decay = y_tdeath * np.exp(-mudeath * (t - tdeath)**2)
    y = np.where(t < tdeath, y_growth, y_decay)
    return y

def garcia            (t, y0, tlag, mu, ymax, tmax, tdeath, mudeath, ):
    y0 = 0   # due to the imposed preprocessing, y0==0 always.
    # written with biologial parameters by GARCIA et al, 2021 (doi 10.3390/sym13081468).
    return y0 + 3/4*(ymax-y0)/np.power(tlag+(ymax-y0)/(2*mu), 2)*np.power(t,2) - 1/4*(ymax-y0)/np.power(tlag+(ymax-y0)/(2*mu), 3)*np.power(t,3)




def get_unused_params(model_id):
    cntNone = 0   # count params not contemplated in the respective models: 
    y0, tlag, mu, ymax, tmax, tdeath, mudeath = [None for i in range(7)]
    
    if model_id == 'three_phase_linear':
        for i in [tdeath, mudeath]: cntNone +=1
    if model_id == 'four_phase_linear':
        for i in []: cntNone +=1
    if model_id == 'gompertz':
        for i in [tmax, tdeath, mudeath]: cntNone +=1
    if model_id == 'logistic':
        for i in [tmax, tdeath, mudeath]: cntNone +=1
    if model_id == 'richards':
        for i in [tmax, tdeath, mudeath]: cntNone +=1
    if model_id == 'baranyi':
        for i in [tmax, tdeath, mudeath]: cntNone +=1
    if model_id == 'baranyi_nolag':
        for i in [tlag, tmax, tdeath, mudeath]: cntNone +=1
    if model_id == 'baranyi_nostat':
        for i in [ymax, tmax, tdeath, mudeath]: cntNone +=1
    if model_id == 'baranyi_wlind':
        for i in [tmax]: cntNone +=1
    if model_id == 'baranyi_wexpd':
        for i in [tmax]: cntNone +=1
    if model_id == 'garcia':
        for i in [tmax, tdeath, mudeath]: cntNone +=1
        
    return cntNone
    
    
    
    
def R2(y_true, y_pred):
    RSS = np.sum((y_true - y_pred)**2)  # residual sum of squares
    TSS = np.sum((y_true - np.mean(y_true))**2) # total sum of squares
    r2 = 1 - (RSS / TSS)
    return round(r2, 2)

def AIC(y_true, y_pred, n_params):
    # taken from Lopez et al, 2004 (doi 10.1016/j.ijfoodmicro.2004.03.026)
    RSS = np.sum((y_true - y_pred)**2)  # residual sum of squares
    n_points = len(y_true)  # assuming len(y_true)==len(y_pred)
    aic = n_points * np.exp(RSS/n_points) + 2*(n_params+1) + 2*(n_params+1)*(n_params+2)/(n_points-n_params-2)
    return round(aic, 2)

def get_more_t_point(time, mult=10):
    # eg: draw fitted curve with 3 times more points
    return np.linspace(min(time), max(time), len(time)*mult)




def guess_params(time, y, n_bins=7):
    
    # STEP 1: create bins
    step = (max(y) - min(y))/ (n_bins-1)
    bins = {}  # alwys n_bins + 1
    for i in range(n_bins):
        bin_start = min(y) + step*i - step/2
        bin_end = bin_start + step
        bins[(bin_start, bin_end)] = []
    

    # STEP 2: populate bins 
    for i, yi in enumerate(y): 
        for (bin_start, bin_end) in bins.keys():
            if yi > bin_start and yi <= bin_end:
                bins[(bin_start, bin_end)].append((time[i], yi))

                
    # STEP 3: guess values 
    key_lag = list(bins.keys())[0]
    key_plateau = list(bins.keys())[-1]
    
    guess_tlag = max([ti for ti, yi in bins[key_lag]])
    guess_ylag = statistics.mean([yi for ti, yi in bins[key_lag]])
    guess_tmax = min([ti for ti, yi in bins[key_plateau]])
    guess_tdeath = max([ti for ti, yi in bins[key_plateau] if yi == max(y)])
    guess_ymax = statistics.mean([yi for ti, yi in bins[key_plateau]])
    
    guess_y0 = 0   # due to the imposed preprocessing
    guess_mu = 4
    guess_mudeath = 1

    
    pnames = ['y0',      'tlag',     'mu',     'ymax',     'tmax',     'tdeath',     'mudeath']
    p0 =     [guess_y0,  guess_tlag, guess_mu, guess_ymax, guess_tmax, guess_tdeath, guess_mudeath]

    return pnames, p0, key_lag, key_plateau


