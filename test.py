import socket
import json

def vndb_api_request(command):
    # VNDB API connection details
    host = 'api.vndb.org'
    port = 19534  # Standard VNDB API port

    # Connect to the VNDB API using TCP
    with socket.create_connection((host, port)) as s:
        # Log in (replace 'username' and 'password' with your VNDB credentials)
        login_command = 'login {"protocol":1,"client":"testclient","clientver":0.1,"username":"shinku4lyfe","password":"Prhj3Wx$Ji_NHz6"}\x04'
        s.sendall(login_command.encode('utf-8'))

        # Check for a successful login
        response = s.recv(1024).decode('utf-8')
        if 'ok' not in response:
            return "Login failed"

        # Send the request command
        s.sendall((command + '\x04').encode('utf-8'))

        response_parts = []
        while True:
            part = s.recv(1024).decode('utf-8')
            response_parts.append(part)
            if '\x04' in part:
                break

        return ''.join(response_parts).replace('\x04', '')

def vndb_api_request_paginated(base_command):
    all_items = []
    page = 1
    more_results = True

    while more_results:
        print(page)
        # Modify the command to include the page number
        command = f"{base_command} {{\"page\": {page}, \"result\": 20}}"
        response = vndb_api_request(command)  # Function that sends command to the API
        print(response)

        # Remove the 'results ' prefix and parse the JSON
        response = response[len('results '):]
        parsed_response = json.loads(response)

        # Add the items from this page to the all_items list
        all_items.extend(parsed_response.get("items", []))

        # Check if there are more results
        more_results = parsed_response.get("more", False)
        page += 1

    return all_items

# command = "get staff basic (id = [14, 855, 272, 752, 2231, 269, 104, 1488, 8, 654, 63, 125, 485, 807, 4264, 1196, 365, 1990, 1013, 833, 1392, 199, 73, 113, 3296, 294, 590, 48, 88, 1819, 802, 2124, 59, 837, 267, 5570, 1821, 1764, 270, 81, 28, 470, 834, 754])"
# command = f"get vn staff (id = {ids})"
command = "get staff aliases,voiced (id = 874)"
response = vndb_api_request_paginated(command)

pretty_response = json.dumps(response, indent=4, ensure_ascii=False)
with open('test_result.json', 'w') as file:
    file.write(pretty_response)

