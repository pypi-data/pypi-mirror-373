from ..client.game_client import GameClient
from loguru import logger




class ImperialPatronage(GameClient):
    
    
    
    async def open_imperial_patronage(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("gdti", {})
            if sync:
                response = await self.wait_for_response("gdti")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
      
      
      
      
      
      
        
        
    async def give_imperial_patronage(
        self,
        devise_id: int,
        amount: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "ddi",
                {
                    "DIV": [{
                        "DII": devise_id, "DIA": amount
                    }]
                }
            )
            if sync:
                response = await self.wait_for_response("ddi")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False