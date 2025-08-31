import asyncio
import time
import random
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Dict, Callable

class GGSCache:
    def __init__(
        self,
        on_expire: Callable[[Any, Any], Optional[asyncio.Future]],
        default_ttl: float = 5.0
        ):
 
        # Memcache logic
        self._data: Dict[Any, Any] = {}
        self._default_ttl = default_ttl
        
        
        
        # Scheduler logic
        self._on_expire = on_expire
        self._tasks: Dict[Any, asyncio.Task] = {}
        self._expiry_times: Dict[Any, float] = {}
        self._locks: Dict[Any, asyncio.Lock] = {}
        
        
        
        

    # ===== Memcache core =====
    def set(self, key: Any, value: Any) -> None:
        self._data[key] = value


    def get(self, key: Any, default: Any = None) -> Any:
        return self._data.get(key, default)

    def delete(self, key: Any) -> None:
        self._data.pop(key, None)

    def set_with_ttl(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        self._data[key] = value
        delay = ttl if ttl is not None else self._default_ttl
        # schedule removal
        asyncio.create_task(self._expire_later(key, delay))


    async def _expire_later(self, key: Any, delay: float) -> None:
        await asyncio.sleep(delay)
        payload = self._data.pop(key, None)
        if payload is not None:
            try:
                result = self._on_expire(key, payload)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                print(f"Error in on_expire for key={key}: {e}")





    # ===== Scheduling API =====
    async def set_in_timeline(
        self,
        key: Any,
        payload: Any,
        *,
        delay: Optional[float] = None,
        run_at: Optional[datetime] = None,
        jitter: float = 0.0
    ) -> None:

        # Compute delay
        if run_at is not None:
            if run_at.tzinfo is None:
                run_at = run_at.replace(tzinfo=timezone.utc)
            delay = max(0.0, run_at.timestamp() - time.time())
        if delay is None:
            raise ValueError("Must specify either delay or run_at")
        delay += random.uniform(0, jitter)

        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            # Cancel existing
            old = self._tasks.get(key)
            if old and not old.done():
                old.cancel()
                self._expiry_times.pop(key, None)

            # Record expiry
            expire_ts = time.time() + delay
            self._expiry_times[key] = expire_ts

            async def _runner():
                try:
                    await asyncio.sleep(delay)
                    try:
                        result = self._on_expire(key, payload)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        print(f"Error in on_expire for key={key}: {e}")
                except asyncio.CancelledError:
                    return
                finally:
                    self._expiry_times.pop(key, None)
                    self._tasks.pop(key, None)

            task = asyncio.create_task(_runner())
            self._tasks[key] = task

    def get_last_key(self) -> Optional[Any]:
        
        if not self._expiry_times:
            return None
        return max(self._expiry_times, key=lambda k: self._expiry_times[k])

    def get_last_scheduled_time(self) -> Optional[datetime]:
 
        last = self.get_last_key()
        if last is None:
            return None
        return datetime.fromtimestamp(self._expiry_times[last], tz=timezone.utc)

    async def schedule_after_last(
        self,
        key: Any,
        payload: Any,
        interval: float,
        *,
        jitter: float = 0.0
    ) -> None:
 
 
        last_time = self.get_last_scheduled_time()
        if last_time:
            run_at = last_time + timedelta(seconds=interval)
        else:
            run_at = datetime.now(timezone.utc) + timedelta(seconds=interval)
        await self.set_in_timeline(key, payload, run_at=run_at, jitter=jitter)



    async def clear_cache(self) -> None:

        # Cancel all tasks
        tasks = list(self._tasks.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._data.clear()
        self._tasks.clear()
        self._expiry_times.clear()
        self._locks.clear()
