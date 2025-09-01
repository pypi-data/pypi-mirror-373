from ..client.game_client import GameClient
from loguru import logger









class Tax(GameClient):
    
    
    
    
    async def get_tax_infos(
        self,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("txi", {})
            if sync:
                response = await self.wait_for_response("txi")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def start_tax(
        self,
        tax_type: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "txs",
                {
                    "TT": tax_type,
                    "TX": 3
                }
            )
            if sync:
                response = await self.wait_for_response("txs")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        

    async def collect_tax(
        self,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("txc", {"TR": 29})
            if sync:
                response = await self.wait_for_response("txc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
