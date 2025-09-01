#!/usr/bin/bash


export CLANG_HEADERS=~/Tools/clang-14.0.6.src/lib/Headers

CUR_DIR="$(dirname $0)"

cd "$CUR_DIR"

# clean output folder before starting
rm -rf temp output

mkdir output

parser_list=$(ls *.dfdl.xsd | grep -v 'DFDLGeneralFormat.dfdl.xsd' | grep -v 'SpacePacketFormat.dfdl.xsd')

for name in $parser_list; do
  echo $name
  short_name=${name%.dfdl.xsd}
  daffodil generate c -s $name temp
  cp temp/c/libruntime/generated_code.c output/generated_${short_name}.c
  cp temp/c/libruntime/generated_code.h output/generated_${short_name}.h
  sed -i "s/generated_code.h/generated_${short_name}.h/" output/generated_${short_name}.c
  # get fixed size if any
  fixed_size="$(grep '<fixedSizeSchema>' ${name} | cut -d '>' -f 2 | cut -d '<' -f 1)"
  echo -e "\nconst int packet_size = ${fixed_size:-0};\n" >> "output/generated_${short_name}.c"
done

rm temp/c/libruntime/generated_code.*

# Copy common files
for name in $(ls temp/c/libruntime); do
  cp "temp/c/libruntime/${name}" output
done

# generate pxd files and trim duplicated typedefs
cd output
for name in $(ls *.h | grep -v 'generated_'); do
  pxdgen "$name" | grep -vE "ctypedef ([a-zA-Z]+) \1" > "$(echo $name | sed 's/.h/.pxd/')"
done

# Apply patches:
#  - remove const qualifier on visitor functions
#  - fix generated code for SLSTR
#  - add extern packet_size
patch -p1 <../custom.patch

# Clean temp dir
cd ..
rm -r temp
