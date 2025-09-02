#Dictionaries in which specific variables' values are stored
#==========================================================

#Scientific index of units turn into numerical values
index={'G':1e9, 'M':1e6, 'k':1e3, 'm':1e-3, 'u':1e-6, 'n':1e-9, 'p':1e-12}

#LaTeX letters for units titles and labels
lat_let={'G':'G', 'M':'M', 'k':'k', ' ':'', 'm':'m', 'u':'\mu', 'n':'n', 'p':'p'}

#LaTeX wordings titles and labels associated to posterior dictionary keys
lat_labels={'dust:Av':r'A$_{\mathrm{V}}$ (mag)',
           'nebular:logU':'log(U)',
           'mass_weighted_zmet':r'Metallicity (Z$_{\odot}$)',
           'sfr':r'SFR (M$_{\odot}$yr$^{-1}$)',
           'stellar_mass':r'Living stellar mass (log$_{10}$(M$_{\odot}$))',
           'formed_mass':r'Total stellar mass (M$_{\odot}$)',
           'veldisp':r'$\sigma_{\mathrm{V}}$ (km/s)',
           }

#logC of Table 1 in Kennicut & Evans 2012
logC={'FUV':43.35,'NUV':43.17,'Halpha':41.27,'TIR':43.21,'24um':42.69,'70um':43.23,'1.4GHz':28.20,'2-10keV':39.77}

#bandwidth of spectral regions, in AA and restframe:
BANDS={#'Ha+Hb':[6484.61,6644.61]+[4782.68,4942.68],
       'UVcont':[1280,3480],
       'UVcontB':[1280,2380],
       'UVcontR':[2380,3480],
       '[OII]':[3677.09,3777.09],
       'OPcontB':[3800,4792],
       'Hb':[4812.68,4912.68],
       '[OIII]':[4916.30,5052.24],
       'OPcontR':[5072,6494],
       'Ha':[6514.61,6614.61]
    } #restframe
