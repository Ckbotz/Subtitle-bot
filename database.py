#!/usr/bin/env python3
"""
Database handler for Subtitle Embedder Bot
"""

import motor.motor_asyncio
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id):
        return dict(
            _id=int(id),                                   
            thumbnail=None,
            caption=None,
            ban_status=dict(
                is_banned=False,
                ban_reason=''
            )
        )

    async def add_user(self, user_id):
        """Add a new user to database"""
        try:
            if not await self.is_user_exist(user_id):
                user = self.new_user(user_id)
                await self.col.insert_one(user)
                logger.info(f"New user added: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False

    async def is_user_exist(self, id):
        """Check if user exists in database"""
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        """Get total number of users"""
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        """Get all users"""
        all_users = self.col.find({})
        return all_users
        
    async def remove_ban(self, id):
        """Remove ban from user"""
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'_id': int(id)}, {'$set': {'ban_status': ban_status}})
        logger.info(f"User {id} unbanned")
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        """Ban a user"""
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'ban_status': ban_status}})
        logger.info(f"User {user_id} banned: {ban_reason}")

    async def get_ban_status(self, id):
        """Get ban status of user"""
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'_id': int(id)})        
        if not user:
            return default
        return user.get('ban_status', default)
        
    async def delete_user(self, user_id):
        """Delete a user from database"""
        await self.col.delete_many({'_id': int(user_id)})
        logger.info(f"User {user_id} deleted")
    
    async def set_thumbnail(self, id, file_id):
        """Set thumbnail for user"""
        await self.col.update_one({'_id': int(id)}, {'$set': {'thumbnail': file_id}})
        logger.info(f"Thumbnail set for user {id}")

    async def get_thumbnail(self, id):
        """Get thumbnail for user"""
        user = await self.col.find_one({'_id': int(id)})
        if not user:
            return None
        return user.get('thumbnail', None)

    async def set_caption(self, id, caption):
        """Set caption for user"""
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})
        logger.info(f"Caption set for user {id}")

    async def get_caption(self, id):
        """Get caption for user"""
        user = await self.col.find_one({'_id': int(id)})
        if not user:
            return None
        return user.get('caption', None)
    
    async def get_user(self, id):
        """Get complete user data"""
        user = await self.col.find_one({'_id': int(id)})
        return user


# Initialize database instance
db = Database(Config.DB_URL, Config.DB_NAME)
