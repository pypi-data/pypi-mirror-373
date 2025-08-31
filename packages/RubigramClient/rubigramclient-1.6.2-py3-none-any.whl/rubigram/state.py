from aiosqlite import connect as conn, Connection
from typing import Optional


class ManageDB:
    def __init__(self, database: str):
        self.database = database
        self.connection: Optional[Connection] = None
    
    
    async def connect(self):
        if not self.connection:
            self.connection = await conn(self.database)
    
    
    async def disconnect(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
    
            
    async def create(self):
        await self.connect()
        await self.connection.execute("""CREATE TABLE IF NOT EXISTS states (user_id TEXT PRIMARY KEY, state TEXT)""")
        await self.connection.execute("CREATE TABLE IF NOT EXISTS user_data (user_id TEXT, var TEXT, res TEXT, PRIMARY KEY (user_id, var))")
        await self.connection.commit()
    
    
    async def set_state(self, user_id: str, state: str) -> None:
        await self.connect()
        await self.connection.execute("INSERT INTO states (user_id, state) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET state=excluded.state ", (user_id, str(state)))
        await self.connection.commit()
        
        
    async def get_state(self, user_id: str) -> Optional[str]:
        await self.connect()
        async with self.connection.execute("SELECT state FROM states WHERE user_id = ?", (user_id,)) as cursor:
            data = await cursor.fetchone()
            return data[0] if data else None
        

    async def remove_state(self, user_id: str):
        await self.connect()
        await self.connection.execute("DELETE FROM states WHERE user_id = ?", (user_id,))
        await self.connection.commit()
        
    
    async def set_data(self, user_id: str, key: str, value: str):
        await self.connect()
        await self.connection.execute("INSERT OR REPLACE INTO user_data (user_id, var, res) VALUES (?, ?, ?)", (user_id, key, str(value)))
        await self.connection.commit()
        
    
    async def get_data(self, user_id: str, key: str = None):
        await self.connect()
        if key:
            async with self.connection.execute("SELECT res FROM user_data WHERE user_id = ? AND var = ?", (user_id, key)) as cursor:
                data = await cursor.fetchone()
                return data[0] if data else None
        else:
            async with self.connection.execute("SELECT var, res FROM user_data WHERE user_id = ?", (user_id,)) as cursor:
                data = await cursor.fetchall()
            return {k: v for k, v in data} if data else {}

            
    async def remove_data(self, user_id: str, key: str = None):
        await self.connect()
        if key:
            await self.connection.execute("DELETE FROM user_data WHERE user_id = ? AND var = ?", (user_id, key))
        else:
            await self.connection.execute("DELETE FROM user_data WHERE user_id = ?", (user_id,))
        await self.connection.commit()
              
        
class StateManager:
    def __init__(self):
        self.db = ManageDB("rubigram.db")
    
    async def start(self):
        await self.db.create()

    async def stop(self):
        await self.db.disconnect()
        
    async def set_state(self, user_id: str, state: str):
        await self.db.set_state(user_id, state)
    
    async def get_state(self, user_id: str):
        return await self.db.get_state(user_id)
    
    async def remove_state(self, user_id: str):
        await self.db.remove_state(user_id)
        
    async def set_data(self, user_id: str, **data):
        data = list(data.items())
        if not data:
            return
        key, value = data[0]
        await self.db.set_data(user_id, key, value)
    
    async def get_data(self, user_id: str, key: str = None):
        return await self.db.get_data(user_id, key)

    async def remove_data(self, user_id: str, key: str = None):
        await self.db.remove_data(user_id, key)