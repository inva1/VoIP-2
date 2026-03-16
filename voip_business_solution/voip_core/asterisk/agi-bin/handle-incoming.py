#!/usr/bin/env python3
"""
Asterisk AGI Script: Handle Incoming Call
Looks up the DID that was called, finds the assigned user, and routes accordingly.
"""

import sys
import os
import requests
import logging

logging.basicConfig(
    filename='/var/log/asterisk/agi-handle-incoming.log',
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


def lookup_did_assignment(did_number):
    """Look up which user a DID is assigned to via the backend API."""
    try:
        resp = requests.get(
            f'{BACKEND_URL}/api/dids/available',
            headers={
                'X-AGI-Key': AGI_API_KEY,
            },
            params={'number': did_number},
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        logging.error(f"Backend API error looking up DID {did_number}: {e}")
        return None


def main():
    env = read_agi_env()
    called_did = env.get('agi_extension', '')
    caller_number = env.get('agi_callerid', 'unknown')

    logging.info(f"Incoming call: {caller_number} -> DID {called_did}")

    if not called_did:
        logging.warning("No DID provided for incoming call")
        set_variable('FORWARD_ALLOWED', 'NO')
        set_variable('FORWARD_REASON', 'NO_DID')
        return

    # Look up DID assignment
    did_info = lookup_did_assignment(called_did)

    if not did_info:
        logging.warning(f"DID {called_did} not found or not assigned")
        set_variable('FORWARD_ALLOWED', 'NO')
        set_variable('FORWARD_REASON', 'DID_NOT_FOUND')
        return

    # If DID is assigned, route to the user's SIP endpoint
    if isinstance(did_info, list) and len(did_info) > 0:
        did_record = did_info[0]
        assigned_user_id = did_record.get('assigned_to')
        if assigned_user_id:
            set_variable('FORWARD_ALLOWED', 'YES')
            set_variable('FORWARD_TO_USER', f'SIP/{assigned_user_id}')
            logging.info(f"Routing incoming call to user {assigned_user_id}")
            return

    logging.warning(f"DID {called_did} is not assigned to any user")
    set_variable('FORWARD_ALLOWED', 'NO')
    set_variable('FORWARD_REASON', 'DID_UNASSIGNED')


if __name__ == '__main__':
    main()
