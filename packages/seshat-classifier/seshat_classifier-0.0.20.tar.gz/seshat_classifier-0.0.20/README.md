# Stellar Evolutionary Stage Heuristic Assessment Tool (SESHAT)

This is a beta version of the SESHAT tool, currently being modified for publication.

The final version will be released pending any suggestions from the referee.

If you use this package, please cite Crompvoets et al. 2025 (submitted). Please also cite the original data producers:  
YSOs: [Richardson et al. (2024)][https://ui.adsabs.harvard.edu/abs/2024ApJ...961..188R/abstract]  
Brown dwarfs: ATMO -- [Phillips et al. (2020)][https://ui.adsabs.harvard.edu/abs/2020A%26A...637A..38P/abstract]  
White dwarfs: [Blouin et al. (2018)][https://ui.adsabs.harvard.edu/abs/2018ApJ...863..184B/abstract]  
Field stars: PARSEC -- [Bressen et al. (2012)][https://ui.adsabs.harvard.edu/abs/2012MNRAS.427..127B/abstract]  
Galaxies: CIGALE -- [Burgarella et al. 2005][https://ui.adsabs.harvard.edu/abs/2005MNRAS.360.1413B/abstract], [Noll et al. 2009][https://ui.adsabs.harvard.edu/abs/2009A%26A...507.1793N/abstract] [Boquin et al. (2020)][https://ui.adsabs.harvard.edu/abs/2019A%26A...622A.103B/abstract]  


## Catalog set-up
Please have your catalog set-up with the columns as:  
Spitzer: ['IRAC1', 'IRAC2', 'IRAC3', 'IRAC4', 'MIPS1', 'MIPS2', 'MIPS3']  
2MASS: ['J', 'H', 'Ks']  
JWST: in the frame of 'f090w', or 'f322w2'.  

Please include errors as 'e_' + filter name; e.g. 'e_f090w'.  

All columns must be in Vega mags.  

If you have labels already known, these should be under the column: 'Class'  
The labels should match the following:  
Young Stellar Objects: "YSO"  
Field stars: "FS"  
Galaxies: "Gal"  
White dwarfs: "WD"  
Brown dwarfs: "BD"   

## Other important information
The function classify accepts pandas DataFrames or Astropy Tables.  

When testing filters, it is assumed the data will have errors that can be approximated by a Gaussian with mean 0.1 mag and standard deviation 0.01 mag.  

SESHAT only takes medium, wide, and very-wide filters as input for JWST, no narrow filters.

## Example of obtaining classifications

~~~
from seshat-classifier import seshat
import pandas as pd

my_catalog = pd.read_csv("my_catalog.csv")

my_catalog_classified = seshat.classify(real=my_catalog, classes=['YSO', 'FS', 'Gal'], filters=['f140m', 'f160m', 'f356w', 'f480m','f770w','f2550w'], cosmological=False, return_test=False, threads = 8)
~~~

## Example of testing filters

~~~
from seshat-classifier import seshat

filter_test = seshat.test_filters(filters = ['f140m', 'f160m', 'f356w', 'f480m','f770w','f2550w'], classes = =['YSO', 'FS', 'BD', 'WD', 'Gal'], threads = 8)
~~~