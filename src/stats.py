'''
Ultimately, these functions should be hosted in some independent package...
But it's in here for now.
'''

import numpy as np
import scipy.stats

def ThompsonCI_onesided( n_samples, percentile, confidence, CI_side='lower', verbose=False):
    '''This function computes a one-sided confidence interval for the given
    percentile, with the given confidence level.
    Unless CI_side='upper', a lower-bound is computed.
    The index of the sample is returned.
    None is returned if there are not enough samples for the desired CI.
    '''

    ##
    # Checking the inputs
    ##

    # Confidence and percentile must be between 0 and 100
    if confidence >= 100 or confidence <= 0:
        raise ValueError("Invalid confidence: "+repr(confidence)+". Provide a real number strictly between 0 and 100.")
    if percentile >= 100 or percentile <= 0:
        raise ValueError("Invalid percentile: "+repr(percentile)+". Provide a real number strictly between 0 and 100.")

    # Handling the CI_side
    if not (CI_side == 'lower' or CI_side == 'upper'):
        raise ValueError("Invalid CI_side: "+repr(CI_side)+". Valid 'CI_side' values: 'lower' or 'upper'")

    # Define the working percentile
    if CI_side == 'upper':
        p_work = 100 - percentile
    else:
        p_work = percentile

    # compute all probabilities from the binomiale distribution for the percentile of interest
    bd=scipy.stats.binom(n_samples,p_work/100)
    ppm = [np.maximum(1-x,0.0) for x in np.cumsum([bd.pmf(k) for k in range(n_samples)])]
    # print([bd.pmf(k) for k in range(n_samples+1)])
    # print(ppm)

    # search the index defining a lower-bound for p_work
    if ppm[0] < confidence/100:
        return np.nan
    else:
        for k in range(n_samples):
            # search for first index reaching below the desired confidence
            if ppm[k] < confidence/100:
                # lower-bound is the previous index
                CI = k-1
                break

    # return the requested CI index
    if CI_side == 'lower':
        return CI
    else:
        return ((n_samples-1) - CI) # First index is 0 (not 1)

def ThompsonCI_twosided( n_samples, percentile, confidence,  verbose=False):
    '''
    Compute a two-sided CI from two symetric one-sided intervals.
    For example, to obtain a two-sided 80%CI, this functions simply computes
    two 90%CI (upper and lower) and combine them.

    Note that the solution is not unique! This is only the simplest way to get
    a two-sided CI.
    '''

    # Confidence and percentile must be between 0 and 100
    if confidence >= 100 or confidence <= 0:
        raise ValueError("Invalid confidence: "+repr(confidence)+". Provide a real number strictly between 0 and 100.")
    if percentile >= 100 or percentile <= 0:
        raise ValueError("Invalid percentile: "+repr(percentile)+". Provide a real number strictly between 0 and 100.")

    # Compute the one-sided confidence
    confidence_one_sided = (confidence+100)/2

    # Compute the bounds
    LB = ThompsonCI_onesided(
        n_samples, percentile, confidence_one_sided, CI_side='lower')
    UB = ThompsonCI_onesided(
        n_samples, percentile, confidence_one_sided, CI_side='upper')

    return LB, UB
