from loguru import logger
from ..client.game_client import GameClient







class Gifts(GameClient):


    async def collect_citizen_gift(self, sync: bool = True) -> dict | bool:

        try:
            await self.send_json_message("irc", {})
            if sync:
                response = await self.wait_for_response("irc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        


    async def collect_citizen_quest(self, choice: int, sync: bool = True) -> dict | bool:

        try:
            await self.send_json_message("jjc", {"CO": choice})
            if sync:
                response = await self.wait_for_response("jjc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        


    async def collect_ressource_gift(self, resource_type: int, sync: bool = True) -> dict | bool:

        try:
            await self.send_json_message("rcc", {"RT": resource_type})
            if sync:
                response = await self.wait_for_response("rcc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False