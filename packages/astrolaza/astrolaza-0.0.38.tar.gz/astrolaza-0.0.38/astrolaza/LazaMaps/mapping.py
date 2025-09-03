#
import numpy as np

import matplotlib.pyplot as pp
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import FormatStrFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable as mal

import matplotlib.gridspec as gs

import glob as glob
from natsort import natsorted as ns

from ..LazaUtils.MPF import mkdirs, centroid, mpd, zoomin, print_errs
import ..LazaPipes.data_handling as LPdh
from ..LazaFlux.mags import fit_line, fit_2line
from ..LazaGal.surface import Eparam

#==========================================================
def map_maker(pixarr,errormap=False,objid='',par='',show=False,save=None):
    """"
    ---------------------------------------------
    INSTRUCTIONS:
    Creates a map of a resolved object
    ---------------------------------------------
    ARGS:
    pixarr: array of 5 columns containing, in this order: x coordinate, y coordinate, parameter value, parameter upper erro and parameter. Mostly this come from the get_from_cat function
    ---------------------------------------------
    KWARGS:
    errormap:   add upper and lower error maps to the figure. Default is False
    objid:  object ID. It must be a string and will be used as figure title
    param:  parameter name. It must be a string and will be used as figure title
    show:   show the resulting map. Default is False
    save:   save the map. Can be a path to be saved at or True, in which case will be saved as 'objid_param_map.png' in the working directory
    ---------------------------------------------
    """
    pp.close('all')
    if len(pixarr.shape)!=2 or pixarr.shape[1]!=5:
        print('The input array must be a Nx5 array, with N the number of pixels in the catalogue, and 5 column array containing the x pixel coordinate, y pixel coordinate, parameter value, parameter upper bound and parameter lower bound, in that order!')
        return
    #loading the variables
    x=pixarr[:,0]
    xmin,xmax=int(np.nanmin(x)),int(np.nanmax(x))
    y=pixarr[:,1]
    ymin,ymax=int(np.nanmin(y)),int(np.nanmax(y))
    param=pixarr[:,2]
    uerr=pixarr[:,3]
    lerr=pixarr[:,4]
    #map creation
    margin=3
    #return xmin,xmax,ymin,ymax
    mapa=np.ones([xmax-xmin+1+margin*2,ymax-ymin+1+margin*2])*np.nan
    umap=np.copy(mapa)
    lmap=np.copy(mapa)
    for i in range(len(x)):
        xi=int(x[i]-xmin+margin)
        yi=int(y[i]-ymin+margin)
        #print(xi,yi,param[i])
        mapa[xi,yi]=param[i]
    if not errormap:
        fig=pp.figure(figsize=(16,9))
        ax=fig.add_subplot(1,1,1)
        ticks=list(np.linspace(np.nanmin(mapa),np.nanmax(mapa),4))
        sp=ax.imshow(mapa,origin='lower',cmap='summer',zorder=10)
        ax.plot(33-ymin+margin,41-xmin+margin,marker='x',c='r',zorder=100)
        #ax.plot(34-ymin+margin,35-xmin+margin,marker='+',c='b',zorder=100)
        ax.plot(27-ymin+margin,31-xmin+margin,marker='o',c='k',zorder=100)
        ax.yaxis.tick_right()
        #cbaxes=inset_axes(ax,width='5%',height='80%',loc='center left')
        fig.colorbar(sp,ax=ax,ticks=ticks,format='%.3f',location='left')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        if par!='':
            ax.set_title(par)
        if objid!='':
            pp.suptitle(objid)
        if show:
            pp.show(block=False)
        if save:
            if type(save)==bool:
                np.savefig(objid+'_'+par+'_map.png',dpi=200)
            elif type(save)==str:
                mkdirs(save)
                pp.savefig(save,dpi=200)
            else:
                print('save must be either a path to the savefile or True to save in the working directory!')
                return
        return
    elif errormap:
        for i in range(len(x)):
            xi=int(x[i]-xmin+margin)
            yi=int(y[i]-ymin+margin)
            umap[xi,yi]=uerr[i]
            lmap[xi,yi]=lerr[i]
        emap=np.stack((umap,lmap),axis=1)
        emin,emax=np.nanmin(emap),np.nanmax(emap)
        fig=pp.figure(figsize=(16,9))
        gsm=gs.GridSpec(3,4,width_ratios=[0.1,2,1,0.1],height_ratios=[1,0.2,1])
        #plot map
        gsmap=pp.subplot(gsm[:,1])
        gsmap.set_yticks([])
        gsmap.set_xticks([])
        gsmap.title.set_text(par)
        val=gsmap.imshow(mapa,origin='lower',cmap='summer',zorder=10)
        eb1=pp.subplot(gsm[:,0])
        ticks=np.linspace(np.nanmin(mapa),np.nanmax(mapa),5)
        fig.colorbar(val,cax=eb1,format='%.3f',location='left',ticks=ticks)
        #plot errormaps
        gsu=pp.subplot(gsm[0,2])
        u=gsu.imshow(umap,origin='lower',cmap='coolwarm',zorder=10,vmin=emin,vmax=emax)
        gsu.title.set_text('Upper error')
        gsu.set_yticks([])
        gsu.set_xticks([])
        gsl=pp.subplot(gsm[2,2])
        l=gsl.imshow(lmap,origin='lower',cmap='coolwarm',zorder=10,vmin=emin,vmax=emax)
        gsl.title.set_text('Lower error')
        gsl.set_yticks([])
        gsl.set_xticks([])
        eb2=pp.subplot(gsm[:,-1])
        ticks=np.linspace(emin,emax,5)
        fig.colorbar(u,cax=eb2,format='%.3f',location='right',ticks=ticks)
        pp.suptitle(objid)
        pp.tight_layout()
        if show:
            pp.show(block=False)
        if save:
            if type(save)==bool:
                np.savefig(objid+'_'+par+'map.png',dpi=200)
            elif type(save)==str:
                mkdirs(save)
                pp.savefig(save,dpi=200)
            else:
                print('save must be either a path to the savefile or True to save in the working directory!')
                return
                
