import requests

server_id = "19802040"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6Ijk1NWRiNTg4NmMyYzgwOTkiLCJpYXQiOjE3Mzc5MjI5NjIsIm5iZiI6MTczNzkyMjk2MiwiaXNzIjoiaHR0cHM6Ly93d3cuYmF0dGxlbWV0cmljcy5jb20iLCJzdWIiOiJ1cm46dXNlcjo2NjUxNzkifQ.cKLLsRemkE6aRrC9novsvRyJ7OWA_EVA4XgREtcmtLE"
url = f"https://api.battlemetrics.com/servers/{server_id}"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get(url, headers=headers)
print(response.json())  # Se hele API-svaret
