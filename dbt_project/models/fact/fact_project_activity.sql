WITH base_data AS (
    SELECT 
        a.date,
        a.client,
        a.project,
        a.name,
        a.task,
        a.hours,
        a.note,
        a.billable
    FROM 
        {{ ref('src_clickup') }} a
),
joined_data AS (
    SELECT 
        md5(CONCAT(d.date_id, c.client_id, p.project_id, t.task_id, r.role_id, e.team_member_id)) AS activity_id,
        d.date_id,
        c.client_id,
        p.project_id,
        t.task_id,
        r.role_id,
        e.team_member_id,
        b.hours,
        CASE WHEN b.billable = 'Yes' THEN TRUE ELSE FALSE END AS billable,
        b.note
    FROM 
        base_data b
    LEFT JOIN {{ ref('dim_date') }} d ON CAST(b.date AS DATE) = d.date
    LEFT JOIN {{ ref('dim_client') }} c ON b.client = c.client_name
    LEFT JOIN {{ ref('dim_project') }} p ON b.project = p.project_name
    LEFT JOIN {{ ref('dim_task') }} t ON b.task = t.task_name
    LEFT JOIN {{ ref('dim_team_member') }} e ON b.name = e.team_member_name
    LEFT JOIN {{ ref('dim_role') }} r ON e.role_id = r.role_id
)
SELECT DISTINCT
    activity_id,
    team_member_id,
    project_id,
    role_id,
    client_id,
    task_id,
    date_id,
    hours,
    billable,
    note
FROM 
    joined_data
