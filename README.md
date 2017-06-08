## Kernel Builder
Kernel Builder is a command line application which automates compiling
the Linux kernel for android devices.

## Project status
Kernel Builder is under active development

## Installation

``` bash
$ make init
$ make install
```

## Usage

Initialize kbuilder and the build environment
```bash
$ kbuilder init
```
[![asciicast](https://asciinema.org/a/123946.png)](https://asciinema.org/a/123946)

Select a compiler to use
```bash
$ kbuilder gcc set
```
[![asciicast](https://asciinema.org/a/4jrgo994uktvcnmos288x6zc2.png)](https://asciinema.org/a/4jrgo994uktvcnmos288x6zc2)

Clean up build files
```bash
$ kbuilder clean
```
[![asciicast](https://asciinema.org/a/123945.png)](https://asciinema.org/a/123945)

Build an OTA package
```bash
$ kbuilder build otapackage
```
[![asciicast](https://asciinema.org/a/123944.png)](https://asciinema.org/a/123944)



