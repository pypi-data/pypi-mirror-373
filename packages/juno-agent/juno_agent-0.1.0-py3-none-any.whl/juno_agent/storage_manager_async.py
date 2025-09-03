"""Async conversation storage manager for juno-agent using TinyAgent's SQLite storage."""

from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid
import json
from datetime import datetime
import logging
import asyncio


class AsyncConversationStorageManager:
    """Async conversation storage manager using TinyAgent's SQLite storage."""
    
    def __init__(self):
        # Create storage directory
        self.storage_dir = Path.home() / ".askbudi"
        self.storage_dir.mkdir(exist_ok=True)
        
        # Database path
        self.db_path = self.storage_dir / "conversations.db"
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize TinyAgent's SQLite storage (lazy initialization)
        self.storage = None
        self.tinyagent_available = False
        
        # Generate user_id from current working directory (escaped)
        self.user_id = self._generate_user_id()

        # Start with a new session
        self.current_session_id = self.new_session()
        
        # CRITICAL: Validate user_id is still not None after new_session
        if self.user_id is None:
            raise ValueError("CRITICAL ERROR: user_id became None after new_session!")
        
        
        self.logger.info(f"Storage manager initialized - User ID: {self.user_id}, Session ID: {self.current_session_id}")
    
    def _initialize_storage(self):
        """Initialize TinyAgent storage on first use."""
        if self.storage is None:
            try:
                from tinyagent.storage.sqlite_storage import SqliteStorage
                self.storage = SqliteStorage(str(self.db_path))
                self.tinyagent_available = True
                self.logger.info(f"TinyAgent storage initialized at {self.db_path}")
            except ImportError as e:
                self.logger.error(f"TinyAgent not available: {e}")
                self.storage = None
                self.tinyagent_available = False
            except Exception as e:
                self.logger.error(f"Failed to initialize TinyAgent storage: {e}")
                self.storage = None
                self.tinyagent_available = False
    
    def _generate_user_id(self) -> str:
        """Generate user_id from current working directory path."""
        cwd_path = Path.cwd().resolve()
        # Create a consistent user_id that won't change between sessions
        user_id = str(cwd_path).replace("/", "_").replace("\\", "_").replace(":", "")
        return user_id
    
    def new_session(self) -> str:
        """Create a new chat session with a unique UUID."""
        # CRITICAL: Store user_id before creating new session to ensure it's preserved
        original_user_id = self.user_id
        
        self.current_session_id = str(uuid.uuid4())
        
        # CRITICAL: Ensure user_id was not modified
        if self.user_id != original_user_id:
            raise ValueError(f"CRITICAL ERROR: user_id changed during new_session! Was: {original_user_id}, Now: {self.user_id}")
        
        if self.user_id is None:
            raise ValueError("CRITICAL ERROR: user_id is None after new_session!")
        
        self.logger.info(f"New session created: {self.current_session_id}")
        return self.current_session_id
    
    def attach_to_agent(self, agent):
        """Attach storage to TinyAgent for auto-persistence."""
        self._initialize_storage()
        
        if self.storage and agent:
            try:
                self.storage.attach(agent)
                self.logger.info(f"Storage attached to agent: {type(agent).__name__}")
            except Exception as e:
                self.logger.error(f"Error attaching storage to agent: {e}")
        else:
            self.logger.warning("Cannot attach storage - storage or agent not available")
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions for the current user/project."""
        self._initialize_storage()
        
        if not self.storage:
            self.logger.warning("No storage available - cannot list sessions")
            return []
        
        try:
            import aiosqlite
            
            # Connect to database directly for querying
            async with aiosqlite.connect(str(self.db_path)) as conn:
                conn.row_factory = aiosqlite.Row
                
                # Check if table exists
                async with conn.execute("""
                    SELECT name FROM sqlite_master WHERE type='table' AND name='tny_agent_sessions'
                """) as cursor:
                    table_exists = await cursor.fetchone()
                    if not table_exists:
                        self.logger.info("Table 'tny_agent_sessions' does not exist")
                        return []
                
                # Get sessions using TinyAgent's schema
                async with conn.execute("""
                    SELECT agent_id, session_id, user_id, memories, metadata, session_data, created_at, updated_at 
                    FROM tny_agent_sessions 
                    WHERE user_id = ? 
                    ORDER BY updated_at DESC
                """, (self.user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    self.logger.info(f"Found {len(rows)} sessions for user_id '{self.user_id}'")
                
                sessions = []
                for row in rows:
                    row_dict = dict(row)
                    session_data = {
                        "session_id": row_dict["session_id"],
                        "created_at": row_dict.get("created_at"),
                        "updated_at": row_dict.get("updated_at")
                    }
                    
                    # Parse JSON data if available
                    try:
                        if row_dict.get("session_data"):
                            session_json = json.loads(row_dict["session_data"])
                            messages = session_json.get("messages", [])
                            session_data["message_count"] = len(messages)
                            
                            # Get first meaningful message as preview (skip system messages)
                            preview_found = False
                            for msg in messages:
                                if isinstance(msg, dict):
                                    role = msg.get("role", "")
                                    content = msg.get("content", "")
                                    
                                    # Skip system messages as they're often repetitive
                                    if role == "system":
                                        continue
                                    
                                    # Prefer user messages, but fall back to assistant if no user message found
                                    if role in ["user", "assistant"] and content:
                                        # For assistant messages, skip common initial responses
                                        if role == "assistant" and any(skip in content.lower() for skip in [
                                            "how can i help",
                                            "i'm here to help",
                                            "what would you like",
                                            "hello", 
                                            "hi there"
                                        ]):
                                            continue
                                        
                                        session_data["preview"] = (content[:50] + "...") if len(content) > 50 else content
                                        preview_found = True
                                        break
                            
                            # If no good preview found, try to use the first non-system message
                            if not preview_found:
                                for msg in messages:
                                    if isinstance(msg, dict) and msg.get("role") != "system":
                                        content = msg.get("content", "")
                                        if content:
                                            session_data["preview"] = (content[:50] + "...") if len(content) > 50 else content
                                            break
                        else:
                            session_data["message_count"] = 0
                            session_data["preview"] = "No messages"
                            
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Failed to parse JSON for session {row_dict['session_id']}: {e}")
                        session_data["message_count"] = 0
                        session_data["preview"] = "Parse error"
                    
                    sessions.append(session_data)
            
            self.logger.info(f"Returning {len(sessions)} sessions")
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error listing sessions: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a specific session's data."""
        self._initialize_storage()
        
        if not self.storage:
            self.logger.warning("No storage available - cannot load session")
            return None
        
        try:
            # First try using TinyAgent storage's load_session method
            if hasattr(self.storage, 'load_session'):
                data = await self.storage.load_session(session_id, self.user_id)
                if data:
                    self.current_session_id = session_id
                    self.logger.info(f"Loaded session via TinyAgent: {session_id}")
                    return data
            
            # Fallback: load directly from database
            return await self._load_session_direct(session_id)
            
        except Exception as e:
            self.logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    async def _load_session_direct(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data directly from the database."""
        try:
            import aiosqlite
            
            async with aiosqlite.connect(str(self.db_path)) as conn:
                conn.row_factory = aiosqlite.Row
                
                # Get session data from TinyAgent's schema
                async with conn.execute("""
                    SELECT agent_id, session_id, user_id, memories, metadata, session_data, model_meta, created_at, updated_at 
                    FROM tny_agent_sessions 
                    WHERE session_id = ? AND user_id = ?
                """, (session_id, self.user_id)) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row:
                        self.logger.warning(f"Session {session_id} not found for user {self.user_id}")
                        return None
                    
                    row_dict = dict(row)
                    
                    # Parse JSON fields
                    session_data = {}
                    try:
                        if row_dict.get("session_data"):
                            session_data = json.loads(row_dict["session_data"])
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Failed to parse session_data for {session_id}: {e}")
                        session_data = {}
                    
                    try:
                        if row_dict.get("metadata"):
                            metadata = json.loads(row_dict["metadata"])
                        else:
                            metadata = {}
                    except json.JSONDecodeError:
                        metadata = {}
                    
                    try:
                        if row_dict.get("memories"):
                            memories = json.loads(row_dict["memories"])
                        else:
                            memories = {}
                    except json.JSONDecodeError:
                        memories = {}
                    
                    # Construct the session data structure
                    loaded_data = {
                        "session_id": row_dict["session_id"],
                        "agent_id": row_dict["agent_id"],
                        "user_id": row_dict["user_id"],
                        "created_at": row_dict["created_at"],
                        "updated_at": row_dict["updated_at"],
                        "metadata": metadata,
                        "memories": memories,
                        "session_data": session_data,  # This contains the messages
                        "messages": session_data.get("messages", [])  # Direct access to messages
                    }
                    
                    self.current_session_id = session_id
                    self.logger.info(f"Loaded session directly from DB: {session_id}")
                    return loaded_data
                    
        except Exception as e:
            self.logger.error(f"Error loading session directly from DB: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a specific session."""
        try:
            import aiosqlite
            async with aiosqlite.connect(str(self.db_path)) as conn:
                await conn.execute(
                    "DELETE FROM tny_agent_sessions WHERE session_id = ? AND user_id = ?",
                    (session_id, self.user_id)
                )
                await conn.commit()
            
            self.logger.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    def get_session_summary(self, session_data: Dict[str, Any]) -> str:
        """Get a brief summary of a session for display."""
        # Handle string input (backward compatibility / error case)
        if isinstance(session_data, str):
            return f"Session {session_data[:8]}..."
        
        if not session_data or not isinstance(session_data, dict):
            return "Empty session"
        
        # Try to get preview from session data (preferred)
        if "preview" in session_data and session_data["preview"]:
            return session_data["preview"]
        
        # Try to get from session state messages
        session_state = session_data.get("session_state", {})
        messages = session_state.get("messages", [])
        
        if not messages:
            return "No messages"
        
        # Get first meaningful message as summary (skip system messages)
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            # Skip system messages as they're often repetitive
            if role == "system":
                continue
            
            # Prefer user messages, but use assistant if available
            if role in ["user", "assistant"] and content:
                # For assistant messages, skip common initial responses
                if role == "assistant" and any(skip in content.lower() for skip in [
                    "how can i help",
                    "i'm here to help", 
                    "what would you like",
                    "hello",
                    "hi there"
                ]):
                    continue
                
                return content[:100] + "..." if len(content) > 100 else content
        
        # Fallback to first non-system message
        for msg in messages:
            if msg.get("role") != "system":
                content = msg.get("content", "")
                if content:
                    return content[:100] + "..." if len(content) > 100 else content
        
        return "No user messages"
    
    def close(self):
        """Close storage connections synchronously."""
        if self.storage:
            try:
                import asyncio
                # Try to get current event loop
                try:
                    loop = asyncio.get_running_loop()
                    # If we have a running loop, create a task
                    asyncio.create_task(self._close_async())
                except RuntimeError:
                    # No running loop, create a new one
                    asyncio.run(self._close_async())
                self.logger.info("Storage close initiated")
            except Exception as e:
                self.logger.error(f"Error closing storage: {e}")
    
    async def _close_async(self):
        """Close storage connections asynchronously."""
        if self.storage:
            try:
                await self.storage.close()
                self.logger.info("Storage closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing storage: {e}")
    
    async def close_async(self):
        """Close storage connections asynchronously (public method)."""
        await self._close_async()
    
    def save_session_metadata(self, metadata: Dict[str, Any]):
        """Save additional metadata for the session (synchronous wrapper)."""
        try:
            import asyncio
            # Try to run the async version
            try:
                loop = asyncio.get_running_loop()
                # If we have a running loop, create a task
                asyncio.create_task(self._save_session_metadata_async(metadata))
            except RuntimeError:
                # No running loop, create a new one
                asyncio.run(self._save_session_metadata_async(metadata))
        except Exception as e:
            self.logger.error(f"Error saving session metadata: {e}")
    
    async def _save_session_metadata_async(self, metadata: Dict[str, Any]):
        """Save additional metadata for the session (async implementation)."""
        self._initialize_storage()
        
        if not self.storage:
            self.logger.warning("Cannot save session metadata - TinyAgent storage not available")
            return
        
        data = {
            "metadata": metadata,
            "session_state": {
                "messages": []  # Empty messages for new session
            }
        }
        
        try:
            await self.storage.save_session(self.current_session_id, data, self.user_id)
            self.logger.info(f"Session metadata saved for session {self.current_session_id}")
        except Exception as e:
            self.logger.error(f"Error saving session metadata: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def switch_to_session(self, session_id: str, user_id: str):
        """Switch storage manager to use different session and user context.
        
        This is critical for properly loading sessions from different users/projects.
        
        Args:
            session_id: The session ID to switch to
            user_id: The user ID to switch to (important for cross-project sessions)
        """
        old_session_id = self.current_session_id
        old_user_id = self.user_id
        
        # CRITICAL FIX: Validate user_id is not None before overwriting
        if user_id is None:
            print(f"[WARNING] switch_to_session: Received None user_id, keeping current user_id: {self.user_id}")
            self.logger.warning(f"switch_to_session called with None user_id, preserving current user_id: {self.user_id}")
        else:
            self.user_id = user_id
        
        self.current_session_id = session_id
        
        self.logger.info(f"Storage context switched - Session: {old_session_id[:8]} -> {session_id[:8]}, User: {old_user_id} -> {user_id}")
        
        # Update storage instance session tracking if available
        if self.storage and hasattr(self.storage, 'current_session_id'):
            self.storage.current_session_id = session_id
            self.logger.info(f"Updated storage instance session_id to {session_id}")
    
    def get_current_context(self) -> Dict[str, str]:
        """Get current session and user context."""
        return {
            "session_id": self.current_session_id,
            "user_id": self.user_id
        }