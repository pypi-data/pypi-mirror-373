#Functions work with magnitudes: work our fluxes, transform magnitudes to fluxes, calculate synthetic magnitudes, transform into luminosity, etc
#==========================================================
import numpy as np

from scipy.integrate import simpson,trapezoid
from scipy.stats import linregress as lr
from scipy.optimize import curve_fit as cf

from astropy.modeling import models,fitting
from astropy.cosmology import FlatLambdaCDM

import random as rd

from ..LazaUtils.get import get_index
import ..LazaPipes.data_handling as LPh
#==========================================================

def flux(band):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Works out the flux of a spectrum within a given range
    ---------------------------------------------
    ARGS:
    band: 2 column array with band range in the first column and flux density in the second column. Units must um and Jy, respectively.
    ---------------------------------------------
    """
    c=2.99792458e14 #um/s
    freq=np.flip(c/band[:,0])
    flux=np.flip(band[:,1]*1e-23)
    #F=cs(flux,x=freq,initial=0) #cummulative simpson
    F=simpson(flux,x=freq)
    #F=trapezoid(flux,freq)
    return F
    
#==========================================================

def cont(sed,ran):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Obtains the "linear" relation of a fv (flux_nu) SED, in a given range. It will ignore all lines included in the range
    ---------------------------------------------
    ARGS:
    sed:    spectra energy distribution. It must be an array of Nx3, with the first column the wavelength, second column the flux in Janskys and the thirs column its associated error
    ran:    range of the continuum whose relation will be obtained. Units must be same as the wavelength. It must be either a list or array with the lower and upper bounds
    ---------------------------------------------
    """
    if type(sed)!=np.ndarray:
        raise TypeError('sed must be an array!')
    elif sed.shape[1]<3:
        raise ValueError('sed must have a size of at least Nx3, with the first column the wavelength, the second the flux and the hird its error!')
    elif type(ran) not in [list,np.ndarray]:
        raise TypeError('ran must be either a list or array of 2 elements!')
    elif len(ran)!=2:
        raise ValueError('ren must be a list or array of 2 elements, lower and upper limit, respectively!')
    sed=sed[sed[:,0]>ran[0]] #keeping the data in the desired range
    sed=sed[sed[:,0]<ran[1]]
    check=sed[:,0]/sed[:,1]
    c_sed=[]
    for i in range(len(sed)):
        if abs(1-check[i]/np.nanmedian(check))<30:
            c_sed.append([sed[i,0],sed[i,1]])
    c_sed=np.asarray(c_sed)
    #return check
    def line(x,m,n):
        return m*x+n
    reg=lr(c_sed[:,0],c_sed[:,1])
    #reg2=cf(line,sed[:,0],sed[:,1])
    return reg[0],reg[1]#,reg[2],reg2 #slope, intercept

#==========================================================

