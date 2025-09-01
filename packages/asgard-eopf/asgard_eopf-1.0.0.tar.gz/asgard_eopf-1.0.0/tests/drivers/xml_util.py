#!/usr/bin/env python
# coding: utf8
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
#
"""
XmlUtil implementation.
"""

# pylint: disable=c-extension-no-member

import xml.etree.ElementTree as ET

import lxml.etree
import lxml.objectify


class XmlUtil:
    """XML utility functions"""

    # Hard-coded XSLT contents to remove namespaces.
    # See: https://stackoverflow.com/a/5875074
    #: :meta hide-value:
    XSLT_REMOVE_NS = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output indent="yes" method="xml" encoding="utf-8" omit-xml-declaration="yes"/>

    <!-- Stylesheet to remove all namespaces from a document -->
    <!-- NOTE: this will lead to attribute name clash, if an element contains
        two attributes with same local name but different namespace prefix -->
    <!-- Nodes that cannot have a namespace are copied as such -->

    <!-- template to copy elements -->
    <xsl:template match="*">
        <xsl:element name="{local-name()}">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:element>
    </xsl:template>

    <!-- template to copy attributes -->
    <xsl:template match="@*">
        <xsl:attribute name="{local-name()}">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>

    <!-- template to copy the rest of the nodes -->
    <xsl:template match="comment() | text() | processing-instruction()">
        <xsl:copy/>
    </xsl:template>

</xsl:stylesheet>
"""

    @classmethod
    def remove_namespaces(cls, path: str) -> str:
        """
        Remove namespaces from XML file contents to facilitate further reading.

        :param str path: XML file path
        :return: XML file contents without namespaces
        """
        # Read XML and xslt
        xml = lxml.etree.parse(path)
        xslt = lxml.etree.fromstring(cls.XSLT_REMOVE_NS)

        # Run XSLT
        transformed = lxml.etree.XSLT(xslt)(xml)

        # Convert the transformed XML to string
        return lxml.etree.tostring(transformed)

    @classmethod
    def read_with_etree(cls, path: str | None, remove_namespaces: bool = True):
        """
        Read an XML file with xml.etree

        :param str|None path: XML file path
        :param bool remove_namespaces: remove namespaces from the XML before reading.
        """
        if path is None:
            raise RuntimeError("XML file path is None")

        if remove_namespaces:
            return ET.fromstring(cls.remove_namespaces(path))
        return ET.parse(path).getroot()

    @classmethod
    def read_with_objectify(cls, path: str | None, remove_namespaces: bool = True):
        """
        Read an XML file with lxml.objectify

        :param str|None path: XML file path
        :param bool remove_namespaces: remove namespaces from the XML before reading.
        """
        if path is None:
            raise RuntimeError("XML file path is None")

        if remove_namespaces:
            return lxml.objectify.fromstring(cls.remove_namespaces(path))
        return lxml.objectify.parse(path).getroot()
