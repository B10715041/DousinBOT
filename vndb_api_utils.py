from collections import defaultdict
from dataclasses import dataclass
import aiohttp
import discord
import json
import re
import socket


@dataclass
class VoiceActor:
    name:   str = ""
    id:     int = -1
    aid:    int = -1
    main:   bool= True



with open('config.json', 'r') as file:
    config = json.load(file)


async def search_vndb(query):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api.vndb.org/kana/vn',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                "filters": ["search", "=", query],
                "fields": "id, titles.title, titles.main, aliases, developers.original, developers.name, released, length_minutes, rating, votecount, image.url, screenshots.thumbnail",
                "sort": "searchrank"
            })
        ) as response:
            with open('.search_vndb.json', 'w') as file:
                file.write(await response.text())

            if response.status == 200:
                return await response.json()
            else:
                return f"Error: Received status code {response.status}"

def search_staff(id,search_alias=False):
    if search_alias:
        return vndb_api_request_paginated(f"get staff aliases (id = {id})")
    return vndb_api_request_paginated(f"get staff basic (id = {id})")



def format_vndb_response_as_embed(data):
    # Create an embed object from the response
    embed = discord.Embed(title="VNDB Search Result", color=0x1E90FF)
    embed2 = discord.Embed(title="Staff Information", color=0x1E90FF)

    # Filter out entries with None rating and sort the remaining by rating
    # valid_entries = [vn for vn in data['results'] if vn.get('rating') is not None]
    valid_entries = [vn for vn in data['results']]

    # Assuming data is the JSON response from VNDB API
    if valid_entries:
        # Sort the results by rating in descending order and take the highest-rated entry
        # vn_highest_rated = max(valid_entries, key=lambda vn: vn.get('rating', 0))
        vn_highest_rated = valid_entries[0]

        title = None
        titles = vn_highest_rated['titles']
        for t in titles:
            if t['main']:
                title = t['title']
                break
        embed.title = title

        embed.description = ", ".join(vn_highest_rated['aliases'])

        # embed.add_field(name="\u200b", value="\u200b", inline=False)

        dev = vn_highest_rated['developers'][0]
        embed.add_field(name="Developer", value=f"[{dev['name']}](https://vndb.org/{dev['id']})", inline=True)
        embed.add_field(name="Release Date", value=vn_highest_rated['released'], inline=True)

        length_minutes = vn_highest_rated['length_minutes']
        length_formatted = f"{length_minutes // 60}h {length_minutes % 60}m" if length_minutes else "N/A"  # Convert minutes to hours and minutes
        embed.add_field(name="Length", value=str(length_formatted), inline=True)

        embed.add_field(name="Rating", value=str(vn_highest_rated['rating']), inline=True)
        embed.add_field(name="Vote Count", value=str(vn_highest_rated['votecount']), inline=True)

        # embed.add_field(name="\u200b", value="\u200b", inline=False)

        vn_id = ''.join(re.findall(r'\d+', vn_highest_rated['id']))
        embed.url = f"https://vndb.org/v{vn_id}"
        character_data = vndb_api_request_paginated(f"get character basic,vns,voiced (vn = {vn_id})")

        va_set = dict()
        for chara in character_data:
            va = chara.get('voiced')
            if va == [] or any(instance.id == va[0]['id'] for instance in va_set.values()):
                continue
            for vn in chara.get('vns'):
                if str(vn[0]) != vn_id:
                    continue
                voiceactor = VoiceActor(id=va[0]['id'], aid=va[0]['aid'])
                if vn[3] not in ['main', 'primary']:
                    voiceactor.main = False 
                va_set[voiceactor.id] = voiceactor
                break

        aid_response = search_staff([va.id for va in va_set.values()], search_alias=True)
        for cur_va in aid_response:
            va = va_set[cur_va['id']]
            for aliase in cur_va['aliases']:
                if va.aid == aliase[0]:
                    va.name = aliase[2]
                    break
        
        va_mainlist = []
        va_sublist = []
        for va in va_set.values():
            if va.main:
                va_mainlist.append(f"[{va.name}](https://vndb.org/s{va.id})")
            else:
                va_sublist.append(f"[{va.name}](https://vndb.org/s{va.id})")

        embed.add_field(name="Main Character Voice Actor", value='|'.join(va_mainlist), inline=False)

        if len(va_sublist):
            if len(''.join(va_sublist)) < 980:
                embed.add_field(name="Side Character Voice Actor", value='|'.join(va_sublist), inline=False)
            else:
                half_index = len(va_sublist) // 2
                va_first = va_sublist[:half_index]
                va_second = va_sublist[half_index:]
                embed.add_field(name="Side Character Voice Actor", value='|'.join(va_first), inline=False)
                embed.add_field(name="\u200b", value='|'.join(va_second))

        if 'url' in vn_highest_rated['image']:
            embed.set_thumbnail(url=vn_highest_rated['image']['url'])

        staff_data = vndb_api_request_paginated(f"get vn staff (id = {vn_id})")[0]
        staff_by_role = defaultdict(list)
        jp_role = ['scenario', 'art', 'director', 'songs', 'music']
        for staff in staff_data['staff']:
            if not staff.get('original') and staff.get('role') not in jp_role:
                continue
            name = staff.get('original') or staff.get('name', 'N/A')
            role = staff.get('role', 'N/A')
            staff_by_role[role].append(f"[{name}](https://vndb.org/s{staff.get('sid')})")

        # Sort roles and add to embed as inline fields
        for role, names in sorted(staff_by_role.items()):
            length = len(role.capitalize())
            name_str = str()
            for name in names:
                length += len(name) + 1
                if length > 1000:
                    break
                name_str = name_str + name + '~'
            embed2.add_field(name=role.capitalize(), value=name_str.strip().replace('~', '\n'), inline=True)

        if vn_highest_rated['screenshots']:
            embed2.set_thumbnail(url=vn_highest_rated['screenshots'][0]['thumbnail'].replace('/st/', '/sf/'))
    else:
        embed.description = "No results found."

    return embed, embed2


