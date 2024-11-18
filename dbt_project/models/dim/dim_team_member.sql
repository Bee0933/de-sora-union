with src_float as (
    select distinct
        name as team_member_name,
        md5(name) as team_member_id,
        md5(role) as role_id
    from {{ ref('src_float') }}
)
select
    team_member_id,
    role_id,
    team_member_name
from src_float