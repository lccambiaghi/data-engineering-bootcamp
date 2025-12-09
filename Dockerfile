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

# Download Hadoop AWS JARs for S3 access (allows reading from public S3 URLs)
RUN cd /tmp && \
    curl -fsSLO https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -fsSLO https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    mv hadoop-aws-*.jar aws-java-sdk-*.jar ${SPARK_HOME}/jars/

# Download PostgreSQL JDBC driver for shared metastore
RUN cd /tmp && \
    curl -fsSLO https://jdbc.postgresql.org/download/postgresql-42.7.1.jar && \
    mv postgresql-*.jar ${SPARK_HOME}/jars/

# Configure Spark for Delta Lake and S3 access
RUN echo 'spark.sql.extensions io.delta.sql.DeltaSparkSessionExtension' >> ${SPARK_HOME}/conf/spark-defaults.conf \
    && echo 'spark.sql.catalog.spark_catalog org.apache.spark.sql.delta.catalog.DeltaCatalog' >> ${SPARK_HOME}/conf/spark-defaults.conf \
    && echo 'spark.hadoop.fs.s3a.aws.credentials.provider org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider' >> ${SPARK_HOME}/conf/spark-defaults.conf

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
