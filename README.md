## LLVM Pass List Generator

This **Python 3** script generates a complete list of LLVM Analysis and Transform passes.

The generated list is structured as a JSON file containing pass names and
associated `opt` command, pass parameters and pass dependencies.

For each pass parameter the dictionary contains the associated command, type,
and default value.

The `llvm_passes.json` file contains passes for **LLVM 3.9.1-2**.

To run the script, it is suggested to run:

```
$ git clone https://github.com/llvm-mirror/llvm.git
$ git clone https://github.com/phrb/generate-llvm-pass-list.git
$ cd generate-llvm-pass-list && python generate_llvm_pass_list.py
```
