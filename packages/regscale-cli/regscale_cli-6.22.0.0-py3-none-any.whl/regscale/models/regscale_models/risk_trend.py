"""
This module contains the Risk Trends model for RegScale.
"""

from typing import Optional

from regscale.models.regscale_models.regscale_model import RegScaleModel


class RiskTrend(RegScaleModel):
    """RegScale Risk Trends

    :return: RegScale Business Impact Assessment
    """

    _module_slug = "riskTrends"
    _module_string = "riskTrends"
    # Should we include baseline, ruleId, check, and results in unique fields?
    _unique_fields = [
        [
            "riskId",
            "category",
        ],
    ]
    _parent_id_field = "riskId"
    # Required fields (Nullable = "NO")
    id: int
    analysis: str = ""
    riskTrend: str = ""
    costImpact: float = 0.0
    scheduleImpact: int = 0
    dateAssessed: str = ""
    riskId: int
    isPublic: bool = True
    difference: float = 0.0
    inherentConsequence: str
    inherentProbability: str
    inherentRiskScore: float = 0.0

    residualConsequence: str
    residualProbability: str
    residualRisk: str
    residualRiskScore: float = 0.0

    targetRiskScore: float = 0.0

    annualLossExpectancy: float = 0.0

    expectedLost: float = 0.0

    lossEventFrequency: float = 0.0

    maximumLoss: float = 0.0

    minimumLoss: float = 0.0

    riskExposure: float = 0.0
    threatEventFrequency: float = 0.0

    # Optional fields (Nullable = "YES")
    uuid: Optional[str] = None
    mitigationEffectiveness: Optional[str] = None
    threatChanges: Optional[str] = None
    impactDescription: Optional[str] = None
    operationalRequirements: Optional[str] = None
    riskStrategy: Optional[str] = None
    assumptions: Optional[str] = None
