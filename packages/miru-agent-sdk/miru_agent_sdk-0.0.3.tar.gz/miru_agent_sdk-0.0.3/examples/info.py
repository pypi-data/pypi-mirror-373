from miru_agent_sdk import Miru

client = Miru()

health = client.agent.health()
print(health.to_json())
