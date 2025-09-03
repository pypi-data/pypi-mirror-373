#

import numpy as np

import matplotlib.pyplot as pp

import random as rd

import bagpipes as bp

from ..LazaUtils.MPF import frac_int
from ..LazaUtils.get import get_z

#==========================================================

def UVfit(sed,z=0,title='UV fitting',show=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    fits, in restframe, the UV part of the SED. Fit must be done in restframe because we are interested in the emitted UV properties, not affected by redshift. This returns the associated beta index and its error

    fv(y)=a*y**(2+B) -> log(fv)=log(a)+(2+B)*log*(y)
    fitting must be done in the rest-frame!!!
    ---------------------------------------------
    ARGS:
    sed:    SED to fit. This must be a Nx3 array with columns Wavelength (in AA), flux_nu and its associated error
    ---------------------------------------------
    KWARGS:
    z:  source's redshift
    title:  title of the plot. Default is 'UV fitting'
    show:   show the resulting fit
    ---------------------------------------------
    """
    def fv(y,a,B):
        return a*y**(2+B)

    wl=sed[:,0]
    l,u=int(np.where(abs(wl-(0.1268*(1+z)))==np.nanmin(abs(wl-(0.1268*(1+z)))))[0]),int(np.where(abs(wl-(0.2580*(1+z)))==np.nanmin(abs(wl-(0.2580*(1+z)))))[0])
    wl=wl[l:u+1]
    f=sed[l:u+1,1]
    e=sed[l:u+1,2]
    #curve fit
    CF,eCF=cv(fv,wl/(1+z),f,p0=np.array([1,-2]),sigma=e)
    eCF=np.sqrt(np.diag(eCF))
    ##linear fit
    #LR=lr(np.log10(wl/(1+z)),np.log10(f))
    #LR1,eLR=np.array([10**LR[1],LR[0]-2]),np.array([10**LR[1]*np.log(10)*LR[-1],LR[-2]])
    #if show:
        #y=np.linspace(0.1268,0.2580,100)
        #pp.close('all')
        #pp.figure(figsize=(16,9))
        ##data
        #pp.fill_between(wl/(1+z),f-e,f+e,linewidth=0,color='k',alpha=0.5)
        #pp.plot(wl/(1+z),f,ls='-',c='k',label='Data')
        ##CF
        #pp.fill_between(y,(CF[0]-eCF[0])*y**(2+CF[1]-eCF[1]),(CF[0]+eCF[0])*y**(2+CF[1]+eCF[1]),linewidth=0,color='r',alpha=0.5)
        #pp.plot(y,CF[0]*y**(2+CF[1]),ls='--',c='r',label='Curve fit: $%.2f\lambda^{%.2f+2}$' % (CF[0],CF[1]))
        ##LR
        #pp.fill_between(y,(LR1[0]-eLR[0])*y**(2+LR1[1]-eLR[1]),(LR1[0]+eLR[0])*y**(2+LR1[1]+eLR[1]),linewidth=0,color='g',alpha=0.5)
        #pp.plot(y,LR1[0]*y**(2+LR1[1]),ls='--',c='g',label='Lin. Reg.: $%.2f\lambda^{%.2f+2}$' % (LR1[0],LR1[1]))
        #pp.xlabel('Wavelength (um)')
        #pp.ylabel('Flux (uJy)')
        #pp.yscale('log')
        #pp.title(title)
        #pp.legend()
        #pp.show(block=True)
    return CF[1],eCF[1]#,LR1,eLR
