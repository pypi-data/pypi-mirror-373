from ..client.game_client import GameClient
from loguru import logger




class Shop(GameClient):
    
    
    
    async def buy_package_generic(
        self,
        kingdom: int,
        shop_type: int,
        shop_id: int,
        package_id: int,
        amount: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "sbp",
                {
                    "PID": package_id,
                    "BT": shop_type,
                    "TID": shop_id,
                    "AMT": amount,
                    "KID": kingdom,
                    "AID": -1,
                    "PC2": -1,
                    "BA": 0,
                    "PWR": 0,
                    "_PO": -1
                }
            )
            if sync:
                response = await self.wait_for_response("sbp")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
    
    
    async def buy_from_master_blacksmith(
        self,
        kingdom: int,
        package_id: int,
        amount: int,
        sync: bool = True
    ) -> dict | bool:
        
        return await self.buy_package_generic(kingdom, 0, 116, package_id, amount, sync)
    


    async def buy_from_armorer(
        self,
        kingdom: int,
        package_id: int,
        amount: int,
        sync: bool = True
    ) -> dict | bool:
        
        return await self.buy_package_generic(kingdom, 0, 27, package_id, amount, sync)
    
    
    async def buy_from_nomad_shop(
        self,
        kingdom: int,
        package_id: int,
        amount: int,
        sync: bool = True
    ) -> dict | bool:
        
        return await self.buy_package_generic(kingdom, 0, 94, package_id, amount, sync)
    
    
    
    async def buy_from_blade_coast(
        self,
        kingdom: int,
        package_id: int,
        amount: int,
        sync: bool = True
    ) -> dict | bool:
        
        return await self.buy_package_generic(kingdom, 0, 4, package_id, amount, sync)
    
    
    
    async def set_buying_castle(
        self,
        castle_id: int,
        kingdom: int = 0,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "gbc",
                {
                    "CID": castle_id,
                    "KID": kingdom
                }
            )
            if sync:
                response = await self.wait_for_response("gbc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False