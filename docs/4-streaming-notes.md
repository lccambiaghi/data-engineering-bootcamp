# Streaming notes

## Why use structure streaming

- Analyze the required frequency of updates of the final solution (e.g. BI dashboard)
- Only process new batches of data

## Streaming

Execution Plan:
- ReadStream
- Transform: StreamingDataFrame
- WriteStream (specify `checkpointLocation`)

- Streaming source `data`
- **Streaming Query**:
  - Coordinator, background thread
  - Will watch for new data in landing zone
- When new data (e.g. `file1`) is available in landing zone:
  - It will be put into the **checkpoint** directory
  - Streaming Query will trigger the execution plan with the **micro-batch**
  - The output will be written to the streaming sink
  - When micro-batch is complete, Streaming Query will commit to the checkpoint directory