#!/usr/bin/env python3

import sys
import os
# For database access (similar to route-call.py)
# from your_flask_app.models import User, DIDNumber
# from your_flask_app.app import db

# --- Mock Database/Service Functions (Replace with actual backend calls) ---

def get_did_assignment(did_number):
    """
    Mock function to get user assignment for a DID number.
    In a real app, this would query the did_numbers table.
    """
    # Example: Query DIDNumber model
    if did_number == "+12025550100": # A DID assigned to user1001
        return {"user_id": 1, "assigned_user_extension": "1001", "status": "assigned"}
    elif did_number == "+442079460000": # Another assigned DID
        return {"user_id": 2, "assigned_user_extension": "user_webrtc_002", "status": "assigned"}
    elif did_number == "08001234567": # A toll-free number routed to an IVR/Queue
        return {"user_id": None, "route_to_context": "ivr-main", "route_to_extension": "s", "status": "system_route"}
    return None

def get_user_details(user_id):
    """
    Mock function to get user details (like if they are active, DND status etc.)
    """
    if user_id == 1:
        return {"id": 1, "username": "user1001", "is_active": True, "dnd_status": False}
    if user_id == 2:
        return {"id": 2, "username": "user_webrtc_002", "is_active": True, "dnd_status": False}
    return None

# --- AGI Environment Handling (Can be shared from a common agi_utils.py) ---

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
        self.log(f"AGI ENV: {self.env}")

    def get_variable(self, name):
        self.send_command(f'GET VARIABLE "{name}"')
        response = self.read_response()
        if response.startswith("200 result=1"):
            return response.split('(', 1)[1].split(')', 1)[0]
        return None

    def set_variable(self, name, value):
        # Ensure value is a string and properly escaped for AGI command
        str_value = str(value).replace('"', '\\"')
        self.send_command(f'SET VARIABLE "{name}" "{str_value}"')
        self.read_response()

    def send_command(self, command):
        sys.stdout.write(command + "\n")
        sys.stdout.flush()
        self.log(f"Sent: {command}")

    def read_response(self):
        response = sys.stdin.readline().strip()
        self.log(f"Recv: {response}")
        return response

    def log(self, message, level="VERBOSE"):
        escaped_message = str(message).replace('"', '\\"').replace('\n', ' ')
        self.send_command(f'{level} "{escaped_message}" "1"')
        self.read_response()

# --- Main AGI Logic ---

