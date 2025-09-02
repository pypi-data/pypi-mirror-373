import asyncio
import logging
from datetime import datetime, timezone
from uuid import uuid4

from threedi_api_client.api import ThreediApi
from threedi_api_client.versions import V3BetaApi

from threedi_cmd.commands.settings import WebSocketSettings
from threedi_cmd.parser import ScenarioParser

logging.basicConfig(level=logging.INFO)


async def main():
    organisation = "61f5a464c35044c19bc7d4b42d7f58cb"
    simulation_name = "run_" + uuid4().hex

    file_path = "scenarios/api_constant_rain.yaml"
    # file_path = 'scenarios/start_pause.yaml'

    client: V3BetaApi = ThreediApi(env_file="staging.env", version="v3-beta")

    context = {
        "organisation_uuid": organisation,
        "simulation_name": simulation_name,
        "datetime_now": datetime.now(timezone.utc).isoformat(),
    }

    websocket_settings = WebSocketSettings(
        api_base_url=client.api_client.configuration.host + "/v3-beta",
        token=client.api_client.configuration.get_api_key_with_prefix("Authorization"),
    )

    parser = ScenarioParser("threedi_cmd/" + file_path)
    scenario = parser.parse(client, websocket_settings, "threedi_cmd/", context=context)

    # Save simulation before using it in the websocket
    scenario.simulation.save()

    await scenario.execute()


if __name__ == "__main__":
    asyncio.run(main())
