from ..client.game_client import GameClient
from loguru import logger





class Defense(GameClient):
    
    
    
    async def get_castle_defense(
        self, 
        x: int, 
        y: int, 
        castle_id: int, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "dfc", {"CX": x, "CY": y, "AID": castle_id, "KID": -1, "SSV": 0}
            )
            if sync:
                response = await self.wait_for_response("dfc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            
            
    async def change_keep_defnse(
        self,
        x: int,
        y: int,
        castle_id: int,
        min_units_to_consume_tools: int,
        melee_percentage: int,
        tools: list[list[int]],
        support_tools: list[list[int]],
        sync: bool = True
        
            
    ) -> dict | bool:
        
        try:
            
            await self.send_json_message(
                "dfk",
                {
                    "CX": x,
                    "CY": y,
                    "AID": castle_id,
                    "MAUCT": min_units_to_consume_tools,
                    "UC": melee_percentage,
                    "S": tools,
                    "STS": support_tools,
                }
            )
            if sync:
                response = await self.wait_for_response("dfk")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            
            
    async def change_wall_defense(
        self,
        x: int,
        y: int,
        castle_id: int,
        left_tools: list[list[int]],
        left_unit_percentage: int,
        left_melee_percentage: int,
        middle_tools: list[list[int]],
        middle_unit_percentage: int,
        middle_melee_percentage: int,
        right_tools: list[list[int]],
        right_unit_percentage: int,
        right_melee_percentage: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            
            await self.send_json_message(
                "dfw",
                {
                    "CX": x,
                    "CY": y,
                    "AID": castle_id,
                    "L": {
                        "S": left_tools,
                        "UP": left_unit_percentage,
                        "UC": left_melee_percentage
                    },
                    "M": {
                        "S": middle_tools,
                        "UP": middle_unit_percentage,
                        "UC": middle_melee_percentage
                    },
                    "R": {
                        "S": right_tools,
                        "UP": right_unit_percentage,
                        "UC": right_melee_percentage,
                    }
                }
            )
            if sync:
                response = await self.wait_for_response("dfw")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            
            
            
    async def change_moat_defense(
        self,
        x: int,
        y: int,
        castle_id: int,
        left_tools: list[list[int]],
        middle_tools: list[list[int]],
        right_tools: list[list[int]],
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "dfm",
                {
                    "CX": x,
                    "CY": y,
                    "AID": castle_id,
                    "LS": left_tools,
                    "MS": middle_tools,
                    "RS": right_tools
                }
            )
            if sync:
                response = await self.wait_for_response("dfm")
                return response
            return True
        
        except Exception as e:
            logger.error(e)