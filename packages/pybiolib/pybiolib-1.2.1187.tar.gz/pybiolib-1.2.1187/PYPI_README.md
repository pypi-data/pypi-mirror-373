# PyBioLib

PyBioLib is a Python package for running BioLib applications from Python scripts and the command line.

### Python Example
```python
# pip3 install -U pybiolib
import biolib
samtools = biolib.load('samtools/samtools')
print(samtools.cli(args='--help'))
```

### Command Line Example
```bash
pip3 install -U pybiolib
biolib run samtools/samtools --help
```
