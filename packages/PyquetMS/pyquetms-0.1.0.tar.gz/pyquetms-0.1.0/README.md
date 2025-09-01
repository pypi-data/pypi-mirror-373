# Pyquet

Memory-efficient mzML to Parquet converter for mass spectrometry files.

## Overview

Pyquet provides streaming conversion of mzML files to Parquet format with minimal memory usage, making it suitable for processing large mass spectrometry datasets without running out of memory. This project was originally developed as a side project inspired by GSoC 25' with OpenMS, with the goal of providing a simple CLI for converting .mzML to .parquet files, which is especially important in big data projects (e.g., machine learning).

## Installation

### From PyPI

```bash
pip install pyquet
```

### From source

```bash
git clone https://github.com/Avni2000/pyquet.git
cd pyquet
pip install .
```

### Development installation

```bash
git clone https://github.com/Avni2000/pyquet.git
cd pyquet
pip install -e ".[dev]"
```

## Usage

### CLI

Basic conversion:
```bash
pyquet input.mzML
```
or
```bash
pyquet ~/Downloads/input.mzML
```

Specify output file (defaults to working directory):
```bash
pyquet input.mzML -o output.parquet
```

Customize batch size and compression. I recommend :
```bash
pyquet input.mzML --batch-size 5000 --compression gzip
```

Get file information without converting:
```bash
pyquet input.mzML --info
```

## Output Format

The converted Parquet files contain the following columns:

Depending on the type of mzml file, we have slightly different columns. 
Some columns may be blank, which is perfectly okay! It doesn't mean your mzml is wrong. 
The main expected values are time, m/z, and intensity

## Contributions

It's quite a small project, feel free to make a PR or open an issue!
