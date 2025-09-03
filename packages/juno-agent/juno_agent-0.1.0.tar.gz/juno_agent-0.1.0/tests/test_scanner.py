"""Tests for project scanner functionality."""

import tempfile
from pathlib import Path

import pytest

from juno_agent.scanner import ProjectScanner, ProjectInfo


class TestProjectInfo:
    """Test ProjectInfo model."""
    
    def test_project_info_creation(self):
        """Test creating ProjectInfo instance."""
        info = ProjectInfo()
        assert info.languages == []
        assert info.frameworks == []
        assert info.dependencies == []
        assert info.package_managers == []
        assert info.config_files == []
        assert info.technologies == []
    
    def test_project_info_with_data(self):
        """Test ProjectInfo with data."""
        info = ProjectInfo(
            languages=["Python", "JavaScript"],
            frameworks=["FastAPI", "React"],
            dependencies=["fastapi", "react"],
            package_managers=["pip", "npm"],
            config_files=["pyproject.toml", "package.json"],
            technologies=["Docker"],
        )
        assert info.languages == ["Python", "JavaScript"]
        assert info.frameworks == ["FastAPI", "React"]
        assert "fastapi" in info.dependencies
        assert "pip" in info.package_managers


class TestProjectScanner:
    """Test ProjectScanner class."""
    
    def test_init(self):
        """Test ProjectScanner initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            scanner = ProjectScanner(workdir)
            assert scanner.workdir == workdir
    
    def test_scan_empty_directory(self):
        """Test scanning empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            scanner = ProjectScanner(workdir)
            
            result = scanner.scan()
            assert isinstance(result, ProjectInfo)
            assert result.languages == []
            assert result.frameworks == []
            assert result.dependencies == []
    
    def test_scan_python_project(self):
        """Test scanning Python project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            
            # Create Python files
            (workdir / "main.py").write_text("print('hello')")
            (workdir / "lib.py").write_text("def func(): pass")
            
            # Create requirements.txt
            requirements_content = """fastapi>=0.95.0
pytest>=7.0.0
# This is a comment
requests==2.28.1
numpy
"""
            (workdir / "requirements.txt").write_text(requirements_content)
            
            scanner = ProjectScanner(workdir)
            result = scanner.scan()
            
            assert "Python" in result.languages
            assert "pip" in result.package_managers
            assert "requirements.txt" in result.config_files
            assert "fastapi" in result.dependencies
            assert "pytest" in result.dependencies
            assert "requests" in result.dependencies
            assert "numpy" in result.dependencies
            assert "FastAPI" in result.frameworks
    
    def test_scan_javascript_project(self):
        """Test scanning JavaScript project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            
            # Create JS files
            (workdir / "index.js").write_text("console.log('hello')")
            (workdir / "app.jsx").write_text("import React from 'react'")
            
            # Create package.json
            package_json_content = """{
  "name": "test-project",
  "dependencies": {
    "react": "^18.0.0",
    "express": "^4.18.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "webpack": "^5.0.0"
  }
}"""
            (workdir / "package.json").write_text(package_json_content)
            
            scanner = ProjectScanner(workdir)
            result = scanner.scan()
            
            assert "JavaScript" in result.languages
            assert "npm" in result.package_managers
            assert "package.json" in result.config_files
            assert "react" in result.dependencies
            assert "express" in result.dependencies
            assert "jest" in result.dependencies
            assert "webpack" in result.dependencies
            assert "React" in result.frameworks
            assert "Express.js" in result.frameworks
    
    def test_scan_typescript_project(self):
        """Test scanning TypeScript project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            
            # Create TS files
            (workdir / "index.ts").write_text("const x: string = 'hello'")
            (workdir / "component.tsx").write_text("export const Component = () => <div/>")
            
            # Create tsconfig.json
            (workdir / "tsconfig.json").write_text('{"compilerOptions": {}}')
            
            scanner = ProjectScanner(workdir)
            result = scanner.scan()
            
            assert "TypeScript" in result.languages
            assert "tsconfig.json" in result.config_files
    
    def test_scan_rust_project(self):
        """Test scanning Rust project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            
            # Create Rust files
            (workdir / "main.rs").write_text("fn main() { println!(\"Hello\"); }")
            
            # Create Cargo.toml
            cargo_toml_content = """[package]
name = "test-project"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }

[dev-dependencies]
assert_cmd = "2.0"
"""
            (workdir / "Cargo.toml").write_text(cargo_toml_content)
            
            scanner = ProjectScanner(workdir)
            result = scanner.scan()
            
            assert "Rust" in result.languages
            assert "cargo" in result.package_managers
            assert "Cargo.toml" in result.config_files
            assert "serde" in result.dependencies
            assert "tokio" in result.dependencies
            assert "assert_cmd" in result.dependencies
    
    def test_scan_go_project(self):
        """Test scanning Go project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            
            # Create Go files
            (workdir / "main.go").write_text("package main\n\nfunc main() {}")
            
            # Create go.mod
            go_mod_content = """module test-project

go 1.19

require (
    github.com/gin-gonic/gin v1.9.0
    github.com/stretchr/testify v1.8.0
)
"""
            (workdir / "go.mod").write_text(go_mod_content)
            
            scanner = ProjectScanner(workdir)
            result = scanner.scan()
            
            assert "Go" in result.languages
            assert "go modules" in result.package_managers
            assert "go.mod" in result.config_files
            assert "github.com/gin-gonic/gin" in result.dependencies
            assert "github.com/stretchr/testify" in result.dependencies
    
    def test_scan_docker_project(self):
        """Test scanning project with Docker."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            
            # Create Docker files
            (workdir / "Dockerfile").write_text("FROM python:3.9\nCOPY . /app")
            (workdir / "docker-compose.yml").write_text("version: '3'\nservices:\n  app:\n    build: .")
            
            scanner = ProjectScanner(workdir)
            result = scanner.scan()
            
            assert "Docker" in result.technologies
            assert "Dockerfile" in result.config_files
            assert "docker-compose.yml" in result.config_files
    
    def test_parse_requirements_txt_with_versions(self):
        """Test parsing requirements.txt with various version specifiers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            scanner = ProjectScanner(workdir)
            
            req_file = workdir / "test_requirements.txt"
            req_content = """django>=3.2.0
flask==2.0.1
requests~=2.28.0
pytest!=7.0.0
numpy<=1.21.0
# comment line
-e git+https://github.com/user/repo.git#egg=package
"""
            req_file.write_text(req_content)
            
            deps = scanner._parse_requirements_txt(req_file)
            
            assert "django" in deps
            assert "flask" in deps
            assert "requests" in deps
            assert "pytest" in deps
            assert "numpy" in deps
            # Should not include comments or -e lines
            assert not any("-e" in dep for dep in deps)
    
    def test_framework_detection(self):
        """Test framework detection from dependencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            
            # Create Python project with Django
            (workdir / "main.py").write_text("import django")
            req_content = "django\ndjango-rest-framework\nnumpy\npandas\n"
            (workdir / "requirements.txt").write_text(req_content)
            
            scanner = ProjectScanner(workdir)
            result = scanner.scan()
            
            assert "Django" in result.frameworks
            assert "NumPy" in result.frameworks
            assert "Pandas" in result.frameworks