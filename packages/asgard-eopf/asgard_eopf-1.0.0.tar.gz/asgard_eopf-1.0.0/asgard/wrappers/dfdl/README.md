## How to add new packet formats?

* Write/Adapt the DFDL schema of your packet format (examples in the `schemas` folder)
* Modify/Call the script `build_parsers.sh` to generate parser C code. This script makes use of:
  - daffodil (version >= 3.6)
  - pxdgen

* A patch file `schema/custom.patch` can be modified to inject specific modifications on generated code

* Copy the generated code from `schema/output` to this folder

Note: to indicate that your packet format has a constant size, you may add it in your schema at
location `schema/annotation/documentation/fixedSizeSchema`. Size is expressed in bytes. See for
example `s3_navatt.dfdl.xsd`.

* Rebuild using `make` or build the whole ASGARD package.

## Caveats

The s3_slstr_slt.dfdl.xsd is using a dynamic structure. Each packet can have a different type and
size. The schema uses a `xs:choice` with `dfdl:discriminator`. Some arrays have dynamic lengths
defined by DFDL expression.

Unfortunately, the daffodil C code generator doesn't handle properly theses features. I have to
manually fix the evaluation of DFDL expression in:

* `array_array_slstrScanEncoderArray_scanpos_slstrData__getArraySize`
* `array_array_slstrBandArray_band_slstrData__getArraySize`

Also, I implemented the switch/case corresponding to the `xs:choice` in:

* `sourceData_ispType__parseSelf`
* `sourceData_ispType__unparseSelf`


## Generating PXD files

The generation of PXD files is simplified with pxdgen. To make it work, you have to install the 
same clang version as the one used by the Python bindings.

After installing Clang on your system, if you still get a message like `libclang-16.so not found`,
you can add a symlink to the actual Clang library. In my case, for instance:

```
/usr/local/lib/libclang-16.so -> /usr/lib/x86_64-linux-gnu/libclang-16.so.16.0.6
```
