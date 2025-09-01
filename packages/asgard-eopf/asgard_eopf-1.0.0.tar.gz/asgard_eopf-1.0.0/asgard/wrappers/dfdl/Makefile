# Copyright 2022 CS GROUP
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
#

# Generic options
WRAPPERS_CODE := $(subst generated_,,$(wildcard generated_*.c))
WRAPPERS := $(WRAPPERS_CODE:.c=.so)
WRAPPERS_NAMES := $(WRAPPERS_CODE:.c=)

# detect python include directory
PYTHON_INCLUDE=$(shell python3 -c "from sysconfig import get_paths; print(get_paths()['include'])")

# Compiler options

CC := gcc
CFLAGS := \
	-fPIC -fwrapv -O2 -Wall -Wextra -fno-strict-aliasing -std=gnu11 \
	-I$(PYTHON_INCLUDE)

# Link to EOCFI

LIBS_DIR := ""

LIBS := ""

# OBJ files:
COMMON_OBJ_FILES := errors.o infoset.o parsers.o unparsers.o validators.o

# targets
default: $(WRAPPERS)

define APPLY_WRAPPER_RULE
$(1).c: template.pyx
	cp template.pyx $(1).pyx
	cython -3 -I ../../.. -I . $(1).pyx
endef
$(foreach l,$(WRAPPERS_NAMES),$(eval $(call APPLY_WRAPPER_RULE,$(l))))

%.o: %.c
	$(CC) -c $(CFLAGS) $< -o $@

%.so: %.o generated_%.o $(COMMON_OBJ_FILES)
	$(CC) -shared -o $@ $^

clean:
	rm -f $(WRAPPERS_CODE) *.o *.so
