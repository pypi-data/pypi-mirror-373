# eoq3pyecoremdb - pyecore-based MDB for EOQ3

This is a model database (MDB) for EOQ3 based on the [pyecore](https://github.com/pyecore/pyecore) framework, but with full compatibility to EOQ3's CRUD interface and Concepts. 
		
## Usage

    from eoq3pyecoremdb import PyEcoreMdb #requres pyecoremdb to be installed
    
	mdb = PyEcoreMdb()
	domain = DomainWithMdb(mdb)

Access to CRUD interface. This is normally not recomended, because it bypasses the domain.

    mdb.Create(classId, createArgs, target, recoveryArgs)
	mdb.Read(target, featureName, context)
    mdb.Update(target, featureName, value, position)
    mdb.Delete(self, target)
	
## Implementation

Large parts of the wrapper between pyecore an EOQ3 are generated from the concepts generation. To regenerate use:

    gen/generatepyecoremdb.py

## Documentation

For more information see EOQ3 documentation: https://eoq.gitlab.io/doc/eoq3/

## Author

2024 Bjoern Annighoefer

