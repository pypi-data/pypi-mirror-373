#!/bin/bash
#
# Copyright 2023 CS GROUP
# Licensed to CS GROUP (CS) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# CS licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

_path2dem="S3AOLCIdataset/S3__AX___DEM_AX_20000101T000000_20991231T235959_20151214T120000___________________MPC_O_AL_001.SEN3"

# This script fixes a AX___DEM_AX.EEF file after is has been deployed alongside
# the DEM it points to.
#
# Usage:
# - there is a ${_path2dem} directory in ${ASGARD_DATA}, with all the DEM and
#   the .EEF file in it
# - Execute:
#   $> ASGARD_DATA=~/dev/asgard/data ./data/fix-EEF.sh
#
# TODO:
# - Support program options to either the _dem_dir or the _eef_file to use as
# alternative

## Toolbox {{{1
# _is_unset                         {{{2
function _is_unset()
{
    [[ -z ${!1+x} ]]
}

# _die                              {{{2
function _die()
{
   local msg=$1
   [ -z "${msg}" ] && msg="Died"
   # echo "BASH_SOURCE: ${#BASH_SOURCE[@]}, BASH_LINENO: ${#BASH_LINENO[@]}, FUNCNAME: ${#FUNCNAME[@]}"
   printf "${BASH_SOURCE[0]:-($0 ??)}:${BASH_LINENO[0]}: ${FUNCNAME[1]}: ${msg}\n" >&2
   for i in $(seq 2 $((${#BASH_LINENO[@]} -1))) ; do
       printf "called from: ${BASH_SOURCE[$i]:-($0 ??)}:${BASH_LINENO[$(($i-1))]}: ${FUNCNAME[$i]}\n" >&2
   done
   # printf "%s\n" "${msg}" >&2
   exit 127
}

# _verbose                          {{{2
function _verbose()
{
    if [ "${verbose:-0}" == 1 ] ; then
        printf " '%s'" "$@"
        echo
    fi
}

# _execute                          {{{2
# Si $noexec est définie à 1, l'exécution ne fait rien
function _execute()
{
    _verbose "$@"
    [ "${noexec:-0}" = "1" ] || "$@"
}


## Main    {{{1

ASGARD_DATA="${1:-$ASGARD_DATA}" # Set to $1, or to itself otherwise
_is_unset ASGARD_DATA && _die "Please set ASGARD_DATA"

_verbose "Patching into ${ASGARD_DATA}"

[ -d "${ASGARD_DATA}" ] || _die "ASGARD_DATA should point to a directory"

_dem_dir="$(readlink -f "${ASGARD_DATA}/${_path2dem}")"

[ -d "${_dem_dir}" ] || _die "'{ASGARD_DATA}/${_path2dem}' should point to a directory"

_eef_file="${_dem_dir}/AX___DEM_AX.EEF"

[ -f "${_eef_file}" ] || _die "'{ASGARD_DATA}/${_path2dem}' should contain the XML file 'AX___DEM_AX.EEF'"

_execute sed -i "s#\(<Directory>\).*\(</Directory>\)#\\1${_dem_dir}\\2#" "${_eef_file}" || _die "Cannot update Data_Block.DEM.DEM_User_Parameters.Directory path to point to '${_dem_dir}'"

echo "The AX___DEM_AX.EEF path to... itself has been correctly injected!"
