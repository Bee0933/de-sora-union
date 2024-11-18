with recursive date_range as (
    select 
        cast('2023-07-03' as date) as date_field
    union all
    select 
        cast(date_field + interval '1 day' as date)
    from date_range
    where date_field + interval '1 day' <= cast('2023-09-04' as date)
),

date_attributes as (
    select
        date_field as date,
        extract(year from date_field) as year,
        extract(month from date_field) as month,
        extract(day from date_field) as day,
        extract(quarter from date_field) as quarter,
        extract(isodow from date_field) as weekday_iso,
        to_char(date_field, 'Day') as weekday_name,
        to_char(date_field, 'Month') as month_name,
        case when extract(isodow from date_field) in (6, 7) then true else false end as is_weekend,
        md5(date_field::text) as date_id
    from date_range
)

select
    date_id, 
    date,
    year,
    month,
    month_name,
    day,
    weekday_iso,
    weekday_name,
    quarter,
    is_weekend
from date_attributes
