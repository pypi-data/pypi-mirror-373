#

import numpy as np

import matplotlib.pyplot as pp

import random as rd

import bagpipes as bp

from ..LazaUtils.MPF import frac_int
from ..LazaUtils.get import get_z

#==========================================================
def resolved_mass(pixarr,rep=1000,single_error=False,plot_gauss=False,plot_map=False):
    """
    ---------------------------------------------
    INSTRUCTIONS
    Calculates the total stellar mass of a resolved object. This is done by, for each pixel, working out the mean value of the gaussian ditribution obtained from N gaussian rolls, where mu=stellar mass and sigma=associated error, and then adding up these values
    ---------------------------------------------
    ARGS:
    pixarr: Nx5 array containing the x and y pixel coordinates, stellar mass value and upper and lower bounds, in that order. It is assumed this array is created using get_from_cat
    ---------------------------------------------
    KWARGS:
    rep:    number of gaussian repetitions, this is, number of times a pixel value is calculated and used to work out the mean value of that pixel. Default is 1000
    single_error:   if your data array lacks upper and lower bound, it will be assumed that the error is in the last column and will be used as sigma for the gaussian analysis. Otherwise, the last 2 columns will be considered upper and lower bounds and their mean will be considered the sigma value for the gaussian analysis
    plot_gauss:
    plot_map:
    ---------------------------------------------
    """
    if type(pixarr)!=np.ndarray or pixarr.shape[1]!=5:
        print('pixarr must be a Nx5 array, with N being the number of pixels and the columns the x and y pixel coordinates, the stellar mass value and the upper and lwoer bounds, respectively!\nHave you tried get_from_cat to create this array?')
        return
    if type(rep) not in [int,float]:
        print('rep must be an integer!')
        return
    else:
        rep=int(rep)
    pSM=[]
    puSM=[]
    plSM=[]
    for pixel in pixarr:
        x=pixel[0]
        y=pixel[1]
        sm=pixel[2]
        if single_error:
            e=pixel[3]
        else:
            u=pixel[3]
            l=pixel[4]
            e=(u+l)/2
        values=[]
        for r in range(rep):
            values.append(rd.gauss(mu=sm,sigma=e))
        values=np.asarray(values)
        SM=np.nanpercentile(values,(50),axis=0)
        uSM=np.nanpercentile(values,(84),axis=0)
        lSM=np.nanpercentile(values,(16),axis=0)
        SM=10**SM
        uSM=10**uSM-SM
        lSM=SM-10**lSM
        pSM.append(SM)
        puSM.append(uSM)
        plSM.append(lSM)
    pSM=np.asarray(pSM)
    puSM=np.asarray(puSM)
    plSM=np.asarray(plSM)
    SM=np.nansum(pSM)
    uSM=np.sqrt(np.nansum(puSM**2))
    lSM=np.sqrt(np.nansum(plSM**2))
    #print(SM,uSM,lSM)
    SM=np.log10(SM)
    uSM=np.log10(10**SM+uSM)-SM
    lSM=SM-np.log10(10**SM-lSM)
    return SM,uSM,lSM
    
#==========================================================

