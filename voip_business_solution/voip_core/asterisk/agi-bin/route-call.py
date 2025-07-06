#!/usr/bin/env python3

import sys
import os

# Add a path to a common library directory if you have one
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')) # Example

# For database access, you would typically use a library like psycopg2 for PostgreSQL
# and import your Flask app's SQLAlchemy models or a direct DB connection utility.
# This is a simplified example that doesn't perform actual DB lookups.
# In a real scenario:
# from your_flask_app.models import User, SubscriptionPlan, UserSubscription, DIDNumber
# from your_flask_app.app import db # If using SQLAlchemy session

# --- Mock Database/Service Functions (Replace with actual backend calls) ---

def get_user_by_callerid(caller_id_num):
    """
    Mock function to get user details based on caller ID.
    In a real app, this would query the database.
    """
    # Example: Query User model where phone_number or assigned DID matches caller_id_num
    if caller_id_num == "1001": # Assuming 1001 is an internal extension used as CallerID
        return {"id": 1, "username": "user1001", "country_code": "NGA"}
    elif caller_id_num == "+12025550104": # An assigned DID
        # Find user associated with this DID
        return {"id": 2, "username": "did_user_us", "country_code": "USA"}
    return None

def get_user_active_subscription(user_id, destination_country_code):
    """
    Mock function to check if a user has an active subscription for a destination country.
    `destination_country_code` should be 2-letter or 3-letter ISO code.
    """
    # Example: Query UserSubscription and SubscriptionPlan models
    # User 1 (Nigerian user) calling US (USA) or UK (GBR)
    if user_id == 1:
        if destination_country_code in ["USA", "GBR"]:
            return {"plan_name": "Premium International", "overage_rate_voice": 0.05, "included_minutes": 500, "usage_minutes": 100}
    # User 2 (US user) calling Nigeria (NGA)
    elif user_id == 2:
        if destination_country_code == "NGA":
            return {"plan_name": "Call Nigeria Plan", "overage_rate_voice": 0.10, "included_minutes": 200, "usage_minutes": 50}
    return None

def get_assigned_did_for_outbound_cid(user_id, destination_country_code):
    """
    Mock: Get the appropriate DID for the user to use as outbound Caller ID.
    For Nigerian user calling US, might be a US DID.
    For US user calling Nigeria, might be a Nigerian DID or their primary US DID.
    """
    if user_id == 1 and destination_country_code == "USA":
        return "+12025550100" # Their assigned US DID
    if user_id == 1 and destination_country_code == "GBR":
        return "+442079460000" # Their assigned UK DID
    if user_id == 2 and destination_country_code == "NGA":
        return "+23414405000" # Their assigned NG DID or a generic one
    return "0000000000" # Fallback or anonymous CID

def get_pstn_gateway_for_country(destination_country_code):
    """
    Mock: Determine PSTN gateway based on destination country.
    These should match the global variables in extensions.conf.
    """
    if destination_country_code == "USA":
        return "PSTN_US_GATEWAY" # This will be SIP/pstn-us-gateway in dialplan
    elif destination_country_code == "GBR":
        return "PSTN_UK_GATEWAY" # SIP/pstn-uk-gateway
    elif destination_country_code == "NGA":
        return "PSTN_NG_GATEWAY" # SIP/pstn-ng-gateway
    return None

def get_country_code_from_e164(number_e164):
    """
    Very basic mock to extract a 'country code' for routing.
    A proper library (e.g., phonenumbers) should be used for this.
    """
    if number_e164.startswith("1"): return "USA" # North America
    if number_e164.startswith("44"): return "GBR" # UK
    if number_e164.startswith("234"): return "NGA" # Nigeria
    # Add more rules or use a library
    return "OTHER"

# --- AGI Environment Handling ---

