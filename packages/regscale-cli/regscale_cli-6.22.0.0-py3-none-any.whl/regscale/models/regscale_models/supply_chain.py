"""Supply Chain model class"""

import logging
from enum import Enum
from typing import Optional, Union

from pydantic import ConfigDict, Field

from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger("regscale")


class SupplyChainStatus(str, Enum):
    """Supply Chain Status"""

    Pending = "Pending"
    Active = "Active"
    Closed = "Closed"

    def __str__(self) -> str:
        """
        Return the string representation of the Supply Chain Status

        :return: The string representation of the Supply Chain Status
        :rtype: str
        """
        return self.value


class SupplyChainTier(str, Enum):
    """Supply Chain Tier"""

    Tier1 = "Tier 1 - Organizational"
    Tier2 = "Tier 2 - Mission"
    Tier3 = "Tier 3 - Information System"
    Tier4 = "Tier 4 - Administrative/Other"

    def __str__(self) -> str:
        """
        Return the string representation of the Supply Chain Tier

        :return: The string representation of the Supply Chain Tier
        :rtype: str
        """
        return self.value


class SupplyChainFipsImpact(str, Enum):
    """Supply Chain Fips Impact Level"""

    Low = "Low"
    Moderate = "Moderate"
    High = "High"

    def __str__(self) -> str:
        """
        Return the string representation of the Supply Chain Fips Impact Level

        :return: The string representation of the Supply Chain Fips Impact Level
        :rtype: str
        """
        return self.value


class SupplyChainContractType(str, Enum):
    """Supply Chain Contract Type"""

    FirmFixedPrice = "Firm Fixed Price (FFP)"
    TimeAndMaterials = "Time and Materials (T&M)"
    CostPlus = "Cost Plus"
    Subcontractor = "Subcontractor"

    def __str__(self) -> str:
        """
        Return the string representation of the Supply Chain Contract Type

        :return: The string representation of the Supply Chain Contract Type
        :rtype: str
        """
        return self.value


class SupplyChain(RegScaleModel):
    """Supply Chain model class"""

    _parent_id_field = "parentId"
    _unique_fields = [
        ["parentId", "parentModule", "contractNumber"],
    ]
    _module_slug = "supplychain"

    title: str
    contractType: Union[SupplyChainContractType, str]  # Required
    strategicTier: Union[SupplyChainTier, str]  # Required
    fips: Union[SupplyChainFipsImpact, str]  # Required
    id: Optional[int] = 0
    status: Union[SupplyChainStatus, str] = SupplyChainStatus.Pending
    uuid: Optional[str] = None
    contractNumber: Optional[str] = None
    isPublic: bool = True
    parentId: int = 0
    parentModule: Optional[str] = None
    orgId: Optional[int] = None
    facilityId: Optional[int] = None
    contractValue: Optional[float] = 0.0
    fundedAmount: Optional[float] = 0.0
    actualCosts: Optional[float] = 0.0
    scope: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    violationURL: Optional[str] = None
    stockURL: Optional[str] = None
    duns: Optional[str] = None
    ein: Optional[str] = None
    cageCodes: Optional[str] = None
    naics: Optional[str] = None
    stockSymbol: Optional[str] = None
    aribaNetworkId: Optional[str] = None
    contractOwnerId: str = Field(default_factory=RegScaleModel.get_user_id)

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the SupplyChain model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_list="/api/{model_slug}/list",
            get_count="/api/{model_slug}/getCount",
            get_all_by_parent="/api/{model_slug}/getAllByParent/intParentId/{strModule}",
            graph="/api/{model_slug}/graph",
            graph_contrat_amount="/api/{model_slug}/graphContractAmount/{year}",
            graph_status_by_month="/api/{model_slug}/graphStatusByMonth/{year}",
            graph_by_date="/api/{model_slug}/graphByDate/{strGroupBy}/{year}",
            filter_supplychain="/api/{model_slug}/filterSupplyChain",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            statusboard="/api/{model_slug}/statusboard/{strSearch}/{strStatus}/{strType}/{strOwner}/{facilityId}/{intPage}/{intPageSize}",
            find_by_uuid="/api/{model_slug}/findByUUID/{strUUID}",
            find_by_ariba_id="/api/{model_slug}/findByAribaId/{strAriba}",
            find_by_stock_symbol="/api/{model_slug}/findByStockSymbol/{strStock}",
            find_by_naic="/api/{model_slug}/findByNAIC/{strNAIC}",
            find_by_cage_code="/api/{model_slug}/findByCageCode/{strCAGE}",
            find_by_ein="/api/{model_slug}/findByEIN/{strEIN}",
            find_by_duns="/api/{model_slug}/findByDUNS/{strDUNS}",
            main_dashboard="/api/{model_slug}/mainDashboard/{intYear}",
            dashboard="/api/{model_slug}/dashboard/{strGroupBy}",
            report="/api/{model_slug}/report/{strReport}",
            schedule="/api/{model_slug}/schedule/{year}/{dvar}",
        )
