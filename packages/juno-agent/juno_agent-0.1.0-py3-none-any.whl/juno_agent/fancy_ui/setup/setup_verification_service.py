"""Setup Verification Service for comprehensive validation of setup completion."""

import os
import json
import yaml
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import subprocess
import logging

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of a verification check."""
    component: str
    status: str  # 'PASS', 'FAIL', 'WARN', 'INFO'
    message: str
    details: Dict[str, Any]
    recommendations: List[str]


class SetupVerificationService:
    """Comprehensive verification service for setup validation."""
    
    def __init__(self, project_root: str, project_name: str):
        self.project_root = Path(project_root)
        self.project_name = project_name
        self.home_dir = Path.home()
        self.askbudi_dir = self.home_dir / ".ASKBUDI"
        
        # Use the same project name generation logic as ExternalContextManager
        generated_project_name = self._generate_project_name(self.project_root)
        self.external_context_global = self.askbudi_dir / generated_project_name / "external_context"
        self.external_context_local = self.project_root / "external_context"
        self.selected_editor = self._get_selected_editor()
    
    def _generate_project_name(self, project_path: Path) -> str:
        """Generate project name for ASKBUDI directory from project path.
        
        This uses the same logic as ExternalContextManager to ensure consistency.
        
        Args:
            project_path: Path to the project root
            
        Returns:
            str: Generated project name with path segments
        """
        # Convert path to string and make it relative to user home if possible
        path_str = str(project_path)
        home_str = str(Path.home())
        
        # Remove home prefix if present
        if path_str.startswith(home_str):
            path_str = path_str[len(home_str):].lstrip('/')
        
        # Replace path separators with underscores and remove leading separators
        project_name = path_str.replace('/', '_').replace('\\', '_').strip('_')
        
        # Ensure we have a valid name
        if not project_name:
            project_name = "project_" + str(abs(hash(str(project_path))))[:8]
            
        return project_name
        
    def verify_all_components(self) -> List[VerificationResult]:
        """Run comprehensive verification of all setup components."""
        results = []
        
        # Run all verification checks
        results.extend(self.verify_mcp_server_config())
        results.extend(self.verify_external_context_setup())
        results.extend(self.verify_ide_configuration_files())
        results.extend(self.verify_dependency_documentation())
        results.extend(self.verify_api_key_configuration())
        results.extend(self.verify_file_permissions())
        results.extend(self.verify_project_analysis_accuracy())
        
        return results
    
    def verify_mcp_server_config(self) -> List[VerificationResult]:
        """Verify MCP server configuration for the user's selected IDE only."""
        results = []
        
        if not self.selected_editor:
            return [VerificationResult(
                component="MCP Server Configuration",
                status="WARN",
                message="No IDE selected - skipping MCP server verification",
                details={"config_path": str(self.project_root / ".juno_config.json")},
                recommendations=["Complete setup wizard to select an IDE"]
            )]
        
        # Use IDE-specific verification methods
        if self.selected_editor == "claude_code" or self.selected_editor == "Claude Code":
            # Use native Claude MCP commands for verification
            result = self._verify_claude_code_mcp()
            results.append(result)
        else:
            # Use file-based verification for other IDEs
            ide_config_path = self._get_ide_config_path(self.selected_editor)
            
            if not ide_config_path:
                return [VerificationResult(
                    component="MCP Server Configuration",
                    status="FAIL",
                    message=f"Unknown IDE configuration for {self.selected_editor}",
                    details={"selected_editor": self.selected_editor},
                    recommendations=["Select a supported IDE from the setup wizard"]
                )]
            
            if ide_config_path.exists():
                result = self._verify_mcp_config_file(self.selected_editor, ide_config_path)
                results.append(result)
            else:
                results.append(VerificationResult(
                    component="MCP Server Configuration",
                    status="FAIL",
                    message=f"MCP configuration file not found for {self.selected_editor}",
                    details={
                        "selected_editor": self.selected_editor,
                        "expected_path": str(ide_config_path)
                    },
                    recommendations=[
                        "Re-run setup wizard MCP server installation step",
                        f"Manually create MCP configuration for {self.selected_editor}",
                        "Verify IDE selection is correct"
                    ]
                ))
        
        return results
    
    def _verify_claude_code_mcp(self) -> VerificationResult:
        """Verify Claude Code MCP configuration using native claude commands."""
        import subprocess
        
        try:
            # First, check if claude command is available
            result = subprocess.run(['claude', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return VerificationResult(
                    component="MCP Server Configuration",
                    status="FAIL",
                    message="Claude CLI not found or not working",
                    details={"command": "claude --version", "exit_code": result.returncode},
                    recommendations=[
                        "Install Claude CLI: https://docs.anthropic.com/en/docs/claude-code",
                        "Ensure claude command is in your PATH"
                    ]
                )
            
            # List all configured MCP servers
            result = subprocess.run(['claude', 'mcp', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return VerificationResult(
                    component="MCP Server Configuration",
                    status="FAIL",
                    message="Failed to list MCP servers",
                    details={
                        "command": "claude mcp list",
                        "exit_code": result.returncode,
                        "stderr": result.stderr.strip() if result.stderr else None
                    },
                    recommendations=[
                        "Check Claude CLI installation",
                        "Verify Claude CLI permissions",
                        "Re-run setup to configure MCP servers"
                    ]
                )
            
            # Check if vibe-context or vibe_context server is configured
            output = result.stdout.strip()
            has_vibe_server = 'vibe-context' in output or 'vibe_context' in output
            
            if not output or not has_vibe_server:
                return VerificationResult(
                    component="MCP Server Configuration",
                    status="FAIL",
                    message="VibeContext MCP server not found in Claude configuration",
                    details={
                        "command": "claude mcp list",
                        "output": output,
                        "expected_server": "vibe-context or vibe_context"
                    },
                    recommendations=[
                        "Re-run setup wizard to install VibeContext MCP server",
                        "Manually add MCP server: claude mcp add vibe-context ...",
                        "Verify ASKBUDI_API_KEY environment variable is set"
                    ]
                )
            
            # Determine which server name to use for detailed check
            server_name = 'vibe_context' if 'vibe_context' in output else 'vibe-context'
            
            # Get detailed configuration for the server
            result = subprocess.run(['claude', 'mcp', 'get', server_name], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return VerificationResult(
                    component="MCP Server Configuration",
                    status="WARN",
                    message="VibeContext server found but cannot get detailed configuration",
                    details={
                        "command": f"claude mcp get {server_name}",
                        "exit_code": result.returncode,
                        "stderr": result.stderr.strip() if result.stderr else None,
                        "list_output": output
                    },
                    recommendations=[
                        "Server is configured but may have issues",
                        f"Try re-configuring: claude mcp remove {server_name} && re-run setup"
                    ]
                )
            
            # Success - server is properly configured
            server_config = result.stdout.strip()
            return VerificationResult(
                component="MCP Server Configuration",
                status="PASS",
                message="VibeContext MCP server properly configured in Claude Code",
                details={
                    "server_name": "vibe-context",
                    "verification_method": "claude mcp commands",
                    "config_summary": server_config[:200] + "..." if len(server_config) > 200 else server_config
                },
                recommendations=[]
            )
            
        except subprocess.TimeoutExpired:
            return VerificationResult(
                component="MCP Server Configuration",
                status="FAIL",
                message="Claude MCP commands timed out",
                details={"timeout": "30 seconds"},
                recommendations=[
                    "Check Claude CLI responsiveness",
                    "Verify network connectivity for MCP servers",
                    "Re-run verification after a few minutes"
                ]
            )
        except FileNotFoundError:
            return VerificationResult(
                component="MCP Server Configuration",
                status="FAIL",
                message="Claude CLI not installed or not in PATH",
                details={"error": "claude command not found"},
                recommendations=[
                    "Install Claude CLI: https://docs.anthropic.com/en/docs/claude-code",
                    "Add claude to your PATH environment variable",
                    "Restart terminal after installing Claude CLI"
                ]
            )
        except Exception as e:
            return VerificationResult(
                component="MCP Server Configuration",
                status="FAIL",
                message=f"Error verifying Claude Code MCP configuration: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__},
                recommendations=[
                    "Check Claude CLI installation and permissions",
                    "Re-run setup wizard MCP installation step",
                    "Report issue if problem persists"
                ]
            )
    
    def _verify_mcp_config_file(self, ide_name: str, config_path: Path) -> VerificationResult:
        """Verify a specific MCP configuration file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check for MCP server configuration structure
            # All IDEs use 'mcpServers' as the key and 'vibe_context' as the server name
            mcp_servers = config.get("mcpServers", {})
            mcp_config = mcp_servers.get("vibe_context")
            
            if not mcp_config:
                return VerificationResult(
                    component=f"MCP Config ({ide_name})",
                    status="FAIL",
                    message="MCP server configuration not found in config file",
                    details={"config_path": str(config_path), "config_structure": list(config.keys())},
                    recommendations=["Add vibe-context MCP server configuration"]
                )
            
            # Check command and args
            command = mcp_config.get("command")
            args = mcp_config.get("args", [])
            
            # Accept both "node" and "npx" as valid commands
            valid_commands = ["node", "npx"]
            if command not in valid_commands:
                return VerificationResult(
                    component=f"MCP Config ({ide_name})",
                    status="WARN",
                    message=f"MCP server command '{command}' is not recognized",
                    details={"command": command, "valid_commands": valid_commands},
                    recommendations=["Verify MCP server executable command"]
                )
            
            # Check if MCP server file exists (only for local builds, not npm packages)
            if args and command == "node":
                # Only check file existence for local node builds
                mcp_server_path = Path(args[0])
                if not mcp_server_path.exists():
                    return VerificationResult(
                        component=f"MCP Config ({ide_name})",
                        status="WARN",
                        message="Local MCP server executable not found",
                        details={"server_path": str(mcp_server_path)},
                        recommendations=[
                            "Build MCP server if using local development",
                            "Consider using npm package with 'npx' command"
                        ]
                    )
            elif command == "npx" and args and "askbudi-context" not in args:
                return VerificationResult(
                    component=f"MCP Config ({ide_name})",
                    status="WARN", 
                    message="NPX command doesn't specify askbudi-context package",
                    details={"args": args},
                    recommendations=["Verify npm package name in MCP configuration"]
                )
            
            # Check environment variables
            env = mcp_config.get("env", {})
            api_key = env.get("ASKBUDI_API_KEY")
            
            if not api_key:
                return VerificationResult(
                    component=f"MCP Config ({ide_name})",
                    status="WARN",
                    message="ASKBUDI_API_KEY not configured in MCP server environment",
                    details={"env_vars": list(env.keys())},
                    recommendations=["Add ASKBUDI_API_KEY to MCP server environment configuration"]
                )
            
            return VerificationResult(
                component=f"MCP Config ({ide_name})",
                status="PASS",
                message="MCP server configuration is valid",
                details={
                    "config_path": str(config_path),
                    "command": command,
                    "server_path": args[0] if args else None,
                    "has_api_key": bool(api_key)
                },
                recommendations=[]
            )
            
        except json.JSONDecodeError as e:
            return VerificationResult(
                component=f"MCP Config ({ide_name})",
                status="FAIL",
                message="Invalid JSON in configuration file",
                details={"error": str(e), "config_path": str(config_path)},
                recommendations=["Fix JSON syntax in configuration file"]
            )
        except Exception as e:
            return VerificationResult(
                component=f"MCP Config ({ide_name})",
                status="FAIL",
                message=f"Error reading configuration file: {str(e)}",
                details={"config_path": str(config_path)},
                recommendations=["Check file permissions and accessibility"]
            )
    
    def verify_external_context_setup(self) -> List[VerificationResult]:
        """Verify external context directory structure and symlinks."""
        results = []
        
        # Get the generated project name for detailed reporting
        generated_project_name = self._generate_project_name(self.project_root)
        
        # Check global external context directory
        if not self.external_context_global.exists():
            results.append(VerificationResult(
                component="External Context Directory",
                status="FAIL",
                message="Global external context directory not found",
                details={
                    "expected_path": str(self.external_context_global),
                    "generated_project_name": generated_project_name,
                    "simple_project_name": self.project_name
                },
                recommendations=[
                    f"Create directory: mkdir -p ~/.ASKBUDI/{generated_project_name}/external_context",
                    "Re-run setup wizard external context step"
                ]
            ))
        else:
            # Check directory contents
            doc_files = list(self.external_context_global.glob("*.md"))
            # Also check in subdirectories for better file counting
            all_doc_files = list(self.external_context_global.glob("**/*.md"))
            results.append(VerificationResult(
                component="External Context Directory",
                status="PASS",
                message=f"Found external context directory with {len(all_doc_files)} documentation files",
                details={
                    "path": str(self.external_context_global),
                    "generated_project_name": generated_project_name,
                    "root_md_files": len(doc_files),
                    "total_md_files": len(all_doc_files),
                    "root_files": [f.name for f in doc_files]
                },
                recommendations=[]
            ))
        
        # Check local symlink
        if not self.external_context_local.exists():
            results.append(VerificationResult(
                component="External Context Symlink",
                status="FAIL",
                message="Local external context symlink not found",
                details={"expected_path": str(self.external_context_local)},
                recommendations=[
                    f"Create symlink: ln -s {self.external_context_global} {self.external_context_local}",
                    "Re-run setup wizard external context step"
                ]
            ))
        elif self.external_context_local.is_symlink():
            # Verify symlink target (compatible with Python < 3.9)
            import os
            target = Path(os.readlink(str(self.external_context_local)))
            if target.resolve() == self.external_context_global.resolve():
                results.append(VerificationResult(
                    component="External Context Symlink",
                    status="PASS",
                    message="Symlink correctly points to global external context",
                    details={
                        "symlink_path": str(self.external_context_local),
                        "target_path": str(target)
                    },
                    recommendations=[]
                ))
            else:
                results.append(VerificationResult(
                    component="External Context Symlink",
                    status="FAIL",
                    message="Symlink points to incorrect location",
                    details={
                        "symlink_path": str(self.external_context_local),
                        "current_target": str(target),
                        "expected_target": str(self.external_context_global)
                    },
                    recommendations=[
                        f"Fix symlink: rm {self.external_context_local} && ln -s {self.external_context_global} {self.external_context_local}"
                    ]
                ))
        else:
            results.append(VerificationResult(
                component="External Context Symlink",
                status="WARN",
                message="External context path exists but is not a symlink",
                details={"path": str(self.external_context_local)},
                recommendations=[
                    "Remove existing path and create proper symlink",
                    "Verify external context setup"
                ]
            ))
        
        return results
    
    def verify_ide_configuration_files(self) -> List[VerificationResult]:
        """Verify IDE-specific configuration files for the selected IDE."""
        results = []
        
        # Always check JUNO.md as it's universal
        juno_file = self.project_root / "JUNO.md"
        if juno_file.exists():
            result = self._verify_ide_file_content("JUNO.md", "Juno CLI", juno_file)
            results.append(result)
        else:
            results.append(VerificationResult(
                component="IDE Config (JUNO.md)",
                status="FAIL",
                message="Universal JUNO.md configuration file not found",
                details={"expected_path": str(juno_file)},
                recommendations=["Re-run setup wizard to create JUNO.md file"]
            ))
        
        # Check IDE-specific file if an IDE is selected
        if self.selected_editor:
            # Load IDE configuration to get the correct instruction file
            config_file = Path(__file__).parent.parent.parent / "config" / "supported_ides.json"
            expected_file = None
            
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # Find matching IDE by key or display name
                    for ide_key, ide_data in config_data.get('ides', {}).items():
                        # Match by IDE key (e.g., "claude_code") or display name (e.g., "Claude Code")
                        if ide_key == self.selected_editor or ide_data.get('display_name') == self.selected_editor:
                            custom_instructions = ide_data.get('custom_instructions', {})
                            expected_file = custom_instructions.get('file_name', 'AGENTS.md')
                            break
                except Exception as e:
                    logger.warning(f"Failed to load IDE configuration: {e}")
            
            # Fallback mapping for backward compatibility
            if not expected_file:
                ide_files = {
                    "claude_code": "CLAUDE.md",
                    "Claude Code": "CLAUDE.md",
                    "windsurf": "WINDSURF.md",
                    "Windsurf": "WINDSURF.md",
                    # All other IDEs use AGENTS.md
                    "cursor": "AGENTS.md",
                    "Cursor": "AGENTS.md",
                    "vscode": "AGENTS.md",
                    "VS Code": "AGENTS.md",
                    "VSCode": "AGENTS.md",
                }
                expected_file = ide_files.get(self.selected_editor, "AGENTS.md")
            if expected_file:
                ide_file_path = self.project_root / expected_file
                if ide_file_path.exists():
                    result = self._verify_ide_file_content(expected_file, self.selected_editor, ide_file_path)
                    results.append(result)
                else:
                    results.append(VerificationResult(
                        component=f"IDE Config ({expected_file})",
                        status="WARN",
                        message=f"IDE-specific configuration file for {self.selected_editor} not found",
                        details={
                            "selected_editor": self.selected_editor,
                            "expected_file": expected_file,
                            "expected_path": str(ide_file_path)
                        },
                        recommendations=[
                            f"Re-run setup wizard to create {expected_file}",
                            "JUNO.md provides universal configuration as fallback"
                        ]
                    ))
        
        return results
    
    def _verify_ide_file_content(self, filename: str, ide_name: str, file_path: Path) -> VerificationResult:
        """Verify content quality of an IDE configuration file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check file size
            if len(content) < 500:
                return VerificationResult(
                    component=f"IDE Config ({filename})",
                    status="WARN",
                    message="IDE configuration file is quite short",
                    details={"file_size": len(content), "path": str(file_path)},
                    recommendations=["Verify file contains comprehensive project information"]
                )
            
            # Check for key sections
            required_sections = [
                "Project Analysis",
                "Dependencies",
                "External Context",
                "MCP Server"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section.lower() not in content.lower():
                    missing_sections.append(section)
            
            if missing_sections:
                return VerificationResult(
                    component=f"IDE Config ({filename})",
                    status="WARN",
                    message="IDE configuration file missing some sections",
                    details={
                        "missing_sections": missing_sections,
                        "file_size": len(content)
                    },
                    recommendations=[
                        "Add missing sections to IDE configuration file",
                        "Re-run setup wizard to regenerate file"
                    ]
                )
            
            return VerificationResult(
                component=f"IDE Config ({filename})",
                status="PASS",
                message="IDE configuration file is comprehensive",
                details={
                    "file_size": len(content),
                    "sections_found": [s for s in required_sections if s.lower() in content.lower()]
                },
                recommendations=[]
            )
            
        except Exception as e:
            return VerificationResult(
                component=f"IDE Config ({filename})",
                status="FAIL",
                message=f"Error reading IDE configuration file: {str(e)}",
                details={"path": str(file_path)},
                recommendations=["Check file permissions and accessibility"]
            )
    
    def verify_dependency_documentation(self) -> List[VerificationResult]:
        """Verify dependency documentation files."""
        results = []
        
        if not self.external_context_global.exists():
            return [VerificationResult(
                component="Dependency Documentation",
                status="FAIL",
                message="External context directory not found",
                details={},
                recommendations=["Run external context setup first"]
            )]
        
        doc_files = list(self.external_context_global.glob("*.md"))
        
        if not doc_files:
            return [VerificationResult(
                component="Dependency Documentation",
                status="FAIL",
                message="No documentation files found",
                details={"context_path": str(self.external_context_global)},
                recommendations=[
                    "Re-run setup wizard dependency documentation step",
                    "Check if dependency extraction worked correctly"
                ]
            )]
        
        # Check each documentation file
        for doc_file in doc_files:
            result = self._verify_documentation_file(doc_file)
            results.append(result)
        
        # Summary result
        passed_files = [r for r in results if r.status == "PASS"]
        total_files = len(results)
        
        if len(passed_files) == total_files:
            status = "PASS"
            message = f"All {total_files} documentation files are valid"
        elif len(passed_files) > total_files // 2:
            status = "WARN"
            message = f"{len(passed_files)}/{total_files} documentation files are valid"
        else:
            status = "FAIL"
            message = f"Only {len(passed_files)}/{total_files} documentation files are valid"
        
        results.append(VerificationResult(
            component="Dependency Documentation Summary",
            status=status,
            message=message,
            details={
                "total_files": total_files,
                "passed_files": len(passed_files),
                "failed_files": total_files - len(passed_files)
            },
            recommendations=[] if status == "PASS" else [
                "Re-fetch documentation for failed files",
                "Check network connectivity during setup"
            ]
        ))
        
        return results
    
    def _verify_documentation_file(self, doc_file: Path) -> VerificationResult:
        """Verify a single documentation file."""
        try:
            content = doc_file.read_text(encoding='utf-8')
            
            # Check file size
            if len(content) < 1000:
                return VerificationResult(
                    component=f"Doc File ({doc_file.name})",
                    status="WARN",
                    message="Documentation file is quite small",
                    details={"file_size": len(content)},
                    recommendations=["Check if documentation was fetched correctly"]
                )
            
            # Check for error indicators
            error_indicators = ["404", "Not Found", "Error", "Page not found", "Access denied"]
            found_errors = [err for err in error_indicators if err.lower() in content.lower()]
            
            if found_errors:
                return VerificationResult(
                    component=f"Doc File ({doc_file.name})",
                    status="FAIL",
                    message="Documentation file contains error content",
                    details={"errors_found": found_errors, "file_size": len(content)},
                    recommendations=["Re-fetch documentation for this dependency"]
                )
            
            return VerificationResult(
                component=f"Doc File ({doc_file.name})",
                status="PASS",
                message="Documentation file appears valid",
                details={"file_size": len(content)},
                recommendations=[]
            )
            
        except Exception as e:
            return VerificationResult(
                component=f"Doc File ({doc_file.name})",
                status="FAIL",
                message=f"Error reading documentation file: {str(e)}",
                details={},
                recommendations=["Check file permissions and encoding"]
            )
    
    def verify_api_key_configuration(self) -> List[VerificationResult]:
        """Verify API key configuration."""
        results = []
        
        # Check environment variable
        env_api_key = os.environ.get("ASKBUDI_API_KEY")
        if env_api_key:
            results.append(VerificationResult(
                component="API Key (Environment)",
                status="PASS",
                message="ASKBUDI_API_KEY found in environment",
                details={"key_length": len(env_api_key), "key_prefix": env_api_key[:8] + "..."},
                recommendations=[]
            ))
        else:
            results.append(VerificationResult(
                component="API Key (Environment)",
                status="WARN",
                message="ASKBUDI_API_KEY not found in environment variables",
                details={},
                recommendations=[
                    "Set ASKBUDI_API_KEY environment variable",
                    "Check if API key is configured in MCP server config"
                ]
            ))
        
        return results
    
    def verify_file_permissions(self) -> List[VerificationResult]:
        """Verify file permissions and accessibility."""
        results = []
        
        # Check key directories and files
        check_paths = [
            (self.askbudi_dir, "ASKBUDI directory"),
            (self.external_context_global, "External context directory"),
            (self.external_context_local, "External context symlink"),
        ]
        
        for path, description in check_paths:
            if path.exists():
                try:
                    # Test read access
                    if path.is_dir():
                        list(path.iterdir())
                        access_test = "Directory readable"
                    else:
                        path.read_text()
                        access_test = "File readable"
                    
                    results.append(VerificationResult(
                        component=f"Permissions ({description})",
                        status="PASS",
                        message=access_test,
                        details={"path": str(path), "permissions": oct(path.stat().st_mode)[-3:]},
                        recommendations=[]
                    ))
                    
                except PermissionError:
                    results.append(VerificationResult(
                        component=f"Permissions ({description})",
                        status="FAIL",
                        message="Permission denied accessing path",
                        details={"path": str(path)},
                        recommendations=["Check and fix file/directory permissions"]
                    ))
        
        return results
    
    def verify_project_analysis_accuracy(self) -> List[VerificationResult]:
        """Verify accuracy of project analysis."""
        results = []
        
        # This is a basic check - in a full implementation you'd want to
        # compare the analysis against actual project structure
        
        # Check if package files exist and match analysis
        package_files = {
            "package.json": "Node.js/JavaScript",
            "pyproject.toml": "Python",
            "requirements.txt": "Python",
            "go.mod": "Go",
            "Cargo.toml": "Rust",
            "pom.xml": "Java (Maven)",
            "build.gradle": "Java (Gradle)"
        }
        
        detected_languages = []
        for package_file, language in package_files.items():
            if (self.project_root / package_file).exists():
                detected_languages.append(language)
        
        if detected_languages:
            results.append(VerificationResult(
                component="Project Analysis",
                status="INFO",
                message=f"Detected project languages: {', '.join(detected_languages)}",
                details={"detected_languages": detected_languages},
                recommendations=["Verify IDE configuration files match detected languages"]
            ))
        else:
            results.append(VerificationResult(
                component="Project Analysis",
                status="WARN",
                message="No common package files detected",
                details={},
                recommendations=["Manually verify project type is correctly identified in IDE files"]
            ))
        
        return results
    
    def generate_summary_report(self, results: List[VerificationResult]) -> str:
        """Generate a comprehensive summary report."""
        # Count results by status
        status_counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
        for result in results:
            status_counts[result.status] += 1
        
        total_components = len(results)
        success_rate = (status_counts["PASS"] / total_components * 100) if total_components > 0 else 0
        
        # Status icons
        status_icons = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}
        
        # Generate report
        report = []
        report.append("# Setup Verification Report")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Project**: {self.project_name}")
        report.append(f"**Platform**: {platform.system()} {platform.release()}")
        report.append("")
        
        # Summary statistics
        report.append("## Summary Statistics")
        report.append(f"- **Total components checked**: {total_components}")
        report.append(f"- **Passed**: {status_counts['PASS']}")
        report.append(f"- **Failed**: {status_counts['FAIL']}")
        report.append(f"- **Warnings**: {status_counts['WARN']}")
        report.append(f"- **Info**: {status_counts['INFO']}")
        report.append(f"- **Setup Success Rate**: {success_rate:.1f}%")
        report.append("")
        
        # Component status overview
        report.append("## Component Status Overview")
        for result in results:
            icon = status_icons.get(result.status, "❓")
            report.append(f"{icon} **{result.status}**: {result.component} - {result.message}")
        
        report.append("")
        
        # Detailed findings
        report.append("## Detailed Findings")
        
        for status in ["FAIL", "WARN", "PASS", "INFO"]:
            status_results = [r for r in results if r.status == status]
            if status_results:
                report.append(f"### {status_icons[status]} {status} Components")
                
                for result in status_results:
                    report.append(f"**{result.component}**")
                    report.append(f"- Message: {result.message}")
                    
                    if result.details:
                        report.append(f"- Details: {result.details}")
                    
                    if result.recommendations:
                        report.append("- Recommendations:")
                        for rec in result.recommendations:
                            report.append(f"  - {rec}")
                    
                    report.append("")
        
        # Overall assessment
        report.append("## Overall Assessment")
        
        if status_counts["FAIL"] == 0:
            if status_counts["WARN"] == 0:
                assessment = "🎉 **EXCELLENT**: Setup is complete and all components are working perfectly!"
            else:
                assessment = "✅ **GOOD**: Setup is functional with some minor warnings that should be addressed."
        elif status_counts["FAIL"] <= 2:
            assessment = "⚠️ **NEEDS ATTENTION**: Setup has some issues that need to be resolved for optimal functionality."
        else:
            assessment = "❌ **CRITICAL ISSUES**: Setup has significant problems that will impact functionality. Please address failures before proceeding."
        
        report.append(assessment)
        report.append("")
        
        # Next steps
        if status_counts["FAIL"] > 0 or status_counts["WARN"] > 0:
            report.append("## Recommended Next Steps")
            
            if status_counts["FAIL"] > 0:
                report.append("1. **Address Critical Failures**: Focus on FAIL status components first")
                report.append("2. **Re-run Setup**: Consider running setup wizard again for failed components")
                report.append("3. **Manual Configuration**: Some components may need manual configuration")
            
            if status_counts["WARN"] > 0:
                report.append("4. **Resolve Warnings**: Address warning components to improve setup quality")
                report.append("5. **Verify Functionality**: Test IDE and MCP server functionality")
            
            report.append("6. **Re-run Verification**: Run verification again after fixing issues")
        else:
            report.append("## Next Steps")
            report.append("🎯 **You're ready to go!** Your development environment is properly configured.")
            report.append("- Start using your AI-powered IDE")
            report.append("- Test MCP server functionality")
            report.append("- Explore external documentation context")
        
        return "\n".join(report)
    
    def _get_selected_editor(self) -> Optional[str]:
        """Get the selected editor from configuration."""
        try:
            # Try to load from config file
            config_file = self.project_root / ".juno_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('editor')
            
            # Fallback: try to detect from existing IDE files
            # Check for IDE-specific files first, then generic ones
            ide_files = {
                "CLAUDE.md": "Claude Code",
                "WINDSURF.md": "Windsurf",
                # Don't assume AGENTS.md means "Generic IDE" - it could be for any IDE
            }
            
            # Check for MCP configuration files to determine IDE
            if (self.project_root / ".cursor" / "mcp.json").exists():
                return "Cursor"
            elif (self.home_dir / ".claude_code_config.json").exists():
                return "Claude Code"
            elif (self.home_dir / ".codeium" / "windsurf" / "mcp_config.json").exists():
                return "Windsurf"
            
            # Then check for instruction files
            for filename, ide_name in ide_files.items():
                if (self.project_root / filename).exists():
                    return ide_name
            
            # If AGENTS.md exists but no specific IDE detected, check for Cursor
            if (self.project_root / "AGENTS.md").exists():
                # If .cursor directory exists, it's likely Cursor
                if (self.project_root / ".cursor").exists():
                    return "Cursor"
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to determine selected editor: {e}")
            return None
    
    def _get_ide_config_path(self, ide_name: str) -> Optional[Path]:
        """Get the MCP configuration path for a specific IDE."""
        try:
            # Load configuration from supported_ides.json
            config_file = Path(__file__).parent.parent.parent / "config" / "supported_ides.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Find matching IDE by key or display name
                for ide_key, ide_data in config_data.get('ides', {}).items():
                    # Match by IDE key (e.g., "claude_code") or display name (e.g., "Claude Code")
                    if ide_key == ide_name or ide_data.get('display_name') == ide_name:
                        mcp_config = ide_data.get('mcp_config', {})
                        config_path = mcp_config.get('config_file_path', '')
                        
                        if config_path.startswith('~/'):
                            return self.home_dir / config_path[2:]
                        elif config_path.startswith('.'):
                            return self.project_root / config_path
                        else:
                            return Path(config_path)
            
            # Fallback to hardcoded mappings for backward compatibility
            ide_configs = {
                # Support both IDE keys and display names
                "claude_code": self.home_dir / ".claude_code_config.json",
                "Claude Code": self.home_dir / ".claude_code_config.json",
                "cursor": self.project_root / ".cursor" / "mcp.json",
                "Cursor": self.project_root / ".cursor" / "mcp.json",
                "windsurf": self.home_dir / ".codeium" / "windsurf" / "mcp_config.json",
                "Windsurf": self.home_dir / ".codeium" / "windsurf" / "mcp_config.json",
                "vscode": self.project_root / ".vscode" / "settings.json",
                "VS Code": self.project_root / ".vscode" / "settings.json",
                "VSCode": self.project_root / ".vscode" / "settings.json"
            }
            
            return ide_configs.get(ide_name)
            
        except Exception as e:
            logger.warning(f"Failed to determine config path for {ide_name}: {e}")
            return None
    
    def save_editor_selection(self, editor_display_name: str) -> bool:
        """Save the selected editor to configuration file.
        
        Args:
            editor_display_name: Display name of the selected editor
            
        Returns:
            bool: True if save was successful
        """
        try:
            config_file = self.project_root / ".juno_config.json"
            config = {}
            
            # Load existing configuration if it exists
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON in .juno_config.json, creating new config")
                    config = {}
            
            # Save editor selection
            config['editor'] = editor_display_name
            
            # Write configuration
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved editor selection: {editor_display_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save editor selection: {e}")
            return False