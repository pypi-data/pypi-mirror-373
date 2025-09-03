In 2025/01/09 the Rubidium calculating code was borrowed from  Andrew M. C. Dawes
[rubidium repository](https://github.com/DawesLab/rubidium)

which itself was based on the paper by 
Paul Siddons: Siddons et al. J. Phys. B: At. Mol. Opt. Phys. 41, 155004 (2008).
preprint available: arXiv:0805.1139.

Changes from original:

# 2025/01/09
 - Numpy is used for several math formulas (scipy does not expose them anymore).
 - Pressure calculation formula changed to the one adopted from [Steck](https://steck.us/alkalidata/).
 - Pressure truly returns Pascals (as claimed by the doc string), old formula did it in torr.
 - Density can terurn combinded isotope (total) density, if isotope="all"
 - Do not use unnecessary plotting related imports in the main body

