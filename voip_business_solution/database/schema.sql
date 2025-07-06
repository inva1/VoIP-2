-- PostgreSQL Schema for VoIP Business Solution
-- Version 2.0

-- Users table with enhanced fields for multi-country support
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    country_code VARCHAR(3), -- ISO 3166-1 alpha-3
    kyc_status VARCHAR(20) DEFAULT 'pending', -- e.g., pending, verified, rejected
    kyc_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Consider trigger for auto-update
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- KYC records table for identity verification
CREATE TABLE kyc_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    document_type VARCHAR(50), -- e.g., passport, national_id
    document_number VARCHAR(100),
    document_country VARCHAR(3), -- ISO 3166-1 alpha-3
    verification_status VARCHAR(20) DEFAULT 'pending', -- e.g., pending, approved, rejected
    risk_score INTEGER,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    verified_by INTEGER, -- Admin user ID who verified
    notes TEXT,
    document_front_url VARCHAR(500),
    document_back_url VARCHAR(500),
    selfie_url VARCHAR(500)
);

-- Subscription plans table
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    plan_code VARCHAR(50) UNIQUE NOT NULL,
    plan_name VARCHAR(100) NOT NULL,
    description TEXT,
    target_country VARCHAR(3), -- Primary market for this plan (e.g., NGA for Nigerian users)
    destination_countries TEXT[], -- Array of ISO 3166-1 alpha-3 country codes this plan allows calling TO
    monthly_fee DECIMAL(10,2),
    included_minutes INTEGER,
    included_messages INTEGER, -- For SMS
    overage_rate_voice DECIMAL(6,4), -- Cost per minute
    overage_rate_sms DECIMAL(6,4),   -- Cost per SMS
    features JSONB, -- e.g., {"caller_id": true, "call_recording": false}
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User subscriptions table
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan_id INTEGER REFERENCES subscription_plans(id),
    status VARCHAR(20) DEFAULT 'active', -- e.g., active, expired, cancelled
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    auto_renew BOOLEAN DEFAULT true,
    usage_minutes INTEGER DEFAULT 0,
    usage_messages INTEGER DEFAULT 0, -- For SMS
    last_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- When usage was last reset (billing cycle start)
);

-- DID numbers table
CREATE TABLE did_numbers (
    id SERIAL PRIMARY KEY,
    number VARCHAR(20) UNIQUE NOT NULL, -- E.164 format
    country_code VARCHAR(3), -- Number's country (ISO 3166-1 alpha-3)
    area_code VARCHAR(10),
    number_type VARCHAR(20), -- local, toll-free, mobile
    provider VARCHAR(100),
    monthly_cost DECIMAL(8,2),
    assigned_to_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- User ID it's assigned to
    status VARCHAR(20) DEFAULT 'available', -- available, assigned, reserved
    assigned_at TIMESTAMP,
    expires_at TIMESTAMP -- Expiry from provider or assignment period
);

-- Call detail records table
CREATE TABLE call_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id), -- Can be NULL for system calls
    call_id VARCHAR(100) UNIQUE, -- From VoIP system (e.g., Asterisk UniqueID)
    caller_number VARCHAR(20),
    called_number VARCHAR(20),
    call_direction VARCHAR(10), -- inbound, outbound, internal
    call_type VARCHAR(20), -- voice, video
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration INTEGER, -- in seconds
    call_status VARCHAR(20), -- answered, busy, failed
    termination_reason VARCHAR(50),
    cost DECIMAL(10,4),
    carrier_used VARCHAR(100),
    quality_score INTEGER, -- e.g., MOS score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SMS records table
CREATE TABLE sms_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id), -- Can be NULL for system messages
    message_id VARCHAR(100) UNIQUE, -- From SMS gateway
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    message_text TEXT,
    message_type VARCHAR(20), -- sms, mms, notification
    direction VARCHAR(10), -- inbound, outbound
    status VARCHAR(20), -- sent, delivered, failed
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cost DECIMAL(8,4),
    carrier_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regulatory CDR table (as per document for compliance)
CREATE TABLE regulatory_cdr (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(100) UNIQUE NOT NULL, -- Can FK to call_records.call_id
    calling_party VARCHAR(20) NOT NULL,
    called_party VARCHAR(20) NOT NULL,
    call_start_time TIMESTAMP NOT NULL,
    call_end_time TIMESTAMP,
    call_duration INTEGER, -- in seconds
    originating_carrier VARCHAR(100),
    terminating_carrier VARCHAR(100),
    call_type VARCHAR(20), -- local, long_distance, international, emergency
    billing_number VARCHAR(20),
    charge_amount DECIMAL(10,4),
    tax_amount DECIMAL(10,4),
    regulatory_fees DECIMAL(10,4),
    jurisdiction VARCHAR(10), -- e.g., US-NY, GBR
    emergency_service_flag BOOLEAN DEFAULT FALSE,
    lawful_intercept_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retention_until TIMESTAMP, -- For data retention policies
    e911_capable BOOLEAN DEFAULT FALSE,
    calea_compliant BOOLEAN DEFAULT FALSE,
    stir_shaken_verified BOOLEAN DEFAULT FALSE
);

