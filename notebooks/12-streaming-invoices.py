# Databricks notebook source
# %%
from bootcamp.databricks_compat import spark, display
from data.config import DATA_DIR
from pyspark.sql.functions import expr

INVOICE_SCHEMA = """
    InvoiceNumber string, CreatedTime bigint, StoreID string, PosID string, CashierID string,
    CustomerType string, CustomerCardNo string, TotalAmount double, NumberOfItems bigint, 
    PaymentMethod string, TaxableAmount double, CGST double, SGST double, CESS double, 
    DeliveryType string,
    DeliveryAddress struct<AddressLine string, City string, ContactNumber string, PinCode string, State string>,
    InvoiceLineItems array<struct<ItemCode string, ItemDescription string, ItemPrice double, ItemQty bigint, TotalValue double>>
"""

# %% STREAMING INVOICE PROCESSING
# Drop table if it exists
spark.sql("DROP TABLE IF EXISTS invoice_line_items")
# Remove table from filesystem
!rm -rf /opt/hive/data/warehouse/invoice_line_items

# %%
# Read invoices stream
invoices_df = (spark.readStream
    .format("json")
    .schema(INVOICE_SCHEMA)
    .load(f"{DATA_DIR}/streaming-course/invoices")
)

# %%
# Explode invoice line items
exploded_df = invoices_df.selectExpr(
    "InvoiceNumber", "CreatedTime", "StoreID", "PosID",
    "CustomerType", "PaymentMethod", "DeliveryType", 
    "DeliveryAddress.City", "DeliveryAddress.State", "DeliveryAddress.PinCode",
    "explode(InvoiceLineItems) as LineItem"
)

# %%
# Debug: write to in-memory table for interactive querying
debug_query = (exploded_df.writeStream
    .format("memory")
    .queryName("debug_invoices")
    .outputMode("append")
    .start()
)

# %%
# Wait a bit for data to arrive, then query the in-memory table
# import time
# time.sleep(5)  # Wait for stream to process some data
spark.sql("SELECT * FROM debug_invoices").show(truncate=False)

# %%
# Stop the debug stream when done
debug_query.stop()

# %%
# Flatten line item struct into columns
flattened_df = (exploded_df
    .withColumn("ItemCode", expr("LineItem.ItemCode"))
    .withColumn("ItemDescription", expr("LineItem.ItemDescription"))
    .withColumn("ItemPrice", expr("LineItem.ItemPrice"))
    .withColumn("ItemQty", expr("LineItem.ItemQty"))
    .withColumn("TotalValue", expr("LineItem.TotalValue"))
    .drop("LineItem")
)

# %%
# Write stream to delta table
stream_query = (flattened_df.writeStream
    .format("delta")
    .option("checkpointLocation", f"{DATA_DIR}/streaming-course/checkpoint/invoices")
    .outputMode("append")
    .toTable("invoice_line_items")
)

print("Invoice processing stream started")

# %%
