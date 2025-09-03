#Functions to work with Spectral Energy Distribution arrays
#==========================================================

import numpy as np

from matplotlib.gridspec import GridSpec as GS

from ..LazaUtils.get import get_index,get_z
from ..LazaUtils.MPF import str2TeX
from ..LazaPipes.data_handling import load_post
from ..LazaPipes.plotting import makebox


#==========================================================
def change_units(sed,wl_unit,f_unit):
    """
    ---------------------------------------------
    INSTRUCTIONS
    Converts AA-ergscma seds into whatever unit you want, for each axis
    ---------------------------------------------
    ARGS:
    sed: Nx2 or Nx3 array with wavelength in AA in the first column and flux density in ergscma in the second column and, optionally, flux error in the third column^
    wl_unit:    output wavelength unit. Can be AA or meter-related (mm,um,nm,etc)
    f_unit: output flux unit. Can be ergscma or jansky related (mjy.ujy,njy,etc)
    ---------------------------------------------
    """
    wl=sed[:,0]
    f=sed[:,1]
    wl_ind,wl_unit=get_index(wl_unit)
    f_ind,f_unit=get_index(f_unit)
    c=2.99792458e+8 #speed of light in m/s
    if wl_unit!='AA' and wl_unit[-1]!='m' and f_unit!='ergscma' and f_unit[-2:]!='jy':
        raise ValueError('Wavelength units must eb either AA or m related, and flux units must be either ergscma or jy related!')
    else:
        if f_unit[-2:]=='jy':
            f=f/(1e-23*f_ind)*((wl)**2/(c*1e10))
        if sed.shape[1]>2:
            e=sed[:,2]
            if f_unit[-2:]=='jy':
                e=e/(1e-23*f_ind)*((wl)**2/(c*1e10))
        else:
            e=ones(len(f))*-99e99
        if wl_unit[-1]=='m':
            wl=wl*(1e-10/wl_ind)
    sed=np.stack((wl,f,e),axis=1)
    print(wl_ind,wl_unit,f_ind,f_unit)
    return sed

#==========================================================

def smooth_sed(sed,bins):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Smooths (i.e., rebins) a given SED
    ---------------------------------------------
    ARGS:
    sed:    Nx2 or Nx3 array, containing the wavelength and the flux and associated error of the SED
    bins:   rebinning vaulue. Must be an integer
    ---------------------------------------------
    """
    try:
        wl=sed[:,0]
        f=sed[:,1]
        e=sed[:,2]
    except IndexError:
        e=np.ones(len(wl))*-99e99
    wl2,f2,e2=[],[],[]
    #lim=np.floor(len(sed[:,0])/bins)
    #for i in range(int(lim)+1000):
        #wl.append(sed[int(bins*i+np.floor(bins/2)),0])
        #f.append(np.nansum(sed[bins*i:bins*(i+1),1])/bins)
        #if sed.shape[1]>2:
            #e.append(np.sqrt(np.nansum(sed[bins*i:bins*(i+1),2]**2))/bins)
        #else:
            #e.append(-99e99)
    lim=int(np.ceil(len(wl)/bins))
    #print(len(wl),len(wl)/bins,np.ceil(len(wl)/bins),lim)
    for i in range(lim):
        #wl
        bwl=np.nanmean(wl[:bins])
        wl=wl[bins:]
        wl2.append(bwl)
        #flux
        bf=np.nanmean(f[:bins])
        f=f[bins:]
        f2.append(bf)
        #error
        be=np.nanmean(e[:bins])
        e=e[bins:]
        e2.append(be)
    bin_sed=np.stack((wl2,f2,e2),axis=1)
    return bin_sed

#----------------------------------------------------------


def smoothSED_IV(sed,bins):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    smooths (i.e. rebins) a given SED using an inverse variance calculation
    ---------------------------------------------
    ARGS:
    sed:    Nx2 or Nx3 array, containing the wavelength and the flux and associated error of the SED
    bins:   rebinning vaulue. Must be an integer
    ---------------------------------------------
    """
    wl,f,e=[],[],[]
    lim=np.floor(len(sed[:,0])/bins)
    for i in range(int(lim)+1):
        #wl.append(sed[int(bins*i+np.floor(bins/2)),0])
        wl.append(np.nanmean(sed[bins*i:bins*(i+1),0]))
        f.append(np.nansum(sed[bins*i:bins*(i+1),1]/sed[bins*i:bins*(i+1),2]**2)/np.nansum(1/sed[bins*i:bins*(i+1),2]**2))
        if sed.shape[1]>2:
            e.append(np.sqrt(1/np.nansum(1/sed[bins*i:bins*(i+1),2]**2)))
        else:
            e.append(-99e99)
    #rest2=sed[(i)*bins,:]
    #print(i,bins,len(sed),i*bins,len(rest2))
    #wl.append(sed[int(bins*i+np.floor(bins/2)),0])
    #f.append(
    bin_sed=np.stack((wl,f,e),axis=1)
    return bin_sed

