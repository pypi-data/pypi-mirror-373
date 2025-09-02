#!/usr/bin/env python
# coding: utf8
#
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

"""pyrugged module init_orekit"""

# pylint: disable=import-error, no-member
import os
import sys

if "java.io" not in sys.modules:
    import orekit_jcc  # pylint: disable=unused-import  # noqa: F401

# pylint: disable=wrong-import-position
from java.io import File
from org.orekit.data import DataContext, DirectoryCrawler


def init_orekit(use_internal_data: bool = True, orekit_data_path: str = None):
    """
    Init orekit

    Parameters
    ----------
        use_internal_data : if true, internal orekit data is used.
        orekit_data_path : path to user orekit data. If specified, user orekit data is used.
    """

    jcc_modules = [name for name in ["orekit_jcc", "sxgeo"] if name in sys.modules]
    if len(jcc_modules) > 1:
        raise RuntimeError(f"Several JCC modules imported, expect only one: {jcc_modules}")
    real_jcc = jcc_modules[0]

    if sys.modules[real_jcc].getVMEnv() is None:
        # VisualVM profiling options, if the env var is set.
        # In VisualVM, go to File -> Add JMX Connection -> enter: localhost:9090
        if "VISUAL_VM_OPTS" in os.environ:
            visual_vm_opts = [
                "-Dcom.sun.management.jmxremote.rmi.port=9090",
                "-Dcom.sun.management.jmxremote=true",
                "-Dcom.sun.management.jmxremote.port=9090",
                "-Dcom.sun.management.jmxremote.ssl=false",
                "-Dcom.sun.management.jmxremote.authenticate=false",
                "-Dcom.sun.management.jmxremote.local.only=false",
                "-Djava.rmi.server.hostname=localhost",
            ]
        else:
            visual_vm_opts = []

        # Init the Java Virtual Machine in debug mode if the JAVA_DEBUG_PORT env var is set, e.g. 5005
        try:
            sys.modules[real_jcc].initVM(
                vmargs=[
                    f"-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address={os.environ['JAVA_DEBUG_PORT']}",
                    *visual_vm_opts,
                ]
            )
        except KeyError:
            sys.modules[real_jcc].initVM(vmargs=[*visual_vm_opts])  # no debug

    if use_internal_data is True and orekit_data_path is None:
        path = os.path.join(os.path.dirname(__file__), "../data/orekit-data-master/")
        DataContext.getDefault().getDataProvidersManager().addProvider(DirectoryCrawler(File(path)))

    if use_internal_data is True and orekit_data_path is not None:
        raise RuntimeError("Cannot specify orekit data path while using already internal data.")

    if use_internal_data is False and orekit_data_path is not None:
        DataContext.getDefault().getDataProvidersManager().addProvider(DirectoryCrawler(File(orekit_data_path)))
