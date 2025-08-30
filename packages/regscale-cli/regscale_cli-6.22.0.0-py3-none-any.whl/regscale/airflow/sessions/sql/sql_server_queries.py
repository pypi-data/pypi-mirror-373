"""SQL Server Platform Queries."""

from regscale.airflow.sessions.sql.queries import SQLQuery


CHECK_WORKFLOW_STATUS_QUERY: str = """
SELECT
  CASE
    WHEN EXISTS (
      SELECT 1
      FROM dbo.WorkflowInstance wi
      WHERE wi.id = {{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }}
      AND NOT EXISTS (
        SELECT 1
        FROM dbo.WorkflowInstanceSteps wis
        WHERE wis.WorkflowInstanceId = wi.id
        AND wis.[Status] <> 'Rejected'
      )
    ) THEN -1
    WHEN EXISTS (
      SELECT 1
      FROM dbo.WorkflowInstance wi
      WHERE wi.id = {{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }}
      AND NOT EXISTS (
        SELECT 1
        FROM dbo.WorkflowInstanceSteps wis
        WHERE wis.WorkflowInstanceId = wi.id
        AND wis.[Status] <> 'Approved'
      )
    ) THEN 1
    WHEN EXISTS(
      SELECT 1
      FROM dbo.WorkflowInstance wi
      WHERE wi.id = {{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }}
      AND NOT EXISTS (
        SELECT 1
        FROM dbo.WorkflowInstanceSteps wis
        WHERE wis.WorkflowInstanceId = wi.id
        AND wis.[Status] <> 'Pending'
    ) THEN 0
    ELSE NULL
  END AS OverallStatus;
"""

NEW_CHECK_WORKFLOW_STATUS_QUERY: str = """
declare @workflowInstanceId int = {{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }}
declare @workflowStepId int = -1
;WITH orderedWorkFlowSteps AS
(
   SELECT
       id, ROW_NUMBER() OVER(ORDER BY [Order] DESC) AS 'RowNum'
   FROM WorkflowInstanceSteps where WorkflowInstanceId = @workflowInstanceId
)
SELECT @workflowStepId = id
FROM orderedWorkFlowSteps
WHERE RowNum = 2
SELECT
    case
        when exists
            (select wis.id from dbo.WorkflowInstanceSteps wis
             where wis.Id = @workflowStepId and wis.WorkflowInstanceId = @workflowInstanceId and wis.[Status] = 'Rejected')
            then -1
        when exists
            (select wis.id from dbo.WorkflowInstanceSteps wis
             where wis.Id = @workflowStepId and wis.WorkflowInstanceId = @workflowInstanceId and wis.[Status] = 'Approved')
            then 1
        when exists
            (select wis.id from dbo.WorkflowInstanceSteps wis
             where wis.Id = @workflowStepId and wis.WorkflowInstanceId = @workflowInstanceId and wis.[Status] = 'Pending')
            then 0
        else
            null
        end as  OverallStatus;
"""

NEWER_CHECK_WORKFLOW_STATUS_QUERY: str = """
declare @workflowInstanceId int = {{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }}
;select * from WorkflowInstanceSteps
where WorkflowInstanceId = @workflowInstanceId and [Order] not in (0, 1000) order by [order] -- this is for validating results only
select top 1
case when wis.status = 'Rejected' then -1
        when wis.status = 'Approved' then 1
        when wis.status = 'Pending' then 0
    else null
    end as OverallStatus,
 *
from WorkflowInstanceSteps wis
where wis.WorkflowInstanceId = @workflowInstanceId
and status in ('Rejected', 'Approved', 'Pending' )
order by [Order] DESC;
"""

CHECK_IF_COMPLETED_QUERY: str = """
DECLARE @workflowInstanceId INT = '{{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }}';
WITH OrderedSteps AS (
    SELECT
        wis.*,
        LEAD(wis.[Order]) OVER (ORDER BY wis.[Order] DESC) AS NextOrder,
        LEAD(wis.[Status]) OVER (ORDER BY wis.[Order] DESC) AS NextStatus
    FROM WorkflowInstanceSteps wis
    WHERE wis.WorkflowInstanceId = @workflowInstanceId
)
SELECT
    CASE
        WHEN [Order] = 1000 AND NextStatus = 'Approved' THEN 1
        ELSE NULL
    END AS Result
FROM OrderedSteps
WHERE [Order] = 1000;
"""

WATCH_WORFKLOW_QUERY: str = """
DECLARE @workflowInstanceId INT = {{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }};
WITH OrderedSteps AS (
    SELECT
        wis.*,
        LEAD(wis.[Order]) OVER (ORDER BY wis.[Order] DESC) AS NextOrder,
        ROW_NUMBER() OVER (ORDER BY wis.[Order] DESC) AS Rn
    FROM WorkflowInstanceSteps wis
    WHERE wis.WorkflowInstanceId = @workflowInstanceId
        AND status IN ('Rejected', 'Approved', 'Pending')
)
SELECT TOP 1
    CASE
        WHEN NextOrder = 1000 THEN 1
        ELSE 0
    END AS Result,
    wis.*
FROM OrderedSteps wis
WHERE Rn = 1;
"""