#==========================================================

def remove_bad_values(arr,col,ratio=1e4):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Removes the rows from an array if a column of an array contains an absolute value larger than ratio*median(abs). This criteria is completely arbitary yet useful for the working data
    ---------------------------------------------
    ARGS:
    arr:    input array, must have at least 2 columns
    col:    column index from which apply the criteria
    ---------------------------------------------
    KWARGS:
    ratio:  ratio between values and median(abs). If a value is above this ratio, that value is removed
    ---------------------------------------------
    """
    ab_arr=abs(arr[:,col])
    ab_med=np.nanmedian(ab_arr)
    new_arr=arr[ab_arr<ab_med*ratio,:]
    return new_arr

#==========================================================

def mean_cont(sed,z,band):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Works out the median value of a continuum in a SED
    ---------------------------------------------
    ARGS:
    sed:    path to the SEDs file (npy or txt) or array with 3 columns (wavelength, flux and flux error). If it is an npy file, it is assumed it comes from LazaPipes.fitting and has units of AA and ergscma. If a txt file or an array, it is assumed the first column is waleventhg in AA, the second flux in uJy and the third its error in the same units
    z:  redshift of the object
    band:   list, tuple or array of 2 eleemtns containing the lower and upper limits of the continuum band, in rest-frame and the same unit as the wavelength in the sed
    ---------------------------------------------
    """
    c=2.99792458e+18 #speed of light in AA/s
    if type(sed)==np.ndarray:
        wl=sed[:,0]
        f=sed[:,1]
        e=sed[:,2]
    elif type(sed)==str:
        if sed[-4:]=='.npy':
            data=load_post(sed)
            wl=data['wavelength_obs']
            f=data['spectrum_obs']*wl**2/c*1e29
            e=data['err_spectrum_obs']*wl**2/c*1e29
        else:
            wl,f,e=np.loadtxt(sed,usecols=(0,1,2))
    else:
        TypeError('sed must be either an npy file obtained from LazaPipes.fitting.BP_fit, a txt file with 3 columns (wavelength, flux and flux error) or an array with 3 columns (wavelength, flux and error)!')
    band_flux=f[np.where((wl>=band[0]*(1+z)) & (wl<=band[1]*(1+z)))]
    band_err=e[np.where((wl>=band[0]*(1+z)) & (wl<=band[1]*(1+z)))]
    cosa=[]
    cosa_e=[]
    for i in range(100): #generating 100 flux values to get a better estimation
        ff=np.random.normal(band_flux,band_err)
        cosa.append([np.nanmean(ff),np.nanmedian(ff)])
        #cosa_e.append([np.sqrt(np.nansum(band_err**2))/len(band_err),np.nanmean(np.nanpercentile(ff,(16,84)))])
    cosa=np.asarray(cosa)
    #cosa_e=np.asarray(cosa_e)
    mean=np.nanmean(cosa[:,0]) #average of the generated fluxes
    #mean_e=np.nanmean(cosa_e[:,0])
    mean_e=np.nanmean(band_err) #average of its error
    median=np.nanmedian(cosa[:,1])
    meadian_e=np.nanpercentile(cosa[:,1],(16,84))
    return mean, mean_e, median, meadian_e

