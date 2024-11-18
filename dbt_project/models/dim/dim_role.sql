with src_float as (
    select
        distinct
        role,
        md5(role) as role_id
    from {{ ref('src_float') }}
)

select
    role_id, 
    role as role_name
from src_float