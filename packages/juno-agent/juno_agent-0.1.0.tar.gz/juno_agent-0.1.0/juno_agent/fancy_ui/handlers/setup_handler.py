"""Setup handler for managing all setup-related functionality."""

import asyncio
import getpass
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import platform

# Import necessary components for setup
from ..setup import (
    ClaudePermissionsService,
    MCPInstaller,
    DependencyScanner,
    ExternalContextManager
)
from ...utils import SystemStatus
from ...tiny_agent import TinyCodeAgentChat
from ...debug_logger import debug_logger


class SetupHandler:
    """Handler for all setup-related operations."""
    
    def __init__(self, app, config_manager, chat_area, storage_manager=None):
        """Initialize SetupHandler with dependencies."""
        self.app = app
        self.config_manager = config_manager
        self.chat_area = chat_area
        self.storage_manager = storage_manager
        self.debug_log = config_manager.create_debug_logger(debug=True)
        
        # Setup state management
        self.setup_active = False
        self.setup_step = 0
        self.setup_data = {}
        self.setup_steps = []
        
        # Setup components (will be initialized when needed)
        self.system_status = None
        self.dependency_scanner = None
        self.external_context_manager = None
        self.mcp_installer_enhanced = None
        self.claude_permissions_service = None
        self.agentic_dependency_resolver = None

    async def auto_start_setup_wizard(self) -> None:
        """Automatically start the setup wizard - called from timer when auto_start_setup is True."""
        await self.handle_setup_command()
    
    async def auto_start_verification_only(self) -> None:
        """Automatically start verification only mode - called from timer when verify_only_mode is True."""
        try:
            self.chat_area.add_message("🔍 **Auto-starting verification-only mode...**\n", is_user=False)
            await self.handle_verification_only_command()
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error in verification mode**: {str(e)}\n", is_user=False)
            self.debug_log.error(f"Error in _auto_start_verification_only: {e}")
            import traceback
            self.debug_log.error(f"Traceback: {traceback.format_exc()}")
    
    async def auto_start_agentic_resolver(self) -> None:
        """Automatically start agentic resolver mode - called from timer when agentic_resolver_mode is True."""
        try:
            self.chat_area.add_message("🤖 **Auto-starting Agentic Dependency Resolver...**\n\nUsing intelligent agent to scan dependencies and fetch documentation.\n", is_user=False)
            await self.handle_agentic_resolver_command()
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error in agentic resolver mode**: {str(e)}\n", is_user=False)
            self.debug_log.error(f"Error in _auto_start_agentic_resolver: {e}")
            import traceback
            self.debug_log.error(f"Traceback: {traceback.format_exc()}")
    
    async def handle_agentic_resolver_command(self) -> None:
        """Handle agentic resolver mode - run full dependency analysis and documentation fetching."""
        self.debug_log.debug("=" * 80)
        self.debug_log.debug("HANDLE_AGENTIC_RESOLVER_COMMAND - START")
        
        self.chat_area.add_message("**🤖 Agentic Dependency Resolver**\n\nUsing intelligent agent to analyze your project and fetch dependency documentation...\n\nThis will:\n- Intelligently scan your project for dependencies\n- Search and select the most relevant documentation\n- Fetch and organize documentation with metadata\n- Create symlinks and external context structure\n\n*Initializing agentic resolver...*\n", is_user=False)
        
        try:
            # Initialize setup components (this creates agentic_dependency_resolver)
            self.debug_log.debug("Initializing setup components...")
            await self.initialize_setup_components()
            self.debug_log.debug("Setup components initialized")
            
            # Use the already initialized resolver from setup components
            if not hasattr(self, 'agentic_dependency_resolver') or not self.agentic_dependency_resolver:
                # Only create if not already created by initialize_setup_components
                self.debug_log.debug("Creating AgenticDependencyResolver instance (not found in setup components)...")
                from ...agentic_dependency_resolver import AgenticDependencyResolver
                
                self.agentic_dependency_resolver = AgenticDependencyResolver(
                    project_path=str(self.config_manager.workdir),
                    config_manager=self.config_manager,
                    ui_callback=self.dependency_progress_callback,
                    storage_manager=self.storage_manager
                )
                self.debug_log.debug("AgenticDependencyResolver instance created")
            else:
                self.debug_log.debug("Using existing AgenticDependencyResolver from setup components")
            
            resolver = self.agentic_dependency_resolver
            
            self.chat_area.add_message("🔄 **Running Agentic Dependency Resolution...**\n", is_user=False)
            
            # Run the complete resolver (scan dependencies + fetch docs)
            self.debug_log.debug("Calling resolver.run()...")
            result = await resolver.run()
            self.debug_log.debug(f"resolver.run() returned. Success: {result.get('success', False)}")
            
            if result.get('success', False):
                # The resolver returns files_created, file_names, etc.
                files_created = result.get('files_created', 0)
                file_names = result.get('file_names', [])
                symlinks_created = result.get('symlinks_created', False)
                
                # Try to get dependencies from scan results if available
                dependencies = result.get('dependencies', [])
                dependencies_count = len(dependencies) if dependencies else 0
                
                # If no dependencies from scan, estimate from files created
                if dependencies_count == 0 and files_created > 0:
                    dependencies_count = files_created
                
                self.chat_area.add_message(f"✅ **Agentic Dependency Resolution Complete!**\n\n**Summary:**\n- Dependencies processed: {dependencies_count}\n- Documentation files created: {files_created}\n- External context created: {'✅' if files_created > 0 else '❌'}\n- Symlinks created: {'✅' if symlinks_created else '❌'}\n\n", is_user=False)
                
                # Show file details if any were created
                if files_created > 0 and file_names:
                    file_list = "\n".join([f"- {name}" for name in file_names[:5]])
                    if len(file_names) > 5:
                        file_list += f"\n- ... and {len(file_names) - 5} more files"
                    self.chat_area.add_message(f"**📄 Documentation Files Created:**\n\n{file_list}\n\n*Agentic resolver has successfully processed your project dependencies.*\n", is_user=False)
                else:
                    self.chat_area.add_message("*Agentic resolver completed but no documentation files were created. This may indicate no suitable dependencies were found or processed.*\n", is_user=False)
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                self.chat_area.add_message(f"⚠️ **Agentic Dependency Resolution Issues**\n\nSome issues occurred during resolution:\n{error_msg}\n\nPlease check the logs for more details.\n", is_user=False)
                
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error in Agentic Resolver**: {str(e)}\n\nThe agentic dependency resolver encountered an error. Please check your configuration and try again.\n", is_user=False)
            self.debug_log.error(f"Error in _handle_agentic_resolver_command: {e}")
            import traceback
            self.debug_log.error(f"Traceback: {traceback.format_exc()}")
    
    async def handle_setup_command(self) -> None:
        """Handle /setup command - start enhanced 8-step setup wizard with TinyAgent integration."""
        self.chat_area.add_message("**🚀 Enhanced AI-Powered Setup Wizard**\n\nWelcome to the comprehensive juno-agent setup process!\n\nThis AI-powered wizard will help you:\n- Analyze your project structure and dependencies\n- Configure your AI IDE preferences\n- Install MCP servers for enhanced functionality\n- Create comprehensive project documentation (JUNO.md)\n- Set up external context for better AI assistance\n- Configure IDE-specific instruction files\n- Set up Claude permissions\n\n*This setup uses TinyAgent with advanced project analysis capabilities.*\n\nLet's get started!\n", is_user=False)
        
        # Initialize setup components
        await self.initialize_setup_components()
        
        # Define the enhanced 9-step setup process
        self.setup_steps = [
            'collect_project_description',
            'editor_selection', 
            'api_key_setup',
            'ai_project_analysis',
            'install_mcp_servers',
            'fetch_dependency_docs',
            'setup_external_context',
            'create_ide_configs',
            'verification_step',
            'completion_summary'
        ]
        
        # Start setup mode
        self.setup_active = True
        self.setup_step = 0
        self.setup_data = {
            'project_description': None,
            'selected_editor': None,
            'ai_analysis_result': None,
            'detected_dependencies': None,
            'installed_mcp_servers': [],
            'fetched_docs': {},
            'external_context_setup': False,
            'permissions_configured': False,
            'ide_configs_created': False
        }
        
        # Start the first step
        await self.start_enhanced_setup_step()
    
    async def initialize_setup_components(self) -> None:
        """Initialize all setup components."""
        try:
            # Initialize system status
            if not hasattr(self, 'system_status') or not self.system_status:
                self.system_status = SystemStatus(self.config_manager.workdir)
            
            # Initialize setup components
            self.dependency_scanner = DependencyScanner(self.config_manager.workdir)
            self.external_context_manager = ExternalContextManager(self.config_manager.workdir) 
            self.mcp_installer_enhanced = MCPInstaller(project_dir=Path(self.config_manager.workdir))
            self.claude_permissions_service = ClaudePermissionsService()
            # Initialize AgenticDependencyResolver (replaces old dependency_docs_api)
            from ...agentic_dependency_resolver import AgenticDependencyResolver
            self.agentic_dependency_resolver = AgenticDependencyResolver(
                project_path=str(self.config_manager.workdir),
                config_manager=self.config_manager,
                ui_callback=self.dependency_progress_callback,
                storage_manager=self.storage_manager
            )
            
            # The dependency documentation functionality is now handled by AgenticDependencyResolver
            
            self.chat_area.add_message("✅ Setup components initialized successfully.\n", is_user=False)
            
        except Exception as e:
            self.chat_area.add_message(f"❌ Failed to initialize setup components: {e}\n", is_user=False)
            # Continue with setup anyway, some components might still work
    
    async def handle_verification_only_command(self) -> None:
        """Handle verification-only mode - run comprehensive verification without setup."""
        self.chat_area.add_message("**🔍 Setup Verification Mode**\n\nRunning comprehensive verification of your current setup...\n\nThis will check:\n- MCP server configuration\n- External context setup\n- IDE configuration files\n- Dependency documentation\n- API key configuration\n- File permissions\n- Project analysis accuracy\n\n*Running verification now...*\n", is_user=False)
        
        try:
            # Run the verification directly
            await self.perform_setup_verification_standalone()
            
        except Exception as e:
            self.chat_area.add_message(f"**❌ Verification Failed**\n\nError: {e}\n\nPlease check your setup and try again.\n", is_user=False)
    
    async def perform_setup_verification_standalone(self) -> None:
        """Run comprehensive setup verification in standalone mode."""
        try:
            from ..setup.setup_verification_service import SetupVerificationService
            import os
            
            # Get project information
            project_root = str(Path(self.config_manager.workdir).resolve())
            project_name = Path(project_root).name
            
            # Initialize verification service
            verification_service = SetupVerificationService(project_root, project_name)
            
            # Run verification
            self.chat_area.add_message("🔄 Running verification checks...\n", is_user=False)
            verification_results = verification_service.verify_all_components()
            
            # Generate report using the verification agent
            report = verification_service.generate_summary_report(verification_results)
            
            # Also run AI verification agent for additional analysis (skip if not available)
            ai_verification_report = None
            try:
                ai_verification_report = await self.run_ai_verification_agent(project_root, project_name, verification_results)
            except Exception as e:
                self.chat_area.add_message(f"ℹ️ AI verification analysis skipped: {str(e)}\n", is_user=False)
            
            # Count status
            status_counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
            for result in verification_results:
                status_counts[result.status] += 1
            
            # Determine overall status
            if status_counts["FAIL"] == 0:
                if status_counts["WARN"] == 0:
                    overall_status = "🎉 EXCELLENT"
                    status_msg = "All components passed verification!"
                    final_msg = "**🎉 Setup is Perfect!**\n\nYour development environment is fully configured and ready to use. All components are working correctly."
                else:
                    overall_status = "✅ GOOD"
                    status_msg = f"Functional with {status_counts['WARN']} warnings"
                    final_msg = "**✅ Setup is Good!**\n\nYour setup is functional but there are some minor warnings to address for optimal performance."
            elif status_counts["FAIL"] <= 2:
                overall_status = "⚠️ NEEDS ATTENTION"
                status_msg = f"{status_counts['FAIL']} failures need resolution"
                final_msg = "**⚠️ Setup Needs Attention**\n\nYour setup has some issues that need to be resolved. Please address the failures listed below."
            else:
                overall_status = "❌ CRITICAL ISSUES"
                status_msg = f"{status_counts['FAIL']} critical failures found"
                final_msg = "**❌ Critical Issues Found**\n\nYour setup has significant problems that will impact functionality. Please address the critical failures before proceeding."
            
            # Show verification summary
            summary_message = f"""---

**Setup Verification Complete**

**Overall Status**: {overall_status}
**Message**: {status_msg}

**Component Summary**:
- ✅ Passed: {status_counts["PASS"]}
- ❌ Failed: {status_counts["FAIL"]}
- ⚠️ Warnings: {status_counts["WARN"]}
- ℹ️ Info: {status_counts["INFO"]}

**Success Rate**: {(status_counts["PASS"] / len(verification_results) * 100):.1f}%

---"""
            
            self.chat_area.add_message(summary_message, is_user=False)
            
            # Show detailed errors and warnings if they exist
            await self.display_detailed_verification_results(verification_results, status_counts)
            
            # Show AI verification insights if available
            if ai_verification_report:
                self.chat_area.add_message("**🤖 AI Verification Analysis**\n\n" + ai_verification_report, is_user=False)
            
            # Final message with next steps
            self.chat_area.add_message(final_msg, is_user=False)
            
            if status_counts["FAIL"] > 0 or status_counts["WARN"] > 0:
                next_steps_msg = "\n**📋 Next Steps:**\n"
                if status_counts["FAIL"] > 0:
                    next_steps_msg += "1. **Address Critical Failures**: Focus on FAIL status components first\n"
                    next_steps_msg += "2. **Re-run Setup**: Consider running `juno-cli setup` for failed components\n"
                    next_steps_msg += "3. **Manual Configuration**: Some components may need manual fixes\n"
                if status_counts["WARN"] > 0:
                    next_steps_msg += "4. **Resolve Warnings**: Address warning components for optimal performance\n"
                next_steps_msg += "5. **Re-run Verification**: Use `juno-cli setup --verify-only` after fixing issues\n"
                self.chat_area.add_message(next_steps_msg, is_user=False)
            else:
                self.chat_area.add_message("**🎯 You're Ready to Go!**\n\n✨ Your development environment is properly configured.\n- Start using your AI-powered IDE\n- Test MCP server functionality  \n- Explore external documentation context\n", is_user=False)
            
        except Exception as e:
            self.chat_area.add_message(f"**❌ Verification Error**\n\nFailed to run verification: {e}\n\nThis could indicate setup issues or missing components.\n", is_user=False)
    
    async def handle_docs_only_command(self) -> None:
        """Handle docs-only mode - fetch documentation for provided/detected dependencies."""
        self.chat_area.add_message("**📚 Documentation Fetching Mode**\n\nFetching documentation for your project dependencies...\n\nThis will:\n- Use previously detected dependencies (if available)\n- Search for dependency documentation\n- Download and organize documentation\n- Create symlinks and external context\n\n*Starting documentation fetching...*\n", is_user=False)
        
        try:
            # Initialize setup components
            await self.initialize_setup_components()
            
            # Check for previously detected dependencies
            config = self.config_manager.load_config()
            previous_scan = getattr(config, 'last_dependency_scan', None)
            
            if not previous_scan or not previous_scan.get('dependencies'):
                self.chat_area.add_message("⚠️ **No Dependencies Found**\n\nNo previously detected dependencies found. Running a quick scan first...\n", is_user=False)
                
                # Run quick dependency scan
                from ...agentic_dependency_resolver import AgenticDependencyResolver
                
                resolver = AgenticDependencyResolver(
                    project_path=str(self.config_manager.workdir),
                    config_manager=self.config_manager,
                    ui_callback=self.dependency_progress_callback,
                    storage_manager=self.storage_manager
                )
                
                scan_result = await resolver.run(dependency_only=True)
                if not scan_result.get('dependencies'):
                    self.chat_area.add_message("**❌ No Dependencies to Process**\n\nNo dependencies were found in your project. Please run dependency scanning first with `juno-cli setup --docs-only` or ensure your project has dependencies configured.\n", is_user=False)
                    return
                
                dependencies = scan_result['dependencies']
            else:
                dependencies = previous_scan['dependencies']
            
            # Proceed with documentation fetching using AgenticDependencyResolver
            from ...agentic_dependency_resolver import AgenticDependencyResolver
            
            resolver = AgenticDependencyResolver(
                project_path=str(self.config_manager.workdir),
                config_manager=self.config_manager,
                ui_callback=self.dependency_progress_callback,
                storage_manager=self.storage_manager
            )
            
            self.chat_area.add_message(f"🔄 Fetching documentation for {len(dependencies)} dependencies...\n", is_user=False)
            
            # Run docs-only mode (fetch docs for provided dependencies)
            dependency_names = [dep['name'] if isinstance(dep, dict) else dep for dep in dependencies]
            result = await resolver.run(docs_only=dependency_names)
            
            # Display results
            documentation_fetched = result.get('documentation_fetched', {})
            if documentation_fetched.get('success'):
                saved_files = documentation_fetched.get('saved_files', [])
                failed_saves = documentation_fetched.get('failed_saves', [])
                
                success_count = len(saved_files)
                failed_count = len(failed_saves)
                
                success_list = "\n".join([f"✅ {file_info['name']}" for file_info in saved_files[:5]])
                if success_count > 5:
                    success_list += f"\n... and {success_count - 5} more"
                
                self.chat_area.add_message(f"**📚 Documentation Fetching Complete**\n\n**Successfully fetched:** {success_count} dependencies\n**Failed:** {failed_count} dependencies\n\n**Recent successes:**\n{success_list}\n\n---", is_user=False)
                
                if failed_saves:
                    failed_list = "\n".join([f"❌ {fail_info['name']}: {fail_info.get('error', 'Unknown error')}" for fail_info in failed_saves[:5]])
                    if failed_count > 5:
                        failed_list += f"\n... and {failed_count - 5} more"
                    self.chat_area.add_message(f"**Failed dependencies:**\n{failed_list}\n", is_user=False)
                
                # Show next steps
                self.chat_area.add_message("**🎯 Documentation Ready!**\n\n✨ Your dependency documentation has been organized and is ready to use.\n- Check the `external_context` directory for downloaded docs\n- Documentation is available through MCP servers\n- AI assistants can now access comprehensive dependency information\n", is_user=False)
            else:
                self.chat_area.add_message("**⚠️ No Documentation Retrieved**\n\nNo documentation could be fetched for the provided dependencies. This could be due to:\n- Network connectivity issues\n- API service limitations\n- Unsupported dependency types\n", is_user=False)
            
        except Exception as e:
            self.chat_area.add_message(f"**❌ Documentation Fetching Failed**\n\nError: {e}\n\nPlease check your configuration and network connection, then try again.\n", is_user=False)
    
    def dependency_progress_callback(self, message: str, data: Dict[str, Any]) -> None:
        """Callback to receive progress updates from dependency resolver."""
        if self.chat_area:
            self.chat_area.add_message(f"🔄 {message}\n", is_user=False)
    
    async def start_enhanced_setup_step(self) -> None:
        """Start the current enhanced setup step with progress tracking."""
        if self.setup_step >= len(self.setup_steps):
            # Setup completed
            await self.complete_enhanced_setup()
            return
        
        current_step = self.setup_steps[self.setup_step]
        step_num = self.setup_step + 1
        total_steps = len(self.setup_steps)
        
        # Show progress
        progress_msg = f"**Step {step_num}/{total_steps}**"
        
        if current_step == 'collect_project_description':
            self.chat_area.add_message(f"{progress_msg} **📋 Project Description**\n\nPlease provide a brief description of your project. This helps AI assistants understand your project context better.\n\n*Example: \"A Python web API using FastAPI for managing user data and authentication\"*\n\n(Press Enter to skip if you prefer)", is_user=False)
        
        elif current_step == 'editor_selection':
            self.chat_area.add_message(f"{progress_msg} **📝 AI IDE Selection**\n\nSelect your preferred AI-powered development environment:", is_user=False)
            # Show the EditorSelectorMenu with proper timing
            self.app.call_after_refresh(self.show_ide_selection_menu)
        
        elif current_step == 'api_key_setup':
            await self.perform_api_key_setup(progress_msg)
        
        elif current_step == 'ai_project_analysis':
            self.chat_area.add_message(f"{progress_msg} **🤖 AI-Powered Project Analysis**\n\nUsing TinyAgent to analyze your project structure, dependencies, and patterns...", is_user=False)
            await self.perform_ai_project_analysis()
        
        elif current_step == 'install_mcp_servers':
            self.chat_area.add_message(f"{progress_msg} **⚙️ Installing MCP Servers**\n\nInstalling VibeContext MCP server for enhanced documentation access...", is_user=False)
            await self.perform_mcp_installation()
        
        elif current_step == 'fetch_dependency_docs':
            self.chat_area.add_message(f"{progress_msg} **📚 Fetching Dependency Documentation**\n\nRetrieving documentation for your project dependencies using AI-powered tools...", is_user=False)
            await self.perform_docs_fetching()
        
        elif current_step == 'setup_external_context':
            self.chat_area.add_message(f"{progress_msg} **📁 Setting Up External Context**\n\nCreating organized documentation structure...", is_user=False)
            await self.perform_external_context_setup()
        
        elif current_step == 'create_ide_configs':
            self.chat_area.add_message(f"{progress_msg} **📝 Creating IDE Configuration Files**\n\nGenerating JUNO.md and updating IDE-specific instruction files...", is_user=False)
            await self.perform_ide_config_creation()
        
        elif current_step == 'verification_step':
            self.chat_area.add_message(f"{progress_msg} **🔍 Setup Verification**\n\nRunning comprehensive verification of all setup components...", is_user=False)
            await self.perform_setup_verification()
        
        elif current_step == 'completion_summary':
            self.chat_area.add_message(f"{progress_msg} **🎉 Setup Summary**\n\nGenerating completion summary...", is_user=False)
            await self.show_completion_summary()
    
    async def handle_setup_input(self, user_input: str) -> None:
        """Handle user input during enhanced setup."""
        if user_input.lower() in ['/cancel', '/quit', '/exit']:
            self.setup_active = False
            self.setup_data = {}
            self.chat_area.add_message("**❌ Setup cancelled.**\n\nYou can restart the setup anytime with `/setup`.", is_user=False)
            return
        
        if not self.setup_active or not hasattr(self, 'setup_steps'):
            return
        
        current_step = self.setup_steps[self.setup_step]
        
        if current_step == 'collect_project_description':
            await self.handle_project_description_input(user_input)
        elif current_step == 'api_key_setup' and self.setup_data.get('api_key_prompt_shown'):
            await self.handle_api_key_input(user_input)
        # Note: editor_selection is handled by the EditorSelectorMenu events
        # Other steps are automated and don't require user input
    
    async def handle_project_description_input(self, description: str) -> None:
        """Handle project description input from user."""
        try:
            if description.strip():
                self.setup_data['project_description'] = description.strip()
                self.chat_area.add_message(f"✅ Project description saved: {description.strip()}\n", is_user=False)
            else:
                self.setup_data['project_description'] = None
                self.chat_area.add_message("✅ Project description skipped.\n", is_user=False)
            
            # Save to config
            config = self.config_manager.load_config()
            if self.setup_data['project_description']:
                config.project_description = self.setup_data['project_description']
                self.config_manager.save_config(config)
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"❌ Error saving project description: {e}\n", is_user=False)
            # Continue with setup anyway
            self.setup_step += 1
            await self.start_enhanced_setup_step()
    
    async def handle_api_key_input(self, user_input: str) -> None:
        """Handle API key input from user during setup."""
        try:
            input_lower = user_input.lower().strip()
            
            if input_lower == 'skip':
                self.chat_area.add_message("✅ Continuing with basic features (no API key configured).\n", is_user=False)
                self.setup_data['has_api_key'] = False
                self.setup_data['api_key_prompt_shown'] = False
                
            elif input_lower == 'learn':
                self.chat_area.add_message(
                    "**Learn More About VibeContext**\n\n"
                    "Visit https://askbudi.com to:\n"
                    "• Sign up for a FREE account\n"
                    "• Get your API key instantly\n"
                    "• Access comprehensive documentation\n"
                    "• Join the developer community\n\n"
                    "VibeContext integrates seamlessly with your workflow and provides intelligent assistance.\n\n"
                    "Please choose an option:\n"
                    "1. Enter 'key:<your_api_key>' to configure\n"
                    "2. Enter 'skip' to continue with basic features\n",
                    is_user=False
                )
                return  # Stay in current step
                
            elif input_lower.startswith('key:'):
                api_key = user_input[4:].strip()
                if not api_key:
                    self.chat_area.add_message("❌ Please provide an API key after 'key:'\n", is_user=False)
                    return
                    
                # Validate and save the API key
                from ..setup.api_key_manager import APIKeyManager
                api_key_manager = APIKeyManager(project_dir=Path(self.config_manager.workdir))
                
                self.chat_area.add_message("🔍 Validating API key...\n", is_user=False)
                
                is_valid = await api_key_manager.validate_api_key(api_key)
                
                if is_valid:
                    # Ask where to save (default to global)
                    api_key_manager.save_api_key(api_key, global_save=True)
                    self.chat_area.add_message("✅ API key validated and saved globally! VibeContext features enabled.\n", is_user=False)
                    self.setup_data['has_api_key'] = True
                    self.setup_data['api_key_source'] = 'Global configuration (setup)'
                    self.setup_data['api_key_prompt_shown'] = False
                else:
                    self.chat_area.add_message("❌ Invalid API key. Please check and try again, or enter 'skip' to continue.\n", is_user=False)
                    return  # Stay in current step
                    
            else:
                self.chat_area.add_message(
                    "❌ Invalid option. Please choose:\n"
                    "1. Enter 'key:<your_api_key>' to configure your API key\n"
                    "2. Enter 'skip' to continue with basic features\n"
                    "3. Enter 'learn' for more information\n",
                    is_user=False
                )
                return  # Stay in current step
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"❌ Error handling API key input: {e}\n\nContinuing with basic features...", is_user=False)
            self.setup_data['has_api_key'] = False
            self.setup_data['api_key_prompt_shown'] = False
            self.setup_step += 1
            await self.start_enhanced_setup_step()
    
    def show_ide_selection_menu(self) -> None:
        """Show the IDE selection menu with proper timing."""
        try:
            self.app.ide_selection_menu.show(
                title="AI IDE Preference",
                message="Choose the AI coding environment you use most often:"
            )
        except Exception as e:
            # Fallback: add a message indicating there was an issue
            self.chat_area.add_message(f"⚠️ IDE selection menu failed to load: {e}\n\nPlease manually specify your preferred AI IDE by typing it in the chat.", is_user=False)

    async def handle_editor_selection(self, editor_name: str) -> None:
        """Handle editor selection from EditorSelectorMenu."""
        try:
            # Special handling for "show_all" - expand the menu to show all IDEs
            if editor_name == "show_all":
                self.chat_area.add_message("📋 **Showing all supported IDEs...**\n", is_user=False)
                
                # Recreate the IDE menu with all IDEs visible
                self.app.ide_selection_menu.remove()
                from ..widgets.ide_selection_menu import IDESelectionMenu
                self.app.ide_selection_menu = IDESelectionMenu(show_all_ides=True)
                await self.app.mount(self.app.ide_selection_menu)
                
                # Show the expanded menu
                self.show_ide_selection_menu()
                return
            
            # Regular IDE selection handling
            self.setup_data['selected_editor'] = editor_name
            self.chat_area.add_message(f"✅ AI IDE selected: **{editor_name}**\n", is_user=False)
            
            # Save editor selection to .juno_config.json for future detection
            try:
                from ..setup.setup_verification_service import SetupVerificationService
                project_name = Path(self.config_manager.workdir).name
                verifier = SetupVerificationService(
                    project_root=Path(self.config_manager.workdir), 
                    project_name=project_name
                )
                if verifier.save_editor_selection(editor_name):
                    debug_logger.log_event("editor_selection_saved", editor=editor_name)
                else:
                    debug_logger.log_event("editor_selection_save_failed", editor=editor_name)
            except Exception as e:
                debug_logger.log_event("editor_selection_save_error", editor=editor_name, error=str(e))
            
            # Save to config
            config = self.config_manager.load_config()
            config.editor = editor_name
            self.config_manager.save_config(config)
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"❌ Error saving editor selection: {e}\n", is_user=False)
            # Continue with setup anyway
            self.setup_step += 1
            await self.start_enhanced_setup_step()
    
    async def perform_api_key_setup(self, progress_msg: str) -> None:
        """Handle API key setup for VibeContext enhancement."""
        try:
            # Check if API key is already available
            if hasattr(self, 'mcp_installer_enhanced') and self.mcp_installer_enhanced.should_install_mcp():
                api_key_status = self.mcp_installer_enhanced.get_api_key_status()
                source = api_key_status.get('api_key_source', 'Unknown')
                self.chat_area.add_message(
                    f"{progress_msg} **🔐 API Key Setup**\n\n"
                    f"✅ ASKBUDI API Key found ({source})!\n\n"
                    f"VibeContext enhanced features will be available.\n",
                    is_user=False
                )
                self.setup_data['has_api_key'] = True
                self.setup_data['api_key_source'] = source
            else:
                # Show value proposition and prompt for API key
                from ..setup.api_key_manager import APIKeyManager
                api_key_manager = APIKeyManager(project_dir=Path(self.config_manager.workdir))
                
                value_prop = api_key_manager.get_value_proposition_message()
                
                self.chat_area.add_message(
                    f"{progress_msg} **🔐 API Key Setup**\n\n"
                    f"{value_prop}\n\n"
                    f"**Options:**\n"
                    f"1. Enter 'key:<your_api_key>' to configure your API key\n"
                    f"2. Enter 'skip' to continue with basic features\n"
                    f"3. Enter 'learn' for more information\n\n"
                    f"*You can get a free API key at https://askbudi.com/signup*",
                    is_user=False
                )
                
                self.setup_data['has_api_key'] = False
                self.setup_data['api_key_prompt_shown'] = True
                return  # Wait for user input
                
        except Exception as e:
            self.chat_area.add_message(f"⚠️ Error during API key setup: {e}\n\nContinuing with basic features...", is_user=False)
            self.setup_data['has_api_key'] = False
        
        # Move to next step
        self.setup_step += 1
        await self.start_enhanced_setup_step()
    
    async def perform_ai_project_analysis(self) -> None:
        """Perform comprehensive AI-powered project analysis using TinyAgent with setup system prompt."""
        try:
            if not self.app.tiny_code_agent:
                self.chat_area.add_message("---\n\n**TinyAgent Unavailable**\n\nUsing basic dependency detection...\n\n---", is_user=False)
                await self.perform_dependency_detection()
                return
            
            # Note: We include setup instructions directly in the analysis request
            # so we don't need to load a separate system prompt
                
            # Create AI analysis message with context
            project_path = str(self.config_manager.workdir)
            project_description = self.setup_data.get('project_description', 'No description provided')
            selected_editor = self.setup_data.get('selected_editor', 'Unknown')
            
            # Create comprehensive analysis request that includes the setup instructions
            analysis_request = f"""You are now acting as an intelligent project setup assistant for juno-cli. Please perform a comprehensive setup analysis for this project using the following guidelines:

**Project Context:**
- Project Path: {project_path}
- Project Description: {project_description}  
- Selected Editor: {selected_editor}
- Platform: {platform.system()} ({platform.machine()})
- Date: {datetime.now().strftime('%Y-%m-%d')}

**Your Task:**
Please execute a comprehensive 8-step project analysis:

### Step 1: Project Analysis & IDE Detection
- Scan for existing IDE configuration files (CLAUDE.md, .cursor/, WINDSURF.md, etc.)
- Read and analyze existing configurations
- Identify project type, frameworks, and architecture
- Create comprehensive project summary

### Step 2: Dependency Extraction & Analysis  
- Scan package files systematically (requirements.txt, package.json, go.mod, Cargo.toml, etc.)
- Extract dependency names and version constraints
- Identify major versions (e.g., "fastapi>=0.68.0" → "fastapi v0.x")
- Prioritize core/framework dependencies over utilities

### Step 3-8: Planning Analysis
- Plan MCP server configuration
- Plan external documentation setup
- Plan IDE configuration enhancement  
- Plan JUNO.md creation
- Plan Claude permissions (if applicable)
- Provide validation summary

**Focus Areas:**
- Analyzing the project structure and identifying frameworks/patterns
- Extracting dependencies and their versions accurately
- Creating a comprehensive project analysis for IDE configuration files
- Understanding project architecture and development patterns

**Tools Available:**
You have access to file operations, shell commands, and project analysis tools. Please use them to thoroughly analyze this project.

Please provide detailed results for each step, focusing especially on dependency extraction and project structure analysis."""
            
            # Use the TinyCodeAgentChat interface to process the analysis request
            ai_response = await self.app.tiny_code_agent.process_chat_message(analysis_request)
            
            # Store the analysis result
            self.setup_data['ai_analysis_result'] = ai_response
            
            # Extract dependency information if available
            detected_deps = self.extract_dependencies_from_ai_response(ai_response)
            self.setup_data['detected_dependencies'] = detected_deps
            
            # Show consolidated results
            self.chat_area.add_message(f"---\n\n**AI Project Analysis Complete**\n\n**Project Type**: {detected_deps.get('project_type', 'Unknown')}\n**Dependencies**: {len(detected_deps.get('dependencies', []))}\n**Language**: {detected_deps.get('language', 'Unknown')}\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**AI Project Analysis Failed**\n\nError: {e}\n\nUsing basic dependency detection...\n\n---", is_user=False)
            await self.perform_dependency_detection()

    async def perform_dependency_detection(self) -> None:
        """Perform dependency detection using DependencyScanner (fallback method)."""
        try:
            # Scan for dependencies
            scan_result = self.dependency_scanner.scan_project_dependencies()
            self.setup_data['detected_dependencies'] = scan_result
            
            # Show consolidated results
            if scan_result['dependencies']:
                summary = self.dependency_scanner.get_dependency_summary()
                self.chat_area.add_message(f"---\n\n**Dependency Detection Complete**\n\n{summary}\n\n---", is_user=False)
            else:
                self.chat_area.add_message("---\n\n**Dependency Detection Complete**\n\nNo dependencies found.\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**Dependency Detection Failed**\n\nError: {e}\n\n---", is_user=False)
            self.setup_data['detected_dependencies'] = {'dependencies': [], 'language': 'Unknown', 'package_files': []}
            self.setup_step += 1
            await self.start_enhanced_setup_step()
    
    async def perform_mcp_installation(self) -> None:
        """Perform MCP server installation."""
        try:
            selected_editor = self.setup_data.get('selected_editor', 'Claude Code')
            
            # Map editor names to identifiers
            editor_mapping = {
                'Claude Code': 'claude_code',
                'Cursor': 'cursor', 
                'Windsurf': 'windsurf',
                'VS Code': 'vscode',
                'VSCode': 'vscode'
            }
            
            editor_id = editor_mapping.get(selected_editor, 'claude_code')
            
            # Get API key if available
            api_key = ""
            if self.config_manager.has_api_key():
                try:
                    api_key = self.config_manager.get_api_key()
                except:
                    api_key = ""
            
            if not api_key:
                # Try to use the global function instead
                from ..setup import install_vibe_context_for_editor
                success = install_vibe_context_for_editor(editor_id, Path(self.config_manager.workdir), "")
            else:
                # Install VibeContext MCP server for the selected editor
                success = self.mcp_installer_enhanced.install_mcp_servers(editor_id, Path(self.config_manager.workdir), api_key)
            
            if success:
                self.setup_data['installed_mcp_servers'].append('vibe_context')
                self.chat_area.add_message(f"---\n\n**MCP Installation Complete**\n\nVibeContext MCP server configured for {selected_editor}.\n\n---", is_user=False)
            else:
                self.chat_area.add_message(f"---\n\n**MCP Installation Issues**\n\nVibeContext MCP server setup encountered problems for {selected_editor}.\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.setup_data['installed_mcp_servers'] = []
            self.chat_area.add_message(f"---\n\n**MCP Installation Failed**\n\nError: {e}\n\nSetup will continue, but MCP functionality may not be available.\n\n---", is_user=False)
            self.setup_step += 1
            await self.start_enhanced_setup_step()
    
    async def perform_docs_fetching(self) -> None:
        """Perform dependency documentation fetching using AgenticDependencyResolver."""
        try:
            detected_deps = self.setup_data.get('detected_dependencies', {})
            dependencies = detected_deps.get('dependencies', [])
            language = detected_deps.get('language', 'Unknown')
            
            if dependencies and language != 'Unknown':
                # Use AgenticDependencyResolver for documentation fetching
                from ...agentic_dependency_resolver import AgenticDependencyResolver
                
                resolver = AgenticDependencyResolver(
                    project_path=str(self.config_manager.workdir),
                    config_manager=self.config_manager,
                    ui_callback=self.dependency_progress_callback,
                    storage_manager=self.storage_manager
                )
                
                # Convert dependencies to names list for docs_only mode
                dependency_names = [dep['name'] if isinstance(dep, dict) else dep for dep in dependencies]
                
                self.chat_area.add_message(f"🔄 Using AgenticDependencyResolver to fetch documentation for {len(dependency_names)} dependencies...\n", is_user=False)
                
                # Fetch documentation using the agentic resolver
                docs_result = await resolver.run(docs_only=dependency_names)
                
                # Convert result format to match existing setup data structure
                if docs_result.get('success'):
                    documentation_fetched = docs_result.get('documentation_fetched', {})
                    saved_files = documentation_fetched.get('saved_files', [])
                    failed_saves = documentation_fetched.get('failed_saves', [])
                    
                    fetched_docs = {
                        'docs': {},
                        'successful': [file_info['name'] for file_info in saved_files],
                        'failed': [fail_info['name'] for fail_info in failed_saves]
                    }
                    
                    # Add documentation content if available
                    for file_info in saved_files:
                        dep_name = file_info['name']
                        fetched_docs['docs'][dep_name] = {
                            'sections': {'overview': f'Documentation fetched for {dep_name}'},
                            'metadata': {
                                'fetched_via': 'AgenticDependencyResolver',
                                'file_path': file_info['path'],
                                'file_size': file_info['size']
                            }
                        }
                    
                    self.setup_data['fetched_docs'] = fetched_docs
                    
                    success_count = len(fetched_docs['successful'])
                    failed_count = len(fetched_docs['failed'])
                    
                    # Create summary message
                    summary = f"**AgenticDependencyResolver Results:**\n"
                    summary += f"- Successfully fetched: {success_count} dependencies\n"
                    summary += f"- Failed to fetch: {failed_count} dependencies\n"
                    
                    if fetched_docs['successful']:
                        summary += f"\n**Successful:**\n"
                        for dep in fetched_docs['successful'][:5]:  # Show first 5
                            summary += f"✅ {dep}\n"
                        if success_count > 5:
                            summary += f"... and {success_count - 5} more\n"
                    
                    if fetched_docs['failed']:
                        summary += f"\n**Failed:**\n"
                        for dep in fetched_docs['failed'][:3]:  # Show first 3 failures
                            summary += f"❌ {dep}\n"
                        if failed_count > 3:
                            summary += f"... and {failed_count - 3} more\n"
                    
                    self.chat_area.add_message(f"---\n\n**Documentation Fetching Complete**\n\n{summary}\n\n---", is_user=False)
                else:
                    # Handle failure case
                    error_msg = docs_result.get('error', 'Unknown error occurred')
                    self.setup_data['fetched_docs'] = {'docs': {}, 'successful': [], 'failed': dependency_names}
                    self.chat_area.add_message(f"---\n\n**Documentation Fetching Failed**\n\nAgenticDependencyResolver error: {error_msg}\n\n---", is_user=False)
            else:
                self.setup_data['fetched_docs'] = {'docs': {}, 'successful': [], 'failed': []}
                self.chat_area.add_message("---\n\n**Documentation Fetching Complete**\n\nNo dependencies found to fetch documentation for.\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**Documentation Fetching Failed**\n\nAgenticDependencyResolver error: {e}\n\n---", is_user=False)
            self.setup_data['fetched_docs'] = {'docs': {}, 'successful': [], 'failed': []}
            self.setup_step += 1
            await self.start_enhanced_setup_step()
    
    async def perform_external_context_setup(self) -> None:
        """Perform external context setup."""
        try:
            # Initialize external context structure
            success = self.external_context_manager.initialize_context_structure()
            
            if success:
                # Add fetched documentation to external context
                fetched_docs = self.setup_data.get('fetched_docs', {}).get('docs', {})
                docs_added = 0
                
                for dep_name, doc_data in fetched_docs.items():
                    if doc_data and doc_data.get('sections'):
                        # Add overview documentation
                        overview = doc_data['sections'].get('overview', f'Documentation for {dep_name}')
                        if self.external_context_manager.add_dependency_documentation(dep_name, overview, 'general'):
                            docs_added += 1
                
                # Add project description if available
                project_desc = self.setup_data.get('project_description')
                if project_desc:
                    self.external_context_manager.add_project_documentation(
                        'project_description', 
                        f"# Project Description\n\n{project_desc}",
                        'md'
                    )
                
                self.setup_data['external_context_setup'] = True
                
                self.chat_area.add_message(f"---\n\n**External Context Setup Complete**\n\n**Documentation**: {docs_added} dependency docs added\n**Location**: `external_context/`\n\n---", is_user=False)
            else:
                self.chat_area.add_message("---\n\n**External Context Setup Issues**\n\nBasic structure created with limited content.\n\n---", is_user=False)
                self.setup_data['external_context_setup'] = False
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**External Context Setup Failed**\n\nError: {e}\n\n---", is_user=False)
            self.setup_data['external_context_setup'] = False
            self.setup_step += 1
            await self.start_enhanced_setup_step()
    
    async def perform_permissions_configuration(self) -> None:
        """Perform Claude permissions configuration."""
        try:
            # Setup Claude permissions for external context
            success = self.claude_permissions_service.setup_claude_permissions(Path(self.config_manager.workdir))
            
            if success:
                self.setup_data['permissions_configured'] = True
                self.chat_area.add_message("---\n\n**Claude Permissions Configured**\n\nClaude Code access configured for external_context directory.\n\n---", is_user=False)
            else:
                self.setup_data['permissions_configured'] = False
                self.chat_area.add_message("---\n\n**Claude Permissions Setup Issues**\n\nCheck `.claude/settings.json` for manual configuration.\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**Claude Permissions Setup Failed**\n\nError: {e}\n\n---", is_user=False)
            self.setup_data['permissions_configured'] = False
            self.setup_step += 1
            await self.start_enhanced_setup_step()
    
    async def perform_ide_config_creation(self) -> None:
        """Create comprehensive IDE configuration files including JUNO.md."""
        try:
            selected_editor = self.setup_data.get('selected_editor', 'Unknown')
            ai_analysis = self.setup_data.get('ai_analysis_result', '')
            detected_deps = self.setup_data.get('detected_dependencies', {})
            fetched_docs = self.setup_data.get('fetched_docs', {})
            
            # Create JUNO.md - comprehensive guide for all AI assistants
            juno_md_path = Path(self.config_manager.workdir) / "JUNO.md"
            juno_content = self.generate_juno_md_content(ai_analysis, detected_deps, fetched_docs)
            
            with open(juno_md_path, 'w', encoding='utf-8') as f:
                f.write(juno_content)
            
            configs_created = ["JUNO.md"]
            
            # Update/create IDE-specific configuration file
            ide_config_created = False
            if selected_editor.lower() in ['claude_code', 'claude code']:
                # Claude Code gets its own specific CLAUDE.md file
                ide_config_created = await self.update_claude_md(ai_analysis, detected_deps, fetched_docs)
                if ide_config_created:
                    configs_created.append("CLAUDE.md")
            elif selected_editor.lower() == 'windsurf':
                # Windsurf gets its own specific WINDSURF.md file
                ide_config_created = await self.update_windsurf_md(ai_analysis, detected_deps, fetched_docs)
                if ide_config_created:
                    configs_created.append("WINDSURF.md")
            else:
                # All other IDEs (including Cursor) use AGENTS.md as default
                ide_config_created = await self.update_agents_md(selected_editor, ai_analysis, detected_deps, fetched_docs)
                if ide_config_created:
                    configs_created.append("AGENTS.md")
            
            self.setup_data['ide_configs_created'] = True
            
            # Show consolidated results
            configs_list = ", ".join(configs_created)
            self.chat_area.add_message(f"---\n\n**IDE Configuration Files Created**\n\n**Files**: {configs_list}\n**Editor**: {selected_editor}\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**IDE Configuration Creation Failed**\n\nError: {e}\n\n---", is_user=False)
            self.setup_data['ide_configs_created'] = False
            self.setup_step += 1
            await self.start_enhanced_setup_step()
    
    async def perform_setup_verification(self) -> None:
        """Run comprehensive setup verification using dedicated verification agent."""
        try:
            from ..setup.setup_verification_service import SetupVerificationService
            import os
            
            # Get project information
            project_root = str(Path(self.config_manager.workdir).resolve())
            project_name = Path(project_root).name
            
            # Initialize verification service
            verification_service = SetupVerificationService(project_root, project_name)
            
            # Run verification
            verification_results = verification_service.verify_all_components()
            
            # Generate report using the verification agent
            report = verification_service.generate_summary_report(verification_results)
            
            # Also run AI verification agent for additional analysis
            ai_verification_report = await self.run_ai_verification_agent(project_root, project_name, verification_results)
            
            # Store results
            self.setup_data['verification_results'] = verification_results
            self.setup_data['verification_report'] = report
            self.setup_data['ai_verification'] = ai_verification_report
            
            # Count status
            status_counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
            for result in verification_results:
                status_counts[result.status] += 1
            
            # Determine overall status
            if status_counts["FAIL"] == 0:
                if status_counts["WARN"] == 0:
                    overall_status = "🎉 EXCELLENT"
                    status_msg = "All components passed verification!"
                else:
                    overall_status = "✅ GOOD"
                    status_msg = f"Functional with {status_counts['WARN']} warnings"
            elif status_counts["FAIL"] <= 2:
                overall_status = "⚠️ NEEDS ATTENTION"
                status_msg = f"{status_counts['FAIL']} failures need resolution"
            else:
                overall_status = "❌ CRITICAL ISSUES"
                status_msg = f"{status_counts['FAIL']} critical failures found"
            
            # Show verification summary
            summary_message = f"""---

**Setup Verification Complete**

**Overall Status**: {overall_status}
**Message**: {status_msg}

**Component Summary**:
- ✅ Passed: {status_counts["PASS"]}
- ❌ Failed: {status_counts["FAIL"]}
- ⚠️ Warnings: {status_counts["WARN"]}
- ℹ️ Info: {status_counts["INFO"]}

**Success Rate**: {(status_counts["PASS"] / len(verification_results) * 100):.1f}%

---"""
            
            self.chat_area.add_message(summary_message, is_user=False)
            
            # Show detailed errors and warnings if they exist
            await self.display_detailed_verification_results(verification_results, status_counts)
            
            # Show AI verification insights if available
            if ai_verification_report:
                self.chat_area.add_message("**🤖 AI Verification Analysis**\n\n" + ai_verification_report, is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self.start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**Setup Verification Failed**\n\nError: {e}\n\nProceeding to completion...\n\n---", is_user=False)
            self.setup_data['verification_failed'] = True
            self.setup_step += 1
            await self.start_enhanced_setup_step()
    
    async def display_detailed_verification_results(self, verification_results, status_counts) -> None:
        """Display detailed breakdown of errors and warnings with actionable recommendations."""
        
        # Show critical failures first
        failed_results = [r for r in verification_results if r.status == "FAIL"]
        if failed_results:
            fail_details = "**❌ CRITICAL FAILURES** *(Must be fixed)*\n\n"
            
            for i, result in enumerate(failed_results, 1):
                fail_details += f"**{i}. {result.component}**\n"
                fail_details += f"   • **Issue**: {result.message}\n"
                
                # Add details if available
                if result.details:
                    detail_items = []
                    for key, value in result.details.items():
                        if isinstance(value, list):
                            detail_items.append(f"{key}: {', '.join(map(str, value))}")
                        else:
                            detail_items.append(f"{key}: {value}")
                    if detail_items:
                        fail_details += f"   • **Details**: {'; '.join(detail_items)}\n"
                
                # Add recommendations
                if result.recommendations:
                    fail_details += "   • **Fix Actions**:\n"
                    for rec in result.recommendations:
                        fail_details += f"     - {rec}\n"
                
                fail_details += "\n"
            
            self.chat_area.add_message(fail_details.rstrip(), is_user=False)
        
        # Show warnings next
        warn_results = [r for r in verification_results if r.status == "WARN"]
        if warn_results:
            warn_details = "**⚠️ WARNINGS** *(Should be addressed)*\n\n"
            
            for i, result in enumerate(warn_results, 1):
                warn_details += f"**{i}. {result.component}**\n"
                warn_details += f"   • **Issue**: {result.message}\n"
                
                # Add details if available
                if result.details:
                    detail_items = []
                    for key, value in result.details.items():
                        if isinstance(value, list):
                            detail_items.append(f"{key}: {', '.join(map(str, value))}")
                        else:
                            detail_items.append(f"{key}: {value}")
                    if detail_items:
                        warn_details += f"   • **Details**: {'; '.join(detail_items)}\n"
                
                # Add recommendations
                if result.recommendations:
                    warn_details += "   • **Improvement Actions**:\n"
                    for rec in result.recommendations:
                        warn_details += f"     - {rec}\n"
                
                warn_details += "\n"
            
            self.chat_area.add_message(warn_details.rstrip(), is_user=False)
        
        # Show successful components summary if there are failures/warnings
        if status_counts["FAIL"] > 0 or status_counts["WARN"] > 0:
            passed_results = [r for r in verification_results if r.status == "PASS"]
            if passed_results:
                success_details = f"**✅ WORKING COMPONENTS** *({len(passed_results)} components)*\n\n"
                
                component_names = [result.component for result in passed_results]
                # Group by similar names to make it more readable
                success_details += "✓ " + "\n✓ ".join(component_names)
                success_details += "\n"
                
                self.chat_area.add_message(success_details, is_user=False)
        
        # Show actionable next steps
        if status_counts["FAIL"] > 0 or status_counts["WARN"] > 0:
            next_steps = "**🎯 RECOMMENDED NEXT STEPS**\n\n"
            
            if status_counts["FAIL"] > 0:
                next_steps += "**Priority 1: Address Critical Failures**\n"
                next_steps += "• Fix the failures listed above - these will prevent proper functionality\n"
                next_steps += "• Re-run the setup wizard for failed components if needed\n"
                next_steps += "• Test each fix by running verification again\n\n"
            
            if status_counts["WARN"] > 0:
                priority = "Priority 2" if status_counts["FAIL"] > 0 else "Priority 1"
                next_steps += f"**{priority}: Resolve Warnings**\n"
                next_steps += "• Address warnings to improve setup quality and prevent future issues\n"
                next_steps += "• These won't block functionality but may cause problems later\n\n"
            
            next_steps += "**Final Step: Re-run Verification**\n"
            next_steps += "• After making changes, run setup verification again to confirm fixes\n"
            next_steps += "• Use command: `py-wizard setup --verify-only` (if available)\n"
            
            self.chat_area.add_message(next_steps, is_user=False)
        else:
            # Everything passed - show success message
            success_msg = "**🎉 PERFECT SETUP!**\n\n"
            success_msg += "All components verified successfully. Your development environment is ready:\n\n"
            success_msg += "• **MCP Server**: Configured and accessible\n"
            success_msg += "• **External Context**: Documentation properly organized\n"
            success_msg += "• **IDE Configuration**: Files created and populated\n"
            success_msg += "• **Dependencies**: All requirements documented\n\n"
            success_msg += "**You can now start using your AI-powered development environment!**"
            
            self.chat_area.add_message(success_msg, is_user=False)

    async def run_ai_verification_agent(self, project_root: str, project_name: str, verification_results) -> str:
        """Run AI verification agent with dedicated system prompt."""
        try:
            # Load verification system prompt
            verification_prompt = self.load_verification_system_prompt()
            
            if not verification_prompt:
                return "AI verification unavailable (prompt not found)"
            
            # Prepare context for AI agent
            context = f"""Project Root: {project_root}
Project Name: {project_name}

Verification Results Summary:
"""
            
            for result in verification_results:
                context += f"\n- {result.status}: {result.component} - {result.message}"
                if result.details:
                    context += f"\n  Details: {result.details}"
                if result.recommendations:
                    context += f"\n  Recommendations: {', '.join(result.recommendations)}"
            
            # Create a mini verification session with TinyAgent
            user_prompt = f"""Please verify the setup completion for this project. Focus on:

1. Analyzing the verification results provided
2. Testing any additional aspects that automated checks might miss
3. Providing honest assessment of setup quality
4. Recommending next steps

Context:
{context}"""

            # Use TinyAgent with verification prompt
            # Create a temporary config manager for verification
            from ...config import ConfigManager
            temp_config = ConfigManager(project_root)
            
            # Create temporary storage manager with verification session ID
            temp_storage_manager = None
            if self.storage_manager:
                try:
                    # Create a new storage manager instance with verification-specific session ID
                    from ...storage_manager_async import AsyncConversationStorageManager
                    temp_storage_manager = AsyncConversationStorageManager()
                    temp_storage_manager.storage = self.storage_manager.storage  # Reuse same storage
                    temp_storage_manager.user_id = self.storage_manager.user_id  # Same user_id
                    temp_storage_manager.current_session_id = f"{self.storage_manager.current_session_id}_setup_verify"
                    print(f"[DEBUG] run_ai_verification_agent: Created temp storage with session_id: {temp_storage_manager.current_session_id}")
                except Exception as e:
                    print(f"[DEBUG] run_ai_verification_agent: Failed to create temp storage manager: {e}")
                    temp_storage_manager = None
            
            tiny_agent = TinyCodeAgentChat(
                config_manager=temp_config,
                debug=False,
                storage_manager=temp_storage_manager,  # Pass storage manager for proper persistence
                enable_custom_instructions=False  # Disable custom instructions for setup agents
            )
            
            # Set the system prompt manually
            if hasattr(tiny_agent, 'agent') and hasattr(tiny_agent.agent, 'system_prompt'):
                tiny_agent.agent.system_prompt = verification_prompt
            
            # Run verification analysis
            response = await tiny_agent.process_chat_message(user_prompt)
            
            return response
            
        except Exception as e:
            return f"AI verification error: {str(e)}"
    
    def load_verification_system_prompt(self) -> str:
        """Load the verification system prompt from prompt_garden.yaml."""
        try:
            import yaml
            
            # Path to prompt_garden.yaml
            prompt_file = Path(__file__).parent.parent.parent / "prompts" / "prompt_garden.yaml"
            
            if not prompt_file.exists():
                return ""
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts_data = yaml.safe_load(f)
            
            verification_prompt_data = prompts_data.get('prompts', {}).get('setup_verification', {})
            verification_prompt = verification_prompt_data.get('prompt', '')
            
            # Substitute system variables
            substitutions = {
                'PLATFORM': platform.system(),
                'ARCHITECTURE': platform.machine(),
                'CURRENT_DATE': datetime.now().strftime('%Y-%m-%d'),
                'WORKING_DIRECTORY': self.config_manager.workdir,
                'USER_ID': self._get_user_id(),
                'SESSION_ID': self._get_session_id()
            }
            
            for key, value in substitutions.items():
                verification_prompt = verification_prompt.replace(f'${{{key}}}', str(value))
            
            return verification_prompt
            
        except Exception as e:
            print(f"Error loading verification prompt: {e}")
            return ""

    def load_setup_system_prompt(self) -> str:
        """Load the setup system prompt from prompt_garden.yaml."""
        try:
            import yaml
            
            # Path to prompt_garden.yaml
            prompt_file = Path(__file__).parent.parent.parent / "prompts" / "prompt_garden.yaml"
            
            if not prompt_file.exists():
                return ""
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts_data = yaml.safe_load(f)
            
            setup_prompt_data = prompts_data.get('prompts', {}).get('setup_command', {})
            setup_prompt = setup_prompt_data.get('prompt', '')
            
            # Substitute system variables
            substitutions = {
                'PLATFORM': platform.system(),
                'ARCHITECTURE': platform.machine(),
                'CURRENT_DATE': datetime.now().strftime('%Y-%m-%d'),
                'WORKING_DIRECTORY': str(self.config_manager.workdir),
                'USER_ID': self._get_user_id(),
                'SESSION_ID': self._get_session_id()
            }
            
            for key, value in substitutions.items():
                setup_prompt = setup_prompt.replace(f'${{{key}}}', str(value))
            
            return setup_prompt
            
        except Exception as e:
            print(f"Failed to load setup system prompt: {e}")
            return ""
    
    def _get_user_id(self) -> str:
        """Generate or retrieve user ID for debugging purposes."""
        try:
            # Try to get user from system
            import os
            username = os.getenv('USER', os.getenv('USERNAME', 'unknown_user'))
            return f"{username}_{hash(str(self.config_manager.workdir)) % 10000:04d}"
        except Exception:
            return "unknown_user"
    
    def _get_session_id(self) -> str:
        """Generate session ID for this setup session."""
        try:
            import uuid
            # Generate a short session ID based on timestamp and random component
            session_time = int(time.time())
            session_rand = str(uuid.uuid4())[:8]
            return f"{session_time}_{session_rand}"
        except Exception:
            return f"session_{int(time.time())}"
    
    def extract_dependencies_from_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Extract dependency information from AI analysis response."""
        try:
            # This is a simple extraction - in practice, you might want more sophisticated parsing
            dependencies = []
            language = "Unknown"
            project_type = "Unknown"
            package_files = []
            
            # Look for common patterns in the AI response
            response_lower = ai_response.lower()
            
            # Extract language
            if 'python' in response_lower:
                language = "python"
            elif 'javascript' in response_lower or 'node.js' in response_lower:
                language = "javascript"
            elif 'typescript' in response_lower:
                language = "typescript"
            elif 'go' in response_lower and 'golang' in response_lower:
                language = "go"
            elif 'rust' in response_lower:
                language = "rust"
            elif 'java' in response_lower:
                language = "java"
            
            # Extract project type
            if 'fastapi' in response_lower or 'flask' in response_lower or 'django' in response_lower:
                project_type = "Python Web API"
            elif 'react' in response_lower:
                project_type = "React Application"
            elif 'express' in response_lower:
                project_type = "Node.js API"
            elif 'cli' in response_lower or 'command' in response_lower:
                project_type = "CLI Application"
            elif 'web' in response_lower:
                project_type = "Web Application"
            
            # Try to use actual dependency scanner as fallback
            if hasattr(self, 'dependency_scanner'):
                scanner_result = self.dependency_scanner.scan_project_dependencies()
                if scanner_result.get('dependencies'):
                    dependencies = scanner_result['dependencies']
                    if scanner_result.get('language') != 'Unknown':
                        language = scanner_result['language']
                    package_files = scanner_result.get('package_files', [])
            
            return {
                'dependencies': dependencies,
                'language': language,
                'project_type': project_type,
                'package_files': package_files,
                'ai_analysis_available': True
            }
            
        except Exception as e:
            print(f"Failed to extract dependencies from AI response: {e}")
            # Return empty structure
            return {
                'dependencies': [],
                'language': 'Unknown',
                'project_type': 'Unknown',
                'package_files': [],
                'ai_analysis_available': False
            }
    
    def generate_juno_md_content(self, ai_analysis: str, detected_deps: Dict, fetched_docs: Dict) -> str:
        """Generate comprehensive JUNO.md content."""
        project_name = Path(self.config_manager.workdir).name
        project_desc = self.setup_data.get('project_description', 'No description provided')
        selected_editor = self.setup_data.get('selected_editor', 'Unknown')
        
        content = f"""# JUNO Development Guide - {project_name}

## Project Overview
This is a comprehensive development guide generated by juno-agent to help AI assistants understand and work effectively with this project.

### Basic Information
- **Project Path**: `{self.config_manager.workdir}`
- **Project Type**: {detected_deps.get('project_type', 'Unknown')}
- **Primary Language**: {detected_deps.get('language', 'Unknown')}
- **Setup Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Platform**: {platform.system()} ({platform.machine()})
- **Selected AI IDE**: {selected_editor}

### Project Description
{project_desc}

## Architecture & Dependencies

### Detected Dependencies
"""
        
        dependencies = detected_deps.get('dependencies', [])
        if dependencies:
            content += "The following dependencies were detected in this project:\n\n"
            for dep in dependencies[:15]:  # Limit to first 15
                content += f"- `{dep}`\n"
            if len(dependencies) > 15:
                content += f"- ... and {len(dependencies) - 15} more dependencies\n"
        else:
            content += "No dependencies were automatically detected.\n"
        
        content += f"""
### Package Files
"""
        
        package_files = detected_deps.get('package_files', [])
        if package_files:
            for pfile in package_files:
                content += f"- `{pfile}`\n"
        else:
            content += "- No package files detected\n"
        
        content += """
## AI Analysis Results

"""
        
        if ai_analysis and detected_deps.get('ai_analysis_available'):
            # Include a summary of the AI analysis (truncated for readability)
            analysis_summary = ai_analysis[:1000] + "..." if len(ai_analysis) > 1000 else ai_analysis
            content += f"The following insights were generated by AI analysis:\n\n```\n{analysis_summary}\n```\n\n"
        else:
            content += "AI analysis was not available during setup.\n\n"
        
        content += """## External Documentation Context

The `external_context/` directory contains up-to-date documentation for project dependencies:

"""
        
        # Add external documentation information
        saved_files = fetched_docs.get('saved_files', [])
        if saved_files:
            for file_info in saved_files:
                dep_name = file_info.get('dependency', 'unknown')
                filename = file_info.get('filename', f"{dep_name}.md")
                content += f"- **{dep_name}**: `external_context/{filename}`\n"
        else:
            content += "- No external documentation was fetched during setup\n"
        
        content += f"""

## Development Workflows

### Recommended Development Process
1. **Analysis First**: Use AI tools to understand code structure before making changes
2. **Reference Documentation**: Check external_context/ for dependency docs
3. **Test-Driven Development**: Write tests before implementing features
4. **AI-Assisted Development**: Leverage {selected_editor} for intelligent code assistance

### AI Assistant Integration
- **Primary IDE**: {selected_editor} configured for this project
- **MCP Tools Available**: VibeContext server with documentation access
- **Preferred Documentation**: Use external_context/ over general knowledge
- **Project Context**: This JUNO.md file provides comprehensive project context

## Best Practices

### Code Development
- Follow {detected_deps.get('language', 'language')}-specific conventions
- Use dependency documentation from external_context/
- Leverage AI IDE features for code completion and analysis
- Test changes thoroughly before committing

### AI Collaboration
- Provide context about your specific task when asking for help
- Reference relevant documentation from external_context/
- Use project-specific terminology and patterns
- Validate AI-generated code against project requirements

## Troubleshooting & Maintenance

### Common Issues
1. **Dependencies**: Check package files and external_context/ for version info
2. **AI IDE Issues**: Verify MCP server configuration and API keys
3. **Documentation**: Re-run juno-agent setup to refresh external context

### Maintenance Tasks
- Update external documentation regularly with `/setup`
- Review and update this JUNO.md when project structure changes
- Keep AI IDE configurations synchronized across team members

---
*This guide was generated by juno-agent v1.0.0 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*For updates, run `juno setup` or `juno-agent setup` in this directory*
"""
        
        return content
    
    async def update_claude_md(self, ai_analysis: str, detected_deps: Dict, fetched_docs: Dict) -> bool:
        """Update CLAUDE.md with project-specific information."""
        try:
            claude_md_path = Path(self.config_manager.workdir) / "CLAUDE.md"
            
            # Read existing CLAUDE.md if it exists
            existing_content = ""
            if claude_md_path.exists():
                with open(claude_md_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Generate enhanced content
            enhanced_content = self.generate_ide_config_content("Claude Code", ai_analysis, detected_deps, fetched_docs)
            
            # If existing content exists, try to merge intelligently
            if existing_content and "## Project Information" not in existing_content:
                # Prepend project information to existing content
                final_content = enhanced_content + "\n\n" + existing_content
            else:
                final_content = enhanced_content
            
            # Write the enhanced file
            with open(claude_md_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            return True
            
        except Exception as e:
            print(f"Failed to update CLAUDE.md: {e}")
            return False
    
    async def update_agents_md(self, selected_editor: str, ai_analysis: str, detected_deps: Dict, fetched_docs: Dict) -> bool:
        """Update AGENTS.md with project-specific information for the selected IDE."""
        try:
            agents_md_path = Path(self.config_manager.workdir) / "AGENTS.md"
            
            # Read existing AGENTS.md if it exists
            existing_content = ""
            if agents_md_path.exists():
                with open(agents_md_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Generate enhanced content for the IDE
            enhanced_content = self.generate_ide_config_content(selected_editor, ai_analysis, detected_deps, fetched_docs)
            
            # If existing content exists and doesn't contain our project section, merge intelligently
            if existing_content and "## Project Information" not in existing_content:
                # Prepend project information to existing content
                final_content = enhanced_content + "\n\n---\n\n" + existing_content
            else:
                final_content = enhanced_content
            
            # Write the enhanced file
            with open(agents_md_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            return True
            
        except Exception as e:
            print(f"Failed to update AGENTS.md: {e}")
            return False
    
    async def update_windsurf_md(self, ai_analysis: str, detected_deps: Dict, fetched_docs: Dict) -> bool:
        """Update WINDSURF.md with project-specific information."""
        try:
            windsurf_md_path = Path(self.config_manager.workdir) / "WINDSURF.md"
            enhanced_content = self.generate_ide_config_content("Windsurf", ai_analysis, detected_deps, fetched_docs)
            
            with open(windsurf_md_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            return True
            
        except Exception as e:
            print(f"Failed to update WINDSURF.md: {e}")
            return False
    
    def generate_ide_config_content(self, ide_name: str, ai_analysis: str, detected_deps: Dict, fetched_docs: Dict) -> str:
        """Generate IDE-specific configuration file content."""
        project_name = Path(self.config_manager.workdir).name
        project_desc = self.setup_data.get('project_description', 'No description provided')
        
        content = f"""# {ide_name} Configuration for {project_name}

## Project Information
- **Project Type**: {detected_deps.get('project_type', 'Unknown')}
- **Primary Language**: {detected_deps.get('language', 'Unknown')}
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Project Description
{project_desc}

## Architecture & Dependencies
"""
        
        if ai_analysis and len(ai_analysis) > 100:
            # Include key insights from AI analysis
            content += "### AI Analysis Insights\n"
            content += "The following key insights were identified during setup:\n\n"
            
            # Extract first few lines or key sections
            analysis_lines = ai_analysis.split('\n')[:10]
            for line in analysis_lines:
                if line.strip() and not line.startswith('#'):
                    content += f"- {line.strip()}\n"
            content += "\n"
        
        content += "### Key Dependencies\n"
        dependencies = detected_deps.get('dependencies', [])
        if dependencies:
            for dep in dependencies[:10]:  # First 10 dependencies
                content += f"- `{dep}`\n"
            if len(dependencies) > 10:
                content += f"- ... and {len(dependencies) - 10} more dependencies\n"
        else:
            content += "- No dependencies detected\n"
        
        content += """
## External Documentation
Access up-to-date docs for dependencies in the `external_context/` directory:
"""
        
        saved_files = fetched_docs.get('saved_files', [])
        if saved_files:
            for file_info in saved_files:
                dep_name = file_info.get('dependency', 'unknown')
                filename = file_info.get('filename', f"{dep_name}.md")
                content += f"- **{dep_name}**: `external_context/{filename}`\n"
        else:
            content += "- No external documentation available\n"
        
        # Add MCP server information if available
        if self.setup_data.get('installed_mcp_servers'):
            content += """
## MCP Server Integration
This project is configured with VibeContext MCP server for enhanced documentation access.

### Available Tools:
- `file_structure`: Analyze large files efficiently with structural overview
- `resolve_library_id`: Search for libraries by name to get correct library ID
- `get_library_docs`: Get specific documentation for libraries using library ID and prompt
- `fetch_doc_url`: Fetch and convert documentation from URLs to markdown

### Usage Guidelines:
1. Always use `resolve_library_id` first to find the correct library identifier
2. Use `get_library_docs` with specific questions about the library
3. Prefer MCP server documentation over general knowledge for accuracy
4. Use `fetch_doc_url` for external documentation when needed
5. Use `file_structure` when processing large text files or encountering token limits
"""
        
        content += f"""
## Development Guidelines

### Code Style & Standards
- Follow {detected_deps.get('language', 'language')}-specific best practices
- Use consistent naming conventions throughout the project
- Write clear, self-documenting code with appropriate comments
- Leverage {ide_name} AI features for intelligent assistance

### Testing & Quality
- Write comprehensive tests for new features
- Maintain high code quality standards
- Run tests before committing changes
- Use AI assistance for test generation and code review

### Documentation  
- Keep documentation up-to-date with code changes
- Use external_context/ for dependency documentation references
- Document complex algorithms and business logic
- Maintain this configuration file as project evolves

### AI Assistant Guidelines
- Use project context from JUNO.md for comprehensive understanding
- Reference external documentation when available
- Be specific in your questions to get better responses
- Validate AI-generated code against project requirements
- Leverage {ide_name}'s intelligent features for code completion and analysis

---
*This file was generated automatically by juno-agent setup on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Update by running `juno setup` or `juno-agent setup` in this directory*
"""
        
        return content
    
    async def show_completion_summary(self) -> None:
        """Show the setup completion summary."""
        try:
            # Generate consolidated summary
            summary_parts = [
                "---\n\n**Setup Complete**\n"
            ]
            
            # Project info
            project_desc = self.setup_data.get('project_description')
            if project_desc:
                summary_parts.append(f"**Project**: {project_desc}")
            
            # Editor info  
            selected_editor = self.setup_data.get('selected_editor')
            if selected_editor:
                summary_parts.append(f"**Editor**: {selected_editor}")
            
            # Dependencies info
            detected_deps = self.setup_data.get('detected_dependencies', {})
            if detected_deps.get('dependencies'):
                dep_count = len(detected_deps['dependencies'])
                language = detected_deps.get('language', 'Unknown')
                summary_parts.append(f"**Dependencies**: {dep_count} {language} packages")
            
            # MCP servers info
            installed_mcp = self.setup_data.get('installed_mcp_servers', [])
            if installed_mcp:
                summary_parts.append(f"**MCP Servers**: {', '.join(installed_mcp)}")
            
            # Documentation info
            fetched_docs = self.setup_data.get('fetched_docs', {})
            successful_docs = len(fetched_docs.get('successful', []))
            if successful_docs > 0:
                summary_parts.append(f"**Documentation**: {successful_docs} docs fetched")
            
            # Status info
            status_items = []
            if self.setup_data.get('external_context_setup'):
                status_items.append("External context")
            if self.setup_data.get('ide_configs_created'):
                status_items.append("IDE configs")
            if self.setup_data.get('permissions_configured'):
                status_items.append("Permissions")
            
            if status_items:
                summary_parts.append(f"**Configured**: {', '.join(status_items)}")
            
            # Verification info
            verification_results = self.setup_data.get('verification_results')
            if verification_results:
                status_counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
                for result in verification_results:
                    status_counts[result.status] += 1
                
                success_rate = (status_counts["PASS"] / len(verification_results) * 100)
                
                if status_counts["FAIL"] == 0 and status_counts["WARN"] == 0:
                    verification_status = "🎉 All components verified"
                elif status_counts["FAIL"] == 0:
                    verification_status = f"✅ Verified with {status_counts['WARN']} warnings"
                else:
                    verification_status = f"⚠️ {status_counts['FAIL']} components need attention"
                
                summary_parts.append(f"**Verification**: {verification_status} ({success_rate:.0f}% success)")
            elif self.setup_data.get('verification_failed'):
                summary_parts.append("**Verification**: ❌ Verification failed - manual check recommended")
            
            summary_parts.append("\n---")
            
            final_message = "\n".join(summary_parts)
            self.chat_area.add_message(final_message, is_user=False)
            
            # Complete setup
            await self.complete_enhanced_setup()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**Setup Summary Error**\n\nError: {e}\n\n---", is_user=False)
            await self.complete_enhanced_setup()
    
    async def complete_enhanced_setup(self) -> None:
        """Complete the enhanced setup process."""
        try:
            # Mark setup as completed in config
            config = self.config_manager.load_config()
            config.setup_completed = True
            self.config_manager.save_config(config)
            
            # Clean up setup state
            self.setup_active = False
            self.setup_data = {}
            
            # Final message
            self.chat_area.add_message("Setup wizard completed. Ready for AI assistance.", is_user=False)
            
        except Exception as e:
            self.chat_area.add_message(f"Setup completion error: {e}", is_user=False)
            self.setup_active = False
            self.setup_data = {}