#==========================================================

def multimap(catalogues,IDs=None,notes=None,title='',same_limits=False,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS
    Creates a figure containing the maps of several objects, up to 12 objects per figure. It is asume inputs of this function come from get_from_cat
    ---------------------------------------------
    ARGS:
    catalogues: list, tuple or array of arrays containing the info of the object, this is, an array of Nx5 with x and y pixel coordiantes, parameter value and aprameter upper and lower bound, in that order (one column each) for each object. It is assumed that this input comes from get_from_cat
    ---------------------------------------------
    KWARGS:
    IDs:    list containing strings with the objects' ID names. IDs must appear in the same order as objects in catalogues. If there are less IDs than objects, no more IDs will be written after the last one is used
    notes:  footnotes to include in each map. They work as the IDs arg
    title:  title of the figure
    same_limits:    set the vmin and vmax values for the whole figure. Can be either False, so each map has its own limits; True, in which case it will take the maximum and minimum values of the whole dataset as limits; or a tuple, list or array with just 2 values that will be used as vmin and vmax for the whole dataset
    show:   show plot. Default is False
    save:   save the resulting figure. It can be a path where the figure will be saved, or True, to save it in teh working directory
    ---------------------------------------------
    """
    mapas=[]
    mascaras=[]
    if type(catalogues) not in [list,tuple]:
        print('Catalogues must be a list or tuple containing the data for each object! Each element of it must be a Nx5 array including the x and y pixel coordinates, the parameter value and the upper and lower bounds of the parameter, in that order')
        return
    else:
        vmin=[]
        vmax=[]
        cent=[]
        for cat in catalogues:
            if type(cat)!=np.ndarray or len(cat.shape)!=2 or cat.shape[1]!=5:
                print('Dataset for each object must be a Nx5 array including the x and y pixel coordinates, the parameter value and the upper and lower bounds of the parameter, in that order')
                print('The object in position %i does not fullfil this condition!' % (catalogues.index(cat)))
                return
            else:
                cent.append(centroid(cat[:,:2]))
        #Getting the maps for each object
        cent=np.asarray(cent)
        centx=int(np.round(np.nanmean(cent[:,0]),0))
        centy=int(np.round(np.nanmean(cent[:,1]),0))
        j=0
        ylim=[]
        for cat in catalogues:
            param=cat[:,2]
            vmin.append(np.nanmin(param))
            vmax.append(np.nanmax(param))
            x=cat[:,0]
            xmin,xmax=int(np.nanmin(x)),int(np.nanmax(x))
            y=cat[:,1]
            ymin,ymax=int(np.nanmin(y)),int(np.nanmax(y))
            mapa=np.ones([54,96])*np.nan
            mask=np.ones([54,96])*np.nan
            for i in range(len(x)):
                #Se supone que los cent debería estar al revés, pero bueno xd
                #Tengo un lío curioso con las x e y, pero así es como funciona (sí, sé que cada rato intercambio coordenadas pero xd)
                xi=int(x[i]+(27-cent[j,0]))
                yi=int(y[i]+(48-cent[j,1]))
                if x[i]==np.nanmax(x): #min,max position for plotting porpuses
                    ymax=int(x[i]+(48-cent[j,0]))
                elif x[i]==np.nanmin(x):
                    ymin=int(x[i]+(48-cent[j,0]))
                if np.isnan(param[i]):
                    mask[xi,yi]=0
                mapa[xi,yi]=param[i]
            ylim.append([ymin,ymax])
            mapas.append(mapa)
            mascaras.append(mask)
            j+=1
    #checking more possible input errors
    if IDs is not None:
        if type(IDs)!=list:
            print('IDs must be a list!')
            return
        while len(IDs)<len(catalogues):
            IDs.append('')
    else:
        IDs=['' for i in range(len(catalogues))]
    if notes is not None:
        if type(notes)!=list:
            print('notes must be a list!')
            return
        while len(notes)<len(catalogues):
            notes.append('')
    else:
        notes=['' for i in range(len(catalogues))]
    if same_limits:
        if type(same_limits) in [list,tuple,np.ndarray]:
            vmin=[same_limits[0] for i in range(len(catalogues))]
            vmax=[same_limits[1] for i in range(len(catalogues))]
        elif type(same_limits)==bool:
            vmin=[np.nanmin(vmin) for i in range(len(catalogues))]
            vmax=[np.nanmax(vmax) for i in range(len(catalogues))]
            vmin=[np.nanmin(np.asarray(vmin)) for i in range(len(catalogues))]
            vmax=[np.nanmax(np.asarray(vmax)) for i in range(len(catalogues))]
        else:
            print('same_limits can be either a 2-element list, True or False!')
            return
    else:
        vmin=[None for i in range(len(catalogues))]
        vmax=[None for i in range(len(catalogues))]
    if type(title)!=str:
        print('title must be a string!')
        return
    #Creating the multimap
    n_figs=int(np.ceil(len(catalogues)/12))
    if len(catalogues)<12: #forcing to have 12 images per plot
        max_sub=len(catalogues)
    else:
        max_sub=11
    for n in range(n_figs): #we create n plots with 12 objects per plot
        fig=pp.figure(n,figsize=(16,9))
        n_sub=0
        while n_sub<=max_sub:
            ax=fig.add_subplot(3,4,n_sub+1)
            mapa=mapas[n_sub]
            mask=mascaras[n_sub]
            mm=ax.imshow(mask,origin='lower',cmap='binary_r',aspect='auto')
            sp=ax.imshow(mapa,origin='lower',cmap='cool',vmin=vmin[n_sub],vmax=vmax[n_sub],aspect='auto')
            ax.set_xticks([])
            ax.set_yticks([])
            if same_limits:
                ticks=np.linspace(vmin[n_sub],vmax[n_sub],5)
                cbaxes=fig.add_axes([0.2125,0.08,0.6,0.01]) #original: [0.2,0.05,0.6,0.01]; top: [0.2125,0.92,0.6,0.01]
                cbaxes.tick_params(labelsize=30)
                fig.colorbar(sp,cax=cbaxes,ticks=ticks,format='%.1f',location='bottom')
                margin=6
            else:
                ticks=np.linspace(np.nanmin(mapa),np.nanmax(mapa),5)
                cbaxes=inset_axes(ax,width='5%',height='80%',loc='center right')
                cbaxes.tick_params(labelsize=30)
                fig.colorbar(sp,cax=cbaxes,ticks=ticks,format='%.1f',location='left')
                margin=12
            #zooming in (xd)
            xl=ax.set_xlim([ylim[n+n_sub][0]-margin,ylim[n+n_sub][1]+margin])
            ratio=9*(ylim[n+n_sub][1]-ylim[n+n_sub][0]+margin*2)/16
            yl=ax.set_ylim(27-ratio+3.375,27+ratio-3.375)
            ax.annotate(IDs[n_sub],(0.05,0.85),xycoords='axes fraction',weight='bold',fontsize=18)
            ax.annotate(notes[n_sub],(0.05,0.10),xycoords='axes fraction',fontsize=14)
            n_sub+=1
        pp.suptitle('\n\n\n'+title,weight='bold')
        pp.subplots_adjust(wspace=0,hspace=0)
        if show:
            pp.show(block=False)
        if save:
            if type(save)==bool:
                pp.savefig(title+'_multimap.png',dpi=1000)
            elif type(save)==str:
                mkdirs(save)
                pp.savefig(save,dpi=500)
            else:
                print('save must be either a path to the savefile or True to save in the working directory!')
                return

#==========================================================

def params_map(ID,run,params,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Creates a figure with the binned map of a source and the value for each parameter in the bin
    ---------------------------------------------
    ARGS:
    ID: source's ID
    run:    (bagpipes) run from where to take the data
    params: list of parameters to create maps of. Aside from Bagpipes posterior quantities, user can also input 'age20' (age, in Gyr, when 20% of the mass was created), 'age50' (age, in Gyr, when 50% of the mass was created), 'Esfr' (SFR surface density), 'Estellar_mass' (stellar mass surface density), 'Ha' (Halpha peak flux emission),'[OIII]5008' ([OIII]5008 peak flux emission),'[OII]' ([OII] peak flux emission),'[OIII]4960' ([OIII]4960 peak flux emission) and 'Hb (Hbeta peak flux emission)'
    ---------------------------------------------
    KWARS:
    show:   show the resulting maps
    save:   save the resulting figure as ID_run_params_binmap.pdf
    ---------------------------------------------
    """
    pp.close('all')

    #loading data
    paths=ns(glob.glob('*%s*/%s/*npy' % (ID,run)))
    #print(paths)
    l=len(paths)
    masks=ns(glob.glob('BINS/*%s*' % (ID)))
    masks=fits.open(masks[0])
    cmap_list=['spring', 'summer', 'autumn', 'winter', 'coolwarm', 'cool', 'Wistia', 'vanimo', 'managua_r', 'jet','Spectral','brg','gnuplot']

    #Creating the figure
    fig,axs=mpd(params)
    fig.suptitle('%s - %s' % (ID,run))
    for i in range(len(params)):
        pval=[]
        mval=[]
        for j in range(l):
            d=LPdh.load_post(paths[j])
            #print(paths[j])
            #print(d[params[i]])
            if params[i] not in ['age20','age50','Esfr','Estellar_mass','Ha','[OIII]5008','[OII]','[OIII]4960','Hb']:
                try:
                    val=np.nanmedian(d[params[i]])
                    m=masks[j+1].data*val
                    pval.append(val)
                    mval.append(m)
                except KeyError:
                    raise KeyError('The parameter %s is not included in the dictionary. It value for the bin will be set to NaN' % (params[i]))
                    pval.append(np.nan)
                    mval.append(masks[j+1].data*np.nan)
            elif params[i] in ['age20','age50']:
                val=cosmo.age(z_dic[ID]).value-d[params[i]][0]
                #print(val)
                m=masks[j+1].data*val
                pval.append(val)
                mval.append(m)
            elif params[i]=='Esfr':
                val=np.nanmedian(d[params[i][1:]])
                val=Eparam(val,masks[j+1].data,z_dic[ID],0.08)
                m=masks[j+1].data*val
                pval.append(val)
                mval.append(m)
            elif params[i]=='Estellar_mass':
                val=np.nanmedian(d[params[i][1:]])
                val=np.log10(Eparam(10**val,masks[j+1].data,z_dic[ID],0.08))
                m=masks[j+1].data*val
                pval.append(val)
                mval.append(m)
            elif params[i]=='Ha':
                wl=d['wavelength_obs'][10:-5]
                f=d['spectrum_obs'][10:-5]
                ind=np.where(wl>5200*(1+z_dic[ID]))
                data=np.stack((wl,f),axis=1)
                data=data[ind]
                g,eg=fit_line(data)
                val=(g[1]-6564.6)/6564.6-z_dic[ID]
                pval.append(val)
                m=masks[j+1].data*val
                mval.append(m)
            elif params[i]=='[OIII]5008':
                wl=d['wavelength_obs'][10:-5]
                f=d['spectrum_obs'][10:-5]*wl**2/c*1e29
                ind=np.where((wl>4900*(1+z_dic[ID]))*(wl<6500*(1+z_dic[ID])))
                data=np.stack((wl,f),axis=1)
                data=data[ind]
                g,eg=fit_2line(data,z_dic[ID])
                val=(g[1]-5008.2)/5008.2-z_dic[ID]
                pval.append(val)
                m=masks[j+1].data*val
                mval.append(m)
            elif params[i]=='[OIII]4960':
                wl=d['wavelength_obs'][10:-5]
                f=d['spectrum_obs'][10:-5]*wl**2/c*1e29
                ind=np.where((wl>4900*(1+z_dic[ID]))*(wl<6500*(1+z_dic[ID])))
                data=np.stack((wl,f),axis=1)
                data=data[ind]
                g,eg=fit_2line(data,z_dic[ID])
                val=(g[4]-4960.3)/4960.3-z_dic[ID]
                pval.append(val)
                m=masks[j+1].data*val
                mval.append(m)
                #print(g[4])
            elif params[i]=='Hb':
                wl=d['wavelength_obs'][10:-5]
                f=d['spectrum_obs'][10:-5]*wl**2/c*1e29
                ind=np.where((wl>3870*(1+z_dic[ID]))*(wl<4900*(1+z_dic[ID])))
                ind=np.where((wl>3870*(1+z_dic[ID]))*(wl<4900*(1+z_dic[ID])))
                data=np.stack((wl,f),axis=1)
                data=data[ind]
                g,eg=fit_line(data)
                val=(g[1]-4862.7)/4862.7-z_dic[ID]
                pval.append(val)
                m=masks[j+1].data*val
                mval.append(m)
                #a=LPdh.load_post('BP_R05_bin5_runs/NP-6_C00/R05_bin5_NP-6_C00_post.npy')
                #wl=a['wavelength_obs'][10:-5]
                #print(g[1],z_dic[ID])
            elif params[i]=='[OII]':
                wl=d['wavelength_obs'][10:-5]
                f=d['spectrum_obs'][10:-5]*wl**2/c*1e29
                ind=np.where((wl>3650*(1+z_dic[ID]))*(wl<4800*(1+z_dic[ID])))
                ind=np.where((wl>3650*(1+z_dic[ID]))*(wl<4800*(1+z_dic[ID])))
                data=np.stack((wl,f),axis=1)
                data=data[ind]
                g,eg=fit_line(data)
                val=(g[1]-3727.1)/3727.1-z_dic[ID]
                pval.append(val)
                m=masks[j+1].data*val
                mval.append(m)

        pval=np.asarray(pval)
        #print(params[i],np.nanmin(pval),np.nanmax(pval))
        mval=np.asarray(mval)
        mapa=np.nansum(mval,axis=0)
        mapa[mapa==0]=np.nan
        pmap=axs[i].imshow(mapa,origin='lower',cmap=cmap_list[i])
        zoomin(mapa,axs[i])
        axs[i].set_xticks([])
        axs[i].set_yticks([])
        try:
            axs[i].set_title('%s' % (lat_labels[params[i]]))
        except KeyError:
            axs[i].set_title('%s' % (params[i]))
        fig.colorbar(pmap,ax=axs[i],ticks=np.linspace(np.nanmin(pval),np.nanmax(pval),3),format='%.2g')
        fig.subplots_adjust(wspace=0)
    if show:
        pp.show(block=False)
    if save:
        fig.savefig('%s_%s_params_binmap.pdf' % (ID,run))

#----------------------------------------------------------

def phys_map(ID,run,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Creates a figure showing 4 maps with the parameters Av, Z, age50 and logU for each binned region in the source. Additionally, a table is generated including the values for each bin for each parameter
    ---------------------------------------------
    ARGS:
    ID: source's ID
    run:    (bagpipes) run from where to take the data
    ---------------------------------------------
    show:   show the resulting figure
    save:   save the resulting figure as ID_run_phys_binmap.pdf
    ---------------------------------------------
    """
    pp.close('all')

    params=['dust:Av','mass_weighted_zmet','age50','nebular:logU']
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
    fig.suptitle('Physical parameters map for %s - run: %s' % (ID,run),fontsize=30)
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
            if params[i] not in ['age20','age50']:
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
            elif params[i] in ['age20','age50']:
                val=cosmo.age(z_dic[ID]).value-d[params[i]][0]
                u=cosmo.age(z_dic[ID]).value-(d[params[i]][0]+d[params[i]][1])
                l=cosmo.age(z_dic[ID]).value-(d[params[i]][0]-d[params[i]][2])
                #print(val)
                m=masks[j+1].data*val*1e3
                pval.append(val*1e3)
                mval.append(m)
                uerr.append((val-u)*1e3)
                lerr.append((l-val)*1e3)
                axs[i].set_title('T$_{50,\mathrm{lookback}}$ (Myr)',fontsize=20)
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
    cols=['A$\mathrm{_{V}}$ (mag)', 'Z (Z$\mathrm{_{\odot}}$)','T$_{50,\mathrm{lookback}}$ (Myr)','log(U)']
    rows=['BIN %i' % (i) for i in range(1,L+1)]
    cell_text=[]
    a=[r'%g$^{+%g}_{-%g}$' % print_errs(tab_dat.reshape(tab_dat.size)[i],tab_uerr.reshape(tab_uerr.size)[i],tab_lerr.reshape(tab_lerr.size)[i]) for i in range(tab_dat.size)]
    a=np.asarray(a)
    cell_text=a.reshape(tab_dat.shape)
    tabax=fig.add_subplot(3,1,3)
    the_table=tabax.table(cellText=cell_text,rowLabels=rows,colLabels=cols,loc='center',fontsize=20)
    tabax.axis('off')
    the_table.scale(1,3)
    pp.tight_layout
    if show:
        pp.show(block=False)
    if save:
        fig.savefig('%s_%s_phys_binmap.pdf' % (ID,run))

#----------------------------------------------------------

def peaks_map(ID,run,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Creates a figure showing 4 maps with line flux values of [OII], Hb, [OIII] and Ha for each binned region in the source. Additionally, a table is generated including the values for each bin for each line
    ---------------------------------------------
    ARGS:
    ID: source's ID
    run:    (bagpipes) run from where to take the data
    ---------------------------------------------
    show:   show the resulting figure
    save:   save the resulting figure as ID_run_phys_binmap.pdf
    ---------------------------------------------
    """
    pp.close('all')
    params=['[OII]','[OIII]5008','[OIII]4960','Hb','Ha']
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
    cmap_list=['spring', 'summer', 'autumn', 'winter','coolwarm']

    #Creating the figure
    # fig,axs=mpd(params)
    fig=pp.figure(figsize=(17,18))
    fig.suptitle('redshift from peaks maps for %s - run: %s' % (ID,run),fontsize=30)
    tab_dat=np.ones([L,5])
    tab_uerr=np.ones([L,5])
    tab_lerr=np.ones([L,5])
    cell_text=[]
    axs=[fig.add_subplot(3,3,i) for i in range(1,6)]
    for i in range(len(params)):
        pval=[]
        mval=[]
        uerr=[]
        lerr=[]
        for j in range(L):
            d=LPdh.load_post(paths[j])
            #print(paths[j])
            #print(d[params[i]])
            if params[i]=='Ha':
                wl=d['wavelength_obs'][10:-5]
                f=d['spectrum_obs'][10:-5]*wl**2/c*1e29
                ind=np.where(wl>5200*(1+z_dic[ID]))
                data=np.stack((wl,f),axis=1)
                data=data[ind]
                g,eg=fit_line(data)
                val=(g[1]-6564.6)/6564.6-z_dic[ID]
                u=(g[1]+eg[1]-6564.6)/6564.6-z_dic[ID]
                l=(g[1]-eg[1]-6564.6)/6564.6-z_dic[ID]
                pval.append(val)
                uerr.append(u-val)
                lerr.append(val-l)
                m=masks[j+1].data*val
                mval.append(m)
                axs[i].set_title(r'H$_{\mathrm{\alpha}}$',fontsize=20)
                # print(g[1],eg[1],val,u,l)
            elif params[i]=='[OIII]5008':
                wl=d['wavelength_obs'][10:-5]
                f=d['spectrum_obs'][10:-5]*wl**2/c*1e29
                ind=np.where((wl>4900*(1+z_dic[ID]))*(wl<6500*(1+z_dic[ID])))
                data=np.stack((wl,f),axis=1)
                data=data[ind]
                g,eg=fit_2line(data,z_dic[ID])
                val=(g[1]-5008.2)/5008.2-z_dic[ID]
                u=(g[1]+eg[1]-5008.2)/5008.2-z_dic[ID]
                l=(g[1]-eg[1]-5008.2)/5008.2-z_dic[ID]
                pval.append(val)
                uerr.append(u-val)
                lerr.append(val-l)
                m=masks[j+1].data*val
                mval.append(m)
                axs[i].set_title(r'[OIII]$_{\mathrm{5008.2}}$',fontsize=20)
            elif params[i]=='[OIII]4960':
                wl=d['wavelength_obs'][10:-5]
                f=d['spectrum_obs'][10:-5]*wl**2/c*1e29
                ind=np.where((wl>4900*(1+z_dic[ID]))*(wl<6500*(1+z_dic[ID])))
                data=np.stack((wl,f),axis=1)
                data=data[ind]
                g,eg=fit_2line(data,z_dic[ID])
                val=(g[4]-4960.3)/4960.3-z_dic[ID]
                u=(g[4]+eg[4]-4960.3)/4960.3-z_dic[ID]
                l=(g[4]-eg[4]-4960.3)/4960.3-z_dic[ID]
                pval.append(val)
                uerr.append(u-val)
                lerr.append(val-l)
                m=masks[j+1].data*val
                mval.append(m)
                axs[i].set_title(r'[OIII]$_{\mathrm{4960.3}}$',fontsize=20)
                #print(g[4])
            elif params[i]=='Hb':
                wl=d['wavelength_obs'][10:-5]
                f=d['spectrum_obs'][10:-5]*wl**2/c*1e29
                ind=np.where((wl>3870*(1+z_dic[ID]))*(wl<4900*(1+z_dic[ID])))
                ind=np.where((wl>3870*(1+z_dic[ID]))*(wl<4900*(1+z_dic[ID])))
                data=np.stack((wl,f),axis=1)
                data=data[ind]
                g,eg=fit_line(data)
                val=(g[1]-4862.7)/4862.7-z_dic[ID]
                u=(g[1]+eg[1]-4862.7)/4862.7-z_dic[ID]
                l=(g[1]-eg[1]-4862.7)/4862.7-z_dic[ID]
                pval.append(val)
                uerr.append(u-val)
                lerr.append(val-l)
                m=masks[j+1].data*val
                mval.append(m)
                axs[i].set_title(r'H$_{\mathrm{\beta}}$',fontsize=20)
                #a=LPdh.load_post('BP_R05_bin5_runs/NP-6_C00/R05_bin5_NP-6_C00_post.npy')
                #wl=a['wavelength_obs'][10:-5]
                #print(g[1],z_dic[ID])
            elif params[i]=='[OII]':
                wl=d['wavelength_obs'][10:-5]
                f=d['spectrum_obs'][10:-5]*wl**2/c*1e29
                ind=np.where((wl>3650*(1+z_dic[ID]))*(wl<4800*(1+z_dic[ID])))
                ind=np.where((wl>3650*(1+z_dic[ID]))*(wl<4800*(1+z_dic[ID])))
                data=np.stack((wl,f),axis=1)
                data=data[ind]
                g,eg=fit_line(data)
                val=(g[1]-3727.1)/3727.1-z_dic[ID]
                u=(g[1]+eg[1]-3727.1)/3727.1-z_dic[ID]
                l=(g[1]-eg[1]-3727.1)/3727.1-z_dic[ID]
                pval.append(val)
                uerr.append(u-val)
                lerr.append(val-l)
                m=masks[j+1].data*val
                mval.append(m)
                axs[i].set_title('[OII]',fontsize=20)
        pval=np.asarray(pval)
        uerr=np.asarray(uerr)
        lerr=np.asarray(lerr)
        tab_dat[:,i]=pval.T
        tab_uerr[:,i]=uerr.T
        tab_lerr[:,i]=lerr.T
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
    cols=['[OII]',r'[OIII]$_{\mathrm{4960.3}}$',r'[OIII]$_{\mathrm{5008.2}}$',r'H$_{\mathrm{\beta}}$',r'H$_{\mathrm{\alpha}}$']
    rows=['BIN %i' % (i) for i in range(1,L+1)]
    cell_text=[]
    a=[r'%g$^{+%g}_{-%g}$' % print_errs(tab_dat.reshape(tab_dat.size)[i],tab_uerr.reshape(tab_uerr.size)[i],tab_lerr.reshape(tab_lerr.size)[i]) for i in range(tab_dat.size)]
    a=np.asarray(a)
    cell_text=a.reshape(tab_dat.shape)
    tabax=fig.add_subplot(3,1,3)
    the_table=tabax.table(cellText=cell_text,rowLabels=rows,colLabels=cols,loc='center',fontsize=20)
    tabax.axis('off')
    the_table.scale(1,3)
    pp.tight_layout
    if show:
        pp.show(block=False)
    if save:
        fig.savefig('%s_%s_peaks_binmap.pdf' % (ID,run))
