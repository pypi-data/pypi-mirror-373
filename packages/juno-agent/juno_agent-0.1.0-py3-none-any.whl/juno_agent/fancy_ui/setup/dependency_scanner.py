"""
Project Dependency Scanner

This service scans a project directory to detect dependencies from various
package managers and build systems, providing a unified view of project
dependencies for documentation setup.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)


class DependencyScanner:
    """Service for scanning project dependencies across different languages and package managers."""
    
    def __init__(self, project_path: Optional[Path] = None):
        """Initialize the dependency scanner.
        
        Args:
            project_path: Path to the project root directory. If None, uses current working directory.
        """
        if project_path is None:
            project_path = Path.cwd()
        self.project_path = Path(project_path).resolve()
        
    def scan_project_dependencies(self) -> Dict[str, Any]:
        """Scan the project for dependencies across all supported languages.
        
        Returns:
            Dict containing:
            - language: detected primary language
            - dependencies: list of detected dependencies
            - package_files: list of package files found
            - metadata: additional project metadata
        """
        result = {
            "language": None,
            "dependencies": [],
            "package_files": [],
            "metadata": {}
        }
        
        try:
            # Scan for different types of dependency files
            python_deps = self._scan_python_dependencies()
            js_deps = self._scan_javascript_dependencies() 
            go_deps = self._scan_go_dependencies()
            rust_deps = self._scan_rust_dependencies()
            java_deps = self._scan_java_dependencies()
            
            # Combine results and determine primary language
            all_deps = []
            package_files = []
            
            if python_deps["dependencies"]:
                all_deps.extend(python_deps["dependencies"])
                package_files.extend(python_deps["package_files"])
                result["language"] = "Python"
                result["metadata"].update(python_deps["metadata"])
            
            if js_deps["dependencies"]:
                all_deps.extend(js_deps["dependencies"])
                package_files.extend(js_deps["package_files"])
                if not result["language"]:
                    result["language"] = "JavaScript"
                result["metadata"].update(js_deps["metadata"])
            
            if go_deps["dependencies"]:
                all_deps.extend(go_deps["dependencies"])
                package_files.extend(go_deps["package_files"])
                if not result["language"]:
                    result["language"] = "Go"
                result["metadata"].update(go_deps["metadata"])
            
            if rust_deps["dependencies"]:
                all_deps.extend(rust_deps["dependencies"])
                package_files.extend(rust_deps["package_files"])
                if not result["language"]:
                    result["language"] = "Rust"
                result["metadata"].update(rust_deps["metadata"])
            
            if java_deps["dependencies"]:
                all_deps.extend(java_deps["dependencies"])
                package_files.extend(java_deps["package_files"])
                if not result["language"]:
                    result["language"] = "Java"
                result["metadata"].update(java_deps["metadata"])
            
            # Remove duplicates while preserving order
            seen = set()
            unique_deps = []
            for dep in all_deps:
                if dep not in seen:
                    seen.add(dep)
                    unique_deps.append(dep)
            
            result["dependencies"] = unique_deps
            result["package_files"] = package_files
            
            # If no specific language detected, try to infer from file extensions
            if not result["language"]:
                result["language"] = self._infer_language_from_files()
            
            logger.info(f"Scanned project: found {len(unique_deps)} dependencies in {result['language']} project")
            
        except Exception as e:
            logger.error(f"Error scanning project dependencies: {e}")
            
        return result
    
    def _scan_python_dependencies(self) -> Dict[str, Any]:
        """Scan for Python dependencies."""
        result = {"dependencies": [], "package_files": [], "metadata": {}}
        
        try:
            # Check for requirements.txt
            req_file = self.project_path / "requirements.txt"
            if req_file.exists():
                result["package_files"].append("requirements.txt")
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before version specifiers)
                            pkg_match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*)', line)
                            if pkg_match:
                                result["dependencies"].append(pkg_match.group(1))
            
            # Check for pyproject.toml
            pyproject_file = self.project_path / "pyproject.toml"
            if pyproject_file.exists():
                result["package_files"].append("pyproject.toml")
                # Proper TOML parsing for dependencies from specific sections only
                with open(pyproject_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract dependencies from [project] dependencies array
                    project_deps_match = re.search(r'\[project\].*?dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
                    if project_deps_match:
                        deps_str = project_deps_match.group(1)
                        # Extract quoted package names from the dependencies array
                        for match in re.findall(r'["\']([^"\'>=<~!]+)', deps_str):
                            # Clean package name (remove version specifiers and extras)
                            pkg_match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*)', match.strip())
                            if pkg_match:
                                result["dependencies"].append(pkg_match.group(1))
                    
                    # Extract dependencies from [tool.poetry.dependencies] section
                    poetry_deps_match = re.search(r'\[tool\.poetry\.dependencies\](.*?)(?=\n\[|\Z)', content, re.DOTALL)
                    if poetry_deps_match:
                        deps_str = poetry_deps_match.group(1)
                        # Extract package names from poetry dependency lines (handles both simple and complex formats)
                        for match in re.findall(r'^\s*([a-zA-Z0-9][a-zA-Z0-9._-]+)\s*=', deps_str, re.MULTILINE):
                            if match not in ['python']:  # Skip Python version specifier
                                result["dependencies"].append(match)
                    
                    # Extract dependencies from [tool.poetry.group.dev.dependencies] section
                    poetry_dev_deps_match = re.search(r'\[tool\.poetry\.group\.dev\.dependencies\](.*?)(?=\n\[|\Z)', content, re.DOTALL)
                    if poetry_dev_deps_match:
                        deps_str = poetry_dev_deps_match.group(1)
                        # Extract package names from poetry dev dependency lines
                        for match in re.findall(r'^\s*([a-zA-Z0-9][a-zA-Z0-9._-]+)\s*=', deps_str, re.MULTILINE):
                            result["dependencies"].append(match)
            
            # Check for setup.py
            setup_file = self.project_path / "setup.py"
            if setup_file.exists():
                result["package_files"].append("setup.py")
                # Try to extract install_requires
                with open(setup_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for install_requires patterns
                    install_requires_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
                    if install_requires_match:
                        deps_str = install_requires_match.group(1)
                        # Extract quoted dependencies
                        for match in re.findall(r'["\']([^"\']+)["\']', deps_str):
                            pkg_match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*)', match)
                            if pkg_match:
                                result["dependencies"].append(pkg_match.group(1))
            
            # Check for pipenv files
            pipfile = self.project_path / "Pipfile"
            if pipfile.exists():
                result["package_files"].append("Pipfile")
                result["metadata"]["uses_pipenv"] = True
                
        except Exception as e:
            logger.error(f"Error scanning Python dependencies: {e}")
            
        return result
    
    def _scan_javascript_dependencies(self) -> Dict[str, Any]:
        """Scan for JavaScript/Node.js dependencies."""
        result = {"dependencies": [], "package_files": [], "metadata": {}}
        
        try:
            # Check for package.json
            package_file = self.project_path / "package.json"
            if package_file.exists():
                result["package_files"].append("package.json")
                with open(package_file, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                    # Extract dependencies
                    for dep_type in ["dependencies", "devDependencies", "peerDependencies"]:
                        if dep_type in package_data:
                            result["dependencies"].extend(package_data[dep_type].keys())
                    
                    # Extract metadata
                    if "name" in package_data:
                        result["metadata"]["project_name"] = package_data["name"]
                    if "scripts" in package_data:
                        result["metadata"]["has_scripts"] = True
            
            # Check for yarn.lock
            yarn_lock = self.project_path / "yarn.lock"
            if yarn_lock.exists():
                result["package_files"].append("yarn.lock")
                result["metadata"]["uses_yarn"] = True
                
            # Check for package-lock.json
            npm_lock = self.project_path / "package-lock.json"
            if npm_lock.exists():
                result["package_files"].append("package-lock.json")
                result["metadata"]["uses_npm"] = True
                
        except Exception as e:
            logger.error(f"Error scanning JavaScript dependencies: {e}")
            
        return result
    
    def _scan_go_dependencies(self) -> Dict[str, Any]:
        """Scan for Go dependencies."""
        result = {"dependencies": [], "package_files": [], "metadata": {}}
        
        try:
            # Check for go.mod
            go_mod_file = self.project_path / "go.mod"
            if go_mod_file.exists():
                result["package_files"].append("go.mod")
                with open(go_mod_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract require statements
                    require_matches = re.findall(r'^\s*([^\s]+)\s+v[^\s]+', content, re.MULTILINE)
                    result["dependencies"].extend(require_matches)
                    
                    # Extract module name
                    module_match = re.search(r'module\s+([^\s]+)', content)
                    if module_match:
                        result["metadata"]["module_name"] = module_match.group(1)
                        
        except Exception as e:
            logger.error(f"Error scanning Go dependencies: {e}")
            
        return result
    
    def _scan_rust_dependencies(self) -> Dict[str, Any]:
        """Scan for Rust dependencies."""
        result = {"dependencies": [], "package_files": [], "metadata": {}}
        
        try:
            # Check for Cargo.toml
            cargo_file = self.project_path / "Cargo.toml"
            if cargo_file.exists():
                result["package_files"].append("Cargo.toml")
                with open(cargo_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple TOML parsing for dependencies
                    deps_section = re.search(r'\[dependencies\](.*?)(?:\[|\Z)', content, re.DOTALL)
                    if deps_section:
                        deps_str = deps_section.group(1)
                        deps_matches = re.findall(r'^\s*([a-zA-Z0-9][a-zA-Z0-9._-]+)\s*=', deps_str, re.MULTILINE)
                        result["dependencies"].extend(deps_matches)
                        
        except Exception as e:
            logger.error(f"Error scanning Rust dependencies: {e}")
            
        return result
    
    def _scan_java_dependencies(self) -> Dict[str, Any]:
        """Scan for Java dependencies."""
        result = {"dependencies": [], "package_files": [], "metadata": {}}
        
        try:
            # Check for pom.xml (Maven)
            pom_file = self.project_path / "pom.xml"
            if pom_file.exists():
                result["package_files"].append("pom.xml")
                result["metadata"]["build_system"] = "maven"
                # Basic XML parsing for Maven dependencies
                with open(pom_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract artifactId from dependency tags
                    artifact_matches = re.findall(r'<artifactId>([^<]+)</artifactId>', content)
                    result["dependencies"].extend(artifact_matches)
            
            # Check for build.gradle (Gradle)
            gradle_file = self.project_path / "build.gradle"
            if gradle_file.exists():
                result["package_files"].append("build.gradle")
                result["metadata"]["build_system"] = "gradle"
                
        except Exception as e:
            logger.error(f"Error scanning Java dependencies: {e}")
            
        return result
    
    def _infer_language_from_files(self) -> Optional[str]:
        """Infer primary language from file extensions."""
        try:
            extensions = {}
            
            # Count file extensions
            for root, dirs, files in os.walk(self.project_path):
                # Skip hidden directories and common non-source directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'target', 'build']]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    ext = Path(file).suffix.lower()
                    if ext:
                        extensions[ext] = extensions.get(ext, 0) + 1
            
            # Map extensions to languages
            lang_mapping = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript', 
                '.go': 'Go',
                '.rs': 'Rust',
                '.java': 'Java',
                '.cpp': 'C++',
                '.c': 'C',
                '.cs': 'C#',
                '.php': 'PHP',
                '.rb': 'Ruby',
                '.swift': 'Swift',
                '.kt': 'Kotlin'
            }
            
            # Find the most common language
            lang_counts = {}
            for ext, count in extensions.items():
                if ext in lang_mapping:
                    lang = lang_mapping[ext]
                    lang_counts[lang] = lang_counts.get(lang, 0) + count
            
            if lang_counts:
                return max(lang_counts.items(), key=lambda x: x[1])[0]
                
        except Exception as e:
            logger.error(f"Error inferring language from files: {e}")
            
        return "Unknown"
    
    def get_dependency_summary(self) -> str:
        """Get a human-readable summary of detected dependencies."""
        scan_result = self.scan_project_dependencies()
        
        if not scan_result["dependencies"]:
            return "No dependencies detected"
        
        summary_parts = []
        
        if scan_result["language"]:
            summary_parts.append(f"**Language**: {scan_result['language']}")
        
        if scan_result["package_files"]:
            files_str = ", ".join(scan_result["package_files"])
            summary_parts.append(f"**Package Files**: {files_str}")
        
        deps_count = len(scan_result["dependencies"])
        summary_parts.append(f"**Dependencies Found**: {deps_count}")
        
        if deps_count <= 10:
            deps_str = ", ".join(scan_result["dependencies"])
            summary_parts.append(f"**Dependencies**: {deps_str}")
        else:
            first_deps = ", ".join(scan_result["dependencies"][:8])
            summary_parts.append(f"**Dependencies**: {first_deps}, ... and {deps_count - 8} more")
        
        return "\n".join(summary_parts)