from ..client.game_client import GameClient
from loguru import logger







class Misc(GameClient):
    

    


    async def change_emblem(
        self,
        bg_type: int,
        bg_color_1: int,
        bg_color_2: int,
        icons_type: int,
        icon_id_1: int,
        icon_color_1: int,
        icon_id_2: int,
        icon_color_2: int,
        sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message(
                "cem",
                {
                    "CAE": {
                        "BGT": bg_type,
                        "BGC1": bg_color_1,
                        "BGC2": bg_color_2,
                        "SPT": icons_type,
                        "S1": icon_id_1,
                        "SC1": icon_color_1,
                        "S2": icon_id_2,
                        "SC2": icon_color_2,
                    }
                },
            )
            if sync:
                response = await self.wait_for_response("cem")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False  