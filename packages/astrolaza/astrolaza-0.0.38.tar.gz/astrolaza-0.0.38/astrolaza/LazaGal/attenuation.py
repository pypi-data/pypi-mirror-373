#

import numpy as np

import matplotlib.pyplot as pp

import random as rd

import bagpipes as bp

from ..LazaUtils.MPF import frac_int
from ..LazaUtils.get import get_z

#==========================================================

def B2Ay(beta,sigbeta,y,Rv=4.05,B0=-2.44):
    """
    --------------------------------------------
    INSTRUCTIONS:
    Gets any attenuation A_y (i.e. Av, Auv) for a given wavelength, according to Calzetti et al. dust attenuation laws, from a given beta slope (UV slope) value
    --------------------------------------------
    ARGS:
    beta:   beta slope of the UV part of the SED. For more information, look LazaGal.UV.UVfit
    sigbeta:    associated error of beta
    y:  wavelength, in AA, where the attenuation is calculated. This can be either a float or an array.
    ---------------------------------------------
    KWARGS:
    Rv: coeffient between Av and Es(B-V), being V the V band flux and B the B band flux. This is a constant value, usually given in the extintion law. Default is 4.05
    B0: intrinsic beta slope value (i.e. B if there were no obscuration). Default is -2.44
    ---------------------------------------------
    """
    #work out any attenuation A(y) from beta slopes
    if y>=0.12 and y<0.63:
        k=2.659*(-2.156+1.509/y-0.198/y**2+0.011/y**3)+Rv
    elif y>=0.63 and y<=2.2:
        k=2.659*(-1.857+1.040/y)+Rv
    Ay=0.44*2.31*k*(beta-B0)/4.39
    sigAy=(2.31/4.39)*np.sqrt((0.03*k*(beta-B0))**2+(0.44*0.8*(beta-B0))**2+(0.44*k*sigbeta)**2)
    return Ay,sigAy
