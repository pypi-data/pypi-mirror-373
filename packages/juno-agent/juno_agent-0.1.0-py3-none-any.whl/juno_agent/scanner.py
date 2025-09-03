"""Project scanning functionality for detecting dependencies and technologies."""

import json
import toml
from pathlib import Path
from typing import Dict, List, Optional, Set

from pydantic import BaseModel


class ProjectInfo(BaseModel):
    """Project information model."""
    languages: List[str] = []
    frameworks: List[str] = []
    dependencies: List[str] = []
    package_managers: List[str] = []
    config_files: List[str] = []
    technologies: List[str] = []


class ProjectScanner:
    """Scans project directory to detect dependencies and technologies."""
    
    def __init__(self, workdir: Path):
        self.workdir = workdir
        
    def scan(self) -> ProjectInfo:
        """Perform comprehensive project scan."""
        project_info = ProjectInfo()
        
        # Scan for different language ecosystems
        self._scan_python(project_info)
        self._scan_javascript(project_info)
        self._scan_typescript(project_info)
        self._scan_rust(project_info)
        self._scan_go(project_info)
        self._scan_java(project_info)
        self._scan_docker(project_info)
        
        # Deduplicate and sort
        project_info.languages = sorted(list(set(project_info.languages)))
        project_info.frameworks = sorted(list(set(project_info.frameworks)))
        project_info.dependencies = sorted(list(set(project_info.dependencies)))
        project_info.package_managers = sorted(list(set(project_info.package_managers)))
        project_info.config_files = sorted(list(set(project_info.config_files)))
        project_info.technologies = sorted(list(set(project_info.technologies)))
        
        return project_info
    
    def _scan_python(self, project_info: ProjectInfo) -> None:
        """Scan for Python project files and dependencies."""
        # Check for Python files
        if list(self.workdir.rglob("*.py")):
            project_info.languages.append("Python")
        
        # Check requirements files
        requirements_files = [
            "requirements.txt",
            "requirements-dev.txt", 
            "requirements-test.txt",
            "dev-requirements.txt",
        ]
        
        for req_file in requirements_files:
            if (self.workdir / req_file).exists():
                project_info.config_files.append(req_file)
                project_info.package_managers.append("pip")
                deps = self._parse_requirements_txt(self.workdir / req_file)
                project_info.dependencies.extend(deps)
        
        # Check pyproject.toml
        pyproject_file = self.workdir / "pyproject.toml"
        if pyproject_file.exists():
            project_info.config_files.append("pyproject.toml")
            project_info.package_managers.append("pip")
            deps = self._parse_pyproject_toml(pyproject_file)
            project_info.dependencies.extend(deps)
        
        # Check setup.py
        if (self.workdir / "setup.py").exists():
            project_info.config_files.append("setup.py")
            project_info.package_managers.append("pip")
        
        # Check Poetry
        if (self.workdir / "poetry.lock").exists():
            project_info.config_files.append("poetry.lock")
            project_info.package_managers.append("poetry")
        
        # Check Pipfile
        if (self.workdir / "Pipfile").exists():
            project_info.config_files.append("Pipfile")
            project_info.package_managers.append("pipenv")
        
        # Check conda environment files
        conda_files = ["environment.yml", "environment.yaml", "conda.yml"]
        for conda_file in conda_files:
            if (self.workdir / conda_file).exists():
                project_info.config_files.append(conda_file)
                project_info.package_managers.append("conda")
        
        # Detect common Python frameworks
        self._detect_python_frameworks(project_info)
    
    def _scan_javascript(self, project_info: ProjectInfo) -> None:
        """Scan for JavaScript project files and dependencies."""
        # Check for JS files
        if list(self.workdir.rglob("*.js")) or list(self.workdir.rglob("*.jsx")):
            project_info.languages.append("JavaScript")
        
        # Check package.json
        package_json = self.workdir / "package.json"
        if package_json.exists():
            project_info.config_files.append("package.json")
            project_info.package_managers.append("npm")
            deps = self._parse_package_json(package_json)
            project_info.dependencies.extend(deps)
        
        # Check for different package managers
        if (self.workdir / "yarn.lock").exists():
            project_info.config_files.append("yarn.lock")
            project_info.package_managers.append("yarn")
        
        if (self.workdir / "pnpm-lock.yaml").exists():
            project_info.config_files.append("pnpm-lock.yaml")
            project_info.package_managers.append("pnpm")
        
        # Detect JS frameworks
        self._detect_js_frameworks(project_info)
    
    def _scan_typescript(self, project_info: ProjectInfo) -> None:
        """Scan for TypeScript project files."""
        # Check for TS files
        if list(self.workdir.rglob("*.ts")) or list(self.workdir.rglob("*.tsx")):
            project_info.languages.append("TypeScript")
        
        # Check tsconfig.json
        if (self.workdir / "tsconfig.json").exists():
            project_info.config_files.append("tsconfig.json")
    
    def _scan_rust(self, project_info: ProjectInfo) -> None:
        """Scan for Rust project files."""
        # Check for Rust files
        if list(self.workdir.rglob("*.rs")):
            project_info.languages.append("Rust")
        
        # Check Cargo.toml
        cargo_toml = self.workdir / "Cargo.toml"
        if cargo_toml.exists():
            project_info.config_files.append("Cargo.toml")
            project_info.package_managers.append("cargo")
            deps = self._parse_cargo_toml(cargo_toml)
            project_info.dependencies.extend(deps)
        
        # Check Cargo.lock
        if (self.workdir / "Cargo.lock").exists():
            project_info.config_files.append("Cargo.lock")
    
    def _scan_go(self, project_info: ProjectInfo) -> None:
        """Scan for Go project files."""
        # Check for Go files
        if list(self.workdir.rglob("*.go")):
            project_info.languages.append("Go")
        
        # Check go.mod
        go_mod = self.workdir / "go.mod"
        if go_mod.exists():
            project_info.config_files.append("go.mod")
            project_info.package_managers.append("go modules")
            deps = self._parse_go_mod(go_mod)
            project_info.dependencies.extend(deps)
        
        # Check go.sum
        if (self.workdir / "go.sum").exists():
            project_info.config_files.append("go.sum")
    
    def _scan_java(self, project_info: ProjectInfo) -> None:
        """Scan for Java project files."""
        # Check for Java files
        if list(self.workdir.rglob("*.java")):
            project_info.languages.append("Java")
        
        # Check Maven
        if (self.workdir / "pom.xml").exists():
            project_info.config_files.append("pom.xml")
            project_info.package_managers.append("maven")
        
        # Check Gradle
        gradle_files = ["build.gradle", "build.gradle.kts"]
        for gradle_file in gradle_files:
            if (self.workdir / gradle_file).exists():
                project_info.config_files.append(gradle_file)
                project_info.package_managers.append("gradle")
    
    def _scan_docker(self, project_info: ProjectInfo) -> None:
        """Scan for Docker files."""
        docker_files = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]
        for docker_file in docker_files:
            if (self.workdir / docker_file).exists():
                project_info.config_files.append(docker_file)
                project_info.technologies.append("Docker")
    
    def _parse_requirements_txt(self, file_path: Path) -> List[str]:
        """Parse requirements.txt file for dependencies."""
        dependencies = []
        try:
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        # Extract package name (before any version specifiers)
                        package = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0]
                        package = package.strip()
                        if package:
                            dependencies.append(package)
        except Exception:
            pass
        return dependencies
    
    def _parse_pyproject_toml(self, file_path: Path) -> List[str]:
        """Parse pyproject.toml file for dependencies."""
        dependencies = []
        try:
            with open(file_path, "r") as f:
                data = toml.load(f)
            
            # Check project dependencies
            if "project" in data and "dependencies" in data["project"]:
                for dep in data["project"]["dependencies"]:
                    package = dep.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0]
                    package = package.strip()
                    if package:
                        dependencies.append(package)
            
            # Check optional dependencies
            if "project" in data and "optional-dependencies" in data["project"]:
                for group, deps in data["project"]["optional-dependencies"].items():
                    for dep in deps:
                        package = dep.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0]
                        package = package.strip()
                        if package:
                            dependencies.append(package)
        except Exception:
            pass
        return dependencies
    
    def _parse_package_json(self, file_path: Path) -> List[str]:
        """Parse package.json file for dependencies."""
        dependencies = []
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Regular dependencies
            if "dependencies" in data:
                dependencies.extend(data["dependencies"].keys())
            
            # Dev dependencies
            if "devDependencies" in data:
                dependencies.extend(data["devDependencies"].keys())
        except Exception:
            pass
        return dependencies
    
    def _parse_cargo_toml(self, file_path: Path) -> List[str]:
        """Parse Cargo.toml file for dependencies."""
        dependencies = []
        try:
            with open(file_path, "r") as f:
                data = toml.load(f)
            
            if "dependencies" in data:
                dependencies.extend(data["dependencies"].keys())
            
            if "dev-dependencies" in data:
                dependencies.extend(data["dev-dependencies"].keys())
        except Exception:
            pass
        return dependencies
    
    def _parse_go_mod(self, file_path: Path) -> List[str]:
        """Parse go.mod file for dependencies."""
        dependencies = []
        try:
            with open(file_path, "r") as f:
                in_require = False
                for line in f:
                    line = line.strip()
                    if line.startswith("require"):
                        in_require = True
                        # Handle single line require
                        if not line.endswith("("):
                            parts = line.split()
                            if len(parts) >= 3:
                                dependencies.append(parts[1])
                    elif in_require:
                        if line == ")":
                            in_require = False
                        elif line and not line.startswith("//"):
                            parts = line.split()
                            if len(parts) >= 2:
                                dependencies.append(parts[0])
        except Exception:
            pass
        return dependencies
    
    def _detect_python_frameworks(self, project_info: ProjectInfo) -> None:
        """Detect Python frameworks from dependencies."""
        framework_map = {
            "django": "Django",
            "flask": "Flask",
            "fastapi": "FastAPI",
            "tornado": "Tornado",
            "pyramid": "Pyramid",
            "bottle": "Bottle",
            "streamlit": "Streamlit",
            "dash": "Dash",
            "jupyter": "Jupyter",
            "pytest": "pytest",
            "numpy": "NumPy",
            "pandas": "Pandas",
            "scipy": "SciPy",
            "matplotlib": "Matplotlib",
            "tensorflow": "TensorFlow",
            "torch": "PyTorch",
            "sklearn": "scikit-learn",
        }
        
        for dep in project_info.dependencies:
            dep_lower = dep.lower()
            if dep_lower in framework_map:
                project_info.frameworks.append(framework_map[dep_lower])
    
    def _detect_js_frameworks(self, project_info: ProjectInfo) -> None:
        """Detect JavaScript frameworks from dependencies."""
        framework_map = {
            "react": "React",
            "vue": "Vue.js",
            "angular": "Angular",
            "svelte": "Svelte",
            "next": "Next.js",
            "nuxt": "Nuxt.js",
            "gatsby": "Gatsby",
            "express": "Express.js",
            "koa": "Koa.js",
            "nestjs": "NestJS",
            "jquery": "jQuery",
            "lodash": "Lodash",
            "axios": "Axios",
            "webpack": "Webpack",
            "rollup": "Rollup",
            "vite": "Vite",
            "eslint": "ESLint",
            "prettier": "Prettier",
            "jest": "Jest",
            "mocha": "Mocha",
        }
        
        for dep in project_info.dependencies:
            dep_lower = dep.lower()
            if dep_lower in framework_map:
                project_info.frameworks.append(framework_map[dep_lower])
            elif dep_lower.startswith("@nestjs"):
                project_info.frameworks.append("NestJS")
            elif dep_lower.startswith("@angular"):
                project_info.frameworks.append("Angular")