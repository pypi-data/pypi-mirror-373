from ..client.game_client import GameClient
from loguru import logger






class Events(GameClient):
    
    
    async def get_events(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("sei", {})
            if sync:
                response = await self.wait_for_response("sei")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def get_event_points(
        self,
        event_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "pep",
                {
                    "EID": event_id
                }
            )
            if sync:
                response = await self.wait_for_response("pep")
                return response
            return True

        except Exception as e:
            logger.error(e)
            return False       
        
        
    async def get_ranking(
        self,
        ranking_type: int,
        category: int = -1,
        search_value: int = -1,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "hgh",
                {
                    "LT": ranking_type,
                    "LID": category,
                    "SV": search_value
                }
            )
            if sync:
                response = await self.wait_for_response("hgh")
                return response
            return True

        except Exception as e:
            logger.error(e)
            return False  
        
        
        
    async def choose_event_difficulty(
        self,
        event_id: int,
        difficulty_id: int,
        premium_unlock: int = 0,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "sede",
                {
                    "EID": event_id,
                    "EDID": difficulty_id,
                    "C2U": premium_unlock
                }
            )
            if sync:
                response = await self.wait_for_response("sede")
                return response
            return True

        except Exception as e:
            logger.error(e)
            return False 