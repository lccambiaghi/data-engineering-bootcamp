# Hive Metastore with PostgreSQL driver
FROM apache/hive:4.0.0

USER root

# Download PostgreSQL JDBC driver (using ADD since curl/wget may not be available)
ADD https://jdbc.postgresql.org/download/postgresql-42.7.1.jar /opt/hive/lib/postgresql-42.7.1.jar
RUN chmod 644 /opt/hive/lib/postgresql-42.7.1.jar

USER hive
