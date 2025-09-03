#Multi-purpose functions, useful for many things outside BagPipes or posterior files handling
#==========================================================

import numpy as np

import os

from astropy.io import fits
from astropy.wcs import WCS
from astropy import units as u
from astropy.coordinates import SkyCoord as SC

from scipy.integrate import trapezoid

from ..LazaVars.dics import lat_labels

from string import ascii_lowercase as abc

#==========================================================
#Redefining scales
#----------------------------------------------------------
def log_bins(i,f,n_bins):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Creates a log10 equally spaced list of values between 2 given limits. Equal spacing in an logarithmic scale means that the will have the same length in such scale (will look linear in the log space).
    The equation is:
    log10(bin_(i+1))-log10(bin_i)=step ---> bin_(i+1)=10**(step+log10(bin_i))
    ---------------------------------------------
    ARGS:
    i:  initial point
    f:  final point
    n_bins: number of bins (values) in the list, including initial and the final values
    ---------------------------------------------
    """
    if type(n_bins)!=int:
        raise TypeError('n_bins must be a integer!')
    log_step=(np.log10(f)-np.log10(i))/(n_bins-1)
    bins=[i] #incluimos el primer borde del bin
    for bi in range(n_bins-1):
        if bi==n_bins:
            bins.append(10**(np.log10(f)-log_step))	#bin final
        else:
            bins.append(10**(log_step+np.log10(bins[-1]))) #resto de bins
    return bins

#==========================================================
#Handling directories
#----------------------------------------------------------

def mkdirs(path,fil=True):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Creates the directories in the given path to save a file
    ---------------------------------------------
    ARGS:
    path:   where to save the file
    ---------------------------------------------
    KWARGS:
    fil:    states if the file is included in the path. Default is True
    ---------------------------------------------
    """
    if type(path)!=str:
        raise TypeError('path must be a string stating the savepath!')
    dirs=path.split('/')
    path=''
    if fil:
        for d in dirs[:-1]:
            path=os.path.join(path,d)
            if not os.path.exists(path):
                os.mkdir(path)
    elif not fil:
        for d in dirs:
            path=os.path.join(path,d)
            if not os.path.exists(path):
                os.mkdir(path)

#==========================================================
#Write structures inside files
#----------------------------------------------------------

def divisor(fil,c='=',l=60):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Adds a commented divisor line, ass seen in this file.
    ---------------------------------------------
    ARGS:
    fil:    open file in which to add the divisor
    ---------------------------------------------
    KWARGS:
    c:  character to use as the divisor. Default is '=' (equal sign)
    l:  length of the divisor. Default is 60
    ---------------------------------------------
    """
    if type(c)!=str or type(l)!=int:
        raise TypeError('c (character) must be a string and l (length) must be an integer!')
    fil.write('\n')
    fil.write('#')
    for i in range(l):
        fil.write(c)
    fil.write('\n')
    fil.write('\n')
    
#----------------------------------------------------------

def choose_var(var):
    if type(var)!=str:
        print('var must be a string!\n')
        return
    try:
        var=lat_labels[var]
        return var
    except KeyError:
        return var

def str2TeX(string):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Transforms input stirngs into TeX strings
    ---------------------------------------------
    ARGS:
    string: string to transform in something that TeX can interpret
    ---------------------------------------------
    """
    a=string.split('_')
    if len(a)==1:
        b=a
    else:
        b='\_'.join(a)

    c=b.split('-')
    if len(c)==1:
        d=b
    else:
        d='\\text{-}'.join(c)
    return d

#----------------------------------------------------------

