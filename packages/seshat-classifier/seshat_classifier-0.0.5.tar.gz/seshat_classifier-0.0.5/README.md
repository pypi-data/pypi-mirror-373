# README for the Stellar Evolutionary Stage Heuristic Assessment Tool (SESHAT)

# Catalog set-up
Please have your catalog set-up with the columns as:
Spitzer: ['IRAC1', 'IRAC2', 'IRAC3', 'IRAC4', 'MIPS1', 'MIPS2', 'MIPS3']
2MASS: ['J', 'H', 'Ks']
JWST: in the frame of 'f090w', or 'f322w2'. 

Please include errors as 'e_' + filter name; e.g. 'e_f090w'

All columns must be in Vega mags.

If you have labels already known, these should be under the column: 'Label'
The labels should match the following:
0: YSOs
1: MS
2: SGB
3: RGB
4: CHeB
7: EAGB
8: TP-AGB
10: Galaxies
11: Brown Dwarfs
12: White Dwarfs
Similarly, the classes key should match that phrasing. If you wish to just pick things as any field star

Accepts pandas DataFrames or Astropy Tables.