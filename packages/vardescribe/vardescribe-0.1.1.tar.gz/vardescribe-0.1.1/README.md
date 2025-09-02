# vardescribe

A simple Python utility to describe the structure, types, and summary statistics of a variable. The generated report is printed to the console and automatically copied to your clipboard.
Intended usage includes sharing the variable description with an LLM or another person for easy collaboration.
The function does not use or access an LLM to generate the description.

## Details
Printed descriptions includes:
* variable name
* shape
* dtype
* summary statistics.
* Pandas DataFrame adds column names

Clipboard Integration: Automatically copies the description to the clipboard for easy pasting into documents, notes, or chat applications (currently supports Windows).

Tested on:
* Windows, VSCode
* Simple variables, Pandas DataFrames, Numpy arrays

## Getting Started

### Dependencies
Required
* numpy
```pip install numpy```

Optional
* Pandas: Required for describing DataFrame objects. If Pandas is not installed, vardescribe will function correctly for all other types.
```pip install pandas```

### Installing

install vardescribe directly from GitHub using pip:
```pip install git+https://github.com/IgorReidler/vardescribe.git```

### Usage
1. Import vardescribe: ```from vardescribe import vardescribe```
2. Use it by passing a variable: ```vardescribe(variable_name)```

## Author
Igor Reidler
igormail@gmail.com

## Version History
* 0.1
    * Initial Release

## License
This project is licensed under the [MIT] License - see the LICENSE.md file for details