def vndb_api_request(command):
    # VNDB API connection details
    host = 'api.vndb.org'
    port = 19534  # Standard VNDB API port

    # Connect to the VNDB API using TCP
    with socket.create_connection((host, port)) as s:
        login_command = f'login {{"protocol":1,"client":"testclient","clientver":0.1,"username":"{config["id"]}","password":"{config["pw"]}"}}\x04'
        s.sendall(login_command.encode('utf-8'))

        # Check for a successful login
        response = s.recv(1024).decode('utf-8')
        if 'ok' not in response:
            print(response)
            return "Login failed"

        # Send the request command
        s.sendall((command + '\x04').encode('utf-8'))

        response_bytes = bytearray()
        while True:
            part = s.recv(1024)
            response_bytes += part
            if part.endswith(b'\x04'):
                break
        try:
            return response_bytes[:-1].decode('utf-8')
        except UnicodeDecodeError as e:
            return f"Decodeing Error: {e}"


def vndb_api_request_paginated(base_command):
    all_items = []
    page = 1
    more_results = True

    while more_results:
        # Modify the command to include the page number
        command = f"{base_command} {{\"page\": {page}}}"
        response = vndb_api_request(command)  # Function that sends command to the API

        print(command)
        print(response, '\n')

        # Remove the 'results ' prefix and parse the JSON
        response = response[len('results '):]
        try:
            parsed_response = json.loads(response)
            # Add the items from this page to the all_items list
            all_items.extend(parsed_response.get("items", []))

            # Check if there are more results
            more_results = parsed_response.get("more", False)
            page += 1
        except Exception as e:
            print(e)
            print(response)
            break

    return all_items

