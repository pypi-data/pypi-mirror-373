"""Conversation storage manager for juno-agent using TinyAgent's SQLite storage."""

from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid
import json
from datetime import datetime
import sqlite3
import logging


class ConversationStorageManager:
    """Manages conversation storage for juno-agent using TinyAgent's SQLite storage."""
    
    def __init__(self):
        # Create storage directory
        self.storage_dir = Path.home() / ".askbudi"
        self.storage_dir.mkdir(exist_ok=True)
        
        # Database path
        self.db_path = self.storage_dir / "conversations.db"
        
        # Initialize logger first
        self.logger = logging.getLogger(__name__)
        # Set up logging to see debug info
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
        
        self.logger.info(f"=== STORAGE MANAGER INITIALIZED ===\nStorage dir: {self.storage_dir}\nDatabase path: {self.db_path}")
        
        # Initialize TinyAgent's SQLite storage (lazy initialization)
        self.storage = None
        
        # Generate user_id from current working directory (escaped)
        self.user_id = self._generate_user_id()
        
        # Start with a new session
        self.current_session_id = self.new_session()
    
    def _initialize_storage(self):
        """Initialize TinyAgent storage on first use."""
        if self.storage is None:
            try:
                from tinyagent.storage.sqlite_storage import SqliteStorage
                self.logger.info(f"Initializing TinyAgent SqliteStorage with path: {self.db_path}")
                self.storage = SqliteStorage(str(self.db_path))
                self.logger.info(f"TinyAgent SqliteStorage initialized successfully: {type(self.storage)}")
            except ImportError as e:
                self.logger.error(f"TinyAgent not available - storage will be limited: {e}")
                self.storage = None
            except Exception as e:
                self.logger.error(f"Failed to initialize TinyAgent storage: {e}")
                self.storage = None
    
    def _generate_user_id(self) -> str:
        """Generate user_id from current working directory path."""
        # Use the absolute path and normalize it
        cwd_path = Path.cwd().resolve()
        # Create a consistent user_id that won't change between sessions
        user_id = str(cwd_path).replace("/", "_").replace("\\", "_").replace(":", "")
        self.logger.info(f"Generated user_id: '{user_id}' from path: {cwd_path}")
        return user_id
    
    def new_session(self) -> str:
        """Create a new chat session with a unique UUID."""
        self.current_session_id = str(uuid.uuid4())
        self.logger.info(f"New session created: {self.current_session_id}")
        return self.current_session_id
    
    def attach_to_agent(self, agent):
        """Attach storage to TinyAgent for auto-persistence."""
        self.logger.info(f"=== ATTACH_TO_AGENT CALLED ===\nAgent: {type(agent) if agent else None}\nAgent ID: {hex(id(agent)) if agent else None}")
        
        self._initialize_storage()
        
        if self.storage and agent:
            try:
                self.logger.info(f"Attempting to attach storage to agent for session: {self.current_session_id}")
                self.logger.info(f"Using user_id: {self.user_id}")
                self.logger.info(f"Database path: {self.db_path}")
                self.logger.info(f"Storage type: {type(self.storage)}")
                self.logger.info(f"Agent type: {type(agent)}")
                
                # Set session info
                self.logger.info("Setting session info...")
                self.storage.set_session_info(self.current_session_id, self.user_id)
                self.logger.info("Session info set successfully")
                
                # Attach storage
                self.logger.info("Attaching storage to agent...")
                self.storage.attach(agent)
                self.logger.info(f"Storage successfully attached to agent for session: {self.current_session_id}")
                
                # Check if agent has storage attribute now
                if hasattr(agent, 'storage'):
                    self.logger.info(f"Agent.storage is now set: {type(agent.storage)}")
                else:
                    self.logger.warning("Agent does not have 'storage' attribute after attach")
                
                # Test that storage is working by checking if we can save metadata
                try:
                    test_metadata = {
                        "test": "storage_attachment",
                        "timestamp": datetime.now().isoformat(),
                        "agent_type": str(type(agent)),
                        "storage_type": str(type(self.storage))
                    }
                    self.save_session_metadata(test_metadata)
                    self.logger.info("Storage test save successful")
                except Exception as e:
                    self.logger.error(f"Storage test save failed: {e}")
                    import traceback
                    self.logger.error(f"Storage test save traceback: {traceback.format_exc()}")
                    
            except Exception as e:
                self.logger.error(f"Error attaching storage to agent: {e}")
                import traceback
                self.logger.error(f"Attach error traceback: {traceback.format_exc()}")
        else:
            self.logger.warning(f"Cannot attach storage - TinyAgent storage available: {self.storage is not None}, agent provided: {agent is not None}")
            if not self.storage:
                self.logger.warning("Storage is None - check TinyAgent initialization")
            if not agent:
                self.logger.warning("Agent is None - no agent to attach to")
    
    def save_session_metadata(self, metadata: Dict[str, Any]):
        """Save additional metadata for the session."""
        self.logger.info(f"=== SAVE_SESSION_METADATA CALLED ===\nSession ID: {self.current_session_id}\nUser ID: {self.user_id}\nMetadata: {metadata}")
        
        self._initialize_storage()
        
        if not self.storage:
            self.logger.warning("Cannot save session metadata - TinyAgent storage not available")
            return
            
        data = {
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            self.logger.info(f"Calling storage.save_session with: session_id={self.current_session_id}, data={data}, user_id={self.user_id}")
            self.storage.save_session(self.current_session_id, data, self.user_id)
            self.logger.info("Session metadata saved successfully")
            
            # Verify the save by trying to load it back
            try:
                loaded_data = self.storage.load_session(self.current_session_id, self.user_id)
                self.logger.info(f"Verification load successful: {loaded_data is not None}")
                if loaded_data:
                    self.logger.info(f"Loaded data keys: {list(loaded_data.keys()) if isinstance(loaded_data, dict) else type(loaded_data)}")
            except Exception as ve:
                self.logger.error(f"Verification load failed: {ve}")
                
        except Exception as e:
            self.logger.error(f"Error saving session metadata: {e}")
            import traceback
            self.logger.error(f"Save metadata traceback: {traceback.format_exc()}")
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions for the current user/project."""
        try:
            # Check if database exists
            if not self.db_path.exists():
                self.logger.info(f"Database does not exist at {self.db_path}")
                return []
            
            # Direct SQL query to get all sessions for this user
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='tny_agent_sessions'
            """)
            table_exists = cursor.fetchone()
            if not table_exists:
                self.logger.info("Table 'tny_agent_sessions' does not exist")
                # Check what tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                self.logger.info(f"Available tables: {[t[0] for t in tables]}")
                conn.close()
                return []
            
            # Debug: Check total sessions
            cursor.execute("SELECT COUNT(*) FROM tny_agent_sessions")
            total_sessions = cursor.fetchone()[0]
            self.logger.info(f"=== DATABASE DEBUG ===\nTotal sessions in DB: {total_sessions}")
            
            # Debug: Check sessions for current user
            cursor.execute("SELECT COUNT(*) FROM tny_agent_sessions WHERE user_id = ?", (self.user_id,))
            user_sessions = cursor.fetchone()[0]
            self.logger.info(f"Sessions for current user_id '{self.user_id}': {user_sessions}")
            
            # If no sessions for current user, check what user_ids exist
            if user_sessions == 0:
                cursor.execute("SELECT DISTINCT user_id FROM tny_agent_sessions LIMIT 10")
                existing_users = cursor.fetchall()
                self.logger.info(f"Existing user_ids in database: {[u[0] for u in existing_users]}")
                
                # Also check the raw data to see what's actually stored
                cursor.execute("SELECT session_id, user_id, created_at FROM tny_agent_sessions ORDER BY created_at DESC LIMIT 5")
                recent_sessions = cursor.fetchall()
                self.logger.info(f"Recent sessions (last 5): {recent_sessions}")
            
            # Get sessions with metadata
            cursor.execute("""
                SELECT session_id, data, created_at, updated_at 
                FROM tny_agent_sessions 
                WHERE user_id = ? 
                ORDER BY updated_at DESC
            """, (self.user_id,))
            
            sessions = []
            for row in cursor.fetchall():
                session_data = {
                    "session_id": row[0],
                    "created_at": row[2],
                    "updated_at": row[3]
                }
                
                # Parse JSON data if available
                if row[1]:
                    try:
                        data = json.loads(row[1])
                        session_data["metadata"] = data.get("metadata", {})
                        session_data["message_count"] = len(data.get("messages", []))
                    except json.JSONDecodeError:
                        session_data["message_count"] = 0
                
                sessions.append(session_data)
            
            conn.close()
            self.logger.info(f"=== LIST_SESSIONS RESULT ===\nFound {len(sessions)} sessions for user '{self.user_id}'")
            if sessions:
                for i, session in enumerate(sessions[:3]):
                    self.logger.info(f"Session {i+1}: {session}")
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error listing sessions: {e}")
            return []
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a specific session's data."""
        self._initialize_storage()
        
        if not self.storage:
            self.logger.warning("Cannot load session - TinyAgent storage not available")
            return None
            
        try:
            data = self.storage.load_session(session_id, self.user_id)
            if data:
                self.current_session_id = session_id
                self.logger.info(f"Loaded session: {session_id}")
            return data
        except Exception as e:
            self.logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a specific session."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM tny_agent_sessions WHERE session_id = ? AND user_id = ?",
                (session_id, self.user_id)
            )
            conn.commit()
            conn.close()
            self.logger.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    def get_session_summary(self, session_id: str) -> str:
        """Get a brief summary of a session for display."""
        data = self.load_session(session_id)
        if not data:
            return "Empty session"
        
        messages = data.get("messages", [])
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
        """Clean up storage resources."""
        if self.storage:
            try:
                # Close storage connection if available
                if hasattr(self.storage, 'close'):
                    self.storage.close()
                elif hasattr(self.storage, '_connection') and self.storage._connection:
                    self.storage._connection.close()
                self.logger.info("Storage resources cleaned up")
            except Exception as e:
                self.logger.error(f"Error closing storage: {e}")
            finally:
                self.storage = None