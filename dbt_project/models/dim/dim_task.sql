with src_float as (
    select
        distinct
        task,
        md5(task) as task_id
    from {{ ref('src_float') }}
)

select
    task_id, 
    task as task_name
from src_float