def emli(sed,ran):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Obtains gaussian profile of a line in a given range
    ---------------------------------------------
    ARGS:
    sed:    spectra energy distribution. It must be an array of Nx3, with the first column the wavelength, second column the flux in erg s-1 cm-2 AA-1 and the thirs column its associated error
    ran:    range of the continuum whose relation will be obtained. Units must be same as the wavelength. It must be either a list or array with the lower and upper bounds
    ---------------------------------------------
    """
    if type(sed)!=np.ndarray:
        raise TypeError('sed must be an array!')
    elif sed.shape[1]<3:
        raise ValueError('sed must have a size of at least Nx3, with the first column the wavelength, the second the flux and the hird its error!')
    elif type(ran) not in [list,np.ndarray]:
        raise TypeError('ran must be either a list or array of 2 elements!')
    elif len(ran)!=2:
        raise ValueError('ren must be a list or array of 2 elements, lower and upper limit, respectively!')
    sed=sed[sed[:,0]>ran[0]] #keeping the data in the desired range
    sed=sed[sed[:,0]<ran[1]]
    def gauss(x,A,mu,sig):
        b=-(x-mu)**2/(2*sig**2)
        return A*np.exp(b)
    FWHM,m,p=fwhm(sed,ran)
    p0=(m,sed[p,0],FWHM/2/np.sqrt(2*np.log(2)))
    try:
        fit=cf(gauss,sed[:,0],sed[:,1],p0=p0)
        return fit[0]
    except RuntimeError:
        return p0

#------------------------------------------------

def fit_line(data):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Fit a single line. Returns the peak value, the associated wavenelngth (mu), the standard deviation (sigma), the slope of the continuum and its value at 0, in that order, and their errrors
    ---------------------------------------------
    ARGS:
    data: Nx2 array with wavelength in the first column and flux in the second. This data should include continuum and line emission only
    ---------------------------------------------
    """
    wl=data[:,0]
    f=data[:,1]
    ind1=np.where(f==np.nanmax(f))[0]
    mu=wl[ind1]
    peak=f[ind1]
    try:
        sig=wl[ind1+2]-wl[ind1-2]
    except IndexError:
        try:
            sig=wl[ind1+1]-wl[ind1-3]
        except IndexError:
            sig=wl[ind1]-wl[ind1-4]
    cont=models.Polynomial1D(1)
    g1=models.Gaussian1D(amplitude=peak,mean=mu,stddev=sig)
    g_total=g1+cont
    fit_g=fitting.LevMarLSQFitter()
    g=fit_g(g_total,wl,f,maxiter = 10000)
    x_g=np.linspace(np.nanmin(wl),np.nanmax(wl),1000)
    # pp.plot(wl,f,ls='-',c='k')
    # pp.plot(x_g,g(x_g),ls='--',c='r')
    # pp.show(block=False)
    fit_errs=np.sqrt(np.diag(fit_g.fit_info['param_cov']))
    #print(g.parameters[1])
    return g.parameters,fit_errs

#------------------------------------------------

def fit_2line(data,z):

    """
    ---------------------------------------------
    INSTRUCTIONS:
    Fit a double line. Returns the peak value, the associated wavenelngth (mu), the standard deviation (sigma) of both lines and the slope of the continuum and its value at 0, in that order, and their errors
    ---------------------------------------------
    ARGS:
    data: Nx2 array with wavelength in the first column and flux in the second. This data should include continuum and line emission only
    z:  redshift associated to the data
    ---------------------------------------------
    """
    wl=data[:,0]
    f=data[:,1]
    ind1=np.where(f==np.nanmax(f))[0]
    peak1=f[ind1]
    mu1=wl[ind1]
    sig1=wl[ind1+2]-wl[ind1-2]
    peak2=peak1/3
    mu2=mu1-48*(1+z)
    sig2=sig1/2
    #print(peak1,mu1,sig1,peak2,mu2,sig2)
    z=z
    #def tie_mean(model):
        #return model.mean_0 + 14*(1+z)
    #def tie_width(model):
        #return model.stddev_0
    cont=models.Polynomial1D(1)
    g1=models.Gaussian1D(amplitude=peak1,mean=mu1,stddev=sig1)
    g2=models.Gaussian1D(amplitude=peak2,mean=mu2,stddev=sig2)
    #g2.mean.tied=tie_mean
    #g2.stddev.tied=tie_width
    g_total=g1+g2+cont
    fit_g=fitting.LevMarLSQFitter()
    g=fit_g(g_total,wl,f,maxiter=1000)
    x_g=np.linspace(np.nanmin(wl),np.nanmax(wl),1000)
    # pp.plot(wl,f,ls='-',c='k')
    # pp.plot(x_g,g(x_g),ls='--',c='r')
    # pp.show(block=False)
    fit_errs=np.sqrt(np.diag(fit_g.fit_info['param_cov']))
    #print(g.parameters)
    return g.parameters,fit_errs

#==========================================================

