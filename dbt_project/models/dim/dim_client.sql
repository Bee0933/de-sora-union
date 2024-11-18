with src_float as (
    select
        distinct
        client,
        md5(client) as client_id
    from {{ ref('src_float') }}
)

select
    client_id, 
    client as client_name
from src_float