class AGI:
    def __init__(self):
        self.env = {}
        self._read_env()

    def _read_env(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                break
            key, value = line.split(': ', 1)
            self.env[key.lower().replace('-', '_')] = value
        # Log environment for debugging
        self.log(f"AGI ENV: {self.env}")


    def get_variable(self, name):
        self.send_command(f'GET VARIABLE "{name}"')
        response = self.read_response() # "200 result=1 (value)" or "200 result=0"
        if response.startswith("200 result=1"):
            return response.split('(', 1)[1].split(')', 1)[0]
        return None

    def set_variable(self, name, value):
        self.send_command(f'SET VARIABLE "{name}" "{value}"')
        self.read_response() # "200 result=0" or "200 result=1"

    def send_command(self, command):
        sys.stdout.write(command + "\n")
        sys.stdout.flush()
        self.log(f"Sent: {command}")

    def read_response(self):
        response = sys.stdin.readline().strip()
        self.log(f"Recv: {response}")
        return response

    def log(self, message, level="VERBOSE"):
        """ Sends a message to Asterisk console via VERBOSE """
        # Sanitize message to prevent issues with quotes or special chars in command
        escaped_message = str(message).replace('"', '\\"').replace('\n', ' ')
        self.send_command(f'{level} "{escaped_message}" "1"') # Level 1 for Verbose
        # Read response, but it's usually just "200 result=0" or similar
        self.read_response()


# --- Main AGI Logic ---

def main():
    agi = AGI()

    caller_id_num = agi.env.get('agi_callerid', 'unknown')
    # Destination number comes as an argument from extensions.conf
    # extensions.conf: AGI(${AGI_ROUTE_CALL},${CALLERID(num)},${EXTEN})
    # So, sys.argv[1] is CALLERID(num), sys.argv[2] is EXTEN (destination)

    # Check if enough arguments are passed (script name + 2 args)
    if len(sys.argv) < 3:
        agi.log("Error: Not enough arguments passed to AGI script.", level="ERROR")
        agi.set_variable("ROUTE_ALLOWED", "NO")
        sys.exit(1)

    # These are passed from extensions.conf: AGI(script, arg1, arg2, ...)
    # Here, arg1 = ${CALLERID(num)}, arg2 = ${EXTEN} (destination number)
    script_caller_id_num = sys.argv[1]
    destination_number_e164 = sys.argv[2] # Number after prefix stripping

    agi.log(f"AGI Script '{os.path.basename(__file__)}' started.")
    agi.log(f"Effective Caller ID: {caller_id_num}, Script Arg Caller ID: {script_caller_id_num}, Destination: {destination_number_e164}")

    # Use the caller ID passed as argument, as agi_callerid might be different
    user_details = get_user_by_callerid(script_caller_id_num)

    if not user_details:
        agi.log(f"User not found for Caller ID: {script_caller_id_num}", level="WARNING")
        agi.set_variable("ROUTE_ALLOWED", "NO")
        sys.exit(0)

    user_id = user_details["id"]
    agi.log(f"User ID: {user_id} found for Caller ID: {script_caller_id_num}")

    # Determine destination country
    dest_country_iso = get_country_code_from_e164(destination_number_e164)
    agi.log(f"Destination number: {destination_number_e164}, Deduced Country ISO: {dest_country_iso}")

    if dest_country_iso == "OTHER":
        agi.log(f"Cannot determine country for destination: {destination_number_e164}", level="WARNING")
        agi.set_variable("ROUTE_ALLOWED", "NO")
        sys.exit(0)

    # Check subscription
    subscription = get_user_active_subscription(user_id, dest_country_iso)
    if not subscription:
        agi.log(f"No active subscription for User ID {user_id} to country {dest_country_iso}", level="WARNING")
        agi.set_variable("ROUTE_ALLOWED", "NO")
        sys.exit(0)

    agi.log(f"User {user_id} has active subscription '{subscription['plan_name']}' for {dest_country_iso}")

    # Check if user has enough minutes or if overage is allowed (simplified)
    # Real logic would involve checking balance for overage, etc.
    # included_minutes = subscription.get("included_minutes", 0)
    # usage_minutes = subscription.get("usage_minutes", 0)
    # if usage_minutes >= included_minutes and subscription.get("overage_rate_voice", 0) == 0: # No overage
    #     agi.log(f"User {user_id} has exceeded included minutes and no overage allowed.", level="WARNING")
    #     agi.set_variable("ROUTE_ALLOWED", "NO")
    #     sys.exit(0)

    # Determine PSTN gateway
    gateway_name_var = get_pstn_gateway_for_country(dest_country_iso)
    if not gateway_name_var:
        agi.log(f"No PSTN gateway configured for country {dest_country_iso}", level="ERROR")
        agi.set_variable("ROUTE_ALLOWED", "NO")
        sys.exit(0)

    # The gateway_name_var is the *name* of the global variable in extensions.conf
    # e.g., "PSTN_US_GATEWAY". Asterisk dialplan will use ${PSTN_US_GATEWAY}.
    # So we pass the variable name itself, not its value from this script.
    # Or, if the AGI sets a generic variable like ROUTE_DIAL_STRING, then resolve it here:
    # resolved_gateway_dial_string = f"SIP/{gateway_name_var.lower()}" # e.g. SIP/pstn_us_gateway
    # For Dial(${ROUTE_GATEWAY}/${ROUTE_NUMBER}), ROUTE_GATEWAY should be PSTN_US_GATEWAY etc.

    agi.log(f"Selected gateway variable: {gateway_name_var} for country {dest_country_iso}")

    # Determine Outbound Caller ID
    outbound_cid = get_assigned_did_for_outbound_cid(user_id, dest_country_iso)
    if not outbound_cid:
        outbound_cid = script_caller_id_num # Fallback to original CID if no specific DID
    agi.log(f"Setting outbound CID to: {outbound_cid}")


    # Set variables for Asterisk dialplan
    agi.set_variable("ROUTE_ALLOWED", "YES")
    agi.set_variable("ROUTE_GATEWAY", gateway_name_var) # e.g., PSTN_US_GATEWAY
    agi.set_variable("ROUTE_NUMBER", destination_number_e164) # Number to dial on the gateway
    agi.set_variable("OUTBOUND_CID", outbound_cid)

    agi.log(f"Routing allowed for {script_caller_id_num} to {destination_number_e164} via {gateway_name_var} with CID {outbound_cid}")
    sys.exit(0) # Important to exit with 0 for success

if __name__ == "__main__":
    # Ensure the script is executable (chmod +x route-call.py)
    # For debugging AGI scripts, it's helpful to redirect stderr to a file
    # Example: in extensions.conf, AGI(..., 2>/tmp/agi_debug.log) - not standard AGI syntax
    # Better: log extensively within the script using agi.log()

    # Create a dummy agi.env for testing if run directly
    # if sys.stdin.isatty(): # If run from console, not Asterisk
    #     sys.stderr.write("This script is intended to be run by Asterisk AGI.\n")
    #     # Simulate AGI environment for testing
    #     # Provide dummy arguments like Asterisk would
    #     # sys.argv.append("1001") # Dummy CallerID
    #     # sys.argv.append("16505551234") # Dummy Destination
    #     # Simulate AGI input
    #     # sim_stdin = "agi_network: yes\nagi_network_script: route-call.py\nagi_callerid: 1001\n\n"
    #     # sys.stdin = io.StringIO(sim_stdin)

    main()