def plot_lines(data,z,title=None,show=False,save=True):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Creates a figure with 4 panels, zooming in the [OII], Hb, [OIII] and Ha lines, showing the observed spectrum, its best fit, the Bagpipes fit spectrum and its best fit. Also, includes a table showing the flux and peack wavelenght of these 4 SEDs.
    ---------------------------------------------
    ARGS:
    data:   Nx2 array, including the SEDs data, being the first column wavelength (in AA) and the second flux (in ergs-1cm-2AA-1), or a string path to the post (npy) file containing the data.
    z:  sourceś redshift
    ---------------------------------------------
    KWARGS:
    title:  title to give to the figure
    show:   show the resulting figure
    save:   save the resulting figure as 'fit_title_lines_plots.pdf'
    ---------------------------------------------
    """
    pp.close('all')
    def gauss(x,A,mu,sig,m,c):
        B=-(x-mu)**2
        C=2*sig**2
        D=c*x+m
        return A*np.exp(B/C)+D
    def continuum(x,m,c):
        return c*x+m
    if type(data)==np.ndarray:
        WL=data[:,0]
        F=data[:,1]
    elif type(data)==str:
        d=LPdh.load_post(data)
        WL=d['wavelength_obs'][10:-5]
        F=d['spectrum_obs'][10:-5]
        Ffit=np.nanmedian(d['spectrum'],axis=0)[10:-5]
    elif type(data)==dict:
        WL=data['wavelength_obs'][10:-5]
        F=data['spectrum_obs'][10:-5]
        Ffit=np.nanmedian(data['spectrum'],axis=0)[10:-5]
    bands=['[OII]','Hb','[OIII]','Ha']
    fig=pp.figure(figsize=(24,19))
    pp.suptitle(title,fontsize=30)
    axs=[fig.add_subplot(3,2,i) for i in range(1,5)]
    Ind=[np.where((WL>3650*(1+z))*(WL<4800*(1+z))),np.where((WL>3870*(1+z))*(WL<4900*(1+z))),np.where((WL>4900*(1+z))*(WL<6500*(1+z))),np.where(WL>5200*(1+z))]
    mus_obs=[]
    mus_fit=[]
    fluxes_obs=[]
    fluxes_fit=[]
    diff=[]
    for i in range(4):
        if i!=2:
            if i==3 and z>7:
                axs[i].annotate('OUTSIDE PRISM RANGE',xy=(0.5,0.5),xycoords='axes fraction')
            else:
                data=np.stack((WL,F),axis=1)
                data=data[Ind[i]]
                dfit=np.stack((WL,Ffit),axis=1)
                dfit=dfit[Ind[i]]
                g,eg=fit_line(data)
                gf,egf=fit_line(dfit)
                ran=np.asarray(LVd.BANDS[bands[i]])*(1+z)
                ind=np.where((WL>=ran[0])*(WL<=ran[1]))
                fobs=F[ind]
                wlobs=WL[ind]
                fit=Ffit[ind]
                wl=WL[ind]
                flux1=trapezoid(gauss(wlobs,g[0],g[1],g[2],g[3],g[4])-continuum(wlobs,g[3],g[4]),wlobs)
                flux2=trapezoid(gauss(wl,gf[0],gf[1],gf[2],gf[3],gf[4])-continuum(wl,gf[3],gf[4]),wl)
                fluxobs=trapezoid(fobs-np.nanmean(continuum(wlobs,g[3],g[4])),wlobs)
                fluxfit=trapezoid(fit-np.nanmean(continuum(wl,gf[3],gf[4])),wl)
                wl=data[:,0]
                f=data[:,1]
                ffit=dfit[:,1]
                wl2=np.linspace(wl[0],wl[-1],1000)
                axs[i].plot(wl,f,ls='--',c='k',label='obs')
                axs[i].plot(wl2,gauss(wl2,g[0],g[1],g[2],g[3],g[4]),c='r',label='modelobs')
                axs[i].plot(wl2,continuum(wl2,g[3],g[4]),c='b',label='contobs')
                axs[i].plot(wl,ffit,ls='--',c='y',label='fit')
                axs[i].plot(wl2,gauss(wl2,gf[0],gf[1],gf[2],gf[3],gf[4]),c='violet',label='modelfit')
                axs[i].plot(wl2,continuum(wl2,gf[3],gf[4]),c='orange',label='contfit')
                axs[i].legend()
                axs[i].set_title(bands[i],fontsize=20)
                axs[i].set_xlabel(r'$\mathrm{\lambda}$ ($\mathrm{\AA}$)',fontsize=20)
                axs[i].set_ylabel(r'f$_{\mathrm{\lambda}}$ ($\mathrm{erg\ s^{-1}\ cm^{-2}\ \AA^{-1}}$)',fontsize=20)
                axs[i].set_xlim(ran)
                mus_fit.append(gf[1])
                mus_obs.append(g[1])
                fluxes_fit.append(flux2)
                fluxes_obs.append(flux1)
                diff.append(g[1]-gf[1])
        elif i==2:
            data=np.stack((WL,F),axis=1)
            data=data[Ind[i]]
            dfit=np.stack((WL,Ffit),axis=1)
            dfit=dfit[Ind[i]]
            g,eg=fit_2line(data,z)
            gf,egf=fit_2line(dfit,z)
            ran=np.asarray(LVd.BANDS[bands[i]])*(1+z)
            ind=np.where((WL>=ran[0])*(WL<=ran[1]))
            fobs=F[ind]
            wlobs=WL[ind]
            fit=Ffit[ind]
            wl=WL[ind]
            flux1a=trapezoid(gauss(wlobs,g[0],g[1],g[2],g[-2],g[-1])-continuum(wlobs,g[-2],g[-1]),wlobs)
            flux2a=trapezoid(gauss(wl,gf[0],gf[1],gf[2],gf[-2],gf[-1])-continuum(wl,gf[-2],gf[-1]),wl)
            flux1b=trapezoid(gauss(wlobs,g[3],g[4],g[5],g[-2],g[-1])-continuum(wlobs,g[-2],g[-1]),wlobs)
            flux2b=trapezoid(gauss(wl,gf[3],gf[4],gf[5],gf[-2],gf[-1])-continuum(wl,gf[-2],gf[-1]),wl)
            fluxobs=trapezoid(fobs-np.nanmean(continuum(wlobs,g[-2],g[-1])),wlobs)
            fluxfit=trapezoid(fit-np.nanmean(continuum(wl,gf[-2],gf[-1])),wl)
            wl=data[:,0]
            f=data[:,1]
            ffit=dfit[:,1]
            wl2=np.linspace(wl[0],wl[-1],1000)
            axs[i].plot(wl,f,ls='--',c='k',label='obs')
            axs[i].plot(wl2,gauss(wl2,g[0],g[1],g[2],g[-2],g[-1]),c='r',label='modelobs a')
            axs[i].plot(wl2,gauss(wl2,g[3],g[4],g[5],g[-2],g[-1]),c='g',label='modelobs b')
            axs[i].plot(wl2,continuum(wl2,g[-2],g[-1]),c='b',label='contobs')
            axs[i].plot(wl,ffit,ls='--',c='y',label='fit')
            axs[i].plot(wl2,gauss(wl2,gf[0],gf[1],gf[2],gf[-2],gf[-1]),c='violet',label='modelfit a')
            axs[i].plot(wl2,gauss(wl2,gf[3],gf[4],gf[5],gf[-2],gf[-1]),c='lightgreen',label='modelfit b')
            axs[i].plot(wl2,continuum(wl2,gf[-2],gf[-1]),c='lightblue',label='contfit')
            axs[i].legend()
            axs[i].set_title(bands[i],fontsize=20)
            axs[i].set_xlabel(r'$\mathrm{\lambda}$ ($\mathrm{\AA}$)',fontsize=20)
            axs[i].set_ylabel(r'f$_{\mathrm{\lambda}}$ ($\mathrm{erg\ s^{-1}\ cm^{-2}\ \AA^{-1}}$)',fontsize=20)
            axs[i].set_xlim(ran)
            mus_fit.append(gf[4])
            mus_fit.append(gf[1])
            mus_obs.append(g[4])
            mus_obs.append(g[1])
            diff.append(g[4]-gf[4])
            diff.append(g[1]-gf[1])
            fluxes_obs.append(flux1a)
            fluxes_obs.append(flux1b)
            fluxes_fit.append(flux2a)
            fluxes_fit.append(flux2b)
    mus_fit=np.asarray(mus_fit)
    mus_obs=np.asarray(mus_obs)
    fluxes_fit=np.asarray(fluxes_fit)
    fluxes_obs=np.asarray(fluxes_obs)
    diff=np.asarray(diff)
    means=np.array([np.nan,np.nan,np.nanmean(diff),np.nan,np.nan,np.nanmean(abs((fluxes_obs-fluxes_fit)/fluxes_obs))])
    res=np.stack((mus_obs,mus_fit,diff,fluxes_obs,fluxes_fit,(fluxes_obs-fluxes_fit)/fluxes_obs),axis=1)
    res=np.vstack((res,means))
    #Table summarising the results
    cols=['y_obs (A)','y_fit (A)','y_diff (A)','f_obs','f_fit','f_diff/f_obs']
    rows=['[OII]','Hb','[OIII]4960','[OIII]5008','Ha','Averages']
    cell_text=[]
    a=['%.5g' % (i) for i in res.flatten()]
    a=np.asarray(a)
    cell_text=a.reshape(res.shape)
    tabax=fig.add_subplot(3,1,3)
    the_table=tabax.table(cellText=cell_text,rowLabels=rows,colLabels=cols,loc='center',fontsize=20)
    tabax.axis('off')
    the_table.scale(1,3)
    # pp.tight_layout
    if show:
        pp.show(block=False)
    if save:
        fig.savefig('fit_%s_lines_plots.pdf' % (title))

#==========================================================

def fwhm(sed,ran):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Estimates the fwhm of a gaussian profile. It's quite orthodox and should be taken with a grain of salt, as it is meant to be used as a prior value during a fitting
    ---------------------------------------------
    ARGS:
    sed:    spectra energy distribution. It must be an array of Nx3, with the first column the wavelength, second column the flux in erg s-1 cm-2 AA-1 and the thirs column its associated error
    ran:    range of the continuum whose relation will be obtained. Units must be same as the wavelength. It must be either a list or array with the lower and upper bounds
    ---------------------------------------------
    """
    sed=sed[sed[:,0]>ran[0]] #keeping the data in the desired range
    sed=sed[sed[:,0]<ran[1]]
    m=np.nanmax(sed[:,1])
    n=np.nanmin(sed[:,1])
    if n<0:
    	n=0
    p=np.where(sed[:,1]==m)[0][0]
    l=p
    while sed[l,1]-n>(m-n)/2:
        l-=1
    r=p
    while sed[r,1]-n>(m-n)/2:
        r+=1
    #print(l,p,r)
    fwhm=np.interp(m/2,np.flip(sed[p:r,1]),np.flip(sed[p:r,0]))-np.interp(m/2,sed[l:p,1],sed[l:p,0])
    return fwhm,m,p

