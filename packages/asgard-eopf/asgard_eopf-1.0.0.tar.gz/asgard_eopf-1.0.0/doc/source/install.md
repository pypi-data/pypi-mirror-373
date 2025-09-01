# Installation Procedure 

## Overall architecture
This manual details the installation procedure for ASGARD and ASGARD-Legacy (which contains
the implementations based on legacy COTS EOCFI and SXGEO) and there dependencies.

Here is a snapshot of ASGARD and ASGARD-Legacy main dependencies:

![](doc/source/resources/dependencies_map.png)

The standard Python dependencies (Numpy, ...) are not shown here for clarity, only the ones not
available on public repository.


### Dependancies

ASGARD is running with `python3.11` and depends on:

* jsonschema, numpy, netcdf4, scikit-learn, forbiddenfruit, lxml, s3fs
* zarr
* PyRugged
* Orekit-jcc

#### PyRugged

PyRugged is a Python port of Java Rugged. The refactored products and low-level API make use of this
implementation of Rugged (not the Java one). It is supplied as a Python wheel from the
[PyRugged package repository](https://gitlab.eopf.copernicus.eu/geolib/pyrugged/-/packages)

It may also be rebuilt from sources, the only non-standard dependency is Orekit-JCC which provides the bindings to Orekit.

#### Orekit-JCC

Orekit-JCC is an interface layer between ASGARD/pyrugged and Orekit. It is a Java project compiled and wrapped to Python using JCC and GraalVM. It is supplied as Python wheel, by the [Orekit-JCC package registry](https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc/-/packages/).

It may also be rebuilt from sources. Its build requirements are:

* Java 8 JDK (with `$JAVA_HOME` pointing to JDK install)
* JCC >= 3 (available on Pypi)
* GCC >= 8
* Graalvm Community Openjdk-17
* Maven


## ASGARD installation procedures

This part is split into 3 sections:
* [Manual installation using downloaded wheels](#manual-installation-using-downloaded-wheels)
* [Automatic installation using pip](#automatic-installation-using-pip)
* [Installation guide for developers](#installation-guide-for-developers)

Note: there is a name conflict for "asgard" on the public repository. If you use `pip` to install
ASGARD from a repository, make sure you use the package named **asgard-eopf**.

### Manual installation using downloaded wheels
Download all wheels from the GEOLIB repository:

* [Orekit-JCC package registry](https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc/-/packages/)
* [PyRugged package repository](https://gitlab.eopf.copernicus.eu/geolib/pyrugged/-/packages)
* [ASGARD package repository](https://gitlab.eopf.copernicus.eu/geolib/asgard/-/packages)

Then follow the procedure below (Requirements will automatically be installed during wheels' installations):
```sh
# Create a Virtual venv with python3.11 and activate it
python3.11 -m venv [VENV_NAME]
source path/to/[VENV_NAME]/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install orekit-jcc from wheel
pip install /path/to/orekit_jcc*.whl

# Install pyrugged from wheel
pip install /path/to/pyrugged*.whl

# Install asgard from wheel
pip install /path/to/asgard_eopf*.whl
```

After doing this procedure once, only the activation of the venv is necessary:
```sh
# Activate the VENV
source path/to/[VENV_NAME]/bin/activate
```

### Automatic installation using pip

In order to be able to use the `pip install` command, pip needs to be configurated to make it aware of multiple private packages hosted on the EOPF GitLab,
It can be done either by:

* `Install through basic pip`
* `Install by setting up the pip extra_index_url environment variable`

#### Install through basic pip

```sh
# Create a Virtual venv with python3.11 and activate it
python3.11 -m venv [VENV_NAME]
source path/to/[VENV_NAME]/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install orekit-jcc from package repository
pip install orekit-jcc==[OREKIT_JCC_VERSION] --index-url https://gitlab.eopf.copernicus.eu/api/v4/projects/94/packages/pypi/simple

# Install pyrugged from package repository
pip install pyRugged==[PYRUGGED_VERSION] --index-url https://gitlab.eopf.copernicus.eu/api/v4/projects/78/packages/pypi/simple

# Install ASGARD from package repository
pip install asgard-eopf==[ASGARD_VERSION] --index-url https://gitlab.eopf.copernicus.eu/api/v4/projects/52/packages/pypi/simple
```

After doing this procedure once, only the activation of the venv is necessary:
```sh
# Activate the VENV
source path/to/[VENV_NAME]/bin/activate
```

#### Install by setting up the PIP_EXTRA_INDEX_URL environment variable.

Setting the PIP_EXTRA_INDEX_URL environment variable makes pip knowledgeable of where to look private packages
that exist on the EOPF GitLab but not on PyPI.

Copy-paste the following lines in your terminal:

```sh
EOPF_ASGARD_EXTRA_INDEX_URL="https://gitlab.eopf.copernicus.eu/api/v4/projects/14/packages/pypi/simple"
EOPF_PYRUGGED_EXTRA_INDEX_URL="https://gitlab.eopf.copernicus.eu/api/v4/projects/78/packages/pypi/simple"
EOPF_OREKITJCC_EXTRA_INDEX_URL="https://gitlab.eopf.copernicus.eu/api/v4/projects/94/packages/pypi/simple"

export PIP_EXTRA_INDEX_URL="
${EOPF_ASGARD_EXTRA_INDEX_URL}
${EOPF_PYRUGGED_EXTRA_INDEX_URL}
${EOPF_OREKITJCC_EXTRA_INDEX_URL}
"
```

**Optional: Persist the environment variable in the `.bashrc` file (Linux-only)**:
```sh
#Add the lines from the previous section at the end of the `.bashrc` file.
[ACTION_TO_COPY]

# Reload your `.bashrc` in your current session:
source ~/.bashrc
```
* The main benefit of this option is that once it is set up, every time a new terminal is opened, the environment variables will already be set. This can also be useful if working with otherprojects dependening on the EOPF and related dependencies.
* Now, if you reopen a terminal, the extra index URLs will already be set thanks to the `~/.bashrc`.

You can then install ASGARD directly with the pip install command:
```sh
# Create a Virtual venv with python3.11 and activate it
python3.11 -m venv [VENV_NAME]
source path/to/[VENV_NAME]/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install orekit-jcc from package repository
pip install orekit-jcc==[OREKIT_JCC_VERSION]

# Install pyrugged from package repository
pip install pyRugged==[PYRUGGED_VERSION]

# Install ASGARD from package repository
pip install asgard-eopf==[ASGARD_VERSION]
```

After doing this procedure once, only the activation of the venv is necessary:
```sh
# Activate the VENV
source path/to/[VENV_NAME]/bin/activate
```

### Installation guide for developers

In this section, all libraries are built from sources, including [pyrugged](https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc) and
[orekit-jcc](https://gitlab.eopf.copernicus.eu/geolib/pyrugged). Depending on the needs, these steps can be skipped and installation of those libraries can be done through wheels available on gitlab.

#### Installation preparation
First, some additional libraries and necessary system dependencies shall be installed:
```sh
sudo apt-get install python3.11-venv python3.11-dev gcc g++ git unzip
```

Then, clone [ASGARD repository](https://gitlab.eopf.copernicus.eu/geolib/asgard),
[pyrugged repository](https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc) and
[orekit-jcc repository](https://gitlab.eopf.copernicus.eu/geolib/pyrugged) 
```sh
git clone https://gitlab.eopf.copernicus.eu/geolib/asgard.git
git clone https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc.git
git clone https://gitlab.eopf.copernicus.eu/geolib/pyrugged.git
```

Instead of cloning orekit_jcc and PyRugged, installation can be done through 
```sh
cd asgard

python3.11 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install pytest-xdist wheel cython
# v11.4 @ https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc/-/packages/
python3 -m pip install orekit-jcc --index-url https://gitlab.eopf.copernicus.eu/api/v4/projects/94/packages/pypi/simple
# v1.0.4.post22 @ https://gitlab.eopf.copernicus.eu/geolib/pyrugged/-/packages/
python3 -m pip install pyRugged --index-url https://gitlab.eopf.copernicus.eu/api/v4/projects/78/packages/pypi/simple
python3 -m pip install -e . --group dev
```

Here, `pip install -e` install the project in editable mode (i.e. setuptools "develop mode").
The "editable mode" is required since cython shared objects need to be kept in place to be able to import the project
in [*flat-layout*](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
*ie*. if `-e` option is not set, you might get `ImportError: no module named asgard.core.math` error,
because the locally built cython binary is deleted after the package installation.

**NOTE**: You can also install the notebook dependencies: `pip install -e . --group notebook`
or the default mode by providing nothing: `pip install -e .`


**LinuxMint users**: please refer to [this link](https://forums.linuxmint.com/viewtopic.php?f=42&p=2103213)
to install specific python version without overwritting the python system version:
In this case you can run this for environment management:
`pyenv virtualenv [PYTHON_VERSION_INSTALLED] ASGARD_VENV` and
`pyenv activate [NOM_DU_VENT]` instead of running `python3.11 -m venv`.


#### Tests and validation

The tests and validation data can be found on S3 bucket, and should be located
in a folder referred by the environment variable: `export ASGARD_DATA=[PATH_TO_ASGARD_DATA]`.
Please ask the credentials and use the script `gitlab-ci/download.py` to download them.

This step can take a while since it needs to download 29GB, once done,
you can run `pytest` command to check if ASGARD is well installed.

## Installation procedure for ASGARD-Legacy 

As ASGARD-Legacy depends on ASGARD, but also on [SXGEO](https://gitlab.eopf.copernicus.eu/geolib/sxgeo) (Java Rugged/Orekit interface) and [EOCFI](https://eop-cfi.esa.int/Repo/PUBLIC/DOCUMENTATION/CFI/EOCFI/) (Earth Observation Customer Furnished Item), the most suitable way to install asgard-legacy is using a docker container.

Note: there is a name conflict for "asgard" on the public repository. If you use `pip` to install
ASGARD from a repository, make sure you use the package named **asgard-eopf**.

You can pull the asgard-build-environment image which contains the following dependencies installed 
* EOCFI (static library)
* GDAL 3.6.2 with java bindings
* Java 8 JDK
* JCC
* Maven

To use this image, run the command

```sh
# Pull the environment docker
docker pull registry.eopf.copernicus.eu/geolib/asgard-build-environment
```

Then you have several choices of installation methodes:
* [Manual installation using downloaded wheels](#manual-installation-using-downloaded-wheels-1)
* [Automatic installation using pip](#automatic-installation-using-pip-1)
* [Installation guide for developers](#installation-guide-for-developers-1)

### Manual installation using downloaded wheels
Download all wheels from the GEOLIB repository:

* [Orekit-JCC package registry](https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc/-/packages/)
* [PyRugged package repository](https://gitlab.eopf.copernicus.eu/geolib/pyrugged/-/packages)
* [ASGARD package repository](https://gitlab.eopf.copernicus.eu/geolib/asgard/-/packages)
* [SXGEO package repository](https://gitlab.eopf.copernicus.eu/geolib/sxgeo/-/packages)
* [ASGARD-Legacy package repository](https://gitlab.eopf.copernicus.eu/geolib/asgard-legacy/-/packages)

Then follow the procedure below (Requirements will automatically be installed during wheels' installations):
```sh
# Create a Virtual venv with python3.11 and activate it
python3.11 -m venv [VENV_NAME]
source path/to/[VENV_NAME]/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install orekit-jcc from wheel
pip install /path/to/orekit_jcc*.whl

# Install pyrugged from wheel
pip install /path/to/pyrugged*.whl

# Install ASGARD from wheel
pip install /path/to/asgard_eopf*.whl

# Install SXGEO from wheel
pip install /path/to/sxgeo*.whl

# Install ASGARD-Legacy from wheel
pip install /path/to/asgard_legacy*.whl
```

After doing this procedure once, only the activation of the venv is necessary:
```python
# Activate the VENV
source path/to/[VENV_NAME]/bin/activate
```

### Automatic installation using pip

In order to be able to use the `pip install` command, pip needs to be configurated to make it aware of multiple private packages hosted on the EOPF GitLab,
It can be done either by:

* `Install through basic pip`
* `Install by setting up the pip extra_index_url environment variable`

#### Install through basic pip

```sh
# Create a Virtual venv with python3.11 and activate it
python3.11 -m venv [VENV_NAME]
source path/to/[VENV_NAME]/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install orekit-jcc from package repository
pip install orekit-jcc==[OREKIT_JCC_VERSION] --index-url https://gitlab.eopf.copernicus.eu/api/v4/projects/94/packages/pypi/simple

# Install pyrugged from package repository
pip install pyRugged==[PYRUGGED_VERSION] --index-url https://gitlab.eopf.copernicus.eu/api/v4/projects/78/packages/pypi/simple

# Install ASGARD from package repository
pip install asgard-eopf==[ASGARD_VERSION] --index-url https://gitlab.eopf.copernicus.eu/api/v4/projects/52/packages/pypi/simple

# Install SXGEO from package repository
pip install sxgeo==[SXGEO_VERSION] --index-url https://gitlab.eopf.copernicus.eu/api/v4/projects/67/packages/pypi/simple

# Install ASGARD-Legacy from package repository
pip install asgard-legacy==[ASGARD_LEGACY_VERSION] --index-url https://gitlab.eopf.copernicus.eu/api/v4/projects/92/packages/pypi/simple
```

After doing this procedure once, only the activation of the venv is necessary:
```sh
# Activate the VENV
source path/to/[VENV_NAME]/bin/activate
```

#### Install by setting up the PIP_EXTRA_INDEX_URL environment variable.

Setting the PIP_EXTRA_INDEX_URL environment variable makes pip knowledgeable of where to look private packages
that exist on the EOPF GitLab but not on PyPI.

Copy-paste the following lines in your terminal:

```sh
EOPF_ASGARD_EXTRA_INDEX_URL="https://gitlab.eopf.copernicus.eu/api/v4/projects/14/packages/pypi/simple"
EOPF_PYRUGGED_EXTRA_INDEX_URL="https://gitlab.eopf.copernicus.eu/api/v4/projects/78/packages/pypi/simple"
EOPF_OREKITJCC_EXTRA_INDEX_URL="https://gitlab.eopf.copernicus.eu/api/v4/projects/94/packages/pypi/simple"
EOPF_SXGEO_EXTRA_INDEX_URL="https://gitlab.eopf.copernicus.eu/api/v4/projects/67/packages/pypi/simple"
EOPF_ASGARD_LEGACY_EXTRA_INDEX_URL="https://gitlab.eopf.copernicus.eu/api/v4/projects/92/packages/pypi/simple"

export PIP_EXTRA_INDEX_URL="
${EOPF_ASGARD_EXTRA_INDEX_URL}
${EOPF_PYRUGGED_EXTRA_INDEX_URL}
${EOPF_OREKITJCC_EXTRA_INDEX_URL}
${EOPF_SXGEO_EXTRA_INDEX_URL}
${EOPF_ASGARD_LEGACY_EXTRA_INDEX_URL}
"
```

**Optional: Persist the environment variable in the `.bashrc` file (Linux-only):**
```sh
#Add the lines from the previous section at the end of the `.bashrc` file.
[ACTION_TO_COPY]

#Reload your `.bashrc` in your current session:
source ~/.bashrc
```
* The main benefit of this option is that once it is set up, every time a new terminal is opened,the environment variables will already be set. This can also be useful if working with otherprojects dependening on the EOPF and related dependencies.
* Now, if you reopen a terminal, the extra index URLs will already be set thanks to the `~/.bashrc`.

You can then install ASGARD directly with the pip install command:
```sh
# Create a Virtual venv with python3.11 and activate it
python3.11 -m venv [VENV_NAME]
source path/to/[VENV_NAME]/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install orekit-jcc from package repository
pip install orekit-jcc==[OREKIT_JCC_VERSION]

# Install pyrugged from package repository
pip install pyRugged==[PYRUGGED_VERSION]

# Install ASGARD from package repository
pip install asgard-eopf==[ASGARD_VERSION]

# Install SXGEO from package repository
pip install sxgeo==[SXGEO_VERSION]

# Install ASGARD-Legacy from package repository
pip install asgard-legacy==[ASGARD_LEGACY_VERSION]
```

After doing this procedure once, only the activation of the venv is necessary:
```sh
# Activate the VENV
source path/to/[VENV_NAME]/bin/activate
```

### Installation guide for developers

Clone the ASGARD-Legacy repository, ASGARD repository and pyrugged repository from the GEOLIB group on the Gitlab, and download orekit-jcc wheel and sxgeo wheel.

Then you can export those environment variables and run the container

```sh
cd $HOME/YOUR/PATH/

export root_dir=$(pwd)
export asgard_dir=$(realpath ./asgard)
export pyrugged_dir=$(realpath ./pyrugged)
export asgard_legacy_dir=$(realpath ./asgard-legacy)
export ASGARD_DATA=$(realpath ./ASGARD_DATA)

docker run -it --rm --name asgard-legacy --user root --network host -v ~/.gitconfig:/root/.gitconfig2 -v ~/.m2:/root/.m2 -v $root_dir:$root_dir -e asgard_dir -e asgard_legacy_dir -e pyrugged_dir -e ASGARD_DATA registry.eopf.copernicus.eu/geolib/asgard-build-environment bash
```

Once inside the container, you can update the bashrc (optionnal) and install the following dependencies:

```sh
# Update bashrc (optionnal)
cat << EOF >> ~/.bashrc
PS1='\u:\W\$ '
alias grep='grep --color=auto'
alias ll='ls -alh --color=always'
alias pytest="pytest -W=ignore::DeprecationWarning:importlib._bootstrap"
EOF

source ~/.bashrc

# Use of git credentials inside docker
cp ~/.gitconfig2 ~/.gitconfig

# Install pytest-xdist in order to run "pytest -n auto" in order to launch unit tests in multi-threads

python3 -m pip install --upgrade pip

pip install pytest-xdist
python3 -m pip install cython

# Add git safe directories
for d in "$asgard_dir" "$asgard_legacy_dir" "$pyrugged_dir"; do
    git config --global --add safe.directory "$d"
done

# Build orekit-jcc
python3 -m pip install path/to/orekit_jcc-*.whl

# Build SXGEO
python3 -m pip install path/to/sxgeo-*.whl

# Build pyrugged
python3 -m pip install $pyrugged_dir # Or install wheel package as orekit-jcc and sxgeo

# Build asgard
python3 -m pip install $asgard_dir

# Build asgard-legacy
cd $asgard_legacy_dir
python3 -m pip install -e . --group dev
```

You can now run `pytest` command in order to check if ASGARD-Legacy is well installed.

As you can see `asgard-legacy` wheel required `asgard` and `sxgeo`. The EOCFI binaries are statically linked in a Cython extension and embedded in the wheel.

All these wheel should be available in the dedicated project repository on Gitlab. In case you need
to rebuild them, the following section detail the requirements for each package.


#### Orekit-JCC

Orekit-JCC is an interface layer between ASGARD/pyrugged and Orekit. It is a Java project compiled 
and wrapped to Python using JCC and GraalVM. It is supplied as Python wheel, by the 
[Orekit-JCC package registry](https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc/-/packages/).

Users also have the option to rebuild it from source. Its build requirements are:

* Java 8 JDK (with `$JAVA_HOME` pointing to JDK install)
* JCC >= 3 (available on Pypi)
* GCC >= 8
* Graalvm Community Openjdk-17
* Maven


The repository
[asgard-build-environment](https://gitlab.eopf.copernicus.eu/geolib/asgard-build-environment)
provides an example of environment used to build the ASGARD stack.

The java dependencies (Rugged, Orekit, hipparchus, ...) are retrieved using maven.

The build procedure is:

```bash
git clone https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc.git
cd orekit-jcc
export GRAALVM_INSTALL=/path/to/graalvm-community-openjdk-17.0.7+7.1
bash ./build_jcc_graalvm.sh
```

You should get the Orekit-JCC wheel package in folder `dist`:

```bash
pip install dist/orekit_jcc-[...].whl
```

Note: due to the nature of JCC bindings, there can be only ONE JCC-built package imported in Python.
You will encounter an error if you try to import both SXGeo and Orekit-JCC. This problem is
automatically avoided in ASGARD:
* If no JCC wrapping have been imported, it uses Orekit-JCC as default
* ASGARD can work with either wrappings, because SXGeo provides a superset of Orekit-JCC.
* In ASGARD-Legacy, we force the import of SXGeo before importing ASGARD, so that we rely on the
  SXGeo wrapping.

#### Build SXGEO from sources

SXGeo is an interface layer between ASGARD and Rugged/Orekit. It is a Java project compiled and
wrapped to Python using JCC and GraalVM. It is supplied as Python wheel, by the
[SXGeo package registry](https://gitlab.eopf.copernicus.eu/geolib/sxgeo/-/packages/).

Users also have the option to rebuild it from source. Its build requirements are:

* Java 8 JDK (with `$JAVA_HOME` pointing to JDK install)
* JCC >= 3 (available on Pypi)
* GCC >= 8
* GDAL >= 3, with Java wrappers built with Java 8.
* Graalvm Community Openjdk-17
* Maven

Note: at the runtime, Java will have to load the library `libgdalalljni.so`, which is part of the
GDAL JAVA bindings. You can either:

* add its location to the `LD_LIBRARY_PATH`
* or place a symbolic link to this library in `/usr/lib`

The repository
[asgard-build-environment](https://gitlab.eopf.copernicus.eu/geolib/asgard-build-environment)
provides an example of environment used to build the SXGeo/ASGARD stack.

The java dependencies (Rugged, Orekit, hipparchus, ...) are retrieved using maven. Only GDAL
bindings needs to be copied to maven local repository:

```bash
mkdir -p ~/.m2/repository/org/gdal/gdal/${GDAL_VERSION}
cp gdal*.jar ~/.m2/repository/org/gdal/gdal/${GDAL_VERSION}
```

The build procedure is:

```bash
git clone https://gitlab.eopf.copernicus.eu/geolib/sxgeo.git
cd sxgeo
make sxgeo-jar
export GRAALVM_INSTALL=/path/to/graalvm-community-openjdk-17.0.7+7.1
./python/build_jcc_graalvm.sh
```

You should get the SXGeo wheel package in folder `dist`:

```bash
pip install dist/sxgeo-[...].whl
```

#### Build ASGARD-Legacy from sources

For ASGARD-Legacy, you need to install ASGARD and SXGeo.
In order to build binary extension, you will need:

* Cython
* EOCFI binaries (pointed by `$EE_DIR` environment variable)

The build procedure is then simple:

```bash
git clone https://gitlab.eopf.copernicus.eu/geolib/asgard-legacy.git
cd asgard-legacy
pip install -e .
```