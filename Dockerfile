# Use official Jupyter PySpark image (much faster - everything pre-built)
FROM quay.io/jupyter/pyspark-notebook:spark-3.5.3

# Switch to root for package installation
USER root

# Install Delta Lake Python package
RUN pip install --no-cache-dir delta-spark==3.2.0

# Download Delta Lake JARs at build time (not runtime)
RUN cd /tmp && \
    curl -fsSLO https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.2.0/delta-spark_2.12-3.2.0.jar && \
    curl -fsSLO https://repo1.maven.org/maven2/io/delta/delta-storage/3.2.0/delta-storage-3.2.0.jar && \
    mv delta-*.jar ${SPARK_HOME}/jars/

# Configure Spark for Delta Lake (no package downloads needed)
RUN echo 'spark.sql.extensions io.delta.sql.DeltaSparkSessionExtension' >> ${SPARK_HOME}/conf/spark-defaults.conf \
    && echo 'spark.sql.catalog.spark_catalog org.apache.spark.sql.delta.catalog.DeltaCatalog' >> ${SPARK_HOME}/conf/spark-defaults.conf

# Create workspace directories
RUN mkdir -p /home/jovyan/work/notebooks /home/jovyan/work/data \
    && chown -R jovyan:users /home/jovyan/work

# Switch back to default user
USER jovyan

WORKDIR /home/jovyan/work

# Expose ports: Jupyter (8888), Spark UI (4040)
EXPOSE 8888 4040

# Disable Jupyter authentication (local dev only)
CMD ["start-notebook.py", "--NotebookApp.token=''", "--NotebookApp.password=''"]
