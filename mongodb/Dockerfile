# Use the official MongoDB image from Docker Hub
FROM mongo:latest

# Copy any initialization scripts you may want to use
# COPY init.sh /docker-entrypoint-initdb.d/

# Expose the default MongoDB port
EXPOSE 27017

# Optionally define MongoDB user and password (overrides defaults if set)
ENV MONGO_INITDB_ROOT_USERNAME=root
ENV MONGO_INITDB_ROOT_PASSWORD=example
