#

import numpy as np

import matplotlib.pyplot as pp
from mpl_toolkits.axes_grid1 import make_axes_locatable as mal

import random as rd

import bagpipes as bp

from ..LazaUtils.MPF import frac_int, print_errs, str2TeX
from ..LazaUtils.get import get_z
import ..LazaPipes.data_handling as LPdh

from natsort import natsorted as ns
import glob as glob



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

def mass_map(ID,run,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Creates a figure with 4 maps showing stellar mass, stellar mass surfaace density, SFR and SFR surface density of a given fit source. Also, the figure includes a table sumarizing the mass properties of each bin in the map
    ---------------------------------------------
    ARGS:
    ID: source's ID
    run:    (bagpipes) run from where to take the data
    ---------------------------------------------
    KWARGS:
    show:   show the resulting figure
    save:   save the resulting figure as ID_run_mass_binmap.pdf
    ---------------------------------------------
    """
    pp.close('all')

    params=['stellar_mass','Estellar_mass','sfr','Esfr']
    #loading data
    paths=ns(glob.glob('*%s*/%s/*npy' % (ID,run)))
    #print(paths)
    L=len(paths)
    masks=ns(glob.glob('BINS/*%s*' % (ID)))
    masks=fits.open(masks[0])
    full_mask=masks[0].data
    full_mask[full_mask>1]=1
    full_mask[full_mask==0]=np.nan
    full_area=source_area(full_mask,z_dic[ID],0.08)
    cmap_list=['spring', 'summer', 'autumn', 'winter']

    #Creating the figure
    # fig,axs=mpd(params)
    fig=pp.figure(figsize=(17,18))
    fig.suptitle('Mass map for %s - run: %s' % (ID,run),fontsize=30)
    tab_dat=np.ones([L,4])
    tab_uerr=np.ones([L,4])
    tab_lerr=np.ones([L,4])
    cell_text=[]
    axs=[fig.add_subplot(3,2,i) for i in range(1,5)]
    for i in range(len(params)):
        pval=[]
        mval=[]
        uerr=[]
        lerr=[]
        for j in range(L):
            d=LPdh.load_post(paths[j])
            #print(paths[j])
            #print(d[params[i]])
            if params[i] not in ['Esfr','Estellar_mass']:
                try:
                    val=np.nanmedian(d[params[i]])
                    u,l=np.nanpercentile(d[params[i]],(84,16))
                    m=masks[j+1].data*val
                    pval.append(val)
                    mval.append(m)
                    uerr.append(u-val)
                    lerr.append(val-l)
                    axs[i].set_title('%s' % (lat_labels[params[i]]),fontsize=20)
                except KeyError:
                    raise KeyError('The parameter %s is not included in the dictionary. It value for the bin will be set to NaN' % (params[i]))
                    pval.append(np.nan)
                    mval.append(masks[j+1].data*np.nan)
                    err.append(np.nan)
                    axs[i].set_title('%s' % (params[i]),fontsize=20)
            elif params[i]=='Esfr':
                val=np.nanmedian(d[params[i][1:]])
                u,l=np.nanpercentile(d[params[i][1:]],(84,16))
                val=Eparam(val,masks[j+1].data,z_dic[ID],0.08)
                u,l=Eparam(u,masks[j+1].data,z_dic[ID],0.08),Eparam(l,masks[j+1].data,z_dic[ID],0.08)
                m=masks[j+1].data*val
                pval.append(val)
                mval.append(m)
                uerr.append(u-val)
                lerr.append(val-l)
                axs[i].set_title(r'$\mathrm{\Sigma_{SFR} (M_{\odot}yr^{-1}kpc^{-2})}$',fontsize=20)
            elif params[i]=='Estellar_mass':
                val=np.nanmedian(d[params[i][1:]])
                u,l=np.nanpercentile(d[params[i][1:]],(84,16))
                val=np.log10(Eparam(10**val,masks[j+1].data,z_dic[ID],0.08))
                u,l=np.log10(Eparam(10**u,masks[j+1].data,z_dic[ID],0.08)),np.log10(Eparam(10**l,masks[j+1].data,z_dic[ID],0.08))
                m=masks[j+1].data*val
                pval.append(val)
                mval.append(m)
                uerr.append(u-val)
                lerr.append(val-l)
                axs[i].set_title(r'$\mathrm{log_{10}(\Sigma_{M^{\star}})}$ $\mathrm{(log_{10}(M_{\odot}kpc^{-2}))}$',fontsize=20)
        pval=np.asarray(pval)
        uerr=np.asarray(uerr)
        lerr=np.asarray(lerr)
        tab_dat[:,i]=pval.T
        tab_uerr[:,i]=uerr.T
        tab_lerr[:,i]=lerr.T
        #print(params[i],np.nanmin(pval),np.nanmax(pval))
        mval=np.asarray(mval)
        mapa=np.nansum(mval,axis=0)
        mapa[mapa==0]=np.nan
        pmap=axs[i].imshow(mapa,origin='lower',cmap=cmap_list[i])
        zoomin(mapa,axs[i])
        axs[i].set_xticks([])
        axs[i].set_yticks([])
        divider=mal(axs[i])
        cax=divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(pmap,cax=cax,ax=axs[i],ticks=np.linspace(np.nanmin(pval),np.nanmax(pval),3),format='%.3g')
        # fig.colorbar(pmap,cax=cax,ax=axs[i],ticks=ticks)
        # fig.subplots_adjust(hspace=0)
    #Table summarising the results
    cols=['log$_{10}$(M$^{\star}$/M$_{\odot}$)','$\mathrm{log_{10}(\Sigma_{M^{\star}})}$ $\mathrm{(log_{10}(M_{\odot}kpc^{-2}))}$','SFR ($\mathrm{M_{\odot}yr^{-1}}$)','$\mathrm{\Sigma_{SFR} (M_{\odot}yr^{-1}kpc^{-2})}$']
    rows=['BIN %i' % (i) for i in range(1,L+1)]
    rows=rows+['TOTAL']
    cell_text=[]
    a=[r'%g$^{+%g}_{-%g}$' % print_errs(tab_dat.reshape(tab_dat.size)[i],tab_uerr.reshape(tab_uerr.size)[i],tab_lerr.reshape(tab_lerr.size)[i]) for i in range(tab_dat.size)]
    totals=['%g$^{+%g}_{-%g}$' % print_errs(np.log10(np.nansum(10**tab_dat[:,0])),np.log10(np.nansum(10**(tab_dat[:,0]+tab_uerr[:,0])))-np.log10(np.nansum(10**tab_dat[:,0])),np.log10(np.nansum(10**tab_dat[:,0]))-np.log10(np.nansum(10**(tab_dat[:,0]-tab_lerr[:,0])))),
            '%g$^{+%g}_{-%g}$' % print_errs(np.log10(np.nansum(10**tab_dat[:,0])/full_area),np.log10((np.nansum(10**(tab_dat[:,0]+tab_uerr[:,0])/full_area)))-np.log10(np.nansum(10**tab_dat[:,0])/full_area),np.log10(np.nansum(10**tab_dat[:,0])/full_area)-np.log10((np.nansum(10**(tab_dat[:,0]-tab_lerr[:,0])))/full_area)),
            '%g$^{+%g}_{-%g}$' % print_errs(np.nansum(print_errs(tab_dat[:,2],tab_uerr[:,2],tab_lerr[:,2]),axis=1)[0],np.nansum(print_errs(tab_dat[:,2],tab_uerr[:,2],tab_lerr[:,2]),axis=1)[1],np.nansum(print_errs(tab_dat[:,2],tab_uerr[:,2],tab_lerr[:,2]),axis=1)[2]),
            '%g$^{+%g}_{-%g}$' % print_errs(np.nansum(print_errs(tab_dat[:,2],tab_uerr[:,2],tab_lerr[:,2]),axis=1)[0]/full_area,np.nansum(print_errs(tab_dat[:,2],tab_uerr[:,2],tab_lerr[:,2]),axis=1)[1]/full_area,np.nansum(print_errs(tab_dat[:,2],tab_uerr[:,2],tab_lerr[:,2]),axis=1)[2]/full_area)]
    a=np.asarray(a+totals)
    cell_text=a.reshape((L+1,4))
    tabax=fig.add_subplot(3,1,3)
    the_table=tabax.table(cellText=cell_text,rowLabels=rows,colLabels=cols,loc='center',fontsize=20)
    tabax.axis('off')
    the_table.scale(1,3)
    pp.tight_layout
    if show:
        pp.show(block=False)
    if save:
        fig.savefig('%s_%s_mass_binmap.pdf' % (ID,run))

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


#==========================================================

def compare_SFHs(ID,run1,run2,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Compares 2 SFHs from the same source but different fitting model. It shows boths SFHs on a top panel and their differences  in the bottom panel
    ---------------------------------------------
    ARGS:
    ID: source's ID
    run1:   first model.
    run2:   second model.
    ---------------------------------------------
    KWARGS:
    show:   show the resulting figure
    save:   save the resulting figure as ID_SFHcomp_model1vsmodel2.pdf
    ---------------------------------------------
    """
    pp.close('all')
    path1=ns(glob.glob('*%s*/*%s*/*%s*.npy' % (ID,run1,run1)))[0]
    path2=ns(glob.glob('*%s*/*%s*/*%s*.npy' % (ID,run2,run2)))[0]
    post1=LPdh.load_post(path1)
    sfr1=np.flip(np.nanmedian(post1['sfh'],axis=0))
    bt1=btime(post1)
    post2=LPdh.load_post(path2)
    sfr2=np.flip(np.nanmedian(post2['sfh'],axis=0))
    bt2=btime(post2)
    fig=pp.figure(figsize=(22,17))
    gs=GS(nrows=2,ncols=1,height_ratios=[3,1])
    #top, both SFHs
    top=fig.add_subplot(gs[0])
    top.semilogy(bt1,sfr1,ls='-',c='r',label='%s' % (run1))
    top.semilogy(bt2,sfr2,ls='-',c='g',label='%s' % (run2))
    top.legend(fontsize=20)
    top.set_ylabel('SFR (M$_{\odot}$yr$^{-1}$)',fontsize=20)
    top.set_title(r'$\bf{%s}$' % (str2TeX(ID))+'\n Model 1: %s \nvs \nModel 2: %s' % (run1,run2),fontsize=30)
    top.set_xlim([np.nanmax(bt1[bt1>=0]),np.nanmin(bt1[bt1>=0])])
    top.tick_params(axis='y',which='major',labelsize=20)
    #bottom, SFH diff
    bottom=fig.add_subplot(gs[1],sharex=top)
    bottom.axhline(0,ls='--',c='k')
    bottom.plot(bt1,sfr1-sfr2,ls='-',c='b')
    bottom.set_ylabel('$\mathrm{\Delta}$SFR (M$_{\odot}$yr$^{-1}$)',fontsize=20)
    bottom.set_xlabel('Time (Gyr)', fontsize=20)
    bottom.tick_params(axis='x',which='major',labelsize=20)
    pp.subplots_adjust(hspace=0)
    if show:
        pp.show(block=False)
    if save:
        mkdirs('SFHcomps',fil=False)
        fig.savefig('SFHcomps/%s_SFHcomp_%svs%s.pdf' % (ID,run1,run2))

#----------------------------------------------------------

def INTvsRES(model,param,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Compares integrated and resolved results of a given parameter, for all sources with available data of a specific model, and plots the comparison
    ---------------------------------------------
    ARGS:
    model:  (bagpipes) run name of the model to compare
    param:  param to compare. At the moment, only stellar_mass is available
    ---------------------------------------------
    KWARGS:
    show:   show the resulting figure
    save:   save the resulting figure as ID_run_mass_binmap.pdf
    ---------------------------------------------
    """
    pp.close('all')
    pathsI=ns(glob.glob('BP*INT*/INT*%s/*npy' % (model)))
    pathsR=ns(glob.glob('BP*bin*/%s/*npy' % (model)))
    IDS=np.unique([pathsR[i].split('/')[0][3:-10] for i in range(len(pathsR))])
    markers={'R05':'s','R08a':'^','R08b':'^','R12':'>','R14':'<','R15':'o','R18':'h','R25':'P','R29':'H','R32':'d','R34a':'*','R34b':'*','R38a':'X','R38b':'X','R39a':'p','R39b':'p'}
    colors=['r','g','b','y','c','pink','orange','brown','purple','gray','lightgreen','navy','violet','gold','coral','m']
    if param=='stellar_mass':
        massI=[]
        massR=[]
        ll=0
        for p in pathsI:
            post=LPdh.load_post(p)
            m=np.nanmedian(post[param])
            # u=np.log10(10**np.nanpercentile(post[param],84)-10**m)
            # l=np.log10(10**m-10**np.nanpercentile(post[param],16))
            u=np.nanpercentile(post[param],84)-m
            l=m-np.nanpercentile(post[param],16)
            massI.append([m,u,l])
        for i in range(len(IDS)):
            vals=[]
            for p in pathsR:
                if p.split('/')[0][3:-10]==IDS[i]:
                    post=LPdh.load_post(p)
                    m=10**np.nanmedian(post[param])
                    u=10**np.nanpercentile(post[param],84)
                    l=10**np.nanpercentile(post[param],16)
                    vals.append([m,u,l])
            vals=np.nansum(np.asarray(vals),axis=0)
            # print(vals)
            m=np.log10(vals[0])
            u=np.log10(vals[1])-m
            l=m-np.log10(vals[2])
            massR.append([m,u,l])
        massI,massR=np.asarray(massI),np.asarray(massR)
        if show:
            fig=pp.figure(figsize=(20,20))
            for i in range(len(IDS)):
                pp.errorbar(massR[i,0],massR[i,0]-massI[i,0],xerr=np.atleast_2d(massR[i,1:]).T,yerr=np.atleast_2d(massR[i,1:]).T+np.atleast_2d(massI[i,1:]).T,ls='none',marker=markers[IDS[i]],capsize=3,markersize=20,label=IDS[i],color=colors[i])
            pp.axhline(0,ls='--',color='k')
            pp.xlabel('Resolved M$_{\star}$ (log$_{10}$(M$_{\star}$/M$_{\odot}$)',fontsize=20)
            pp.ylabel('M$_{\star}$ diffrence (Resolved - Integrated) (dex)',fontsize=20)
            pp.title(r'$\bf{Stellar\ mass\ comparison}$'+'\nModel: %s' % (model),fontsize=30)
            pp.xticks(fontsize=20)
            pp.yticks(fontsize=20)
            median=np.nanmedian(massR[:,0]-massI[:,0])
            um,lm=np.nanpercentile(massR[:,0]-massI[:,0],(84,16))
            print(um,lm)
            um,lm=um-median,median-lm
            print(um,lm)
            aver=np.nanmean(massR[:,0]-massI[:,0])
            ua,la=np.sqrt(np.nansum((massR[:,1]+massI[:,1])**2))/len(massR[:,1]),np.sqrt(np.nansum((massR[:,2]+massI[:,2])**2))/len(massR[:,2])
            pp.axhline(aver,ls=':',c='r',zorder=-1,label='Average: %g$^{+%g}_{-%g}$' % (print_errs(aver,ua,la)))
            pp.axhline(median,ls=':',c='g',zorder=-1,label='Median: %g$^{+%g}_{-%g}$' % (print_errs(median,um,lm)))
            print(median,um-median,median-lm)
            pp.legend(fontsize=20)
            pp.show(block=False)
        if save:
            fig.savefig('INTvsRES_%s_model-%s.pdf' % (param,model))
        return massI,massR
    else:
        print('This param is not yet available. Available comparisons are: stellar_mass')

#----------------------------------------------------------

def RESvsRES(model1,model2,param,show=True,save=True):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Compares resolved results of a given parameter, for all sources with available data of 2 different models, and plots the comparison
    ---------------------------------------------
    ARGS:
    model1:  (bagpipes) run name of the first model to compare. It will be the x-axis
    model2:  (bagpipes) run name of the second model to compare.
    param:  param to compare. At the moment, only stellar_mass is available
    ---------------------------------------------
    KWARGS:
    show:   show the resulting figure
    save:   save the resulting figure as ID_run_mass_binmap.pdf
    ---------------------------------------------
    """
    pp.close('all')
    pathsR1=ns(glob.glob('BP*bin*/*%s*/*npy' % (model1)))
    pathsR2=ns(glob.glob('BP*bin*/*%s*/*npy' % (model2)))
    IDS=np.unique([pathsR1[i].split('/')[0][3:-10] for i in range(len(pathsR1))])
    markers={'R05':'s','R08a':'^','R08b':'^','R12':'>','R14':'<','R15':'o','R18':'h','R25':'P','R29':'H','R32':'d','R34a':'*','R34b':'*','R38a':'X','R38b':'X','R39a':'p','R39b':'p'}
    colors=['r','g','b','y','c','pink','orange','brown','purple','gray','lightgreen','navy','violet','gold','coral','m']
    if param=='stellar_mass':
        massR1=[]
        massR2=[]
        for i in range(len(IDS)):
            vals1=[]
            vals2=[]
            for j in range(len(pathsR1)):
                if pathsR1[j].split('/')[0][3:-10]==IDS[i]:
                    post1=LPdh.load_post(pathsR1[j])
                    m1=10**np.nanmedian(post1[param])
                    u1=10**np.nanpercentile(post1[param],84)
                    l1=10**np.nanpercentile(post1[param],16)
                    vals1.append([m1,u1,l1])
                    post2=LPdh.load_post(pathsR2[j])
                    m2=10**np.nanmedian(post2[param])
                    u2=10**np.nanpercentile(post2[param],84)
                    l2=10**np.nanpercentile(post2[param],16)
                    vals2.append([m2,u2,l2])
            vals1=np.nansum(np.asarray(vals1),axis=0)
            # print(vals)
            m=np.log10(vals1[0])
            u=np.log10(vals1[1])-m
            l=m-np.log10(vals1[2])
            massR1.append([m,u,l])
            vals2=np.nansum(np.asarray(vals2),axis=0)
            # print(vals)
            m=np.log10(vals2[0])
            u=np.log10(vals2[1])-m
            l=m-np.log10(vals2[2])
            massR2.append([m,u,l])
        massR1,massR2=np.asarray(massR1),np.asarray(massR2)
        if show:
            fig=pp.figure(figsize=(20,20))
            for i in range(len(IDS)):
                pp.errorbar(massR1[i,0],massR2[i,0],xerr=np.atleast_2d(massR1[i,1:]).T,yerr=np.atleast_2d(massR2[i,1:]).T,ls='none',marker=markers[IDS[i]],capsize=3,markersize=20,label=IDS[i],color=colors[i])
            ax=pp.gca()
            axx=ax.get_xlim()
            axy=ax.get_ylim()
            pp.plot(np.linspace(axx[0],axx[1],100),np.linspace(axx[0],axx[1],100),ls='--',c='k',label='Same M$^{\star}$ line')
            pp.xlabel('M$_{\star}$ (log$_{10}$(M$_{\star}$/M$_{\odot}$)\nModel 1: %s' % (model1),fontsize=20)
            pp.ylabel('Model 2: %s\nM$_{\star}$ (log$_{10}$(M$_{\star}$/M$_{\odot}$)' % (model2),fontsize=20)
            pp.title(r'$\bf{Stellar\ mass\ comparison}$'+'\nModel 1: %s\nvs\nModel 2: %s' % (model1,model2),fontsize=30)
            pp.xticks(fontsize=20)
            pp.yticks(fontsize=20)
            pp.legend(fontsize=20)
            pp.show(block=False)
        if save:
            fig.savefig('RESvsRES_%s_model1-%s_model2-%s.pdf' % (param,model1,model2))
        return massR1,massR2
    else:
        print('This param is not yet available. Available comparisons are: stellar_mass')