def print_errs(val,u,l):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Returns float values according to the significant figures rules, this is, transforms 1.23 into 1.2, 4.56 into 4.5, 0.00004456 into 0.00004, etc. It returns the value plus its upper and lower errors.
    Not that this function RETURNS FLOATS, and the ideal course of action is formating these values using %g, usually like '%g$^{+%g}_{-%g}$' % (print_errs(val,u,l))
    ---------------------------------------------
    ARGS:
    val:    parameter value
    u:  parameter upper error
    l:  parameter lower error
    ---------------------------------------------
    """
    uf=np.floor(abs(val)/u)*10
    lf=np.floor(abs(val)/l)*10
    e=np.nanmin([u,l])
    if e<1:
        ep=np.ceil(np.log10(abs(1/e))) #power
        ef=10**np.ceil(np.log10(abs(1/e))) #factor
        val=np.round(val*ef)/ef
        u=np.round(u*ef)/ef
        l=np.round(l*ef)/ef
    else:
        val=np.round(val)
        u=np.round(u)
        l=np.round(l)
    return val,u,l

#==========================================================
#Modify and work with 2D images (or 2D slices of 3D cubes)
#----------------------------------------------------------

def rebin(data,ps1,ps2,cval=np.nan,Pi=0,Qi=0,Pf=np.nan,Qf=np.nan):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Rebins a 2D image, changing the pixel size, using interpolation
    ---------------------------------------------
    ARGS:
    data:   2D array, containing the image data
    ps1:    original pixel scale, in arcsec/px
    ps2:    new pixel scale, in arcsec/px
    ---------------------------------------------
    cval:   value into which inputed nan values will be transformed. Default is nan
    Pi: initial pixel in the X-axis from which the rebinning will start
    Qi: initial pixel in the Y-axis from which the ribinning will start
    ---------------------------------------------
    """
    A=np.copy(data)
    nanval=1234e-20 #valor con el que sustituir los píxeles nan
    A[np.isnan(A)==True]=nanval #converitmos valores nan en 0
    if len(A.shape)!=2: #comprobamos que tenemos datos en 2D
        print('INPUT DATA MUST BE 2-DIMENSIONAL!!!')
        return
    p1x=data.shape[0] #píxeles en el eje horizontal
    p1y=data.shape[1] #píxeles en el eje vertical
    f=ps2/ps1 #factor de escalas de píxeles, o factor de rebineado
    p2x=int(np.floor((p1x-Pi)/f)) #píxeles rebineados en el eje horizontal
    p2y=int(np.floor((p1y-Qi)/f)) #píxeles rebineados en el eje vertical
    B=np.zeros([p2x,p2y]) #Nuevo array con dimensiones reescaladas
    nanmask2=np.zeros([p2x,p2y])
    x2=np.linspace(0,p1x-1,p2x)
    y2=np.linspace(0,p1y-1,p2y)
    x1=np.linspace(0,p1x-1,p1x)
    y1=np.linspace(0,p1y-1,p1y)
    coords=(x1,y1)
    x,y=np.meshgrid(x1,y1)
    values=A
    #print(x2,p2x)
    for i in range(p2x):
        for j in range(p2y):
            point=np.array([x2[i],y2[j]])
            B[i,j]=i2d(coords,values,point)#*f**2
            #print(point,i,j)
    B=B*np.sum(A)/np.sum(B) #renormalizamos para tener la misma cantidad de flujo en la nuev ay en la vieja imagen
    B[(B<=1e2*nanval)*(B>0)]=cval #Reconvertimos los 0 en cval (nan)
    return B

#----------------------------------------------------------

