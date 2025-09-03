"""AI Agent integration for juno-agent using TinyAgent-py."""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import ConfigManager


class TinyAgentChat:
    """Chat interface with TinyAgent-py integration."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.console = Console()
        self.conversation_history: List[Dict[str, Any]] = []
        
    async def process_chat_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process a chat message using TinyAgent-py (placeholder)."""
        # This is a placeholder for TinyAgent integration
        # In the future, this will connect to the actual TinyAgent-py library
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": message,
            "context": context or {}
        })
        
        # Simulate processing time with spinner
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("🤖 Processing with TinyAgent...", total=None)
            await asyncio.sleep(1)  # Simulate processing
            
        # Generate intelligent response based on message content
        response = await self._generate_response(message, context)
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant", 
            "content": response,
            "context": context or {}
        })
        
        return response
    
    async def _generate_response(self, message: str, context: Optional[Dict] = None) -> str:
        """Generate response using AI agent logic (placeholder)."""
        config = self.config_manager.load_config()
        
        # Analyze message intent
        message_lower = message.lower()
        
        # Project-related queries
        if any(keyword in message_lower for keyword in ["project", "dependencies", "scan", "analyze"]):
            if config.libraries:
                dep_count = len(config.libraries)
                main_deps = config.libraries[:5] if dep_count > 5 else config.libraries
                response = f"""🔍 **Project Analysis**

I can see your project has {dep_count} dependencies including: {', '.join(main_deps)}
{'...' if dep_count > 5 else ''}

Would you like me to:
• Analyze dependency relationships
• Suggest optimization opportunities  
• Generate updated documentation rules
• Check for security vulnerabilities

*Use `/scan` to refresh project analysis*"""
            else:
                response = """🔍 **Project Analysis**

I don't see any project scan data yet. Let me help you get started:

• Run `/scan` to analyze your project structure
• I'll detect languages, frameworks, and dependencies
• Then I can provide intelligent insights and suggestions

*This will enable smarter assistance tailored to your project*"""
        
        # Setup and configuration queries
        elif any(keyword in message_lower for keyword in ["setup", "configure", "install", "mcp"]):
            setup_status = []
            if self.config_manager.has_api_key():
                setup_status.append("✅ API Key configured")
            else:
                setup_status.append("❌ API Key needed")
                
            if config.editor:
                setup_status.append(f"✅ Editor: {config.editor}")
            else:
                setup_status.append("❌ No editor selected")
                
            if config.mcp_server_installed:
                setup_status.append("✅ MCP Server installed")
            else:
                setup_status.append("❌ MCP Server not installed")
            
            response = f"""⚙️ **Setup Status**

{chr(10).join(setup_status)}

Next steps:
• Run `/setup` for guided configuration
• Use `/editor` to configure your code editor
• Install MCP server for enhanced AI assistance

*Proper setup enables all advanced features*"""
        
        # Documentation and help queries
        elif any(keyword in message_lower for keyword in ["help", "how", "what", "explain", "document"]):
            response = """📚 **Getting Help**

I'm your AI assistant for development workflow optimization. I can help with:

🔧 **Setup & Configuration**
• API key management
• Editor integration (Claude Code, Cursor, Windsurf)
• MCP server installation

📊 **Project Analysis**  
• Dependency scanning and analysis
• Technology stack detection
• Code organization insights

🤖 **AI Integration**
• Smart documentation generation
• Context-aware assistance
• Workflow optimization

*Type `/help` for command reference or ask me specific questions!*"""
        
        # API and integration queries
        elif any(keyword in message_lower for keyword in ["api", "key", "askbudi", "authentication"]):
            if self.config_manager.has_api_key():
                response = """🔑 **API Configuration**

✅ Your ASKBUDI API key is configured and ready!

Available features:
• Access to latest library documentation
• Real-time code analysis and suggestions
• Advanced AI-powered project insights
• MCP server integration

*Use `/apikey` to update your key if needed*"""
            else:
                response = """🔑 **API Key Setup**

You'll need an ASKBUDI API key to unlock full functionality:

1. Visit https://askbudi.ai to get your free API key
2. Run `/apikey` to configure it
3. Enjoy enhanced AI assistance!

Benefits:
• Access to 1000+ library documentation sets
• Real-time code suggestions and analysis
• Advanced project insights and optimization tips

*Get started at https://askbudi.ai* 🚀"""
        
        # General conversation
        else:
            response = f"""🤖 **AI Assistant**

I understand you said: *"{message}"*

I'm here to help with your development workflow! I can assist with:

• Project setup and configuration
• Dependency analysis and management  
• Code editor integration
• Documentation generation
• Development best practices

Try asking me about:
- "How do I set up my project?"
- "Analyze my dependencies"
- "Help with editor configuration"
- Or use commands like `/scan`, `/setup`, `/help`

*What would you like to work on?* ✨"""
        
        return response
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation for context."""
        return {
            "total_exchanges": len([h for h in self.conversation_history if h["role"] == "user"]),
            "last_user_message": next(
                (h["content"] for h in reversed(self.conversation_history) if h["role"] == "user"), 
                None
            ),
            "conversation_topics": self._extract_topics(),
            "session_start": self.conversation_history[0]["timestamp"] if self.conversation_history else None
        }
    
    def _extract_topics(self) -> List[str]:
        """Extract topics from conversation history."""
        topics = set()
        keywords_map = {
            "setup": ["setup", "configure", "install"],
            "project": ["project", "dependencies", "scan"],
            "api": ["api", "key", "askbudi"],
            "editor": ["editor", "mcp", "integration"],
            "help": ["help", "how", "what", "explain"]
        }
        
        for message in self.conversation_history:
            if message["role"] == "user":
                content_lower = message["content"].lower()
                for topic, keywords in keywords_map.items():
                    if any(keyword in content_lower for keyword in keywords):
                        topics.add(topic)
        
        return list(topics)
    
    def save_conversation(self) -> None:
        """Save conversation history to file."""
        if not self.conversation_history:
            return
            
        conversation_file = self.config_manager.config_dir / "conversation_history.json"
        
        # Load existing conversations
        conversations = []
        if conversation_file.exists():
            try:
                with open(conversation_file, 'r') as f:
                    conversations = json.load(f)
            except:
                conversations = []
        
        # Add current conversation
        conversation_data = {
            "session_id": datetime.now().isoformat(),
            "messages": self.conversation_history,
            "summary": self.get_conversation_summary()
        }
        conversations.append(conversation_data)
        
        # Keep only last 10 conversations
        conversations = conversations[-10:]
        
        # Save updated conversations (create directory if needed)
        conversation_file.parent.mkdir(parents=True, exist_ok=True)
        with open(conversation_file, 'w') as f:
            json.dump(conversations, f, indent=2)


class ProjectAnalysisAgent:
    """Agent for intelligent project analysis."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.console = Console()
    
    async def analyze_project_context(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project context for intelligent assistance."""
        # This is a placeholder for TinyAgent integration
        # Future implementation will use TinyAgent-py for deep analysis
        
        context = {
            "analysis_timestamp": datetime.now().isoformat(),
            "project_path": str(project_path),
            "detected_patterns": [],
            "optimization_suggestions": [],
            "security_recommendations": [],
            "documentation_gaps": []
        }
        
        # Simulate analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("🔍 Analyzing project structure...", total=None)
            await asyncio.sleep(2)
            
        # Generate mock insights based on config
        config = self.config_manager.load_config()
        
        if config.libraries:
            # Analyze dependencies
            context["detected_patterns"].extend([
                "Standard dependency management detected",
                f"Project uses {len(config.libraries)} external dependencies",
                "Code organization follows best practices"
            ])
            
            # Generate suggestions
            context["optimization_suggestions"].extend([
                "Consider dependency vulnerability scanning",
                "Documentation could be enhanced with library-specific guides",
                "MCP server integration recommended for AI assistance"
            ])
        
        if config.editor and not config.mcp_server_installed:
            context["optimization_suggestions"].append(
                f"Install MCP server for {config.editor} to enable advanced AI features"
            )
        
        return context
    
    def generate_insights_report(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable insights report."""
        report_sections = []
        
        if analysis.get("detected_patterns"):
            patterns = "\n".join(f"• {pattern}" for pattern in analysis["detected_patterns"])
            report_sections.append(f"**🔍 Detected Patterns:**\n{patterns}")
        
        if analysis.get("optimization_suggestions"):
            suggestions = "\n".join(f"• {suggestion}" for suggestion in analysis["optimization_suggestions"])
            report_sections.append(f"**🚀 Optimization Suggestions:**\n{suggestions}")
        
        if analysis.get("security_recommendations"):
            security = "\n".join(f"• {rec}" for rec in analysis["security_recommendations"])
            report_sections.append(f"**🔒 Security Recommendations:**\n{security}")
        
        if not report_sections:
            return "**📊 Project Analysis**\n\nRun `/scan` to analyze your project structure and get intelligent insights!"
        
        return "\n\n".join(report_sections)