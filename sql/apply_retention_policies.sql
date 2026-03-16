-- SQL Script for Applying Data Retention Policies
-- Based on VoIP Business Solution: Enhanced Deployment Guide (Version 2.0)
--
-- This script contains SQL commands to delete or anonymize old data
-- according to the defined retention policies.
-- It should be executed periodically (e.g., by a cron job running a shell script
-- that invokes psql with these commands or this file).

-- Ensure you are connected to the correct database (e.g., voip_production)
-- before running these commands.
-- The user executing these commands needs appropriate DELETE and UPDATE privileges.

-- Automated data retention procedures

-- 1. Delete old call records (retain for 2 years)
-- Policy: Delete call_records older than 2 years from their creation date.
\echo 'Deleting call records older than 2 years...'
DELETE FROM call_records
WHERE created_at < NOW() - INTERVAL '2 years';
\echo Deletion of old call records complete. Affected rows: \ බලපෑමට ලක් වූ පේළි

-- 2. Delete old SMS records (retain for 2 years)
-- Policy: Delete sms_records older than 2 years from their creation date.
\echo 'Deleting SMS records older than 2 years...'
DELETE FROM sms_records
WHERE created_at < NOW() - INTERVAL '2 years';
\echo Deletion of old SMS records complete. Affected rows: \ බලපෑමට ලක් වූ පේළි

-- 3. Anonymize old KYC records (retain for 7 years, then anonymize)
-- Policy: For KYC records verified over 7 years ago, anonymize sensitive document URLs and notes.
-- This assumes `verification_status = 'verified'` for records to be anonymized.
\echo 'Anonymizing KYC records older than 7 years (verified)...'
UPDATE kyc_records
SET
    document_front_url = NULL,
    document_back_url = NULL,
    selfie_url = NULL,
    document_number = CASE WHEN document_number IS NOT NULL THEN 'ANONYMIZED_' || SUBSTRING(document_number FROM LENGTH(document_number)-3 FOR 4) ELSE NULL END, -- Example: Keep last 4 chars, prefix
    notes = COALESCE(notes, '') || ' Anonymized due to retention policy on ' || CURRENT_DATE || '.'
WHERE
    verified_at < NOW() - INTERVAL '7 years'
    AND verification_status = 'verified'
    AND (document_front_url IS NOT NULL OR document_back_url IS NOT NULL OR selfie_url IS NOT NULL); -- Only update if there's something to anonymize
\echo Anonymization of old KYC records complete. Affected rows: \ බලපෑමට ලක් වූ පේළි

-- 4. Delete inactive user accounts (retain for 3 years after last login if inactive)
-- Policy: Delete user accounts that are marked inactive AND whose last login was over 3 years ago.
-- This is a destructive action. Ensure criteria are correct and backups exist.
-- Consider whether related data (subscriptions, KYC) should be handled first or via CASCADE.
\echo 'Deleting inactive user accounts (last login > 3 years ago)...'
-- First, ensure related data that might prevent deletion due to FK constraints is handled.
-- E.g., anonymize or delete associated KYC, subscriptions if not using CASCADE DELETE.
-- For this example, assuming CASCADE DELETE is NOT universally used, or that those records are already old.

-- It might be safer to first mark users for deletion or review.
-- UPDATE users SET status = 'pending_deletion' WHERE last_login < NOW() - INTERVAL '3 years' AND is_active = false;
-- Then a separate review or automated process deletes them.

-- Direct deletion as per document's implication:
DELETE FROM users
WHERE
    last_login < NOW() - INTERVAL '3 years'
    AND is_active = false;
\echo Deletion of inactive user accounts complete. Affected rows: \ බලපෑමට ලක් වූ පේළි

-- 5. Delete old regulatory CDRs based on their specific retention_until timestamp
-- Policy: Delete regulatory_cdr records where the current date is past their `retention_until` date.
-- This assumes `retention_until` is populated correctly based on jurisdictional requirements.
\echo 'Deleting regulatory CDRs past their retention_until date...'
DELETE FROM regulatory_cdr
WHERE retention_until IS NOT NULL AND retention_until < NOW();
\echo Deletion of expired regulatory CDRs complete. Affected rows: \ බලපෑමට ලක් වූ පේළි


-- General Notes for Execution:
-- - Test these commands thoroughly on a staging environment before running in production.
-- - Monitor performance, especially for DELETE operations on large tables. They can be I/O intensive.
--   Consider running during off-peak hours and in smaller batches if necessary.
-- - Ensure proper indexing on date columns used in WHERE clauses (e.g., created_at, verified_at, last_login, retention_until).
-- - Back up the database before running these scripts for the first time or after major changes.
-- - The `\echo` commands are for psql. If using a different client, adjust logging/output.
-- - The `\ බලපෑමට ලක් වූ පේළි` is a psql meta-command to show affected row count, if supported or use `GET DIAGNOSTICS row_count = ROW_COUNT;` in a plpgsql block.
--   A simpler way is to just let psql echo the DELETE/UPDATE counts.

\echo 'Data retention policy script execution finished.'

/*
Example shell script (`apply-retention-policies.sh`) to run this SQL file:

#!/bin/bash
DB_NAME="voip_production"
DB_USER="voip_admin" # User with appropriate privileges
DB_HOST="db-server-01"
SQL_SCRIPT_PATH="/opt/scripts/sql/apply_retention_policies.sql" # Path to this SQL file

# Ensure PGPASSWORD is set in environment or ~/.pgpass is configured for DB_USER
# export PGPASSWORD="your_voip_admin_password"

echo "Applying data retention policies from ${SQL_SCRIPT_PATH} to database ${DB_NAME} on ${DB_HOST}..."
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -a -f "$SQL_SCRIPT_PATH"

if [ $? -eq 0 ]; then
  echo "Data retention policies applied successfully."
else
  echo "ERROR: Failed to apply data retention policies."
  exit 1
fi
exit 0

*/
