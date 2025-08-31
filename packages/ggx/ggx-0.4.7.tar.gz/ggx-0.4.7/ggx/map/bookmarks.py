from ..client.game_client import GameClient
from loguru import logger














class Bookmarks(GameClient):
    
    
    async def get_bookmarks(self, sync: bool = True) -> dict:
        
        try:
            
            await self.send_json_message("gbl", {})
            if sync:
                response = await self.wait_for_response("gbl")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False