def SNR_enforcer(data,snr,bgval=0):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Forces a total SNR to a 2D image or the slices of a 3D cube. This function is meant for objects, this is, it is assumed as mask for the object inside the image is used before applying this function
    ---------------------------------------------
    ARGS:
    data:   2D image or 3D cube composed of 2D image slices
    snr:    total SNR for the image(s) to have
    ---------------------------------------------
    bgval:  background value (mask value)
    ---------------------------------------------
    """
    gal_n=[] #array donde colocar el sigma_n obtenido
    if len(data.shape)==3: #cubo de datos
        for wl in data: #vamos frame por frame
            sli=np.copy(wl)
            sli[sli==bgval]=np.nan #convertimos en nan aquellos valores calificados como 'fondo'
            P=sli.shape[0]*sli.shape[1]-len(np.where(np.isnan(sli)==True)[0]) #número de píxeles que conforman el objeto (todos los píxeles que no son bgval)
            S=np.nansum(sli) #flujo total del obejto
            sigma=S/(snr*np.sqrt(P))
            gal_n.append(sigma)
    elif len(data.shape)==2: #1 sola imagen
        sli=np.copy(data)
        sli[sli==bgval]=np.nan #convertimos en nan aquellos valores calificados como 'fondo'
        P=sli.shape[0]*sli.shape[1]-len(np.where(np.isnan(sli)==True)[0]) #número de píxeles que conforman el objeto (todos los píxeles que no son bgval)
        S=np.nansum(sli) #flujo total del obejto
        sigma=S/(snr*np.sqrt(P))
        gal_n.append(sigma)
    else:
        raise ValueError('Input data must be either 2- or 3-dimensional!')
    gal_n=np.array(gal_n) # y al terminar, la convertimos en array
    return gal_n

#----------------------------------------------------------

def contours(cube,noise,snr_conts,title='',bins=10):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Calculates SNR contours of an image (2D or 3D) and returns the flux recovery fraction in a distirbution plot
    ---------------------------------------------
    ARGS:
    cube:   3D cube or 2D slice containing the image flux data
    noise:  3D cube or 2 D slice containing the associated noise of the image noise data. It must have the same shape and size than noise
    snr_conts:  number fo contours to calculate in each slice
    ---------------------------------------------
    KWARGS:
    title:  title of the distribution plot
    bins:   number of bins in the distirbution plot
    ----------------------------------------------
    """
    flux_frac=[] #lista donde pondremos las fracciones de flujo para todos los contornos de snr itroducidos
    cube_len=cube.shape[0]
    for i in range(cube_len):
        sli=np.copy(cube[i])
        n=np.copy(noise[i])
        frac=[]
        for snr in snr_conts:
            snr_frac=sli[sli/n>=snr] #píxeles con snr mayor que el contorno dado
            snr_flux=np.nansum(snr_frac) #flujo total de tales píxeles
            sli_flux=np.nansum(sli) #flujo total del frame
            frac.append(snr_flux/sli_flux) #fracción del flujo de snr respecto al flujo total
        flux_frac.append(frac) #cada set de fracciones de flujo es guardada en la lista
    flux_frac=np.asarray(flux_frac) #que convertimos en array
    #Representación gráfica
    pp.figure()
    pp.xlabel(r'$\mathrm{\lambda} (\mathrm{\mu}$m)') #eje x con wl en um
    pp.ylabel('Percentage (%)') #eje y con porcentaje de recuperación
    if not title=='title': #en caso de que se haya dado algún título a la figura, se usa tal título
        pp.title(title)
    wl=np.linspace(0,cube.shape[0]-1,cube.shape[0])*0.005+0.6 # eje x, longitudes de onda en um
    color=iter(cm.rainbow(np.linspace(0,1,len(snr_conts)+1))) #colores pa la gráfica
    snr=iter(snr_conts)
    for per in flux_frac.T: #trasponemos para tener tantas filas como contornos y tantas columnas como frames(wl)
        pp.plot(wl,per,c=next(color),ls='-',label='SNR=%.1f' % (next(snr)))
    pp.legend()
    pp.xticks(np.linspace(wl[0],wl[-1],11))
    pp.yticks(np.linspace(0,1,11))
    pp.ylim([-0.1,1.1])
    pp.grid()
    color=iter(cm.turbo(np.linspace(0,1,len(snr_conts)+1))) #colores pa la gráfica
    #cálculo de los puntos (bins) de medianas para mostra run comportamiento más claro
    for per in flux_frac.T: #volvemos a ir fracción por fracción
        wl=np.linspace(0,cube.shape[0]-1,cube.shape[0])*0.005+0.6 #longitud de onda
        medians=[] #lista donde guardar als medianas de fraccioens de flujo
        med_wl=[] #lista donde guardar las medianas de wl
        while len(per)>bins: #corremos el bucle de hasta que hayamos pasado por todos los puntos
            medians.append(np.nanmedian(per[:bins+1]))
            med_wl.append(np.nanmedian(wl[:bins+1]))
            per=per[bins+1:]
            wl=wl[bins+1:]
        medians.append(np.nanmedian(per)) #y añadimos el punto final con los valores extras cuyo número era menor que un bin
        med_wl.append(np.nanmedian(wl[-len(per)-1:]))
        pp.plot(med_wl,medians,marker='.',markersize=6,c='k',ls='--') #los incluimos en la gráfica
    return flux_frac #devolvemos el array con fracciones de flujo apra los SNR dados