#==========================================================

def apply_cont(sed,z,bands,lines):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Removes emission lines from a SED and subtitites them with their continuum. The continuums are calculated as the interpolated mean values of the adjacent continuums; see mean_cont for mor info
    ---------------------------------------------
    ARGS:
    sed:    path to the SEDs file (npy or txt) or array with 3 columns (wavelength, flux and flux error). If it is an npy file, it is assumed it comes from LazaPipes.fitting and has units of AA and ergscma. If a txt file or an array, it is assumed the first column is waleventhg in AA, the second flux in uJy and the third its error in the same units
    bands:  conitnuum bands. This must be a list with each element a list, tuple or array of 2 elements, the lower and upper limits of the continuums, in restframe and the same unit as the wavelength in sed (preferably AA)
    lines:  list of line ranges. It follows the same behaviour as bands.
    NOTE THAT BANDS AND LINES MUST BE IN ASCENDING ORDER
    ---------------------------------------------
    """
    c=2.99792458e+18 #speed of light in AA/s
    conts=[]
    if type(sed)==np.ndarray:
        wl=sed[:,0]
        f=sed[:,1]
        e=sed[:,2]
    elif type(sed)==str:
        if sed[-4:]=='.npy':
            data=load_post(sed)
            wl=data['wavelength_obs']
            f=data['spectrum_obs']*wl**2/c*1e29
            e=data['err_spectrum_obs']*wl**2/c*1e29
        else:
            wl,f,e=np.loadtxt(sed,usecols=(0,1,2))
    else:
        TypeError('sed must be either an npy file obtained from LazaPipes.fitting.BP_fit, a txt file with 3 columns (wavelength, flux and flux error) or an array with 3 columns (wavelength, flux and error)!')
    for b in bands:
        # y=np.split(wl,[b[0]*(1+z),b[1]*(1+z)])[1]
        y=wl[np.where((wl>=b[0]*(1+z)) & (wl<=b[1]*(1+z)))]
        mc=mean_cont(sed,z,b)[:2]
        # print(mc)
        # y=np.linspace(b[0],b[1],100)
        conts.append(np.vstack((y,np.ones(len(y))*mc[0],np.ones(len(y))*mc[1])).T)
    # return conts
    # conts=np.asarray(conts)
    i=0
    for l in lines:
        index=np.where((wl>=l[0]*(1+z)) & (wl<=l[1]*(1+z)))
        y=np.linspace(l[0]*(1+z),l[1]*(1+z),len(index[0]))
        if l==lines[0] and l[1]*(1+z)<=conts[0][0,0]:
            # print('a')
            wl[index]=y
            f[index]=np.interp(y,conts[0][:,0],conts[0][:,1])
            e[index]=np.interp(y,conts[0][:,0],conts[0][:,2])
            #e[index]=np.ones(len(index))*4e-3
            f[index]=np.random.normal(f[index],e[index])
        elif l==lines[-1] and l[0]*(1+z)>=conts[-1][-1,0]:
            # print('b')
            wl[index]=y
            f[index]=np.interp(y,conts[-1][:,0],conts[-1][:,1])
            e[index]=np.interp(y,conts[-1][:,0],conts[-1][:,2])
            #e[index]=np.ones(len(index))*13e-3
            f[index]=np.random.normal(f[index],e[index])
        else:
            # print('c')
            wl[index]=y
            cosa=np.vstack((conts[i],conts[i+1]))
            f[index]=np.interp(y,cosa[:,0],cosa[:,1])
            e[index]=np.interp(y,cosa[:,0],cosa[:,2])
            #e[index]=np.ones(len(index))*5e-3
            f[index]=np.random.normal(f[index],e[index])
            i+=1
    new_data=np.stack((wl,f,e),axis=1)
    return new_data

#==========================================================

def MJysr2uJypx(flux,ps):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Transforms image units MJy/sr to uJy/px
    ---------------------------------------------
    ARGS:
    flux:   array with flux values
    ps: pixel scale, in arcsec/px
    """
    #flux*1e6 Jy in flux MJy, 1e6 uJy in 1 Jy, 206265**2 arcsec**2 in 1 sr, ps**2 in arcsec**2/px
    c=flux*1e6*1e6*ps**2/206265**2
    return c

