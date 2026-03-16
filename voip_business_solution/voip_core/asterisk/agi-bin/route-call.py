#!/usr/bin/env python3
"""
Asterisk AGI Script: Route Outbound Call
Checks user subscription and routes to the correct PSTN gateway via Flask backend API.
"""

import sys
import os
import requests
import logging

logging.basicConfig(
    filename='/var/log/asterisk/agi-route-call.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

BACKEND_URL = os.environ.get('AGI_BACKEND_URL', 'http://localhost:5000')
AGI_API_KEY = os.environ.get('AGI_API_KEY', 'agi-internal-secret')


def read_agi_env():
    """Read AGI environment variables from stdin."""
    env = {}
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        if ':' in line:
            key, _, value = line.partition(':')
            env[key.strip()] = value.strip()
    return env


def agi_command(cmd):
    """Send an AGI command and return the result."""
    sys.stdout.write(f'{cmd}\n')
    sys.stdout.flush()
    return sys.stdin.readline().strip()


def set_variable(name, value):
    """Set an Asterisk channel variable."""
    agi_command(f'SET VARIABLE {name} {value}')


def get_user_subscription(caller_id):
    """Check if the caller has an active subscription via the backend API."""
    try:
        resp = requests.get(
            f'{BACKEND_URL}/api/subscriptions/usage',
            headers={
                'X-AGI-Key': AGI_API_KEY,
                'X-Caller-ID': caller_id
            },
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        logging.error(f"Backend API error checking subscription for {caller_id}: {e}")
        return None


def get_user_did(caller_id):
    """Get the user's assigned DID for outbound caller ID."""
    try:
        resp = requests.get(
            f'{BACKEND_URL}/api/dids/my-numbers',
            headers={
                'X-AGI-Key': AGI_API_KEY,
                'X-Caller-ID': caller_id
            },
            timeout=5
        )
        if resp.status_code == 200:
            dids = resp.json()
            if dids:
                return dids[0]['number']
        return None
    except Exception as e:
        logging.error(f"Backend API error getting DID for {caller_id}: {e}")
        return None


def determine_gateway(called_number):
    """Determine the PSTN gateway based on the called number prefix."""
    if called_number.startswith('1') or called_number.startswith('+1'):
        return 'SIP/pstn-us-gateway'
    elif called_number.startswith('44') or called_number.startswith('+44'):
        return 'SIP/pstn-uk-gateway'
    elif called_number.startswith('234') or called_number.startswith('+234'):
        return 'SIP/pstn-ng-gateway'
    else:
        return 'SIP/pstn-us-gateway'  # Default gateway


def main():
    env = read_agi_env()
    caller_id = env.get('agi_callerid', 'unknown')
    called_number = env.get('agi_extension', '')

    logging.info(f"Route call: {caller_id} -> {called_number}")

    # Check subscription
    sub_data = get_user_subscription(caller_id)
    if not sub_data or sub_data.get('usage') is None:
        logging.warning(f"No active subscription for {caller_id}")
        set_variable('ROUTE_ALLOWED', 'NO')
        set_variable('ROUTE_REASON', 'NO_SUBSCRIPTION')
        return

    usage = sub_data
    remaining = usage.get('remaining_minutes', 0)
    if remaining <= 0:
        logging.warning(f"No remaining minutes for {caller_id}")
        set_variable('ROUTE_ALLOWED', 'NO')
        set_variable('ROUTE_REASON', 'NO_MINUTES')
        return

    # Get outbound caller ID from assigned DID
    outbound_cid = get_user_did(caller_id) or caller_id

    # Determine gateway
    gateway = determine_gateway(called_number)
    clean_number = called_number.lstrip('+')

    set_variable('ROUTE_ALLOWED', 'YES')
    set_variable('ROUTE_GATEWAY', gateway)
    set_variable('ROUTE_NUMBER', clean_number)
    set_variable('OUTBOUND_CID', outbound_cid)
    logging.info(f"Route approved: {caller_id} -> {called_number} via {gateway}")


if __name__ == '__main__':
    main()
