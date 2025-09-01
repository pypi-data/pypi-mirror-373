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

"""Reader for java TimeStampedPVCoordinates and TimeStampedAngularCoordinates outputs"""


from typing import Dict, List

from org.hipparchus.geometry.euclidean.threed import Rotation, Vector3D
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import TimeStampedAngularCoordinates, TimeStampedPVCoordinates


def read_pv_elements_from_txt(txt_file_path: str) -> List[Dict[str, float]]:
    """Transforms txt file in python dictionnary.

    Parameters
    ----------
        txt_file_path : file path

    Returns
    -------
        pv_elements : list of dictionnaries containing PV Coordinates elements"""

    pv_elements = []

    with open(txt_file_path, "r", encoding="utf-8") as txt_file:
        lines = txt_file.readlines()

        for line in lines:
            parts = line.split(", ")

            for index, element in enumerate(parts):
                if index == 0:
                    parts[index] = element.split("{")[1]

                elif index in [1, 4, 7]:
                    parts[index] = element.split("(")[1]

                elif index in [3, 6, 9]:
                    parts[index] = element.split(")")[0]

            pv_elements.append(dict(zip(["date", "px", "py", "pz", "vx", "vy", "vz", "ax", "ay", "az"], parts)))

    return pv_elements


def read_q_elements_from_txt(txt_file_path: str) -> List[Dict[str, float]]:
    """Transforms txt file in python list of dictionaries.

    Parameters
    ----------
        txt_file_path : file path

    Returns
    -------
        q_elements : list of dictionaries containing Q Coordinates elements"""

    q_elements = []

    with open(txt_file_path, "r", encoding="utf-8") as txt_file:
        lines = txt_file.readlines()

        for line in lines:
            parts = line.split(", ")

            for index, element in enumerate(parts):
                if index == 0:
                    parts[index] = element.split("{")[1]

                if index == 1:
                    parts[index] = element.split("(")[1]

                if index == 4:
                    parts[index] = element.split(")")[0]

            q_elements.append(dict(zip(["date", "q0", "q1", "q2", "q3"], parts)))

    return q_elements


def generate_date_from_pv_txt(date: str) -> AbsoluteDate:
    """Generates date object from string format."""

    date_part, hour_part = date.split("T")

    year, month, day = date_part.split("-")
    hour, minutes, seconds = hour_part.split(":")

    return AbsoluteDate(
        int(year), int(month), int(day), int(hour), int(minutes), float(seconds), TimeScalesFactory.getUTC()
    )


def generate_date_from_q_txt(date: str) -> AbsoluteDate:
    """Generates date object from string format."""

    date_part, hour_part = date.split("T")
    hour_part = hour_part.split("Z")[0]

    year, month, day = date_part.split("-")
    hour, minutes, seconds = hour_part.split(":")

    return AbsoluteDate(
        int(year), int(month), int(day), int(hour), int(minutes), float(seconds), TimeScalesFactory.getUTC()
    )


def create_pv_from_elements(pv_elements: List[Dict[str, float]], d_t: float = None) -> List[TimeStampedPVCoordinates]:
    """Creates TimeStampedPVCoordinates from lists,
    which is obtained by read_pv_elements_from_txt() method.

    """

    pv_list = []

    for element in pv_elements:

        if d_t is None:
            date = generate_date_from_pv_txt(element["date"])
        else:
            date = generate_date_from_pv_txt(element["date"]).shiftedBy(d_t)

        pv_list.append(
            TimeStampedPVCoordinates(
                date,
                Vector3D(float(element["px"]), float(element["py"]), float(element["pz"])),
                Vector3D(float(element["vx"]), float(element["vy"]), float(element["vz"])),
                Vector3D(float(element["ax"]), float(element["ay"]), float(element["az"])),
            )
        )

    return pv_list


def create_q_from_elements(
    q_elements: List[Dict[str, float]], d_t: float = None
) -> List[TimeStampedAngularCoordinates]:
    """Creates TimeStampedAngularCoordinates from lists,
    which is obtained by read_q_elements_from_txt() method.

    """

    q_list = []

    for element in q_elements:

        if d_t is None:
            date = generate_date_from_q_txt(element["date"])
        else:
            date = generate_date_from_q_txt(element["date"]).shiftedBy(d_t)

        q_list.append(
            TimeStampedAngularCoordinates(
                date,
                Rotation(float(element["q0"]), float(element["q1"]), float(element["q2"]), float(element["q3"]), True),
                Vector3D.ZERO,
                Vector3D.ZERO,
            )
        )

    return q_list


def extract_pv_from_txt(txt_file_path: str, d_t: float = None) -> List[TimeStampedPVCoordinates]:
    """Extract TimeStampedPVCoordinates from java output text file."""

    # Extract PV Coordinates elements from text
    pv_elements = read_pv_elements_from_txt(txt_file_path)

    # Build PV Coordinates instances from pv_elements
    pv_list = create_pv_from_elements(pv_elements, d_t)

    return pv_list


def extract_q_from_txt(txt_file_path: str, d_t: float = None) -> List[TimeStampedAngularCoordinates]:
    """Extract TimeStampedAngularCoordinates from java output text file."""

    # Extract Q Coordinates elements from text
    q_elements = read_q_elements_from_txt(txt_file_path)

    # Build Q Coordinates instances from q_elements
    q_list = create_q_from_elements(q_elements, d_t)

    return q_list
