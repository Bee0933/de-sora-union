WITH src_float AS (
	SELECT 
		client,
		project,
		role,
		name,
		task,
		start_date,
		end_date,
		estimated_hours
	FROM {{ source('float_clickup', 'float_cleaned') }}
)
SELECT DISTINCT * FROM src_float