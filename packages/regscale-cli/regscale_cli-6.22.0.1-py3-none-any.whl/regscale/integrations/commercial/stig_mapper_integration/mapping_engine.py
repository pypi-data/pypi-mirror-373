"""
STIG Mapping Engine
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from regscale.models import SecurityPlan
from regscale.models.regscale_models import Asset, AssetMapping, Component

logger = logging.getLogger(__name__)


class StigMappingEngine:
    """
    A class to map assets to STIGs based on defined rules
    """

    comparator_functions = {
        "equals": lambda a, b: a == b,
        "contains": lambda a, b: b in a,
        "notcontains": lambda a, b: b not in a,
        "startswith": lambda a, b: a.startswith(b),
        "notin": lambda a, b: b not in a,
        "endswith": lambda a, b: a.endswith(b),
        "notstartswith": lambda a, b: not a.startswith(b),
        "notendswith": lambda a, b: not a.endswith(b),
        "gt": lambda a, b: a > b,
        "lt": lambda a, b: a < b,
        "gte": lambda a, b: a >= b,
        "lte": lambda a, b: a <= b,
        "ne": lambda a, b: a != b,
        "in": lambda a, b: a in b,
        "nin": lambda a, b: a not in b,
    }

    def __init__(self, json_file: str):
        self._mapping_cache = None
        self._component_cache = None
        self.rules = self.load_rules(json_file)
        logger.info(f"Loaded {len(self.rules)} rules from {json_file}")
        # Preprocess rules for faster access
        self.stig_to_rules = {}
        for rule in self.rules:
            stig_name = rule.get("stig")
            if stig_name not in self.stig_to_rules:
                self.stig_to_rules[stig_name] = []
            self.stig_to_rules[stig_name].append(rule.get("comparators", []))

    @staticmethod
    def load_rules(json_file: str) -> List[Dict[str, str]]:
        """
        Load rules from a JSON file

        :param str json_file: The path to the JSON file
        :return: A list of rules
        :rtype: List[Dict[str, str]]
        """
        if not os.path.exists(json_file):
            logger.error(f"File not found: {json_file}")
            return []
        try:
            with open(json_file, "r") as file:
                data = json.load(file)
                return data.get("rules", [])
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in file {json_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading rules from {json_file}: {e}")
        return []

    def evaluate_match(self, item: Any, comparators: List[Dict[str, str]]) -> bool:
        """
        Evaluates a single item (Asset or software inventory item) against multiple comparator rules

        :param Any item: The asset or software inventory item
        :param List[Dict[str, str]] comparators: List of comparators
        :return: True if item meets all 'and' comparators or at least one 'or' comparator, otherwise False
        :rtype: bool
        """
        # Separate comparators by their logical operator
        and_comparators = [comp for comp in comparators if comp.get("logical_operator", "and").lower() == "and"]
        or_comparators = [comp for comp in comparators if comp.get("logical_operator", "and").lower() == "or"]

        # Evaluate 'and' comparators
        if not all(self.evaluate_single_comparator(item, comp) for comp in and_comparators):
            return False

        # Evaluate 'or' comparators
        if or_comparators:
            return any(self.evaluate_single_comparator(item, comp) for comp in or_comparators)

        # If all 'and' comparators passed and there are no 'or' comparators
        return True

    @staticmethod
    def get_item_value(item: Any, property_name: Any) -> Optional[Any]:
        """
        Fetches the property value from the item, or None if not found

        :param Any item: The asset or software inventory item
        :param Any property_name: The property name
        :return: The property value
        :rtype: Optional[Any]
        """
        if isinstance(item, dict):
            return item.get(property_name)
        return getattr(item, property_name, None)

    def evaluate_single_comparator(self, item: Any, comparator: dict) -> bool:
        """
        Evaluates a single comparator against the item

        :param Any item: The asset or software inventory item
        :param Dict[str, str] comparator: The comparator
        :return: True if the item satisfies the comparator, otherwise False
        :rtype: bool
        """
        property_name = comparator.get("property")
        item_value = self.get_item_value(item, property_name)

        if item_value is None:
            return False

        operator = comparator.get("comparator")
        value = comparator.get("value")
        comparator_func = StigMappingEngine.comparator_functions.get(operator)

        return comparator_func(item_value, value) if comparator_func else False

    @staticmethod
    def find_matching_stigs(items: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> List[str]:
        """
        Checks a list of items (software inventory or assets) to see which STIGs they match

        :param List[Dict[str, Any]] items: List of items (e.g., software inventory dictionaries)
        :param List[Dict[str, Any]] rules: List of STIG rules, each containing a "stig" name and comparators
        :return: List of matched STIG names
        :rtype: List[str]
        """
        matched_stigs = []

        for rule in rules:
            stig_name = rule.get("stig")
            comparators = rule.get("comparators", [])

            # Track satisfaction of each comparator across all items
            comparator_match = {i: False for i in range(len(comparators))}

            # Go through each comparator and attempt to satisfy it with any item
            for i, comparator in enumerate(comparators):
                property_name = comparator.get("property")
                value = comparator.get("value")
                operator = comparator.get("comparator")

                # Check if any item satisfies this comparator
                for item in items:
                    item_value = item.get(property_name)

                    # Retrieve the comparison function
                    comparator_func = StigMappingEngine.comparator_functions.get(operator)
                    if comparator_func and comparator_func(item_value, value):
                        comparator_match[i] = True
                        break  # Move to the next comparator once a match is found

            # Evaluate final match based on logical operators
            if all(comparator_match.values()):
                matched_stigs.append(stig_name)

        return matched_stigs

    @staticmethod
    def asset_matches_comparators(asset: Asset, comparators: List[Dict[str, str]]) -> bool:
        """
        Determine if the asset matches the given comparators

        :param Asset asset: An asset
        :param List[Dict[str, str]] comparators: List of comparator dictionaries
        :return: True if the asset matches the comparators, False otherwise
        :rtype: bool
        """
        match_result = True

        for comparator in comparators:
            property_name = comparator.get("property")
            if not hasattr(asset, property_name):
                return False

            operator = comparator.get("comparator")
            comparator_func = StigMappingEngine.comparator_functions.get(operator)
            if not comparator_func:
                return False

            value = comparator.get("value")
            asset_value = getattr(asset, property_name)
            comparison_result = comparator_func(asset_value, value)

            logical_operator = comparator.get("logical_operator", "and").lower()

            if logical_operator == "and":
                match_result = match_result and comparison_result
                if not match_result:
                    return False
            elif logical_operator == "or":
                match_result = match_result or comparison_result
            else:
                logger.warning(f"Unknown logical operator: {logical_operator}")
                return False

        return match_result

    def match_asset_to_stigs(
        self, asset: Asset, ssp_id: int, software_inventory: Optional[List] = None
    ) -> List[Component]:
        """
        Match an asset to STIG components based on rules

        :param Asset asset: An asset
        :param int ssp_id: The security plan ID
        :param Optional[List] software_inventory: A list of software inventory
        :return: A list of matching components
        :rtype: List[Component]
        """
        if software_inventory is None:
            software_inventory = []
        if not self.rules:
            return []

        matching_components = []

        # Ensure component cache is initialized
        if self._component_cache is None:
            self._component_cache = self.get_component_dict(ssp_id)

        for stig_name, comparators_list in self.stig_to_rules.items():
            component = self._component_cache.get(stig_name)
            if not component:
                continue

            for comparators in comparators_list:
                if self.asset_matches_comparators(asset, comparators):
                    matching_components.append(component)
                    break  # No need to check other comparators for this STIG

        return matching_components

    def map_stigs_to_assets(
        self,
        assets: List[Asset],
        ssp_id: int,
    ) -> List[AssetMapping]:
        """
        Map STIG components to assets based on rules

        :param List[Asset] asset_list assets: A list of assets
        :param List[Component] ssp_id: The security plan ID
        :return: A list of asset mappings
        :rtype: List[AssetMapping]
        """
        new_mappings = []

        # Cache components to avoid redundant database queries
        components = self.get_components(ssp_id)

        # Build a mapping of existing mappings for quick lookup
        existing_mappings = {}
        for component in components:
            mappings = AssetMapping.find_mappings(component_id=component.id)
            existing_mappings[component.id] = {m.assetId for m in mappings}

        for stig_name, comparators_list in self.stig_to_rules.items():
            component = self._component_cache.get(stig_name)
            if not component:
                continue

            component_existing_asset_ids = existing_mappings.get(component.id, set())

            for asset in assets:
                for comparators in comparators_list:
                    if self.asset_matches_comparators(asset, comparators):
                        if asset.id not in component_existing_asset_ids:
                            mapping = AssetMapping(assetId=asset.id, componentId=component.id)
                            new_mappings.append(mapping)
                            component_existing_asset_ids.add(asset.id)
                            logger.info(f"Mapping -> Asset ID: {asset.id}, Component ID: {component.id}")
                        else:
                            logger.info(
                                f"Existing mapping found for Asset ID: {asset.id}, Component ID: {component.id}"
                            )
                        break  # No need to check other comparators for this asset and STIG

        return new_mappings

    def get_components(self, ssp_id: int) -> List[Component]:
        """
        Get all components for the given security plan

        :param int ssp_id: The security plan ID
        :return: A list of components
        :rtype: List[Component]
        """
        if not hasattr(self, "_component_cache"):
            components = Component.get_all_by_parent(parent_module=SecurityPlan.get_module_slug(), parent_id=ssp_id)
            self._component_cache = {comp.title: comp for comp in components}
        else:
            components = self._component_cache.values()
        return components

    def get_component_dict(self, ssp_id: int) -> Dict[str, Component]:
        """
        Get a dictionary of components for the given security plan

        :param int ssp_id: The security plan ID
        :return: A dictionary of components
        :rtype: Dict[str, Component]
        """
        if not hasattr(self, "_component_cache") or self._component_cache is None:
            components = Component.get_all_by_parent(parent_module=SecurityPlan.get_module_slug(), parent_id=ssp_id)
            self._component_cache = {comp.title: comp for comp in components}
        return self._component_cache

    def map_associated_stigs_to_asset(self, asset: Asset, ssp_id: int) -> List[AssetMapping]:
        """
        Map associated STIGs to an asset based on rules

        :param Asset asset: An asset
        :param int ssp_id: The security plan ID
        :return: A list of asset mappings
        :rtype: List[AssetMapping]
        """
        new_mappings = []
        associated_components = self.match_asset_to_stigs(asset, ssp_id)

        # Initialize or update the mapping cache
        if not hasattr(self, "_mapping_cache") or self._mapping_cache is None:
            mappings = AssetMapping.get_all_by_parent(parent_module=Asset.get_module_slug(), parent_id=asset.id)
            self._mapping_cache = {m.componentId: m for m in mappings}

        existing_component_ids = set(self._mapping_cache.keys())

        for component in associated_components:
            if component.id not in existing_component_ids:
                mapping = AssetMapping(assetId=asset.id, componentId=component.id)
                mapping.create()
                new_mappings.append(mapping)
                self._mapping_cache[component.id] = mapping
                logger.debug(f"Created mapping for Asset ID: {asset.id}, Component ID: {component.id}")
            else:
                logger.debug(f"Mapping already exists for Asset ID: {asset.id}, Component ID: {component.id}")

        return new_mappings