#==========================================================

def line_flux(sed,ran):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    works out the flux (integrates) of a given line plus associated continuum. For more information, see cont and emli
    ---------------------------------------------
    ARGS:
    sed:    spectra energy distribution. It must be an array of Nx3, with the first column the wavelength, second column the flux in erg s-1 cm-2 AA-1 and the thirs column its associated error
    ran:    range of the continuum whose relation will be obtained. Units must be same as the wavelength. It must be either a list or array with the lower and upper bounds
    ---------------------------------------------
    """
    sed=sed[sed[:,0]>ran[0]] #keeping the data in the desired range
    sed=sed[sed[:,0]<ran[1]]
    m,n=cont(sed,ran)
    c=m*sed[:,0]+n
    g=emli(sed,ran)
    l=g[0]*np.exp(-(sed[:,0]-g[1])**2/(2*g[2]**2))
    f_l=simpson(l,x=sed[:,0]) #line flux
    f_c=simpson(c,x=sed[:,0]) #continuum flux
    fwfm=(sed[:,0]>=g[1]-5*g[2])*(sed[:,0]<=g[1]+5*g[2])
    c2=c[fwfm]
    #print(g[1],g[2])
    f_c2=simpson(c2,x=sed[fwfm][:,0]) #continuum flux in the mu+-5sig region
    return f_l,f_c,f_c2

#==========================================================

def f2Lum(f,z,cosmo='FLCDM'):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Transforms flux (in erg s-1 cm-2) into luminosity (in erg s-1)
    ---------------------------------------------
    ARGS:
    f:  flux to transform. It can be either a number, a list or an array
    z:  redshift of the object. It must have the same length as f
    ---------------------------------------------
    KWARGS:
    cosmo:  cosmology to be used. Default is 'FLCDM', which refers to flat lambda Cold Dark Matter, and uses the FlatLambdaCDM astropy.cosmology function wth values H0=70 and Om0=0.3. Any other astropy.cosmology can be given, however they must eb created outside this function.
    ---------------------------------------------
    """
    import abc #just importing for the data type
    if cosmo=='FLCDM': #Flat lambda Cold Dark Matter model (FRLW)
        cosmo=FlatLambdaCDM(H0=70., Om0=0.3)
        DL=cosmo.luminosity_distance(z).value*1e3
    else: #any other model given by the user but coming from astropy
        try:
            DL=cosmo.luminosity_distance(z).value*1e3
        except AttributeError:
            raise ValueError('cosmo must be either the default value "FLCDM" (H0=70, Om0=0.3) or another cosmology model taken from astropy.cosmology!')
    if type(f) in [int,float,np.float64]:
        f=np.asarray([f])
    elif type(f)==list:
        f=np.asarray(f)
    elif type(f)!=np.ndarray:
        raise TypeError('f must be a number, list or array!')
    if type(z) in [int,float,np.float64]:
        z=np.asarray([z])
    elif type(z)==list:
        z=np.asarray(z)
    elif type(z)!=np.ndarray:
        raise TypeError('z must be a number, list or array!')
    kpc2cm=3.08567758128e+21 #kpc to cm conversion
    L=4*np.pi*(DL*kpc2cm)**2*f
    return L
    
