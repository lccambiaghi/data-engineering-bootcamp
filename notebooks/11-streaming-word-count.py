# Databricks notebook source
# %%
from bootcamp.databricks_compat import spark, display
from data.config import DATA_DIR
from pyspark.sql.functions import explode, split, trim, lower

# %% 1. BATCH WORD COUNT
# Read raw text data
lines = (spark.read
    .format("text")
    .option("lineSep", ".")
    .load(f"{DATA_DIR}/streaming-course/text")
)

# Split into words
raw_df = lines.select(explode(split(lines.value, " ")).alias("word"))

# %%
display(raw_df)

# %%
# Clean and filter words
quality_df = (raw_df
    .select(lower(trim(raw_df.word)).alias("word"))
    .where("word is not null")
    .where("word rlike '[a-z]'")
)
quality_df.show()

# %%
# Count words
word_count_df = quality_df.groupBy("word").count()
word_count_df.show()

# %%

# Write to delta table
(word_count_df.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("word_count_table")
)

print("Batch word count done")

# %%
!ls /opt/hive/data/warehouse/word_count_table

# %% 2. STREAMING WORD COUNT
# Drop table if it exists
spark.sql("DROP TABLE IF EXISTS word_count_table")
# Remove table from filesystem
!rm -rf /opt/hive/data/warehouse/word_count_table

# %%
# Read streaming text data
stream_lines = (spark.readStream
    .format("text")
    .option("lineSep", ".")
    .load(f"{DATA_DIR}/streaming-course/text")
)

# Split into words
stream_raw_df = stream_lines.select(explode(split(stream_lines.value, " ")).alias("word"))

# Clean and filter words
stream_quality_df = (stream_raw_df
    .select(lower(trim(stream_raw_df.word)).alias("word"))
    .where("word is not null")
    .where("word rlike '[a-z]'")
)

# Count words
stream_word_count_df = stream_quality_df.groupBy("word").count()

# Write streaming to delta table
stream_query = (stream_word_count_df.writeStream
    .format("delta")
    .option("checkpointLocation", f"{DATA_DIR}/streaming-course/checkpoint/word_count")
    .outputMode("complete")
    .toTable("word_count_table")
)

print("Streaming word count started")
