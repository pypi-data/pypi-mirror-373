# Agent

Types:

```python
from miru_agent_sdk.types import AgentHealthResponse, AgentVersionResponse
```

Methods:

- <code title="get /health">client.agent.<a href="./src/miru_agent_sdk/resources/agent.py">health</a>() -> <a href="./src/miru_agent_sdk/types/agent_health_response.py">AgentHealthResponse</a></code>
- <code title="get /version">client.agent.<a href="./src/miru_agent_sdk/resources/agent.py">version</a>() -> <a href="./src/miru_agent_sdk/types/agent_version_response.py">AgentVersionResponse</a></code>

# Device

Types:

```python
from miru_agent_sdk.types import DeviceRetrieveResponse, DeviceSyncResponse
```

Methods:

- <code title="get /device">client.device.<a href="./src/miru_agent_sdk/resources/device.py">retrieve</a>() -> <a href="./src/miru_agent_sdk/types/device_retrieve_response.py">DeviceRetrieveResponse</a></code>
- <code title="post /device/sync">client.device.<a href="./src/miru_agent_sdk/resources/device.py">sync</a>() -> <a href="./src/miru_agent_sdk/types/device_sync_response.py">DeviceSyncResponse</a></code>