#----------------------------------------------------------

def pix2hmsdms(pixels,wcs):
    """
    -------------------------------------------------------
    INSTRUCTIONS:
    Transforms pixel positions into sky coordinates, in the h:m:s,d:m:s format
    -------------------------------------------------------
    ARGS:
    pixels: array of Nx2 with X and Y pixel coords
    wcs:    World Coordinate System to transform the pixels
    -------------------------------------------------------
    """
    w=wcs.wcs_pix2world(pixels,0)
    sc=SC(ra=w[:,0]*u.degree,dec=w[:,1]*u.degree,frame='icrs')
    hd=sc.to_string('decimal',precision=10)
    hd_list=[]
    for i in range(len(hd)):
        hd_list.append(hd[i].split(' '))
    hd_arr=np.asarray(hd_list)
    hd_list=[]
    for i in range(len(hd_arr)):
        ra=float(hd_arr[i,0])/15
        hh=np.floor(ra)
        mm=(ra-hh)*60
        ss=np.round((mm-np.floor(mm))*60,2)
        ra=str(int(hh))+r'$^{\mathrm{h}}$'+str(int(np.floor(mm)))+r"$^{\mathrm{m}}$"+str(ss)+r'$^{\mathrm{s}}$'
        print(hh,mm,ss,ra)
        dec=abs(float(hd_arr[i,1]))
        dd=np.floor(dec)
        mm=(dec-dd)*60
        ss=np.round((mm-np.floor(mm))*60,2)
        if hd_arr[i,1][0]=='-':
            dec='-'+str(int(dd))+'º'+str(int(np.floor(mm)))+"'"+str(ss)+'"'
        else:
            dec='+'+str(int(dd))+'º'+str(int(np.floor(mm)))+"'"+str(ss)+'"'
        hd_list.append([ra,dec])
    hd_arr=np.asarray(hd_list)
    return hd_arr

#----------------------------------------------------------

def centroid(xy):
    """
    INSTRUCTIONS
    ---------------------------------------------
    Calculates de coordiantes of the centroid (geometrical wieghted center) of a given set of coordinates
    ---------------------------------------------
    ARGS:
    xy: Nx2 array, containing the x and y coordinates
    ---------------------------------------------
    """
    x=xy[:,0]
    y=xy[:,1]
    cen=np.inf
    for i in range(len(x)):
        dist=[]
        for j in range(len(x)):
            d=np.sqrt((x[i]-x[j])**2+(y[i]-y[j])**2)
            dist.append(d)
        dist=np.asarray(dist)
        c=np.nansum(dist)
        if c<cen:
            cen=c
            cxy=[x[i],y[i]]
    return cxy
    
#----------------------------------------------------------

def aislar(mask,minpix=4,save_fits=False):
    """
    -------------------------------------------------------
    INSTRUCTIONS:
    Given a mask of 0s and 1s, with distinct regions separated by at least 1 diagonal pixel, this functions creates separate masks for each fo the regions.
    -------------------------------------------------------
    ARGS:
    mask:   2D array of 0s and 1s
    -------------------------------------------------------
    minpix: minimum number of pixels in a mask to be considered an object and not a a bad detection. Default is 4
    save_fits:  save the resulting masks in a FITS file. If True, masks will be saved as 'New_mask_n.fits', where n is a,b,c,etc.. If a string is given, it will be saved as 'string_n.fits', where n is a,b,c,etc..
    -------------------------------------------------------
    """
    structure=np.array([[0,1,0],[1,1,1],[0,1,0]])
    lab,nlab=label(mask*5,structure) #multiplicamos por 5 ya que si todo es 1 y 0 da error xd
    masks=[]
    for i in range(nlab):
        clab=np.copy(lab)
        clab[clab!=(i+1)]=0
        clab[clab!=0]=1
        if np.nansum(clab)>minpix:
            masks.append(clab)
    if save_fits:
        if type(save_fits)==bool:
            for i in range(len(masks)):
                hdu=fits.PrimaryHDU(np.zeros(1))
                hdum=fits.ImageHDU(masks[i],name='MASK')
                hdul=fits.HDUList([hdu,hdum])
                #hdul.writeto('New_mask_%s.fits' % (abc[i]), overwrite=True)
                if len(masks)>1:
                    hdul.writeto('New_mask_%s.fits' % (abc[i]), overwrite=True)
                else:
                    hdul.writeto('New_mask.fits',overwrite=True)
        elif type(save_fits)==str:
            for i in range(len(masks)):
                hdu=fits.PrimaryHDU(np.zeros(1))
                hdum=fits.ImageHDU(masks[i],name='MASK')
                hdul=fits.HDUList([hdu,hdum])
                mkdirs(save_fits)
                name=save_fits.split('/')[-1][:-5]
                dirs='/'.join(save_fits.split('/')[:-1])
                if len(masks)>1:
                    hdul.writeto('%s/%s%s_mask.fits' % (dirs,name,abc[i]), overwrite=True)
                else:
                    hdul.writeto('%s/%s_mask.fits' % (dirs,name), overwrite=True)
        else:
            ValueError('save_fits must be either bool or string path to the save location (plus filename)!')
    return masks

