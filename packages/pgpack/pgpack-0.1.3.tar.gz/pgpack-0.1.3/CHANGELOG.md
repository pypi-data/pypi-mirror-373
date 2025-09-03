# Version History

## 0.1.3

* Add PGParam class
* Add values length and numeric precision/scale
* Add pgparam attibute into PGPackReader and PGPackWriter
* Fix ZSTD unpacked length where write with to_python() method
* Update requeriments.txt

## 0.1.2

* Rename project to pgpack
* Rename classes from PGCrypt* to PGPack*
* Change header to b"PGPACK\n\x00"
* Add size parameter into to_python, to_pandas, to_polars and to_bytes methods
* Update requirements.txt
* Fix nan values from pandas.DataFrame

## 0.1.1

* Add CHANGELOG.md
* Update README.md
* Improve ZstdDecompressionReader.seek() method

## 0.1.0

* Add methods from_python(),  from_pandas(),  from_polars() to PGPackWriter
* Add detect_oid function for generate oids from python types
* Add metadata_from_frame function
* Rename dtypes to pgtypes
* Change PGDataType to PGOid in pgtypes
* New __str__ and __repr__ output in PGPackReader and PGPackWriter

## 0.0.4

* Add support CopyByffer object as buffer

## 0.0.3

* Remove columns count from __str__ method

## 0.0.2

* Fix ZstdDecompressionReader.readall()
* Add docstring into __init__.py
* Improve docs
* Publish library to Pip

## 0.0.1

First version of the library pgcrypt
