# chname

chname renames files in powerful ways.

```
Usage:
    chname [options] [<files>...]

Options:
    -a, --append=<suffix>                      Suffix to be appended
    -d, --delimiter=<delimiter>                Specifies the delimiter for fixing numerical filenames
    --directory=<directory>                    Destination directory [default: .]
    -f, --fix=<maximum number of digits>       Fixes numerical file names
    -h, --help                                 Show this help screen
    -l, --lower                                Translates the filenames to lowercase
    --merge                                    Merges the files in order specfied on command line
    -o, --order                                Take any input files and renames them in numerical order
    -p, --prepend=<prefix>                     Prefix to be prepended
    --random                                   Randomizes the files
    -r, --remove=<pattern>                     Pattern to be removed, can be a regex
    -q, --quiet                                Quiet mode
    -s, --substitute=<substitution pattern>    Substitutes a pattern (old/new, old can be a regex)
    -t, --test                                 Test mode (Just prints the rename operations)
    --titles=<input file with titles>          Rename the files by names in the specified input file
    --usage                                    Detailed usage information
    -v, --verbose                              Verbose mode
    --version                                  Prints the version
```

## Installation

```bash
pip install chname
```

## License

chname is freeware released under the [MIT License](https://github.com/scholnicks/chname/blob/main/LICENSE).
