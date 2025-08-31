"""
The strings in this file are used to dynamically generate a SQL query that aggregates data from source table.
This is an example full query:

WITH TimeBuckets AS (
   SELECT
       first_name,last_name,
       EXPLODE(SEQUENCE(
           TIMESTAMP '2024-08-27 00:00:00',
           TIMESTAMP '2024-09-02 04:00:00' + INTERVAL 1 DAY,
           INTERVAL 1 DAY
       )) AS _agg_bucket_time
   FROM
       ds_fs.dlt_test.sample_data_multiple_pk
   GROUP BY 
       first_name,last_name
),

Agg_1 AS (
 SELECT
     tb.first_name,tb.last_name,
     tb._agg_bucket_time AS ts,
     SUM(t.transaction) AS sum_agg
 FROM
     TimeBuckets tb
 LEFT JOIN
     ds_fs.dlt_test.sample_data_multiple_pk t
 ON
     t.ts >= tb._agg_bucket_time - INTERVAL 0 DAY - INTERVAL 2 DAY AND t.ts < tb._agg_bucket_time - INTERVAL 0 DAY
     AND tb.first_name = t.first_name AND tb.last_name = t.last_name
 GROUP BY
     tb._agg_bucket_time, tb.first_name,tb.last_name
)

SELECT
   tb.first_name,tb.last_name,
   tb._agg_bucket_time AS ts,
   sum_agg
FROM
   TimeBuckets tb

LEFT JOIN
 Agg_1 aa1
ON
 tb.first_name = aa1.first_name AND tb.last_name = aa1.last_name
 AND tb._agg_bucket_time = aa1.ts

ORDER BY
   tb.first_name,tb.last_name, tb._agg_bucket_time;

"""
TIME_BUCKET_ALIAS = "tb"
AGGREGATED_TABLE_ALIAS = "aa"
SOURCE_TABLE_ALIAS = "t"

AGG_JOIN_CONDITIONS_TEMPLATE = """
LEFT JOIN
 Agg_{i} {AGGREGATED_TABLE_ALIAS}_{i}
ON
 {agg_join_lookup_expr}
 AND {TIME_BUCKET_ALIAS}._agg_bucket_time = {AGGREGATED_TABLE_ALIAS}_{i}.{timestamp_key}
"""

AGG_TABLES_TEMPLATE = """
Agg_{i} AS (
 SELECT
     {tb_lookup_key_expr},
     {TIME_BUCKET_ALIAS}._agg_bucket_time AS {timestamp_key},
     {agg_function} AS {output_column_name}
 FROM
     TimeBuckets {TIME_BUCKET_ALIAS}
 LEFT JOIN
     {table_name} {SOURCE_TABLE_ALIAS}
 ON
     {SOURCE_TABLE_ALIAS}.{timestamp_key} >= {TIME_BUCKET_ALIAS}._agg_bucket_time - INTERVAL {offset} - INTERVAL {window} AND {SOURCE_TABLE_ALIAS}.{timestamp_key} < {TIME_BUCKET_ALIAS}._agg_bucket_time - INTERVAL {offset}
     AND {agg_tables_lookup_key_expr}
 GROUP BY
     {TIME_BUCKET_ALIAS}._agg_bucket_time, {tb_lookup_key_expr}
)
"""

QUERY_TEMPLATE = """
WITH TimeBuckets AS (
   SELECT
       {lookup_key},
       EXPLODE(SEQUENCE(
           {start_time},
           {end_time} + INTERVAL {granularity},
           INTERVAL {granularity}
       )) AS _agg_bucket_time
   FROM
       {table_name}
   GROUP BY 
       {lookup_key}
),
{agg_tables}
SELECT
   {tb_lookup_key_expr},
   {TIME_BUCKET_ALIAS}._agg_bucket_time AS {timestamp_key},
   {output_columns}
FROM
   TimeBuckets {TIME_BUCKET_ALIAS}
{agg_join_conditions}
ORDER BY
   {tb_lookup_key_expr}, {TIME_BUCKET_ALIAS}._agg_bucket_time;
"""