#==========================================================

def Lum2SFR(L,band):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Obtains the star formation rate (SFR) from luminosity based on Kennicutt+12 conversions
    ---------------------------------------------
    ARGS:
    L:	luminosity in erg s-1
    band:	band, according to Table 1 in Kennicutt+12
    --------------------------------------------
    """
    Tab1={'FUV':43.35,'NUV':43.17,'Halpha':41.27,'TIR':43.41,'24um':42.69,'70um':43.23,'1.4GHz':28.20,'2-10keV':39.77}
    try:
        logCx=Tab1[band]
    except KeyError:
        print('Band must be: ',Tab1.keys())
        return
    logSFR=np.log10(L)-logCx
    return 10**logSFR

#==========================================================

def m2f(mag,prefix=1e-6):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Transforms magnitude into flux, in Jy
    ---------------------------------------------
    ARGS:
    mag: magnitude
    ---------------------------------------------
    KWARGS:
    prefix:	resulting flux prefix, i.e. mJy, uJy, nJy, etc.
    ---------------------------------------------
    """
    #prefix=prefijo de la unidad de Jy (ej.: mJy=1e-3, uJy=1e-6,etc), para que la referencia tenga la misma unidad
    #asumimos que trabajamos en uJy y en el sistema AB
    fref=3631/prefix
    mref=2.5*np.log10(fref)
    return 10**(-0.4*(mag-mref))