GET_WORKFLOW_STEPS_QUERY: str = """
SELECT COUNT(*) as Steps
FROM WorkflowInstanceSteps as wis
WHERE wis.WorkflowInstanceId = {{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }}
GROUP BY WorkflowInstanceId;
"""

BETTER_GET_WORKFLOW_STEPS_QUERY: str = """
declare @workflowInstanceId int = {{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }}
;select
    stepCount.Steps,
FROM
    (
    SELECT
        @workflowInstanceId WorkflowinstanceId) as t1
left JOIN (
    SELECT
        @workflowInstanceId ID,
        COUNT(*) as Steps
    FROM
        WorkflowInstanceSteps as wis
    WHERE
        wis.WorkflowInstanceId = @workflowInstanceId
    group by
        WorkflowInstanceId) as stepCount on
    t1.workflowInstanceId = stepCount.ID
LEFT JOIN (
    select
        top 1
wis.WorkflowinstanceId,
        case
            when wis.status = 'Rejected' then -1
            when wis.status = 'Approved' then 1
            when wis.status = 'Pending' then 0
            else null
        end as OverallStatus
    from
        WorkflowInstanceSteps as wis
    where
        wis.WorkflowInstanceId = @workflowInstanceId
        and status in ('Rejected', 'Approved', 'Pending' )
    order by
        [Order] DESC) as status on
    t1.WorkflowinstanceId = status.WorkflowinstanceId
"""

GET_STATUS_WORKFLOW_QUERY: str = """
declare @workflowInstanceId int = {{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }};
select
    t1.WorkflowinstanceId,
    stepCount.Steps,
    status.OverallStatus
FROM
    (
    SELECT
        @workflowInstanceId WorkflowinstanceId) as t1
left JOIN (
    SELECT
        @workflowInstanceId ID,
        COUNT(*) as Steps
    FROM
        WorkflowInstanceSteps as wis
    WHERE
        wis.WorkflowInstanceId = @workflowInstanceId
    group by
        WorkflowInstanceId) as stepCount on
    t1.workflowInstanceId = stepCount.ID
LEFT JOIN (
    select
        top 1
wis.WorkflowinstanceId,
        case
            when wis.status = 'Rejected' then -1
            when wis.status = 'Approved' then 1
            when wis.status = 'Pending' then 0
            else null
        end as OverallStatus
    from
        WorkflowInstanceSteps as wis
    where
        wis.WorkflowInstanceId = @workflowInstanceId
        and status in ('Rejected', 'Approved', 'Pending' )
    order by
        [Order] DESC) as status on
    t1.WorkflowinstanceId = status.WorkflowinstanceId;
"""

GET_STEPS_QUERY: str = """
declare @workflowInstanceId int = {{ dag_run.conf['workflow_id'] if dag_run and dag_run.conf and 'workflow_id' in dag_run.conf else params.workflow_id }};
select
    stepCount.Steps
FROM
    (
    SELECT
        @workflowInstanceId WorkflowinstanceId) as t1
left JOIN (
    SELECT
        @workflowInstanceId ID,
        COUNT(*) as Steps
    FROM
        WorkflowInstanceSteps as wis
    WHERE
        wis.WorkflowInstanceId = @workflowInstanceId
    group by
        WorkflowInstanceId) as stepCount on
    t1.workflowInstanceId = stepCount.ID;
"""

NEW_WORKFLOW_SQL_QUERY: SQLQuery = SQLQuery(query=NEWER_CHECK_WORKFLOW_STATUS_QUERY)
WORKFLOW_SQL_QUERY: SQLQuery = SQLQuery(query=NEW_CHECK_WORKFLOW_STATUS_QUERY)
CHECK_IF_COMPLETED_SQL_QUERY: SQLQuery = SQLQuery(query=CHECK_IF_COMPLETED_QUERY)
WATCH_WORKFLOW_SQL_QUERY: SQLQuery = SQLQuery(query=WATCH_WORFKLOW_QUERY)
GET_WORKFLOW_STEPS_SQL_QUERY: SQLQuery = SQLQuery(query=GET_WORKFLOW_STEPS_QUERY)
BETTER_GET_WORFKLOW_STEPS_SQL_QUERY: SQLQuery = SQLQuery(query=BETTER_GET_WORKFLOW_STEPS_QUERY)
GET_STATUS_WORKFLOW_SQL_QUERY: SQLQuery = SQLQuery(query=GET_STATUS_WORKFLOW_QUERY)
GET_STEPS_SQL_QUERY: SQLQuery = SQLQuery(query=GET_STEPS_QUERY)
