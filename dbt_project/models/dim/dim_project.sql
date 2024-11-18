with src_float as (
    select
        distinct
        project,
        md5(project) as project_id,
        md5(client) as client_id,
        min(start_date) as project_start_date,
        max(end_date) as project_end_date
    from {{ ref('src_float') }}
    group by project, client
)

select
    project_id,
    client_id,
    project as project_name,
    project_start_date,
    project_end_date
from src_float