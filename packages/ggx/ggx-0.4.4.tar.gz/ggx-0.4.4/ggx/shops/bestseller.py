from ..client.game_client import GameClient
from loguru import logger






class BestSeller(GameClient):
    
    
    
    async def buy_from_bestseller(
        self,
        bestseller_id: int,
        package_type: int,
        amount: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "bso",
                {
                    "OID": package_type,
                    "AMT": amount,
                    "POID": bestseller_id
                }
            )
            if sync:
                response = await self.wait_for_response("bso")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False