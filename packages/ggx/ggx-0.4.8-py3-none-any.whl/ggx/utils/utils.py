from loguru import logger
import asyncio
import aiohttp






class Utils:
    
    API_IN_URL = "http://2captcha.com/in.php"
    API_RES_URL = "http://2captcha.com/res.php"
    
    
    
    
    def __init__(self):
        
        self.polling_interval = 5
        self.max_attempts = 20
        self.site_key = '6Lc7w34oAAAAAFKhfmln41m96VQm4MNqEdpCYm-k'
        self.site_url = 'https://empire.goodgamestudios.com/'
    
    

    
    
    
    async def get_recaptcha_token(self, api_key: str) -> str:
        
        payload = {
            'key': api_key,
            'method': 'userrecaptcha',
            'googlekey': self.site_key,
            'pageurl': self.site_url,
            'json': 1
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.API_IN_URL, data=payload) as resp:
                data = await resp.json()
                if data.get('status') != 1:
                    logger.error(f"2Captcha submission error: {data}")
                    raise RuntimeError(f"Submit failed: {data.get('request')}")

                request_id = data.get('request')
                logger.info(f"Submitted CAPTCHA, request ID: {request_id}")

            for attempt in range(self.max_attempts):
                await asyncio.sleep(self.polling_interval)
                params = {
                    'key': api_key,
                    'action': 'get',
                    'id': request_id,
                    'json': 1
                }
                async with session.get(self.API_RES_URL, params=params) as res:
                    result = await res.json()
                    if result.get('status') == 1:
                        token = result.get('request')
                        logger.info("Retrieved token from 2Captcha")
                        return token
                    elif result.get('request') == 'CAPCHA_NOT_READY':
                        logger.debug(f"Attempt {attempt+1}/{self.max_attempts}: CAPTCHA not ready")
                        continue
                    else:
                        logger.error(f"2Captcha retrieval error: {result}")
                        raise RuntimeError(f"Get failed: {result.get('request')}")

        raise TimeoutError("2Captcha solving timed out")
    
    
    
    def skip_calculator(
        
        self,
        time: int,
        skip_type: list[str] = None
        
        ) -> list[str]:
        
        
        all_skip_values = [(86400, "MS7"), (18000, "MS6"), (3600, "MS5"), (1800, "MS4"), (600, "MS3"), (300, "MS2"), (60, "MS1")]
        
        if skip_type:
            skip_values = [(sec, lbl) for sec, lbl in all_skip_values if lbl in skip_type]
            if not skip_values:
                logger.error("Your skips are not allowed!")
                
        else:
            skip_values = all_skip_values
            
        minutes = time // 60
        skip_minutes = [(sec // 60, label) for sec, label in all_skip_values]
        INF = float('inf')
        dp = [INF] * (minutes + 1)
        prev = [None] * (minutes + 1)
        dp[0] = 0
        
        for i in range(1, minutes + 1):
            for m, label in skip_minutes:
                if i >= m and dp[i - m] + 1 < dp[i]:
                    dp[i] = dp[i - m] + 1
                    prev[i] = (i - m, label)
        skips = []
        cur = minutes
        while cur > 0 and prev[cur]:
            j, label = prev[cur]
            skips.append(label)
            cur = j
        used = sum(sec * skips.count(lbl) for sec, lbl in all_skip_values)
        rem = time - used
        if rem > 0:
            for sec, label in sorted(all_skip_values, key=lambda x: x[0]):
                if sec >= rem:
                    skips.append(label)
                    break
        
        return skips