#==========================================================

def synth_mag(spec,filt,mock=1e3,wlunit='um',funit='Jy',mean=False,cont=False,fact=0.02,mean_cont=None): #los inputs serán el filtro el especteo donde queremos calcular la magnitud sintetica y el filtro cuya magnitud queremos calcular
    """
    --------------------------------------------
    INSTRUCTIONS
    works out the synthetic magnitude (the supposedly photometric magnitude) from a spectrum for a given band/filter.
    This is done by generating a (large) number of mock spectra from the original spectrum (each data point will have a gaussian distirbution centered at the flux and standard deviation equal to its error), and from each of them a magnitude is calculated. These magnitudes are calculated using Eq. A2 from Maíz-Apelláinz 06.
    Finally, all magnitudes put together as a distribution, whose median and percentiles 16 and 84 will be the synthetic magnitude and its associated errors
    --------------------------------------------
    ARGS:
    spec:   array with 3 columns containing the wavelength, flux and flux error of the spectrum
    filt:   array with 2 columns containing the wavelength and associated transmission of the filter
    ---------------------------------------------
    KWARGS:
    mock:   number of mock spectra generated to work out the synthetic magnitude distirbution
    funit:   flux units. It can be either 'Jy' (1e-23 erg s-1 cm-2 Hz-1) or 'ergscmA' (erg s-1 cm-2 A-1). Default is 'Jy'
    wlunit: wavelength units. It can be either meter related ('mm', 'um', etc) or amstrong ('AA')
    mean:   returns the mean and standard deviation of the gaussian distribution associated to the magnitude distribution. Default is False. If True, these values will be returned together with the emdian and percentiles
    cont:   if the synthetic magnitude calculated belongs to a continuum, this should be set to True so possible emission lines are ignored during the process.
    fact:   limit factor for emission lines to be removed if a continuum sythetic amgnited is worked out. Default is 2%, i.e. values above de 1.02*cont_median will be removed (considered emission lines)
    mean_cont:  median value of the continuum. Default is 'None', and if left as is, the mean value will be worked out if 'cont' is True. If given a value, it will be used as mean value of the continuum
    ------------------------------------------------------
    """
    #spec debe tener  columnas: wl, flux y eflux
    wls=spec[:,0] #debe tener unidades de wlprefix*m (auto: micŕometros - um 1e-6)
    flux=spec[:,1]
    eflux=spec[:,2]
    #filt debe tener 2 columnas: wl, trans
    wlf=filt[:,0] #debe tener unidades de wlprefix*m (auto: micŕometros - um 1e-6)
    trans=filt[:,1]
    #------------------------------------------------------
    wlprefix=get_index(wlunit)[0]
    uprefix=get_index(funit)[0]
    #------------------------------------------------------
    #fref=3631/uprefix #prefixJy #flujo de referencia, constante en sistema AB y de valor 3631 Jy (tenemos que ajustarlo a nuestro caso)
    ZP=0 #punto 0 en el sistema AB
    c=2.99792458e8/wlprefix #vel luz en prefix*metros por segundo
    #------------------------------------------------------
    #Puesto es harto problable que el espectro sea mayor que el rango del filtro, podemos reescribir el espectro de modo que solo incluya puntos en el rango del filtro, así nos ahorramos cuentas
    if np.nanmin(wls)<np.nanmin(wlf):
        menor=np.where(wls<np.nanmin(wlf)) #eliminamos esos puntos por debajo de la menor longitud de onda
        wls=np.delete(wls,menor)
        flux=np.delete(flux,menor)
        eflux=np.delete(eflux,menor)
    elif np.nanmin(wlf)<np.nanmin(wls): #si ocurre al revés, acortamos el rango del filtro
        menor=np.where(wlf<np.nanmin(wls))
        wlf=np.delete(wlf,menor)
        trans=np.delete(trans,menor)
    #Y repetimos este mismo proceso pero con el maximo de longitud de onda
    if np.nanmax(wls)>np.nanmax(wlf):
        mayor=np.where(wls>np.nanmax(wlf))
        wls=np.delete(wls,mayor)
        flux=np.delete(flux,mayor)
        eflux=np.delete(eflux,mayor)
    elif np.nanmax(wlf)>np.nanmax(wls):
        mayor=np.where(wlf>np.nanmax(wls))
        wlf=np.delete(wlf,mayor)
        trans=np.delete(trans,mayor)
    if cont and mean_cont:
        flux=mean_cont*c/wls**2
    elif cont:
        fv=flux*wls**2/c
        mean_cont=np.nanmedian(fv) #calculamos la mediana del continuo en f_NU (si lo hacemos en f_lambda, no queda plano y pasan weas)
        fact=fact #porcentaje por encima de la mediana que nos quedamos #2% porque sí
        flux[np.where(fv>mean_cont*(1+fact))]=mean_cont*(1+fact/2)/(wls[np.where(fv>mean_cont*(1+fact))]**2/c) #cambiamos esos valores que son superiores por el valor de la mediana
    #Lo primero será poner el flujo en unidades correctas, esto es, en f_lambda
    if funit=='Jy' or funit=='jy':
        flux=(c/wls**2)*flux
        eflux=(c/wls**2)*eflux
        fref=3631/uprefix #prefixJy #flujo de referencia, constante en sistema AB y de valor 3631 Jy (tenemos que ajustarlo a nuestro caso)
        new_fref=(c/wls**2)*fref #flujo de referencia, en unidades de f_lambda, en el rango últil de longitudes de onda
    elif funit=='ergscmA' or funit=='ergscma': #SI TENEMOS ESTA UNIDAD, UPREFIX DEBE SER 1E23
        uprefix=1e23
        fref=3631/uprefix #prefixJy #flujo de referencia, constante en sistema AB y de valor 3631 Jy (tenemos que ajustarlo a nuestro caso)
        new_fref=(c/wls**2)*fref #flujo de referencia, en unidades de f_lambda, en el rango últil de longitudes de onda
    else:
        return print('ERROR: spectral units must be either Jy or 10**-23 erg s**-1 cm**-2 A**-1')
    #necesitamos que ambos tengan la misma longitud y, además, coincidan los mismos puntos de wl creo que habia que usar la funcion np.interpolate, pero no recuerdo los inputs
    new_trans=np.interp(wls,wlf,trans) #hacemos una interpolación para que la cantidad de puntos de de la curva de transmisión coincida con la de puntos del espectro
    #new_fref=(c/wls**2)*fref #flujo de referencia, en unidades de f_lambda, en el rango últil de longitudes de onda
    #Hecho esto, pasamos a crear una gran cantidad de espectros falsos, a los que calcular la magnitud sintentica:
    msynth=[] #lista donde guardsr las magnitudes sinteticas que obtengamos de los falsos espectros
    for i in range(int(mock)):
    #se podra aplicar la funcion gauss a todo un array, o debo ir 1 por 1?
        mspec=[] #lista donde almacenaremos el falso espectro
        for j in range(len(wls)):
            mspec.append([wls[j],rd.gauss(mu=flux[j],sigma=eflux[j])]) #añadimos la wl y un valor aleatorio gaussiano del espectro, basado en el valor obtenido (mu) y su error (sigma)
        mspec=np.asarray(mspec) #convertimos la lista en array
        #print(new_trans,mspec,wls)
        It=trapezoid(new_trans*mspec[:,1]*wls) #integral de arriba (top)
        Ib=trapezoid(new_trans*new_fref*wls) #hay que redefinir fref, no me acuerdo bien de como era #integral de abajo (bottom)
        m=-2.5*np.log10(It/Ib)+ZP
        msynth.append(m)
    msynth=np.asarray(msynth)#convertimos la lista resultante en array
    #Una vez tengamos una gran cantidsd de magnitudes sintenticas, las dividimos en bins pequeños (orden de la centesima), y calculamos la mediana y su desviacion media
    #no recuerdo bien los comando pa esto
    #Alternativamente, podemos calcular usando percentile/median, mi nueva funcion favorita:
    msynth1=np.percentile(msynth,(50))
    msynth2=np.mean(msynth) #no sw si era mean; si mal no recuerdo en gauss coinciden
    #print(msynth1==msynth2) #pa comprobar si son iguales o no jajaja
    merru=np.percentile(msynth,84)-msynth1 #1sigma para eo 84
    merrl=msynth1-np.percentile(msynth,16) #1sigma para el 16; deberia ser igual o muy parecido al de 84
    merr=np.std(msynth) #alternativamente, podemos seguir usando otros comandos de numpy
    #finalmente, devolvemos la magnitud sintetica obtenida y su error
    if mean:
        return (msynth1,merru,merrl,msynth2,merr) #devolvemos todo lo calculado, al menos de momento que hacemos pruebas
    else:
        return (msynth1,merru,merrl)
