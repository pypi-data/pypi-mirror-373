![](cleanifier_overview.png)


# Cleanifier: Fast lightweight accurate contamination removal

This tool, Cleanifier, uses a probabilistic Cuckoo filter or Cuckoo hash table to efficiently remove contamination of a species from samples.


In case of problems file an issue in the issue tracker.

See CHANGELOG.md for recent changes.
Thank you!

----


# Usage Guide

Cleanifier is a multi-command tool with several subcommands (like git), in particular
- `cleanifier index` builds an index (a bucketed 3-way Cuckoo hash table or Cuckoo filter)
- `cleanifier download` downloads the pre-built human index from Zenodo
- `cleanifier filter` cleans a sample (FASTQ files) using an existing index

It is a good idea to run `cleanifier filter --help` to see all available options.\
Using `--help` works on any subcommand.

### Installation guide

`cleanifier` is available via bioconda. If you have `conda` already installed, you can create a new environment including `cleanifier` by running
```
conda create --name cleanifier -c conda-forge -c bioconda cleanifier
```

Our software can also be obtained by cloning this public git repository:
```
https://gitlab.com/rahmannlab/cleanifier
```
To run our software, a [conda](https://docs.conda.io/en/latest/) environment with the required libraries needs to be created.\
A list of needed libraries is provided in the ``environment.yml`` file in the cloned repository;\
it can be used to create a new environment:

```
cd cleanifier  # the directory of the cloned repository
conda env create
```
which will create an environment named ``cleanifier`` with the required dependencies,
using the provided ``environment.yml`` file in the same directory.

After all dependencies are downloaded, you activate the environment and install the package from the repository into this environment.\
Make sure that you are in the root directory of the cloned repository (where this `README.md` file or the `CHANGELOG.md` file is) and run
```
conda activate cleanifier  # activate environment
pip install -e .  # install cleanifier package using pip
```

### Prebuild index
We provide an index to filter human data.
The index contains all gapped $k$-mers ($k=29,w=33$) of the t2t-reference genome, and in addition, all variants, reported by the 1000 Genome Project, that have an allele frequency of at least `0.01`, all HLA variants from the IPD-IMGT/HLA database and all 47 assemblies from the Human Pangenome consortium.
The index can be downloaded [here](https://doi.org/10.5281/zenodo.15639519).

Alternatively, the index may also be downloaded using the `cleanifier download` command.
To download the index using a probabilistic Cuckoo filter (< 7 GB), run
```
cleanifier download --checksum --dir index_dir
```
which stores the index in the `index_dir` folder (the folder must already exists) and compares the checksum after the download. If you want to store the index in the current directory, don´t provide the `--dir` argument.

To download the exact hash table (13GB), run
```
cleanifier download --version exact --checksum --dir index_dir
```

### How to classify

To clean a FASTQ sample (single-end or paired-end files), make sure you are in an environment where Cleanifier and its dependencies are installed (see **Installation guide**).\
In addition, the index must either be downloaded (here `myindex.filter` and `myindex.info`) or an own custom index was created (see **How to build a custom index**).\
Then run the `cleanifier filter` command with a previously built index, such as
```
cleanifier filter --index myindex --fastq single.fq.gz --prefix myresults
```
for single-end reads, or
```
cleanifier filter --index myindex --fastq paired.1.fq.gz --pairs paired.2.fq.gz --prefix myresults
```
for paired-end reads.

The most important parameter is `--threshold` which defines at which point a read should be filtered out (default `0.5`).\
The filtering depends on the number of bases that are covered by a $k$-mer that is contained in the original set.\
This means, that given a read length of 100 and a $k$-mer size of $k=25$ we should at least pick a threshold of `0.25`. This sorts out a read that already contains a single 25-mer. This also applies to a threshold `<0.25` as 25 bases are always covered by a 25-mer.
For a strict filtering, this can work, but there is a probability that sequencing errors change a $k$-mer in the read to a $k$-mer in the set. If we pick a threshold slightly bigger than the minimum (`0.25`), we need at least 2 or more $k$-mers to be included in the index.\
The default threshold is `0.5`, which performs well on short and long reads.

The parameter `--prefix` or equivalently `--out` is required and defines the prefix for all output files; this can be a combination of path and file prefix, such as `/path/to/sorted/samplename`.

The compression type can be specified using the `--compression` parameter, otherwise it is automatically deduced from the input files.\
Currently we support `gz` (default), `bzip`, `xz` and `none` (uncompressed).\
To write compressed output, the wall time decreases if you increase the compression threads (parameter `--compression-threads`, default 1).


By default, we sample the $k$-mers of a read that overlap the previous one by $k/2$.
In addition we provide a sensitive mode (using the parameter `--sensitive`) which checks all $k$-mers in the read.

Use
```
cleanifier filter --help
```
to get a full list of optional parameters.


### How to build a custom index

To build an index for Cleanifier, several parameters must be provided, which are described in the following.

First, a file name and a path for the index must be chosen.
The index is stored in two files. We will use `myindex` to store the index in the current folder.

Second, all reference genomes that should be removed must be provided (in FASTA files).
These files can be provided as an uncompressed file or compressed using `gzip`, `bzip2` or `xz`.
The corresponding option is `--files`.
Each option can take several arguments as files. 
```
cleanifier index --index myindex --files ref1.fa.gz [ref2.fa.gz ...]
```

We must specify the size of the hash table:

- `-n` or  `--nobjects`: number of k-mers that will be stored in the hash table. This depends on the used reference genomes and must be estimated beforehand! As a precise estimate of the number of different k-mers can be difficult, you can err on the safe side and provide a generously large estimate, examine the final (low) load factor and then rebuild the index with a smaller `-n` parameter to achieve the desired load. There are also some tools that quickly estimate the number of distinct k-mers in large files, such as [ntCard](https://github.com/bcgsc/ntCard) or [KmerEstimate](https://github.com/srbehera11/KmerEstimate). As a guide: The Human genome consists of roughly 2.5 billion 25-mers.
**This option must be specified; there is no default!**


We may further specify additional properties of the hash table:

- `-b` or `--bucketsize` indicates how many elements can be stored in one bucket (or page). This is 4 by default.

- `--fill` between 0.0 and 1.0 describes the desired fill rate or load factor of the hash table.
Together with `-n`, the number of slots in the table is calculated as `ceil(n/fill)`. In our experiments we used 0.88. (The number of buckets is then the smallest odd integer that is at least `ceil(ceil(n/fill)/p)`.)

- `--aligned` or `--unaligned`: indicates whether each bucket should consume a number of bits that is a power of 2. Using `--aligned` ensures that each bucket stays within the same cache line, but may waste space (padding bits), yielding faster speed but possibly (much!) larger space requirements. With `--unaligned`, no bits are used for padding and buckets may cross cache line boundaries. This is slightly slower, but may save a little or a lot of space (depending on the bucket size in bits). The default is `--unaligned`, because the speed decrease is small and the memory savings can be significant.

- `--hashfunctions` defines the parameters for the hash functions used to store the key-value pairs. If the parameter is unspecified, different random functions are chosen each time. The hash functions can be specified using a colon separated list: `--hashfunctions linear945:linear9123641:linear349341847`. It is recommended to have them chosen randomly unless you need strictly reproducible behavior, in which case the example given here is recommended.

The final important parameter is about parallelization:

Most of the parameters can also be provided in a config file (`.yaml`):
- `--cfg` or `--config` defines the path the the config file.


### Reproduce results from the paper

To reproduce all results, check the `workflows` folder for more information.

### Please cite

> Zentgraf, J., Schmitz, J. E., Rahmann, S. (2025). Cleanifier: A fast and lightweight k-mer based tool to remove contamination in microbial sequence data. Biorxiv. <https://doi.org/10.1101/2025.06.24.661305>

If you use our pre-built index, please cite

> Schmitz, J. E., Zentgraf, J., & Rahmann, S. (2025). Human index for Cleanifier (0.1.0). Zenodo. <https://doi.org/10.5281/zenodo.15639519>
