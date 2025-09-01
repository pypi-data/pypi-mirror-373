# eoq3 - EOQ3 core implementation for python

This implements EOQ3 domains, values, queries and commands in python. 
It is the central module of the EOQ3 implementation for python. 
It contains a ready-to-use domainwithmdb for programmatic model interactions.

## Getting started example 

This example implements the ["Why EOQ?"](https://eoq.gitlab.io/doc/eoq3/10_eoq.html#why-eoq-an-application-example) example and some additional prints of model information.

```python
from eoq3.domainwithmdb import DomainWithMdb
from eoq3.command import Crt, Get,Set #commands
from eoq3.query import Cls,Pth #queries
from eoq3.concepts import * #import constants as CONCEPTS, ....
from eoq3.examples.warehouse import CreateWarehouseM1Model, CreateWarehouseM2Model #creation of example models
# currently PyecoreMdb is the only local domain. eoq3pyecoremdb must be installed.
from eoq3pyecoremdb import PyEcoreMdb #requres pyecoremdb to be installed

# Initialize a local domain
mdb = PyEcoreMdb()
domain = DomainWithMdb(mdb)
# Init warehouse meta and user model
CreateWarehouseM2Model(domain) #open function to see model creation commands
CreateWarehouseM1Model(domain) #open function to see model creation commands
# Would you like to get a list of articles?
articles = domain.Do( Get( Cls('Article') ) )
print("Articles: %s"%(articles))
# Would you like to know which one is sold less than 3-times?
badArticles = domain.Do( Get( Cls('Article').Sel(Pth('sells').Les(3)) ) )
print("Bad articles: %s"%(badArticles))
# You might want to reduce their price by 10%?
nameAndPrice = domain.Do( Get( Cls('Article').Zip([Pth('name'),Pth('price')])))
print("Article prices: %s"%(nameAndPrice))
domain.Do( Set( 
	Cls('Article').Sel(Pth('sells').Les(3)),
	'price',
	Cls('Article').Sel(Pth('sells').Les(3)).Pth('price').Mul(0.9) 
) )
nameAndPrice = domain.Do( Get( Cls('Article').Zip([Pth('name'),Pth('price')])))
print("Article prices: %s"%(nameAndPrice))
# Would you like to see a list of the names of the categories of the badly selling articles sorted by ascendingly?
badCategories = domain.Do( Get( Cls('Article').Sel(Pth('sells').Les(3)).Met('PARENT').Pth('name').Uni([]).Idx('SORTASC') ) )
print(badCategories)
```

This example is available as  https://gitlab.com/eoq/py/pyeoq/Examples/Eoq3/WhyWarehouseExample.py

## Documentation

For more information see EOQ3 documentation: https://eoq.gitlab.io/doc/eoq3/

## pyeoq repository

Pyeoq module's source can be found here: https://gitlab.com/eoq/py/pyeoq

## Author

2024 Bjoern Annighoefer


