#
import numpy as np

import matplotlib.pyplot as pp
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import FormatStrFormatter

import matplotlib.gridspec as gs

import glob as glob
from natsort import natsorted as ns

from ..LazaUtils.MPF import mkdirs, centroid

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

