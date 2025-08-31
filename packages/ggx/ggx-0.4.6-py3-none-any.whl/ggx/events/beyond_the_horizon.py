from ..client.game_client import GameClient
from loguru import logger





class BeyondTheHorizon(GameClient):
    
    
    
    async def get_bth_points(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("tsh", {})
            if sync:
                response = await self.wait_for_response("tsh")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
        
    async def choose_bth_castle(
        self,
        castle_id: int,
        only_rubies: int = 0,
        use_rubies: int = 0,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "tsc",
                {
                    "ID": castle_id,
                    "OC2": only_rubies,
                    "PWR": use_rubies,
                    "GST": 3
                }
            )
            if sync:
                response = await self.wait_for_response("tsc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def get_bth_token(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message(
                "glt",
                {
                    "GST": 3
                }
            )
            if sync:
                response = await self.wait_for_response("glt")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def login_bth(
        self,
        token: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "tlep",
                {
                    "TLT": token
                }
            )
            if sync:
                response = await self.wait_for_response("lli")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False