#==========================================================

def cube2SED(cube,mask=None,bins=None,Smask=None,name=None,wl=np.arange(6025,6025+941*50,50),save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    gets the SED (in uJy-wl_units) from a IFU cube (in MJy/sr-None)
    ---------------------------------------------
    ARGS:
    cube:   IFU cube. It can be either a fits file or the path to the file. Also, it is assumed that the cube data is stored in the second section? (id=1) and its associated error in the third (id=2) section
    ---------------------------------------------
    KWRGS:
    mask:   mask to apply to the cube. it must be either a path to a fits file or fits
    bins:   if mask is fits file containing several masks (of different regions), this must be a list of ints or strings of the shape 'i+j+...' in case several masks are wanted to be joined together. Additionally, it can be 'all', which will automatically take all binned masks in mask
    Smask:  secondary mask, to be applied before the mask, for whatever reason
    name:   name of the file/source. Used only when saving the SEDs
    wl: wavelength associated to each slice of the cube. It must be an array of same length as the number of slices
    save:   save the resulting SEDs in a directory called extracted_specs
    ----------------------------------------------
    """
    pp.close('all')
    if type(cube)==str:
        err=MJysr2uJypx(fits.open(cube)[2].data,0.08)
        cube=MJysr2uJypx(fits.open(cube)[1].data,0.08)
    elif type(cube)==astropy.io.fits.hdu.hdulist.HDUList:
        err=MJysr2uJypx(cube[2].data,0.08)
        cube=MJysr2uJypx(cube[1].data,0.08)
    else:
        TypeError('cube must eb either a fits or a path to a fits file!')
    if mask:
        if type(mask)==str:
            mask=fits.open(mask)
        else:
            mask=mask
    else:
        mask=1
    if Smask:
        if type(Smask)==str:
            Smask=fits.open(Smask)[1].data
        else:
            Smask=Smask[1].data
    else:
        Smask=1
    if bins:
        if bins=='all':
            bins=list(range(1,mask.info(0)[-1][0]+1))
        #return bins
        masks=[]
        cube_bin=[]
        specs=[]
        for b in bins:
            m=0
            if type(b)==str:
                b=b.split('+')
                for i in b:
                    m=m+mask[int(i)].data
            elif type(b)==int:
                m=mask[b].data
            masks.append(m)
        #for i in range(len(masks)):
            #pp.figure(i+1)
            #pp.imshow(masks[i])
        #pp.show(block=False)
        #return masks
            #print('c',cube,'cb',cube_bin[-1],'S',Smask,'m',masks[-1])
            cube_bin.append(cube*Smask*masks[-1])
            #print(cube.shape)
            wl=wl
            f=np.nansum(cube_bin[-1],axis=(1,2))
            e=np.sqrt(np.nansum((err*Smask*masks[-1])**2,axis=(1,2)))
            specs.append(np.asarray([wl,f,e]).T)
    elif not bins:
        if mask:
            mask=mask[1].data
        else:
            mask=1
        f=np.nansum(cube*Smask*mask,axis=(1,2))
        e=np.sqrt(np.nansum((err*Smask*mask)**2,axis=(1,2)))
        specs=np.asarray([wl,f,e]).T
    if save:
        sav='extracted_specs/'
        mkdirs(sav,fil=False)
        if name:
            sav=sav+name
        else:
            sav=sav+'unknown'
        if bins:
            for i in range(len(bins)):
                np.savetxt(sav+'_bin%s_spec.dat' % (str(bins[i])),specs[i])
    else:
        return specs

#==========================================================

def plot_all_masks_and_seds(ID,run,box=None,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Creates a pdf file including a figure that shows the mask of a region/source and its associated SEDs, including the best fit SED according to Bagpipes. Masks must be saved in a directored called BINS
    ---------------------------------------------
    ARGS:
    ID: source's ID
    run:    (bagpipes) run from which extract the SED
    The idea is to have a figure with bins on the left and SEDs on the right, and all bins in the same figure figure in different subplots
    ---------------------------------------------
    KWARGS:
    box:    list of parameters whose values will eb included in the SED plot, in a box. Default is none.
    show:   show the resulting figure
    save:   save the resulting figure in a directory called bins_and_seds as ID_run_all_bins_and_SEDs.pdf
    ---------------------------------------------
    """
    pp.close('all')

    #loading data
    paths=ns(glob.glob('*%s*/%s/*npy' % (ID,run)))
    l=len(paths)
    masks=ns(glob.glob('BINS/*%s*' % (ID)))
    masks=fits.open(masks[0])

    #creating the figure
    fig=pp.figure(figsize=(15,6*l))
    pp.suptitle('%s - %s' % (ID,run),fontsize=40)
    gs=GS(nrows=3*l,ncols=2,width_ratios=[1,1.5],height_ratios=[3,1,0.5]*l)
    bins=gs[:,0]
    seds=gs[:,1]
    for i in range(l):
        #bin
        b=fig.add_subplot(gs[3*i:3*(i+1),0])
        b.set_xticks([])
        b.set_yticks([])
        b.set_ylabel('BIN %i' % (i+1),fontsize=30)
        mask=masks[0].data/masks[0].data
        bini=masks[i+1].data
        mapa=mask*bini
        b.imshow(mapa,origin='lower')
        zoomin(mapa,b)
        #SED
        sed=LPdh.load_post(paths[i])
        wl=sed['wavelength_obs'][10:-5]
        fobs=sed['spectrum_obs'][10:-5]*wl**2*1e29/c
        eobs=sed['err_spectrum_obs'][10:-5]*wl**2*1e29/c
        ffit=np.nanmedian(sed['spectrum'],axis=0)[10:-5]*wl**2*1e29/c
        ufit=np.nanpercentile(sed['spectrum'],(84),axis=0)[10:-5]*wl**2*1e29/c
        lfit=np.nanpercentile(sed['spectrum'],(16),axis=0)[10:-5]*wl**2*1e29/c
        #top
        st=fig.add_subplot(gs[3*i,1])
        st.fill_between(wl*1e-4,fobs-eobs,fobs+eobs,color='lightgreen',linewidth=1,alpha=0.5)
        st.plot(wl*1e-4,fobs,color='g',ls='--',label='OBS')
        #st.fill_between(wl*1e-4,0,fobs,color='g',ls='--',label='OBS',step='mid',alpha=0.5)
        st.fill_between(wl*1e-4,lfit,ufit,color='lightcoral',linewidth=1,alpha=0.5)
        st.plot(wl*1e-4,ffit,c='r',ls='-',label='FIT')
        #st.fill_between(wl*1e-4,0,ffit,color='lightcoral',alpha=0.5,step='mid')
        if box:
            text,props=make_box(sed,box)
            st.text(0.01,0.9,text,fontsize=12,va="top",ha="left",bbox=props,transform=st.transAxes)
        st.set_ylabel(r'Flux ($\mathrm{\mu}$Jy)',fontsize=20)
        st.legend(loc='upper right')
        #bottom
        sedobs16=smooth_sed(np.stack((wl,fobs,eobs),axis=1),16)
        sedfit16=smooth_sed(np.stack((wl,ffit,(ufit+lfit)/2),axis=1),16)
        sb=fig.add_subplot(gs[3*i+1,1],sharex=st)
        sb.plot(sedobs16[:,0]*1e-4,sedobs16[:,1],c='g',ls='--',drawstyle='steps-mid')
        sb.fill_between(sedobs16[:,0]*1e-4,0,sedobs16[:,1],color='lightgreen',alpha=0.5,step='mid')
        #sb.plot(sedfit16[:,0]*1e-4,sedfit16[:,1],c='r',ls='-',drawstyle='steps-mid')
        #sb.fill_between(sedfit16[:,0]*1e-4,0,sedfit16[:,1],color='lightcoral',alpha=0.5,step='mid')
        sb.fill_between(wl*1e-4,lfit,ufit,color='lightcoral',linewidth=1,alpha=0.5)
        sb.plot(wl*1e-4,ffit,c='r',ls='-',label='FIT')
        rfwl=wl/(1+get_z(sed))
        if (sedobs16[:,0]/(1+get_z(sed))>6564.6).any():
            ind=np.where(sedobs16[:,0]/(1+get_z(sed))>6600)
            ulim=np.nanmax(sedobs16[ind,1])*1.2
        else:
            ind=np.where(sedobs16[:,0]/(1+get_z(sed))>5100)
            ulim=np.nanmax(sedobs16[ind,1])*1.2
        sb.set_ylim([-0.1*np.nanmedian(sedobs16),ulim])
        sb.yaxis.get_major_ticks()[-1].label1.set_visible(False)
        #Extras
        pp.subplots_adjust(hspace=0)
        if i==l-1:
            sb.set_xlabel(r'Wavelength ($\mathrm{\mu}$m)',fontsize=20)
    if show:
        pp.show(block=False)
    if save:
        mkdirs('bins_and_seds',fil=False)
        fig.savefig('%s_%s_all_bins_and_SEDs.pdf' % (ID,run))

#==========================================================

def compare_SEDs(ID,run1,run2,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Compares 2 SEDs from the same source but different fitting model. It shows boths models and observed SEDs on a top panel and their differences in the bottom panel
    ---------------------------------------------
    ARGS:
    ID: source's ID
    run1:   first model.
    run2:   second model.
    ---------------------------------------------
    KWARGS:
    show:   show the resulting figure
    save:   save the resulting figure as ID_SEDcomp_model1vsmodel2.pdf
    ---------------------------------------------
    """
    pp.close('all')
    path1=ns(glob.glob('*%s*/*%s*/*%s*.npy' % (ID,run1,run1)))[0]
    path2=ns(glob.glob('*%s*/*%s*/*%s*.npy' % (ID,run2,run2)))[0]
    # print('path1:'+path1+'\n')
    # print('path2:'+path2+'\n')
    c=2.99792458e18
    post1=LPdh.load_post(path1)
    wl1=post1['wavelength_obs'][10:-5]
    fobs1=post1['spectrum_obs'][10:-5]*wl1**2/c*1e29
    ffit1=np.nanmedian(post1['spectrum'],axis=0)[10:-5]*wl1**2/c*1e29
    post2=LPdh.load_post(path2)
    wl2=post2['wavelength_obs'][10:-5]
    fobs2=post2['spectrum_obs'][10:-5]*wl2**2/c*1e29
    ffit2=np.nanmedian(post2['spectrum'],axis=0)[10:-5]*wl2**2/c*1e29
    fig=pp.figure(figsize=(22,16))
    gs=GS(nrows=2,ncols=1,height_ratios=[3,2])
    #top plot, SEDs
    top=fig.add_subplot(gs[0])
    top.plot(wl1,fobs1,ls='--',c='k',label='Flux$_{\mathrm{Obs}}$')
    top.plot(wl1,ffit1,ls='-',c='r',label=r'Flux$_{\mathrm{Mod1: %s}}$' % (str2TeX(run1)))
    top.plot(wl2,ffit2,ls='-',c='g',label=r'Flux$_{\mathrm{Mod2: %s}}$' % (str2TeX(run2)))
    top.legend(fontsize=20)
    top.set_title(r'$\bf{%s}$' % (str2TeX(ID))+'\n Model 1: %s \nvs \nModel 2: %s' % (run1,run2),fontsize=30)
    top.set_ylabel(r'Flux ($\mathrm{\mu}$Jy)',fontsize=30)
    top.tick_params(axis='y',which='major',labelsize=20)
    #bottom plot, diffs
    bottom=fig.add_subplot(gs[1],sharex=top)
    bottom.axhline(0,ls='--',c='k')
    # bottom.plot(wl1,ffit1-ffit2,ls='-',c='b',label='%s - %s' % (run1,run2))
    # bottom.plot(wl1,ffit1-fobs1,ls='-',c='r',label='obs - %s' % (run1))
    # bottom.plot(wl2,ffit2-fobs2,ls='-',c='g',label='obs - %s' % (run2))
    bottom.plot(wl1,ffit1-ffit2,ls='-',c='b',label='Model diff')
    bottom.plot(wl1,ffit1-fobs1,ls='-',c='r',label='Obs - Mod1')
    bottom.plot(wl2,ffit2-fobs1,ls='-',c='g',label='Obs - Mod2')
    bottom.legend(fontsize=20)def RSEDvsISED(ID):
    pp.close('all')
    extract_spectra()
    specs=ns(glob.glob('extracted_specs/*%s*' % (ID)))
    wlb=[]
    fb=[]
    for s in specs:
        fb.append(np.loadtxt(s,usecols=(1)))
        wlb.append(np.loadtxt(s,usecols=(0)))
    fb=np.nansum(np.asarray(fb),axis=0)
    wlb=np.nanmedian(np.asarray(wlb),axis=0)
    # pp.plot(wlb,fb,c='g',label='bin sum')
    extract_spectra_int()
    spec=ns(glob.glob('extracted_specs/*%s*' % (ID)))[0]
    wli=np.loadtxt(spec,usecols=(0))
    fi=np.loadtxt(spec,usecols=(1))
    fig=pp.figure(1)
    ax1=fig.add_subplot(2,1,1)
    ax1.plot(wlb,fb,c='r',label='bins')
    ax1.plot(wli,fi,c='k',label='int')
    ax1.legend()
    ax2=fig.add_subplot(2,1,2)
    ax2.plot(wlb,fb-fi)
    print(np.nanmax(fb-fi),np.nanmin(fb-fi))
    pp.show(block=False)
    bottom.set_ylabel(r'$\mathrm{\Delta}$Flux ($\mathrm{\mu}$Jy)',fontsize=30)
    bottom.tick_params(axis='y',which='major',labelsize=20)
    bottom.set_xlabel(r'Wavelength ($\mathrm{\AA}$)',fontsize=30)
    bottom.tick_params(axis='x',which='major',labelsize=20)
    pp.subplots_adjust(hspace=0)
    if show:
        pp.show(block=False)
    if save:
        mkdirs('SEDcomps',fil=False)
        fig.savefig('SEDcomps/%s_SEDcomp_%svs%s.pdf' % (ID,run1,run2))

#----------------------------------------------------------

def RSEDvsISED(ID):
    pp.close('all')
    extract_spectra()
    specs=ns(glob.glob('extracted_specs/*%s*' % (ID)))
    wlb=[]
    fb=[]
    for s in specs:
        fb.append(np.loadtxt(s,usecols=(1)))
        wlb.append(np.loadtxt(s,usecols=(0)))
    fb=np.nansum(np.asarray(fb),axis=0)
    wlb=np.nanmedian(np.asarray(wlb),axis=0)
    # pp.plot(wlb,fb,c='g',label='bin sum')
    extract_spectra_int()
    spec=ns(glob.glob('extracted_specs/*%s*' % (ID)))[0]
    wli=np.loadtxt(spec,usecols=(0))
    fi=np.loadtxt(spec,usecols=(1))
    fig=pp.figure(1)
    ax1=fig.add_subplot(2,1,1)
    ax1.plot(wlb,fb,c='r',label='bins')
    ax1.plot(wli,fi,c='k',label='int')
    ax1.legend()
    ax2=fig.add_subplot(2,1,2)
    ax2.plot(wlb,fb-fi)
    print(np.nanmax(fb-fi),np.nanmin(fb-fi))
    pp.show(block=False)