-- Create indexes for performance
-- Users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_kyc_status ON users(kyc_status);
CREATE INDEX idx_users_country_code ON users(country_code);

-- KYC records table
CREATE INDEX idx_kyc_records_user_id ON kyc_records(user_id);
CREATE INDEX idx_kyc_records_status ON kyc_records(verification_status);
CREATE INDEX idx_kyc_records_document_country ON kyc_records(document_country);

-- Subscription plans table
CREATE INDEX idx_subscription_plans_target_country ON subscription_plans(target_country);
CREATE INDEX idx_subscription_plans_is_active ON subscription_plans(is_active);

-- User subscriptions table
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_plan_id ON user_subscriptions(plan_id);
CREATE INDEX idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX idx_user_subscriptions_expires_at ON user_subscriptions(expires_at);

-- DID numbers table
CREATE INDEX idx_did_numbers_assigned_to_user_id ON did_numbers(assigned_to_user_id);
CREATE INDEX idx_did_numbers_status ON did_numbers(status);
CREATE INDEX idx_did_numbers_country_code ON did_numbers(country_code);

-- Call records table
CREATE INDEX idx_call_records_user_id ON call_records(user_id);
CREATE INDEX idx_call_records_start_time ON call_records(start_time);
CREATE INDEX idx_call_records_caller_number ON call_records(caller_number);
CREATE INDEX idx_call_records_called_number ON call_records(called_number);

-- SMS records table
CREATE INDEX idx_sms_records_user_id ON sms_records(user_id);
CREATE INDEX idx_sms_records_from_number ON sms_records(from_number);
CREATE INDEX idx_sms_records_to_number ON sms_records(to_number);
CREATE INDEX idx_sms_records_sent_at ON sms_records(sent_at);

-- Regulatory CDR table
CREATE INDEX idx_regulatory_cdr_call_start_time ON regulatory_cdr(call_start_time);
CREATE INDEX idx_regulatory_cdr_jurisdiction ON regulatory_cdr(jurisdiction);
CREATE INDEX idx_regulatory_cdr_emergency_service_flag ON regulatory_cdr(emergency_service_flag);
CREATE INDEX idx_regulatory_cdr_calling_party ON regulatory_cdr(calling_party);
CREATE INDEX idx_regulatory_cdr_called_party ON regulatory_cdr(called_party);


-- Trigger function to update 'updated_at' timestamp on users table
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_modtime
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Note: Similar triggers can be added for other tables if they have an 'updated_at' column
-- and require automatic updates on modification. For example, subscription_plans if it gets an updated_at.

-- Data Retention Policy Stubs (to be implemented as cron jobs or scheduled tasks)
-- These are conceptual based on the document; actual implementation would be external scripts or procedures.
-- Example:
-- -- Delete old call records (retain for 2 years)
-- -- DELETE FROM call_records WHERE created_at < NOW() - INTERVAL '2 years';
-- -- Delete old SMS records (retain for 2 years)
-- -- DELETE FROM sms_records WHERE created_at < NOW() - INTERVAL '2 years';
-- -- Anonymize old KYC records (retain for 7 years)
-- -- UPDATE kyc_records
-- -- SET document_front_url = NULL, document_back_url = NULL, selfie_url = NULL, notes = 'Anonymized due to retention policy'
-- -- WHERE verified_at < NOW() - INTERVAL '7 years' AND verification_status = 'verified';
-- -- Delete inactive user accounts (retain for 3 years after last login)
-- -- DELETE FROM users WHERE last_login < NOW() - INTERVAL '3 years' AND is_active = false;

-- End of Schema
-- Consider adding foreign key constraints for `verified_by` in `kyc_records` if it refers to an admin users table (not defined here).
-- Consider adding constraints for `country_code` fields to ensure valid ISO codes if necessary, though application logic usually handles this.
-- The `TEXT[]` type for `destination_countries` in `subscription_plans` is PostgreSQL specific.
-- `JSONB` for `features` is also PostgreSQL specific.
-- `ON DELETE CASCADE` and `ON DELETE SET NULL` are used for referential integrity. Review these based on business logic.
-- For example, `ON DELETE CASCADE` for `kyc_records` means if a user is deleted, their KYC records are also deleted.
-- `ON DELETE SET NULL` for `did_numbers` means if a user is deleted, their assigned DIDs become unassigned (available).
-- `user_id` in `call_records` and `sms_records` is nullable to allow for system-generated calls/SMS or calls/SMS not tied to a specific user.
-- `call_id` in `regulatory_cdr` could have a foreign key to `call_records.call_id` if every regulatory CDR corresponds to a record in `call_records`.

-- Default password for voip_admin as per document (for initial setup, should be changed)
-- The user creation and grant are done via psql commands in the document:
-- CREATE DATABASE voip_production;
-- CREATE USER voip_admin WITH ENCRYPTED PASSWORD 'secure_password_here';
-- GRANT ALL PRIVILEGES ON DATABASE voip_production TO voip_admin;
-- This SQL file defines the schema *within* that database.
