-- Users table with enhanced fields for multi-country support
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    country_code VARCHAR(3),
    kyc_status VARCHAR(20) DEFAULT 'pending',
    kyc_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- KYC records table for identity verification
CREATE TABLE kyc_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    document_type VARCHAR(50),
    document_number VARCHAR(100),
    document_country VARCHAR(3),
    verification_status VARCHAR(20) DEFAULT 'pending',
    risk_score INTEGER,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    verified_by INTEGER, -- Could reference an admin user table
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
    target_country VARCHAR(3), -- Country this plan is intended for
    destination_countries TEXT[], -- Array of country codes this plan allows calling
    monthly_fee DECIMAL(10,2),
    included_minutes INTEGER,
    included_messages INTEGER,
    overage_rate_voice DECIMAL(6,4),
    overage_rate_sms DECIMAL(6,4),
    features JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User subscriptions table
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    plan_id INTEGER REFERENCES subscription_plans(id),
    status VARCHAR(20) DEFAULT 'active', -- e.g., active, expired, cancelled
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    auto_renew BOOLEAN DEFAULT true,
    usage_minutes INTEGER DEFAULT 0,
    usage_messages INTEGER DEFAULT 0,
    last_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- When usage was last reset
);

-- DID numbers table
CREATE TABLE did_numbers (
    id SERIAL PRIMARY KEY,
    number VARCHAR(20) UNIQUE NOT NULL,
    country_code VARCHAR(3),
    area_code VARCHAR(10),
    number_type VARCHAR(20), -- local, toll-free, mobile
    provider VARCHAR(100),
    monthly_cost DECIMAL(8,2),
    assigned_to INTEGER REFERENCES users(id) NULL, -- Can be unassigned
    status VARCHAR(20) DEFAULT 'available', -- e.g., available, assigned, suspended
    assigned_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL -- For DID numbers that have an expiry from provider
);

-- Call detail records table
CREATE TABLE call_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    call_id VARCHAR(100) UNIQUE, -- From Asterisk or Kamailio
    caller_number VARCHAR(20),
    called_number VARCHAR(20),
    call_direction VARCHAR(10), -- inbound, outbound
    call_type VARCHAR(20), -- voice, video
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration INTEGER, -- in seconds
    call_status VARCHAR(20), -- e.g., completed, failed, busy
    termination_reason VARCHAR(50),
    cost DECIMAL(10,4),
    carrier_used VARCHAR(100),
    quality_score INTEGER, -- e.g., MOS score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SMS records table
CREATE TABLE sms_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    message_id VARCHAR(100) UNIQUE, -- From SMS provider
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    message_text TEXT,
    message_type VARCHAR(20), -- sms, mms
    direction VARCHAR(10), -- inbound, outbound
    status VARCHAR(20), -- e.g., sent, delivered, failed
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cost DECIMAL(8,4),
    carrier_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CDR table with regulatory compliance fields
CREATE TABLE regulatory_cdr (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(100) UNIQUE NOT NULL, -- Can be FK to call_records.call_id if always present
    calling_party VARCHAR(20) NOT NULL,
    called_party VARCHAR(20) NOT NULL,
    call_start_time TIMESTAMP NOT NULL,
    call_end_time TIMESTAMP,
    call_duration INTEGER,
    originating_carrier VARCHAR(100),
    terminating_carrier VARCHAR(100),
    call_type VARCHAR(20), -- local, long_distance, international
    billing_number VARCHAR(20),
    charge_amount DECIMAL(10,4),
    tax_amount DECIMAL(10,4),
    regulatory_fees DECIMAL(10,4),
    jurisdiction VARCHAR(10),
    emergency_service_flag BOOLEAN DEFAULT FALSE,
    lawful_intercept_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Retention period based on jurisdiction
    retention_until TIMESTAMP,
    -- Compliance flags
    e911_capable BOOLEAN DEFAULT FALSE,
    calea_compliant BOOLEAN DEFAULT FALSE,
    stir_shaken_verified BOOLEAN DEFAULT FALSE
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_kyc_status ON users(kyc_status);
CREATE INDEX idx_kyc_records_user_id ON kyc_records(user_id);
CREATE INDEX idx_kyc_records_status ON kyc_records(verification_status);
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX idx_call_records_user_id ON call_records(user_id);
CREATE INDEX idx_call_records_start_time ON call_records(start_time);
CREATE INDEX idx_sms_records_user_id ON sms_records(user_id);
CREATE INDEX idx_did_numbers_assigned_to ON did_numbers(assigned_to);
CREATE INDEX idx_did_numbers_status ON did_numbers(status);
CREATE INDEX idx_regulatory_cdr_call_start_time ON regulatory_cdr(call_start_time);
CREATE INDEX idx_regulatory_cdr_jurisdiction ON regulatory_cdr(jurisdiction);
CREATE INDEX idx_regulatory_cdr_emergency ON regulatory_cdr(emergency_service_flag);

-- Data Retention Policy Placeholder Script (to be run by a cron job or scheduled task)
-- This is illustrative; actual implementation will be via a script.

-- Example: Delete old call records (retain for 2 years)
-- DELETE FROM call_records WHERE created_at < NOW() - INTERVAL '2 years';

-- Example: Delete old SMS records (retain for 2 years)
-- DELETE FROM sms_records WHERE created_at < NOW() - INTERVAL '2 years';

-- Example: Anonymize old KYC records (retain for 7 years)
-- UPDATE kyc_records
-- SET document_front_url = NULL,
--     document_back_url = NULL,
--     selfie_url = NULL,
--     notes = 'Anonymized due to retention policy'
-- WHERE verified_at < NOW() - INTERVAL '7 years' AND verification_status = 'verified';

-- Example: Delete inactive user accounts (retain for 3 years after last login)
-- DELETE FROM users WHERE last_login < NOW() - INTERVAL '3 years' AND is_active = false;

-- Note: Regulatory CDR retention might have specific jurisdictional rules.
-- The `retention_until` field in `regulatory_cdr` should be populated based on those rules.
-- A separate process would query `regulatory_cdr` where `NOW() > retention_until` for deletion.

-- User for the application
-- CREATE USER voip_admin WITH ENCRYPTED PASSWORD 'secure_password_here';
-- CREATE DATABASE voip_production;
-- GRANT ALL PRIVILEGES ON DATABASE voip_production TO voip_admin;
-- Make sure to run these user/db creation commands separately with appropriate privileges.
-- Also, connect to the voip_production database before running the schema creation.

-- Grant privileges on tables to the application user (run after tables are created)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO voip_admin;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO voip_admin;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO voip_admin;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO voip_admin;