def compare_masses(pixarr1,pixarr2,dtype='pixel',IDs=None,title='',xlabel='',ylabel='',show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS
    Creates a plot to compare the masses of 2 sets of models. y-axis will be model1-model2, while x-axis will be model1
    ---------------------------------------------
    ARGS:
    pixarr1:    list containing the pixel values of each resolved object to plot, or the mass value of the object. This array will be used as x-axis values
    pixarr2:    same as pixarr1, but for the other model. Order of the objects must be the same as in pixarr1
    ---------------------------------------------
    KWARGS:
    dtype:  type of data in the pixarr lists. It can be 'pixel', if both lsit contain resolved data, in which case must be an Nx5 array including the x and y pixel positions, the mass values and its upper and lower bounds, in that order;'fo', if the list correspond to the values of the full object mass and its errors; 'pix1fo2' if the first lsit contain resolved data and the second full object; 'fo1pix2' if viceversa
    IDs:    list containing the names of the objects
    title:  plot title
    xlabel: xlabel title
    ylabel: ylabel title
    show:   show resulting plot. Can be either True or False
    save:   save the figure. Can be True, to eb saved in the working directory as 'mass_comparison.svg', or a path to the wanted directory + file name
    ---------------------------------------------
    """
    if type(pixarr1)!=list:
        print('pixarr1 must be a list containing the arrays with the mass value of the objects!')
        return
    elif type(pixarr2)!=list:
        print('pixarr2 must be a list contianing the arrays with the mass value of the objects!')
        return
    elif len(pixarr1)!=len(pixarr2):
        print('Bothh path lists must have the same length! Also, it is assumed both contain the same obtjects in the same order!')
        return
    if type(title)!=str:
        print('title must be a string!')
        return
    elif type(xlabel)!=str:
        print('xlabel must be a string!')
        return
    elif type(ylabel)!=str:
        print('ylabel must be a string!')
        return
    l=len(pixarr1)
    SM1,SM2=[],[]
    if dtype=='pixel':
        for i in range(l):
            SM1.append(resolved_mass(pixarr1[i]))
            SM2.append(resolved_mass(pixarr2[i]))
    elif dtype=='fo':
        for i in range(l):
            SM1.append(pixarr1[i])
            SM2.append(pixarr2[i])
    elif dtype=='pix1fo2':
        for i in range(l):
            SM1.append(resolved_mass(pixarr1[i]))
            SM2.append(pixarr2[i])
    elif dtype=='fo1pix2':
        for i in range(l):
            SM1.append(pixarr1[i])
            SM2.append(resolved_mass(pixarr2[i]))
    else:
        print('dtype must be "pixel" if both list contain pixel data of resolved objects, "fo" if both list contain data of full objects, "pix1fo2" if the first data is of a resolved object and the second of a full object or "fo1pix2" if the first data is of a full object and the second of resolved objects')
        return
    SM1=np.asarray(SM1)
    eSM1=SM1[:,1:].T
    SM2=np.asarray(SM2)
    eSM2=SM2[:,1:].T
    pp.figure(figsize=(16,9))
    pp.errorbar(SM1[:,0],SM1[:,0]-SM2[:,0],xerr=eSM1,yerr=eSM1+eSM2,c='b',ls='None',capsize=3)
    pp.plot(np.linspace(np.nanmin(SM1[:,0]*0.95),np.nanmax(SM1[:,0]*1.05),100),np.zeros(100),c='r',ls='--',label='Same mass line')
    if type(IDs) in [list,tuple,np.ndarray]:
        for i in range(len(IDs)):
            #if you want to change the distance of the annotation, change the 0.99 and 0.95 values
            pp.annotate('%s' % (IDs[i]),(SM1[i,0],(SM1[i,0]-SM2[i,0]+eSM1[1,i]+eSM2[1,i])),weight='bold',ha='center',fontsize=20)
    pp.title(title)
    pp.xlabel(xlabel,fontsize=30)
    pp.ylabel(ylabel,fontsize=30)
    pp.xlim([9.5,10.2])
    pp.plot([],[],' ',label=r'median $\mathrm{\Delta M^{dex}_{\star}}$=0.165')
    pp.legend(fontsize=25)
    pp.tick_params(axis='both',which='both',labelsize=30)
    if show:
        pp.show(block=False)
    if save:
        if type(save)==str:
            pp.savefig(save,dpi=10000)
        else:
            pp.savefig('mass_comparison.png',dpi=900)

#==========================================================

def ageX(fit,X):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    works out the age of a galaxy when it had X% of its total stellar mass
    ---------------------------------------------
    ARGS:
    fit:   dictionary including the star formation history (SFH) distribution of the galaxy. See LazaPipes.BP_fit for more info
    X:     fraction, from 0 to 1, of the total stellar mass formed
    ---------------------------------------------
    """
    sfr=np.flip(np.percentile(fit["sfh"],(50,84,16),axis=0).T,axis=0)
    bt=btime(fit)
    ind=frac_int(bt,sfr[:,0],X)[0]
    iX=frac_int(bt,sfr[:,0],X)[1]
    #cálculo del error
    sfr_u=sfr[:,0]
    sfr_uu=sfr[:,1]
    sfr_ul=sfr[:,2]
    ind_t=[np.max(np.where(sfr[:,0]<=sfr_u[i])) for i in range(len(sfr_u))]
    ind_t.insert(0,np.nanmin(np.where(bt>=0)))
    ind_t=np.asarray(ind_t,dtype=int)
    ind_int=np.asarray([bt[ind_t[i+1]]-bt[ind_t[i]] for i in range(len(ind_t)-1)])
    usfr=sfr[ind,1]-sfr[ind,0]#sigma+ sfr
    lsfr=sfr[ind,0]-sfr[ind,2]#sigma- sfr
    mask=sfr_u<sfr[ind,0]
    #return ind,sfr_u,sfr_uu,sfr_ul
    algou=sfr_uu[mask]-sfr_u[mask]
    algol=sfr_u[mask]-sfr_ul[mask]
    #se asume que sigmaM(iX)=sum((sigSFR*int_t)**2)-(SFRx*intx)**2
    iXu=(usfr/sfr[ind,0])*np.sqrt(2*np.nansum((algou*ind_int[mask])**2))
    iXl=(lsfr/sfr[ind,0])*np.sqrt(2*np.nansum((algol*ind_int[mask])**2))
    return iX,iXu,iXl

#==========================================================

def btime(fit):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Returns the backwards time (i.e. 0: time of observation, age: time of the BB) of a given fit galaxy
    ---------------------------------------------
    ARGS:
    fit:   dictionary including the star formation history (SFH) distribution of the galaxy. See LazaPipes.BP_fit for more info 
    """
    z=get_z(fit)
    aou=np.interp(z,bp.utils.z_array,bp.utils.age_at_z)
    ht=bp.utils.age_at_z[bp.utils.z_array==0] #hubble time #taken from bp files
    lam=np.log10(ht)+9+2*0.0025 #log age max # taken from bp files
    ages=10**np.arange(6,lam,0.0025) #taken from bp files
    btime=np.flip(aou-ages/10**9) #backwards time
    return btime

#==========================================================

def join_SFH(paths,title=None):
    all_sfr=[]
    age20=[]
    age50=[]
    fig=pp.figure(2,figsize=(16,9))
    ax1=fig.add_subplot(1,2,1)
    if title:
        pp.suptitle(title)
    for p in paths:
        fit=load_post(p)
        sfr=np.flip(np.percentile(fit["sfh"],(50),axis=0).T,axis=0)
        bt=btime(fit)
        age20.append(ageX(fit,0.2)[0])
        age50.append(ageX(fit,0.5)[0])
        pp.xlim([np.nanmax(bt[bt>=0]),np.nanmin(bt[bt>=0])])
        all_sfr.append(sfr)
        ax1.plot(bt,sfr,alpha=0.5,c='gray')
        #ax1.axvline(age20[-1],c='r',alpha=0.2,ls='--')
        #ax1.axvline(age50[-1],c='b',alpha=0.2,ls='--')
    all_sfr=np.asarray(all_sfr)
    age20=np.asarray(age20)
    age50=np.asarray(age50)
    ax1.plot(bt,np.nanmean(all_sfr,axis=0),c='k',label='mean SFH')
    ax1.axvline(np.nanmean(age20),ls='-',c='r')
    ax1.axvline(np.nanmean(age50),ls='-',c='b')
    ax1.axvline(frac_int(bt,np.nanmean(all_sfr,axis=0),0.2)[1],c='r',ls='--')
    ax1.axvline(frac_int(bt,np.nanmean(all_sfr,axis=0),0.5)[1],c='b',ls='--')
    ax1.legend()
    ax1.set_xlabel('time (Gyr)')
    ax1.set_ylabel('SFR (M/yr)')
    ax1.set_title('all SFH')
    ax2=fig.add_subplot(1,2,2)
    ax2.set_xlabel('time (Gyr)')
    ax2.set_ylabel('SFR (M/yr)')
    ax2.set_title('sum SFH')
    ax2.plot(bt,np.nansum(all_sfr,axis=0),c='k',label='sum SFR')
    ax2.axvline(frac_int(bt,np.nansum(all_sfr,axis=0),0.2)[1],c='r',ls='--')
    ax2.axvline(frac_int(bt,np.nansum(all_sfr,axis=0),0.5)[1],c='b',ls='--')
    pp.xlim([np.nanmax(bt[bt>=0]),np.nanmin(bt[bt>=0])])
    ax2.legend()

