#!/bin/bash

# Script to initialize the PostgreSQL database and schema.
# This script is intended to be run by a user with PostgreSQL admin privileges.

# Database connection parameters (can be overridden by environment variables)
DB_HOST="${PG_HOST:-localhost}"
DB_PORT="${PG_PORT:-5432}"
DB_SUPERUSER="${PG_SUPERUSER:-postgres}" # User with rights to create databases and users
DB_NAME="${VOIP_DB_NAME:-voip_production}"
DB_USER="${VOIP_DB_USER:-voip_admin}"
DB_PASSWORD="${VOIP_DB_PASSWORD:-secure_password_here}" # Default password from document, CHANGE THIS!

# Schema file path
SCHEMA_FILE="$(dirname "$0")/schema.sql"

echo "Starting database initialization..."

# Check if psql is available
if ! command -v psql &> /dev/null
then
    echo "psql command could not be found. Please ensure PostgreSQL client tools are installed and in your PATH."
    exit 1
fi

# Check if schema file exists
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "Schema file not found at $SCHEMA_FILE"
    exit 1
fi

# Step 1: Create the database (if it doesn't exist)
echo "Checking if database '$DB_NAME' exists..."
if PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Database '$DB_NAME' already exists."
else
    echo "Creating database '$DB_NAME'..."
    PGPASSWORD=$DB_SUPERUSER_PASSWORD createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" "$DB_NAME"
    if [ $? -ne 0 ]; then
        echo "Failed to create database '$DB_NAME'. Exiting."
        exit 1
    fi
    echo "Database '$DB_NAME' created successfully."
fi

# Step 2: Create the application user (if it doesn't exist)
echo "Checking if user '$DB_USER' exists..."
# Note: psql command to check user existence can be tricky. This is a common approach.
user_exists_query="SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'"
if PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -tAc "$user_exists_query" | grep -q 1; then
    echo "User '$DB_USER' already exists."
    # Optionally, update password if needed, but be cautious
    # echo "Updating password for user '$DB_USER' (if different)..."
    # PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "ALTER USER \"$DB_USER\" WITH ENCRYPTED PASSWORD '$DB_PASSWORD';"
else
    echo "Creating user '$DB_USER'..."
    PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "CREATE USER \"$DB_USER\" WITH ENCRYPTED PASSWORD '$DB_PASSWORD';"
    if [ $? -ne 0 ]; then
        echo "Failed to create user '$DB_USER'. Exiting."
        # Consider dropping the database if user creation fails and it was newly created
        # PGPASSWORD=$DB_SUPERUSER_PASSWORD dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" "$DB_NAME"
        exit 1
    fi
    echo "User '$DB_USER' created successfully."
fi

# Step 3: Grant privileges to the application user on the database
echo "Granting privileges on database '$DB_NAME' to user '$DB_USER'..."
PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME\" TO \"$DB_USER\";"
if [ $? -ne 0 ]; then
    echo "Failed to grant privileges to user '$DB_USER' on database '$DB_NAME'. Exiting."
    exit 1
fi
echo "Privileges granted successfully."

# Step 4: Apply the schema to the database
# This should be run as the application user to ensure objects are owned by them,
# or ensure the superuser grants ownership later.
# For simplicity, we can run as superuser and then grant ownership, or let the app user run it.
# The document implies the schema is applied *after* user creation and grants.
# If Flask-Migrate is used, this script might only handle DB/user creation, and Migrate handles schema.
# However, the plan asks for schema.sql to be created AND this script.

echo "Applying schema from '$SCHEMA_FILE' to database '$DB_NAME' as user '$DB_USER'..."
# It's often better to let the voip_admin user own the tables.
# So we execute the schema file as voip_admin.
# Make sure voip_admin has permissions to create tables, sequences etc.
# GRANT ALL PRIVILEGES ON DATABASE includes this, but for more fine-grained control:
# PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "GRANT CREATE ON SCHEMA public TO \"$DB_USER\";"
# PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "GRANT USAGE ON SCHEMA public TO \"$DB_USER\";"


PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -a -f "$SCHEMA_FILE"
if [ $? -ne 0 ]; then
    echo "Failed to apply schema from '$SCHEMA_FILE'. Exiting."
    # Consider logging the error from psql
    exit 1
fi
echo "Schema applied successfully."


# Grant necessary permissions on schema objects if not already covered by GRANT ALL or ownership
# This is important if the schema was created by a superuser but should be fully accessible by DB_USER
echo "Ensuring user '$DB_USER' has necessary permissions on tables, sequences, functions in public schema..."
PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO \"$DB_USER\";"
PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO \"$DB_USER\";"
PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO \"$DB_USER\";"
# Alter default privileges for future objects created by DB_USER (or other roles if applicable)
PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO \"$DB_USER\";"
PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO \"$DB_USER\";"
PGPASSWORD=$DB_SUPERUSER_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO \"$DB_USER\";"


echo "Database initialization completed successfully."
echo "--------------------------------------------------"
echo "Database Name: $DB_NAME"
echo "Application User: $DB_USER"
echo "Application Password: (set to '$DB_PASSWORD' - ensure this is changed for production!)"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "--------------------------------------------------"
echo "IMPORTANT: If using Flask-Migrate, this script handles initial DB and User creation."
echo "Schema changes should then be managed via Flask-Migrate migrations after the initial setup."
echo "If not using Flask-Migrate, this script applies the full schema.sql."
echo "Remember to set PGPASSWORD or use a .pgpass file for non-interactive execution in production."
echo "The default password for '$DB_USER' is '$DB_PASSWORD'. CHANGE THIS IN A PRODUCTION ENVIRONMENT."

# How to run:
# 1. Ensure PostgreSQL is running and accessible.
# 2. Set environment variables if defaults are not suitable:
#    export PG_SUPERUSER_PASSWORD="your_postgres_superuser_password"
#    export VOIP_DB_PASSWORD="your_desired_strong_voip_admin_password" (optional, will use default if not set)
# 3. Make the script executable: chmod +x init_db.sh
# 4. Run the script: ./init_db.sh
#
# Note on PGPASSWORD:
# This script uses PGPASSWORD for non-interactive password input.
# In a secure environment, consider using a .pgpass file or other secure methods for password management.
# For example, create ~/.pgpass with entries like:
# localhost:5432:*:postgres:your_postgres_superuser_password
# localhost:5432:voip_production:voip_admin:your_desired_strong_voip_admin_password
# And ensure its permissions are 600 (chmod 600 ~/.pgpass).
# Then you can remove PGPASSWORD=$... from the script commands.
# This script assumes it's run in an environment where PGPASSWORD can be set or .pgpass is configured.
