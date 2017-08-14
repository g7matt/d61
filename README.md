# Aim

Here I consider a task of entity resolution.  In particular, an algorithm is developed to determine
which papers in the `DBLP` collection are the same as papers in the `Google Scholar` collection.
The algorithm is assessed against a gold standard which is supplied.

# Documentation
The development of the algorithm is described in some detail in "DBLP-Scholar Algorithm Development Details.ipynb".
A summary of the results is given in "DBLP-Scholar Summary.ipynb".  These are Jupyter notebooks.  
Instructions for installing and running notebooks may be found at [install](http://jupyter.org/install.html).  Alternatively,
if there are difficulties running these notebooks, then HTML versions are also contained in this distribution
(although, they're obviously non-interactive).

**Note**: don't look at the notebooks directly on GitHub, as whilst they look like they're OK, you won't see any results,
so the notebooks will be somewhat incomprehensible.

# Files

Notebooks
- DBLP-Scholar Algorithm Development Details.ipynb
- DBLP-Scholar Summary.ipynb

HTML versions of the notebooks
- DBLP-Scholar Algorithm Development Details.html
- DBLP-Scholar Summary.html

Data Files
- DBLP-Scholar\_perfectMapping.csv
- DBLP1.csv
- Scholar.csv

### Code
File                 | Description
:--------------------|:-------------
main.py              | The main entry point for the development notebook.
top.py               | The main entry point for the summary notebook.
paper.py             | A class for representing a paper.
paper\_collection.py | A class for representing a collection of papers.
matcher.py           | Classes for modelling paper-matching functions, allowing the functions to be composed.
match\_results.py    | A class for holding the results of a match in such a way to facilitate analysis.
scorer.py            | A couple of classes for evaluating and presenting matches.
utils.py             | The edit\_distance() function.
venues.py            | Some utility functions for processing venue data.
