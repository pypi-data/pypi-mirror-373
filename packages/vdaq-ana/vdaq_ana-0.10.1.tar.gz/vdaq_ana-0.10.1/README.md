# AliVATA data analysis

This is a collection of data analysis examples

## Python
Data can also be analyzed with python. The philosophy is the same as in C++. There is a `AliVATAData` class to navigate the data and a `AliVATAModule` class that contains the data of a given module.

### `AliVATAData`
`AliVATAData`will get all the information abou the run type, etc.

If the daa file comes from a ScanRun, `AliVATAData` will provide a ScanManager via the `scan_manager`method and will tell if this is this kind of run with the `has_scan` method. In principle, the user does not neet to care about the ScanManager unless there is need of getting information about the number of ScanVariables and their definition.

The most important role of  it will help creating the iterators that help navigating the data. 

* `AliVATAData`is itself an iterator that will yield all the events of all the modules ordered by time.
* `create_module_ierator(mid)` will return an iterator yielding the data from modiel with ID `mid`.
* `create_iterator_at_time(T, [mod_ids])` will return an iterator that starts iteratinig at the given daq_time. The data will be restricted to the modules given in the list. If the list is empty, all the modules will provide data.
* `create_iterator_at_event(ievt, [mod_ids])` will create an iterator that starts at the given event number.
* `ScanManager` is itself an iterator of ScanPoints. Tnis will be retrived via the `AliVATAData.scan_manager`method.
* `create_iterator_at_scan_point(ipoint, [mod_ids])` will create an iterator taht gives all the events in that ScanPoint. 

An example of use:

````python
# We open here the file
vdaq_ana = AliVATAData(fname)

#  Go through all the envents
for evt in vdaq_ana:
	# evt contains the data of the event.
	...
	analyze the event
	...
	

````

If we want to analyze the data of a ScanRun:

````python
# We open here the file
vdaq_ana = AliVATAData(fname)

# loop over the scan points
for ipoint, scP in enumerate(vdaq_ana.scan_iter()):
	point_values.append(scP.values[11])
	
	# loop on all the events of the ScanPoint for module mid
	for evt in vdaq_ana.create_iterator_at_scanpoint(ipoint, mid):
		# evt contains the data of the event
		...
		analyze the data
		...
    

````

### `AliVATAModule`
`AliVATAModule`contains all the information relative to a module. The main role of this object is to analyze the module data.

### Python examples.
There are a number or examples to read data with Python. 

#### Command line programs
- getSpectrum to make a very rough analysis and show the energy distribution.
- show_data to see the raw data in the file.
- getFileInfo to get information about the data file (date, no. of events, etc.)

#### `fit-utils.py`
Some utilities to fit different distributions.

#### `read_data.py`
Shows how to iterate on the data

#### `analyze_data.py`
Reads all events in a file and tries to fit something.

#### `data_spectral_analysis.py`
Makes an spectral analysis of the calibation data.

#### `hold_delay_scan.py`
Example of a ScanRun analysis. Thsi particular one to check the signal variation with Hold Delay parameter.

#### `test_channel_scan.py`
Analysis of a channel scan.

#### `show_data.py`
Useful to spy the data in a file. Also an interesting example of different iterators.


# Vdaq data format
Vdaq stores the data using the HDF5 library.
The data in the output file is organized in different blocks:
   +/header
   +/modules
   +/scan

## The header is described elsewhere.
The header has an attribute with the definition of the run. The run description contains the type of run, the run number the number of events and the time

The header contains 2 groups
### /header/modules
This is a list with the module descriptions. They are encoded as 0xnn0tiii with
   +nn = number of chips
   +t  = data type
   +iii = module identifier

### /header/run_records
Contains the start of run and end of run records.

## The module
The module group has one subgroup per module named with the module ID

   >
   > /modules/iii
   >

where iii is the module ID.

The module group has the _data_ group where the user defined data format resides and the _configuration_ array that contains an array of integers with the configurations values returned by GenModule::write_config(). Finally, there is the pedestal group that contains:

>
>    /modules/iii/pedestals/pedestal - the pedestals
>    /modules/iii/pedestals/noise    - the noise
>

## The scan
The scan block has two records, one that defines the scan (/scan/def) and the second that tells when Vdaq changed to the new scan point and the values of the variables.

>    /scan/def/nevt      - number of events per scanpoint
>    /scan/def/nvar      - number o variables to scan
>    /scan/def/variables - The variable descriptions (type, from, to)  
