#!/bin/bash
# Automated Database Backup Script for VoIP Business Solution
# Based on VoIP Business Solution: Enhanced Deployment Guide (Version 2.0)
#
# This script would typically be placed in /opt/scripts/backup-database.sh
# and made executable (chmod +x /opt/scripts/backup-database.sh).

# Configuration - Adjust these variables as necessary
DB_HOST="${DB_HOST:-db-server-01}" # Default to db-server-01 if not set by env
DB_NAME="${DB_NAME:-voip_production}"
DB_USER="${DB_USER:-backup_user}"
DB_PASSWORD="${DB_PASSWORD:-backup_password}" # IMPORTANT: Store password securely, e.g., in ~/.pgpass or use environment variables

BACKUP_DIR_BASE="/opt/backups" # Base directory for all backups
BACKUP_DIR="${BACKUP_DIR_BASE}/database"
S3_BUCKET="${S3_BUCKET:-voip-backups}" # S3 bucket name for cloud storage
S3_PREFIX="database" # Sub-folder within the S3 bucket

RETENTION_DAYS="${RETENTION_DAYS:-30}" # Number of days to keep local backups (S3 cleanup is separate)
DATE_FORMAT=$(date +%Y%m%d_%H%M%S)
BACKUP_FILENAME="voip_db_${DB_NAME}_${DATE_FORMAT}.sql"
BACKUP_FILEPATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"
if [ $? -ne 0 ]; then
  echo "$(date): ERROR: Failed to create backup directory $BACKUP_DIR. Exiting."
  exit 1
fi

# Logging function
log_message() {
  echo "$(date): $1"
}

log_message "INFO: Starting database backup for $DB_NAME from $DB_HOST..."

# Create database dump using pg_dump
# --verbose: provides more details during the dump
# --clean: includes commands to clean (drop) database objects before recreating
# --no-owner: excludes ownership commands (useful if restoring to a different user/owner)
# --no-privileges (or --no-acl): excludes grant/revoke commands
# The document specifies --no-owner and --no-privileges.
export PGPASSWORD="$DB_PASSWORD" # Set PGPASSWORD for non-interactive authentication
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
  --verbose --clean --no-owner --no-privileges \
  > "$BACKUP_FILEPATH"

# Check if pg_dump was successful
if [ $? -eq 0 ]; then
  log_message "INFO: Database dump completed successfully: $BACKUP_FILEPATH"

  # Compress backup file
  log_message "INFO: Compressing backup file $BACKUP_FILEPATH..."
  gzip "$BACKUP_FILEPATH"
  if [ $? -eq 0 ]; then
    BACKUP_FILEPATH_GZ="${BACKUP_FILEPATH}.gz"
    log_message "INFO: Backup file compressed successfully: $BACKUP_FILEPATH_GZ"

    # Upload to S3 (if AWS CLI is configured and S3_BUCKET is set)
    if [ -n "$S3_BUCKET" ]; then
      log_message "INFO: Uploading $BACKUP_FILEPATH_GZ to s3://${S3_BUCKET}/${S3_PREFIX}/ ..."
      aws s3 cp "$BACKUP_FILEPATH_GZ" "s3://${S3_BUCKET}/${S3_PREFIX}/" --acl private
      if [ $? -eq 0 ]; then
        log_message "INFO: Backup uploaded to S3 successfully."
        # Remove local backup after successful S3 upload to save space
        log_message "INFO: Removing local backup file $BACKUP_FILEPATH_GZ."
        rm "$BACKUP_FILEPATH_GZ"
      else
        log_message "ERROR: Failed to upload backup to S3. Local file kept: $BACKUP_FILEPATH_GZ"
        # Consider adding retry logic or alternative notification here.
        # exit 1 # Optionally exit if S3 upload is critical
      fi
    else
      log_message "WARN: S3_BUCKET not set. Skipping S3 upload. Local file kept: $BACKUP_FILEPATH_GZ"
    fi
  else
    log_message "ERROR: Failed to compress backup file $BACKUP_FILEPATH. SQL dump kept."
    # exit 1 # Optionally exit if compression fails
  fi
else
  log_message "ERROR: Database backup (pg_dump) failed. No backup file created or file is incomplete."
  # Remove potentially incomplete backup file
  if [ -f "$BACKUP_FILEPATH" ]; then
    rm "$BACKUP_FILEPATH"
  fi
  exit 1
fi

# Clean up old local backups (older than RETENTION_DAYS)
# This part is for local cleanup. S3 cleanup is handled separately in the document.
if [ -d "$BACKUP_DIR" ]; then
    log_message "INFO: Cleaning up local backups older than $RETENTION_DAYS days in $BACKUP_DIR..."
    find "$BACKUP_DIR" -name "voip_db_*.sql.gz" -type f -mtime +"$RETENTION_DAYS" -print -delete
    log_message "INFO: Local backup cleanup complete."
else
    log_message "WARN: Backup directory $BACKUP_DIR not found for local cleanup."
fi


# S3 cleanup logic (from the document)
# This part requires AWS CLI and appropriate permissions.
# It lists files, parses dates, and deletes if older than RETENTION_DAYS.
# This is a bit complex in shell; consider S3 lifecycle policies for robustness.
if [ -n "$S3_BUCKET" ]; then
  log_message "INFO: Cleaning up old S3 backups from s3://${S3_BUCKET}/${S3_PREFIX}/ older than $RETENTION_DAYS days..."

  # Get current time in seconds since epoch
  NOW_SECONDS=$(date +%s)
  RETENTION_SECONDS=$((RETENTION_DAYS * 24 * 60 * 60))

  aws s3api list-objects-v2 --bucket "$S3_BUCKET" --prefix "${S3_PREFIX}/" --query 'Contents[?LastModified <= `'"$(date -d "@$((NOW_SECONDS - RETENTION_SECONDS))" --iso-8601=seconds)"'`].[Key]' --output text | while read -r s3_key; do
    if [[ -n "$s3_key" && "$s3_key" != "None" ]]; then # Ensure key is not empty or "None" string
      log_message "INFO: Deleting old S3 backup: s3://${S3_BUCKET}/${s3_key}"
      aws s3 rm "s3://${S3_BUCKET}/${s3_key}"
      if [ $? -ne 0 ]; then
        log_message "ERROR: Failed to delete s3://${S3_BUCKET}/${s3_key}"
      fi
    fi
  done
  log_message "INFO: S3 backup cleanup process complete."
else
  log_message "WARN: S3_BUCKET not set. Skipping S3 cleanup."
fi

# Unset PGPASSWORD
unset PGPASSWORD

log_message "INFO: Database backup process completed."
exit 0

# Crontab entry example (run daily at 2 AM):
# 0 2 * * * /opt/scripts/backup-database.sh >> /var/log/backup_database.log 2>&1
#
# Ensure the script is executable: chmod +x /opt/scripts/backup-database.sh
# Ensure AWS CLI is installed and configured with credentials that have S3 access
# (e.g., via IAM roles for EC2 instances, or ~/.aws/credentials).
# Ensure ~/.pgpass is configured for the backup_user or PGPASSWORD is handled securely if not via env.
# Example for ~/.pgpass (permissions 0600):
# hostname:port:database:username:password
# db-server-01:5432:voip_production:backup_user:backup_password
