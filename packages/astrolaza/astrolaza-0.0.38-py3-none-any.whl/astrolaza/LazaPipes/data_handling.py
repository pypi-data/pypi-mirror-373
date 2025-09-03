#Functions to handle data (save and load) from post and catalogue files, mostly from a BagPipes fit

from ..LazaUtils.get import get_z
from ..LazaUtils.MPF import mkdirs

import numpy as np

#==========================================================

def load_post(path,frmt='npy',print_keys=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    This function loads the file (either h5 or npy format) from a given path. This file has a dictionary-like structure
    ---------------------------------------------
    ARGS:
    path:   path to the file that needs to be loaded
    ---------------------------------------------
    KWARGS:
    frmt:   format of the file. Can be either 'npy' or 'h5'. Default is 'npy'
    print_keys: prints a list of the keys included in the file. Bool; default is False
    ---------------------------------------------
    """
    if frmt=='npy':
        data=np.load(path,allow_pickle=True)[()]
        #print('\n==============================================\nData from %s successfully loaded\n==============================================\n' % (path))
        if type(print_keys)==bool and print_keys:
            print('\n------------------------------------\nKeys of the data are:\n')
            for k in list(data.keys()):
                print('%s' % (k))
            print('\n------------------------------------\n')
            return data
        return data
    elif frmt=='h5': #TODO TODO TODO TODO TODO TODO
        print('======================================================\nWork in progress! Come back in a future update :)\n======================================================')
        #el problema de querer cargar el archivo h5, es que no consigo aislar la clase desde BP y ahorrarme todo el proceso de hacer cosas, y xd
        #Ahora mismo, la solución más simple es invocar el fit de BP, pero esto solo nos ahorrará un nuevo fit si el run+ID se llaman igual y hay copia en pipes/posterior.
        #Básicamente, esto es una muy mala solución, y es la única razón por la que se ha implementado que se guarde el fichero en una rchivo npy
        return
    else:
        raise TypeError('File format must be either "npy" or "h5"!')

#==========================================================

def save_results(post,results,out='.'):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Save the results from the plot in a file. This file wil contain a row array with the ID, redshift and the asked parameters of the object with upper and lower errors, in that order. It is assumed that the post file has been obtained using this package (see AstroLaza.LazaPipes.fitting-->BP_fit)
    ---------------------------------------------
    ARGS:
    post:   posterior dictionary or path to posterior dictionary from where to extract the data
    results:    list or tuple including the keys in post to be saved
    ---------------------------------------------
    KWARGS:
    out:   path to the directory and file where results will be saved. If left as default, file will be saved in the working directory as ID_run.res.
    ---------------------------------------------
    """
    if type(results)==str:
        results=[results]
    elif type(results) not in [list,tuple]:
        raise TypeError('results must be either a table or tuple contianing the keys of the wanted parametners!\n')
    if type(post)==str:
        post=load_post(post)
    elif type(post) not in [str,dict]:
        raise TypeError('post must be either a dictionary contianing the data or a path to said dictionary!\n')
    if type(out)==str and out!='.':
        mkdirs(out)
        fname=out.split('/')[-1]
    elif type(out)==str and out=='.':
        try:
            info=post['info']
            if info['run']!='.':
                fname=info['ID']+'_'+info['run']+'.res'
            else:
                fname=info['ID']+'.res'
        except KeyError:
            info={}
            fname='unknown_object.res'
            n=1
            while os.path.isfile(fname):
                fname=fname[:-4]+'_'+str(n)+'.res'
                n+=1
            print('======================================================\nThis posterior file was not obtained with this package and lacks the "info" key. The returned results will be saved as %s\n======================================================' % (fname))
    else:
        raise TypeError('out must be the path to where the file will be saved!\n')
    fil=open(out,'w')
    fil.write('#ID z ')
    for r in results:
        fil.write('%s uerr lerr ' % (r))
    try:
        fil.write('\n%s %f ' % (fname[:-4],get_z(post)))
    except KeyError:
        fil.write('\n%s %f ' % (fname[:-4],np.nan))
        print('This object posterior file has not been obtained using this package. ID will be %s and redshift will be nan\n' % (fname[:-4]))
    for r in results:
        if r=='age20' or r=='age50':
            fil.write('%.4f %.4f %.4f ' % (post[r]))
        else:
            try:
                val=np.nanpercentile(post[r],(50,84,16),axis=0).T
                fil.write('%.4f %.4f %.4f ' % (val[0],val[1]-val[0],val[0]-val[2]))
            except KeyError:
                fil.write('nan nan nan ')
                print('The key %s is not in the given file. Values will be nan\n' % (r))
    fil.close()
    return

#==========================================================

def join_results(paths,results,out='catalogue.res'):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Joins results from differents post files from the given paths into a single file. The structure of this file will be the same as in save_results, with each row for a different object
    Note that it is assumed the keys in the posterior file are come from functions of these package, and if an exterior posterior file is used, it may occur that the parameters are not found in the keys list
    ---------------------------------------------
    ARGS
    paths:  list containing the paths to the post files of the desired objects
    results:   list or tuple including the keys in posts to be saved
    ---------------------------------------------
    KWARGS:
    out:    output path for the file. If left as default, a file named 'catalogue.res' will be saved in the working directory
    ---------------------------------------------
    """
    if type(paths)!=list or type(paths[0])!=str:
        raise TypeError('paths must be a list of strings containing the paths to the posterior files to join!')
    elif type(results)!=list:
        raise TypeError("results must be a list of strings containing the keys' names in the posterior dictionaries!")
    fil=open(out,'w')
    fil.write('# ID z ')
    if 'xy' in results: #Check if X and Y pixel positions are in the results list, and add at the beginning of the catalogue if so
        fil.write('x y ')
    for r in results: #Add rest of params in the given order
        if r!='xy':
            fil.write('%s uerr lerr ' % (r))
    fil.write('\n')
    fil.close()
    n=0
    for post in paths:
        fil=open(out,'a')
        if type(post)==str:
            post=load_post(post)
        try: #check if the ID of the object is given, and will be included if so or stated as unknown if not
            fil.write('%s %f ' % (post['info']['ID'],get_z(post)))
        except KeyError:
            fname='unknown_object_%i' % (n)
            n+=1
            fil.write('\n%s %f ' % (fname,np.nan))
            print('This object posterior file has not been obtained using this package and lacks the "info" key. Thus, ID will be %s and redshift will be nan\n' % (fname))
        if 'xy' in results: #include the xy positions
            try:
                fil.write('%i %i ' % (post['xy'][0],post['xy'][1]))
            except KeyError:
                fil.write('nan nan ')
        for r in results: #include the rest of parameters
            if r=='xy':
                continue
            elif r=='age20' or r=='age50':
                fil.write('%.4f %.4f %.4f ' % (post[r]))
            else:
                try:
                    val=np.nanpercentile(post[r],(50,84,16),axis=0).T
                    fil.write('%.4f %.4f %.4f ' % (val[0],val[1]-val[0],val[0]-val[2]))
                except KeyError:
                    fil.write('nan nan nan ')
                    print('The key %s is not in the given posterior file. Values will be nan\n' % (r))
        fil.write('\n')
        fil.close()
    return

#==========================================================

def IDpixels(path):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Returns ID and x&y pixel position of a resolved spectrum
    ---------------------------------------------
    ARGS:
    path:   path to the spectrum file. IT IS ASSUMED IT WAS OBTAINED USING correct_input_resolved, OR THAT FOLLOWS DE ID_X_Y.dat FORMAT. If not, this won't be usefull at all
    ---------------------------------------------
    """
    fname=path.split('/')[-1]
    fsplit=fname.split('_')
    IDpix=[fsplit[0],fsplit[1],fsplit[2][:-4]]
    return IDpix