def main():
    agi = AGI()

    # Arguments from extensions.conf: AGI(${AGI_HANDLE_INCOMING},${EXTEN},${CALLERID(num)})
    # sys.argv[0] is the script name
    # sys.argv[1] is ${EXTEN} (the DID number that was called)
    # sys.argv[2] is ${CALLERID(num)} (the external caller's number)

    if len(sys.argv) < 3:
        agi.log("Error: Not enough arguments passed to handle-incoming.py AGI script.", level="ERROR")
        agi.set_variable("FORWARD_ALLOWED", "NO")
        sys.exit(1)

    called_did_number = sys.argv[1]
    external_caller_id_num = sys.argv[2]

    agi.log(f"AGI Script '{os.path.basename(__file__)}' started.")
    agi.log(f"Incoming call to DID: {called_did_number} from External CID: {external_caller_id_num}")

    did_info = get_did_assignment(called_did_number)

    if not did_info:
        agi.log(f"DID number {called_did_number} is not assigned or not found.", level="WARNING")
        agi.set_variable("FORWARD_ALLOWED", "NO")
        # Optionally, route to a generic "number not in service" announcement
        # agi.stream_file("ss-noservice") # Example sound file
        sys.exit(0)

    agi.log(f"DID Info: {did_info}")

    if did_info.get("status") == "system_route":
        # Example: DID routes to an IVR or Queue, not a specific user
        route_context = did_info.get("route_to_context")
        route_extension = did_info.get("route_to_extension", "s")
        route_priority = did_info.get("route_to_priority", "1")
        if route_context:
            agi.log(f"DID {called_did_number} is a system route. Forwarding to context {route_context}, exten {route_extension}, prio {route_priority}")
            # To forward to another context/extension, you typically set variables and let dialplan handle it,
            # or use AGI commands like 'EXEC Dial Local/...' or 'SET CONTEXT/EXTENSION/PRIORITY'
            # For simplicity, we'll set FORWARD_TO_USER to a Local channel target.
            # This requires a [dial-local-channel] context in extensions.conf
            # agi.set_variable("FORWARD_TO_USER", f"Local/{route_extension}@{route_context}")
            # agi.set_variable("FORWARD_ALLOWED", "YES")

            # A more direct way if the dialplan is simple:
            # This example will try to Dial Local/s@ivr-main
            # Ensure you have a context that can handle Local channels like this.
            # Example: [dial-local-channel]
            #           exten => _X.,1,Goto(${EXTEN}@${CONTEXT_TO_GOTO})
            # agi.set_variable("FORWARD_TO_USER", f"Local/{route_extension}@{route_context}")

            # For now, let's assume the dialplan handles this with a specific forward variable
            # if the AGI doesn't find a user. This script will focus on user forwarding.
            # Or, if the AGI is expected to fully qualify the dial string:
            # agi.set_variable("FORWARD_TO_USER", f"Goto({route_context},{route_extension},{route_priority})") # This won't work directly with Dial()
            # A common pattern is that AGI sets variables, and the dialplan uses GotoIfs

            # Based on the current extensions.conf, we need to provide a dialable string for FORWARD_TO_USER
            # Let's assume a specific SIP peer for IVR for this example.
            agi.set_variable("FORWARD_TO_USER", "SIP/ivr_system_peer") # Example: Dial SIP/ivr_system_peer
            agi.set_variable("FORWARD_ALLOWED", "YES")

        else:
            agi.log(f"DID {called_did_number} is system_route but no route_to_context defined.", level="ERROR")
            agi.set_variable("FORWARD_ALLOWED", "NO")
        sys.exit(0)


    if did_info.get("status") != "assigned" or not did_info.get("user_id"):
        agi.log(f"DID {called_did_number} is not in 'assigned' status or no user_id found.", level="WARNING")
        agi.set_variable("FORWARD_ALLOWED", "NO")
        sys.exit(0)

    user_id = did_info["user_id"]
    assigned_user_extension = did_info.get("assigned_user_extension") # This is the internal SIP extension/username

    if not assigned_user_extension:
        agi.log(f"No assigned user extension for User ID {user_id} linked to DID {called_did_number}.", level="ERROR")
        agi.set_variable("FORWARD_ALLOWED", "NO")
        sys.exit(0)

    user = get_user_details(user_id)
    if not user or not user.get("is_active"):
        agi.log(f"User ID {user_id} (ext: {assigned_user_extension}) is inactive or not found.", level="WARNING")
        agi.set_variable("FORWARD_ALLOWED", "NO")
        sys.exit(0)

    if user.get("dnd_status"):
        agi.log(f"User ID {user_id} (ext: {assigned_user_extension}) has DND enabled.", level="INFO")
        agi.set_variable("FORWARD_ALLOWED", "NO") # Or route to voicemail directly
        # agi.exec("VoiceMail", f"{assigned_user_extension}@default,u") # Example: unavailable message
        sys.exit(0)

    # At this point, user is found, active, not DND, and has an assigned extension.
    # The FORWARD_TO_USER variable should be something Dial() can use, e.g., "SIP/1001"
    forward_dial_string = f"SIP/{assigned_user_extension}"

    agi.set_variable("FORWARD_ALLOWED", "YES")
    agi.set_variable("FORWARD_TO_USER", forward_dial_string)

    agi.log(f"Incoming call to DID {called_did_number} will be forwarded to {forward_dial_string} for User ID {user_id}.")
    sys.exit(0)

if __name__ == "__main__":
    main()
