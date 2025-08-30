"""
Rosetta Stone class Standardized approach to mapping identifiers between control id in FedRAMP and other frameworks
"""

import json
from typing import Dict
from regscale.core.decorators import singleton
from pathlib import Path


@singleton
class RosettaStone:
    """
    Rosetta Stone class Standardized approach to mapping identifiers between control id in FedRAMP and other frameworks
    """

    def __init__(self):
        self.map = None
        self.rs_data = {}
        self.rosetta = {}
        self.name = ""
        self.uuid = ""
        self.description = ""
        self.list0_name = ""
        self.list1_name = ""
        self.list2_name = ""
        self.stone = []

    def __str__(self):
        return self.name

    def loads(self, json_str: str):
        """
        Load json from a str
        :param str json_str: JSON string
        """
        parsed_json = json.loads(json_str)
        self._populate(parsed_json)

    def load_json_from_file(self, json_file: str):
        """
        Load json from a file
        :param str json_file: string name of a file
        """
        with open(json_file) as jf:
            parsed_json = json.load(jf)
        self._populate(parsed_json)

    def load_fedramp_version_5_mapping(self):
        """
        Load FedRAMP version 5 mapping
        """
        from importlib.resources import path as resource_path

        with resource_path("regscale.integrations.public.fedramp.mappings", "fedramp_r5_params.json") as json_file_path:
            self.load_json_from_file(json_file_path.__str__())

    def _populate(self, rs_dict: Dict):
        """
        Populate attributes from dictionary
        :param Dict rs_dict: Dictionary of Rosetta Stone data
        """
        self.rs_data = rs_dict
        self.rosetta = self.rs_data.get("rosetta", None)
        self.name = self.rosetta.get("name", None)
        self.uuid = self.rosetta.get("uuid", None)
        self.description = self.rosetta.get("description", None)
        self.list0_name = self.rosetta.get("list0_name", None)
        self.list1_name = self.rosetta.get("list1_name", None)
        self.list2_name = self.rosetta.get("list2_name", None)
        self.stone = self.rosetta.get("stone", None)
        # create quick_maps
        self.quick_map = self.lookup_l1_by_l0()
        self.reverse_quick_map = self.lookup_l0_by_l1()
        self.list_guessed = self.guessed()

    def lookup_l1_by_l0(self) -> Dict:
        """
        Map first items of list0, list1 as dictionary
        :return: Dict
        :rtype: Dict
        """
        self.map = {}
        for item in self.stone:
            self.map[item["list0"][0]] = item["list1"][0]
        return self.map

    def lookup_l0_by_l1(self) -> Dict:
        """
        Map first items of list0, list1 as dictionary
        :return: Dict
        :rtype: Dict
        """
        self.map = {}
        for item in self.stone:
            self.map[item["list1"][0]] = item["list0"][0]
        return self.map

    def guessed(self) -> Dict:
        """
        Return list of items with guesses
        :return: Dict
        :rtype: Dict
        """
        self.map = {}
        for line in self.stone:
            for c_score in line.get("confidence", None):
                if 0 < c_score < 1:
                    self.map[line.get("list0")[0]] = line.get("list1")[0]
        return self.map
