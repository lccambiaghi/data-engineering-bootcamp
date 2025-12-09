WITH raw_hosts AS (
    SELECT * FROM airbnb.raw.hosts
)

SELECT 
    id AS host_id,
    name AS host_name,
    is_superhost AS host_is_superhost,
    created_at AS host_created_at,
    updated_at AS host_updated_at
FROM 
    raw_hosts