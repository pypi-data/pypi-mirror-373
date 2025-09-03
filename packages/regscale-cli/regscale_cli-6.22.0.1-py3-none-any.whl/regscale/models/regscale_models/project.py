"""Model for a RegScale Link"""

from typing import Optional

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from .regscale_model import RegScaleModel


class Project(RegScaleModel):
    _module_slug = "projects"

    title: Optional[str] = ""  # Required
    phase: Optional[str] = ""  # Required
    projectManagerId: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)  # Required
    id: Optional[int] = 0
    uuid: Optional[str] = ""
    otherID: Optional[str] = ""
    description: Optional[str] = ""
    benefits: Optional[str] = ""
    startDate: Optional[str] = Field(default_factory=get_current_datetime)
    endDate: Optional[str] = ""
    actualFinish: Optional[str] = ""
    percentComplete: Optional[int] = 0
    budget: Optional[float] = 0.0
    actualCosts: Optional[float] = 0.0
    legislativeMandate: Optional[bool] = True
    auditFinding: Optional[bool] = True
    strategicPlan: Optional[bool] = True
    costSavings: Optional[bool] = True
    newRequirement: Optional[bool] = True
    riskReduction: Optional[bool] = True
    revenue: Optional[bool] = True
    facilityId: Optional[int] = 0
    orgId: Optional[int] = 0
    parentId: Optional[int] = 0
    parentModule: Optional[str] = ""
    isPublic: Optional[bool] = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Links model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_list="/api/{model_slug}/getList",
            calendar_projects="/api/{model_slug}/calendarProjects/{dtDate}/{fId}/{orgId}/{userId}",
            gantt_chart="/api/{model_slug}/ganttChart/{intId}",
            status_board="/api/{model_slug}/statusboard/{strSearch}/{strPhase}/{strOwner}/{intPage}/{pageSize}",
            graph="/api/{model_slug}/graph",
            graph_by_date="/api/{model_slug}/graphByDate/{strGroupBy}/{year}",
            filter_projects="/api/{model_slug}/filterProjects",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            report="/api/{model_slug}/report/{strReport}",
            schedule="/api/{model_slug}/schedule/{year}/{dvar}",
            dashboard="/api/{model_slug}/dashboard/{strGroupBy}",
            main_dashboard="/api/{model_slug}/mainDashboard/{intYear}",
            main_dashboard_chart="/api/{model_slug}/mainDashboardChart/{year}",
        )
