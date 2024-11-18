WITH src_clickup AS (
	SELECT 
		client,
		project,
		name,
		task,
		date,
		hours,
		note, 
		billable
	FROM {{ source('float_clickup', 'clickup_cleaned') }}
)

SELECT DISTINCT * FROM src_clickup