import asyncio

import pytest

from egse.async_control import AsyncControlClient
from egse.async_control import AsyncControlServer
from egse.async_control import is_control_server_active

pytestmark = pytest.mark.skip("Implementation and tests are still a WIP")


@pytest.mark.asyncio
async def test_control_server(caplog):
    # First start the control server as a background task.
    server = AsyncControlServer()
    server_task = asyncio.create_task(server.serve())

    await asyncio.sleep(0.5)  # give the server time to startup

    # Now create a control client that will connect to the above server.
    with await AsyncControlClient.create(service_type="async-control-server") as client:
        caplog.clear()

        # Sleep some time, so we can see the control server in action, e.g. status reports, housekeeping, etc
        await asyncio.sleep(5.0)

        assert "Sending status updates" in caplog.text  # this should there be 5 times actually

        response = await client.ping()
        print(f"{response = }")
        assert isinstance(response, str)
        assert response == "pong"

        response = await client.info()
        print(f"{response = }")
        assert isinstance(response, dict)
        assert "name" in response
        assert "hostname" in response
        assert "device commanding port" in response
        assert "service commanding port" in response

        assert await is_control_server_active(service_type="async-control-server")

        response = await client.terminate()
        print(f"{response = }")
        assert isinstance(response, dict)
        assert response["status"] == "terminating"

    await server_task
