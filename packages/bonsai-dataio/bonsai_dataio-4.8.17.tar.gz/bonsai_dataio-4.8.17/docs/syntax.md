# Metadata syntax

Metadata in the dataio package is a dictionary where most fields are optional and are compliant with the frictionless framework. In what follows we emphasize the ones which are mandatory and which are not compliant with the frictionless framework. We also elaborate on recommended choices of table field and record values. The chapter is organized as follows:

1. [Base level](syntax-base) describes base-level fields.
2. [Table](syntax-table) describes subfields of a 'tables' list element.
3. [Field](syntax-field) describes subfields of a 'fields' list element.
4. [Foreign keys](syntax-foreign) describes subfields of a 'foreignKeys' list element.

(syntax-base)=
## Base level

We show a non-exhaustive list of base-level keys in figure 1. An asterisk (*) denotes the ones which the follow-up text elaborates upon. Identity (=) indicates a default value. Colon (:) indicates type.

```
metadata/
  ├── datapackages (*) : list
  │     └── <table> : dict
  │           ├── name : str
  │           ├── path : str
  │           └── version : str
  ├── encoding = utf-8 : str
  ├── format = csv : str
  ├── hashing = md5 : str
  ├── name (*) : str
  ├── path (*) : str
  ├── tables/ (*) : list
  │     └── <table> : dict
  ├── scheme = file : str
  ├── target_language = eng : str
  ├── timestamp (*) : datetime
  └── version = v0.0.0 (*) : str
```
Figure 1. Metadata base-level keys.

- `datapackage`: list of dictionaries with 'name', 'path' and 'version' of any datapackage referenced in foreign keys.
- `name`: alphanumeric string, eventually with underscore, '_', besides letters and numbers, starting with a letter, and with no spaces. This is used for internal referencing.
- `path`: path of datapackage relative to a root which is common to different datapackages.
- `tables`: list of tables in the datapackage, the syntax of a particular table is described below.
- `timestamp`: date and time of datapackage creation.
- `version`: semantic version of this datapackage release, of the form 'vMAJOR.MINOR.PATCH'.

Extra fields can be added. Fields `parameters` and `config` are used in the GettingTheDataRight project to handle dependencies. Fields `description` and `comments` should be used for long text strings. Extra fields can be added. Fields `description` and `comments` should be used for long text strings. Run `validate()` to check whether the desired field is not already taken by frictionless.


(syntax-table)=
## Table

Figure 2 shows a non-exhaustive list of 'table' keys, using the same conventions as in figure 1.

```
<table>/
  ├── dialect (*) : dict
  │     └── csv : dict
  │           ├── delimiter : str
  │           ├── quoteChar : str
  │           └── skipInitialValue : bool
  ├── encoding = utf-8 : str
  ├── format = csv : str
  ├── mediatype = tet/csv : str
  ├── name (*) : str
  ├── path (*) : str
  ├── schema/ (*) : list
  │     ├── fields (*) : list
  │     │     └── <field> : dict
  │     ├── primarykeys = ['id'] (*): list of strings
  │     └── foreignKeys (*) : list
  │           └── <foreign_key> : dict
  ├── scheme = file : str
  ├── tabletype (*) : str
  └── type = table : str
```
Figure 2. Subfields of a 'tables' list entry.

- `dialect`: special characters to parse file fields. 'delimiter' = separator between fields, 'quoteChar' = symbol that starts and terminates strings, 'skipInitialValue' = True if there is a space after the delimiter and before the field starts (to be avoided).
- `name`: used for internal referencing, same rules as base-level `name`.
- `path`: path of table file relative to the datapackage folder.
- `schema`: schema of the table, has two mandatory fields ('fields' and 'primaryKeys') and one optional ('foreignKeys').
- `fields`: list of fields. A particular field is described below.
- `primaryKeys`: list of primary keys. If 'tabletype' is different from 'other', primaryKeys: [id].
- `foreignKeys`: list of foreign keys. A particular foreign key is described below.
- `tabletype`: should be one of [other, fact, dimension, tree, concordance]. If different from 'other':
    - function dataio.describe() and dataio.validate() will information about fields, primary and foreign keys;
    - 'name' of table should have prefix in [fact_, dim_, tree_, conc_], respectively for 'tabletype' in [fact, dimension, tree, concordance].

Extra fields can be added. Fields `description` and `comments` should be used for long text strings. Run `validate()` to check whether the desired field is not already taken by frictionless.

(syntax-field)=
## Field

Figure 3 shows the list of 'field' keys, using the same conventions as in figure 1.

```
<field>/
  ├── name (*) : str
  └── type (*) : str
```
Figure 3. Subfields of a 'fields' list entry.

- `name`: used for internal referencing, same rules as base-level `name`. If 'tabletype' is not 'other' should comply with constraints described below.
- `type`: type of field, should be one of [boolean, integer, number, string].

The following field names are expected, depending on table type:
- If 'tabletype' = 'fact':
    - `id`: mandatory; string; primary key
    - `<name>`: optional; string; foreign key to file `<name>.csv`
    - `value`: mandatory; number

- If 'tabletype' = 'dim':
    - `id`: mandatory; string; primary key
    - `position`: mandatory; integer

- If 'tabletype' = 'tree':
    - `id`: mandatory; string; primary key
    - `parent_id`: mandatory; string; foreign key to field `id`

- If 'tabletype' = 'conc':
    - `id`: mandatory; string; primary key
    - `<name0>`: mandatory; string; foreign key to `<name0>.csv`
    - `<name1>`: mandatory; string; foreign key to `<name1>.csv`

All table types can have optional field that will not be intepreted
as foreign keys, of type string and of name:
- name
- description
- comment

(syntax-foreign)=
## Foreign key

Figure 4 shows the list of 'foreign_key' keys, using the same conventions as in figure 1.

```
<foreign_key>/
  ├── fields (*) : list
  └── reference (*) : dict
        ├── fields (*) : list of strings
        ├── table (*) : str
        ├── datapackage (*) : str
        ├── direction (*) : str
        └── style (*) : str
```
Figure 4. Subfields of a 'fields' list entry.

- `fields`: list with a single element, the name of the field with the foreign key in the child table.
- `reference`: information about the child table, has one mandatory key, 'fields', and two optional ones, 'table' and 'datapackage'.
- `fields`: list with a single element, the name of the field with the primary key in the parent table.
- `table`: name of the parent table, can be ommitted if the parent and child tables are the same.
- `datapackage`: name of the parent datapackage, can be ommitted if the parent and child datapackages are the same.
- `direction`: used by dataio.plot(), accepted values are ['forward', 'back'] (the former means left-to-right, the latter the reverse).
- `style`: used by dataio.plot(), accepted values are ['solid', 'invis'] (the latter meaning 'invisible'). 

Function dataio.describe() infers a foreign key if the first n characters of a child table field name match the full name of a table in the datapackage. For example, if table 'fact_trade' has field 'dim_region_source' and there is a separate 'dim_region' table, the function will assume there is a foreign key. Function dataio.describe() infers a self foreign key if there is a field is called 'parent_id'. Both cases are illustrated in the tutorial.