#==========================================================
#Math
#-----------------------------------------------------------

def frac_int(x,y,frac):
	"""
	-----------------------------------------
	INSTRUCTIONS:
	Given a function from a set of y=f(x), returns the point xi where the integral F(xi) fulfils frac=F(xi)/F, this is, the point up to where you have to integrate from the whole range of values to obtain the desired fraction
	-----------------------------------------
	ARGS:
	x:	array of x values
	y:	array of y=f(x) values
	frac:	fraction of the integral, from 0 to 1
	-----------------------------------------
	"""
	if frac<=0 or frac>1:
		print('frac must be between 0 and 1!')
		return
	val=trapezoid(y,x)
	f=[]
	for i in range(1,len(x)+1):
		f.append(trapezoid(y[:i],x[:i]))
	f=np.asarray(f)
	ffrac=f/val
	F=abs(1-ffrac/frac)
	ind=np.where(F==np.min(F))[0][0]
	truex=np.interp(frac,ffrac,x)

	return ind,truex


#==========================================================
#General plotting applications
#----------------------------------------------------------

def zoomin(data,ax,nan=np.nan):
    """
    ---------------------------------------------
    INSTRUCTIONS
    Makes a zoom in in a 2D map with border NaN (or other non-valid) values
    ---------------------------------------------
    ARGS:
    data:   2D array containing the data
    ax: ax object where to plot the figure
    ---------------------------------------------
    nan:    value which will be ingnored when zooming in. Default is numpy.nan
    ---------------------------------------------
    """
    data[data==nan]=np.nan
    bound=np.argwhere(~np.isnan(data))
    ax.set_xlim(min(bound[:, 1])-2, max(bound[:, 1])+2)
    ax.set_ylim(min(bound[:, 0])-2, max(bound[:, 0])+2)

#----------------------------------------------------------

def mpd(plist): #multiple plots distribution
    """
    ---------------------------------------------
    INSTRUCTIONS:
    returns the figure object with rows and columns necessary to have a figure with multiple, same size plots following a squared shape i.e. 4 plots in a 2x2, 6 plots in a 2x3, 7 plots in a 3x3, etc
    ---------------------------------------------
    ARGS:
    plist:  list or array containing all the plots data, i.e. 7 plots imlpies a list or array with 7 elements
    ---------------------------------------------
    """
    l=len(plist)
    i=1
    while i**2<l:
        i+=1
    n_cols,n_rows=i,i
    while n_rows*n_cols>=l:
        n_rows-=1
    n_rows=n_rows+1
    #gs=GS(nrows=3*l,ncols=2,width_ratios=[1,1.5],height_ratios=[3,1,0.5]*l)
    fig=pp.figure(figsize=(n_cols*4,n_rows*4))
    ax_list=[]
    n=1
    while n<=l:
        ax=fig.add_subplot(n_cols,n_rows,n)
        ax_list.append(ax)
        n+=1
    #for r in range(n_rows):
        #for c in range(n_cols):
            #if n>=l:
                #break
            #else:
                #ax=fig.add_subplot(r+1,c+1,n)
                #n+=1
                #ax_list.append(ax)
    return fig,ax_list

