# Future developments

The dataio package currently wraps frictionless validate and describe and graphviz plotting, and allows creating, loading and saving datapackages in, to and from Python, where tables are pandas dataframes. Possible future developments are as follows:

1. Refactoring [current](future-current) functionalities.
2. Expanding [datapackage](future-datapackage) functionalities.
3. Creating [database](future-database) functionalities.

(future-current)=
## Current functionalities

The six current functionalities (validate, describe, plot, create, load, save) are presented as functions, since the first two are wraps around frictionless functionalities that work directly on files. The other ones can in principle be presented as methods of the DataPackage class, but the interface then becomes asymmetric, which harms the user experience. To move all functionalities to methods is doable but requires some thought on how to ensure consistency between the live and stored versions of the datapackage, as well as to have have a seamless user experience with full and empty versions of DataPackage objects.

One option is to use have a DataPackage class whose __init__() method corresponds to create, to have load() as a @classmethod, save() as a standard method, and validate(), describe() and plot() as @staticmethod; in all cases roughly keeping the current arguments. A @classmethod allows returning an object as my_datapackage = DataPackage.load(full_path), and the staticmethods allow performing the relevant action without instantiating any object, e.g., DataPackage.describe(full_path).

There are several types of path when handling DataPackage objects: 'root_path' = path from the current working directory (or absolute path) to the root of the database; datapackage 'path' (field in the base level of metadata) = path from root of database to datapackage; table 'path' (field in an item of the 'tables' metadata field); 'full_path' = path from current working directory (or absolute path) to the dataio.yaml file. Most functionalities were organized around 'full_path' because in some cases it is the only option, and the other cases were arranged that way to ensure a similar user experience. The organization of paths in parameters and the naming of paths can naturally be revised.

Plotting might require more parameters for fine-tuning.


(future-datapackage)=
## Additional functionalities

It would be convenient to have functionalities wrapping pandas and numpy to convert a datacube in matrix format to a star-schema representation (fact and dimension tables) and vice-versa.

It would be convenient to have a functionality that would use the metadata foreign keys to join tables and extract selected fields and records.

It would be convenient to handle .zip files besides .csv. More modern compact formats like parquet are probably not an option since their internal architecture is very different from frictionless. 

It would be convenient to allow multiprocessing, in particular for loading and saving files. If it turns out that the package is slow it is relatively easy to explore that possibility. 

(future-database)=
## DataBase class

Besides the DataPackage class it would be convenient to have a DataBase class, which would hold DataPackage objects as instances, with methods that propagate actions across datapackages. For example: recursively loading parent datapackage; a join method for foreign keys across datapackages.



