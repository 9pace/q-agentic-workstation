"""
Project context system for Q Agentic Workstation.

Analyzes codebase to understand tech stack, patterns, and architecture.
Generates steering documents that guide agents.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from collections import Counter
import logging

logger = logging.getLogger(__name__)


@dataclass
class TechStack:
    """Detected technology stack."""

    languages: List[str]
    frameworks: List[str]
    package_managers: List[str]
    databases: List[str]
    tools: List[str]


@dataclass
class ProjectPatterns:
    """Detected code patterns and conventions."""

    file_structure: Dict[str, int]  # directory -> file count
    naming_conventions: List[str]
    common_patterns: List[str]
    test_framework: Optional[str]


@dataclass
class ProjectContext:
    """Complete project context."""

    project_root: str
    tech_stack: TechStack
    patterns: ProjectPatterns
    architecture: str
    constraints: List[str]
    project_type: str = "general"  # Added project_type with default

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ProjectContext":
        """Create from dictionary."""
        return cls(
            project_root=data["project_root"],
            tech_stack=TechStack(**data["tech_stack"]),
            patterns=ProjectPatterns(**data["patterns"]),
            architecture=data["architecture"],
            constraints=data["constraints"],
            project_type=data.get("project_type", "general"),  # Handle missing field
        )


class CodebaseAnalyzer:
    """Analyzes codebase to extract context."""

    # File patterns for tech detection
    TECH_INDICATORS = {
        "package.json": ["Node.js", "npm"],
        "requirements.txt": ["Python", "pip"],
        "Pipfile": ["Python", "pipenv"],
        "pyproject.toml": ["Python", "poetry"],
        "Cargo.toml": ["Rust", "cargo"],
        "go.mod": ["Go", "go modules"],
        "pom.xml": ["Java", "Maven"],
        "build.gradle": ["Java", "Gradle"],
        "Gemfile": ["Ruby", "bundler"],
        "composer.json": ["PHP", "composer"],
        "yarn.lock": ["Node.js", "yarn"],
        "pnpm-lock.yaml": ["Node.js", "pnpm"],
    }

    FRAMEWORK_INDICATORS = {
        "react": ["package.json", "React"],
        "next.js": ["next.config", "Next.js"],
        "vue": ["package.json", "Vue.js"],
        "angular": ["angular.json", "Angular"],
        "django": ["manage.py", "Django"],
        "flask": ["app.py", "Flask"],
        "fastapi": ["main.py", "FastAPI"],
        "express": ["package.json", "Express"],
        "rails": ["Gemfile", "Rails"],
    }

    DATABASE_INDICATORS = {
        "postgres": ["postgresql", "psycopg2", "pg"],
        "mysql": ["mysql", "pymysql"],
        "mongodb": ["mongodb", "mongoose", "pymongo"],
        "redis": ["redis"],
        "sqlite": ["sqlite3", "sqlite"],
    }

    def __init__(self, project_root: Path):
        """
        Initialize analyzer.

        Args:
            project_root: Root directory of project
        """
        self.project_root = project_root

    def analyze(self) -> ProjectContext:
        """
        Analyze project and generate context.

        Returns:
            ProjectContext with all detected information
        """
        logger.info(f"Analyzing project at {self.project_root}")

        tech_stack = self._detect_tech_stack()
        patterns = self._analyze_patterns()
        architecture = self._infer_architecture(patterns)
        constraints = self._generate_constraints(tech_stack, patterns)
        project_type = self._infer_project_type(tech_stack, patterns)

        return ProjectContext(
            project_root=str(self.project_root),
            tech_stack=tech_stack,
            patterns=patterns,
            architecture=architecture,
            constraints=constraints,
            project_type=project_type,
        )

    def _detect_tech_stack(self) -> TechStack:
        """Detect technologies used in project."""
        languages = set()
        frameworks = set()
        package_managers = set()
        databases = set()
        tools = set()

        # Check for config files
        for file_pattern, tech_info in self.TECH_INDICATORS.items():
            if self._file_exists(file_pattern):
                if len(tech_info) > 1:
                    languages.add(tech_info[0])
                    package_managers.add(tech_info[1])
                else:
                    languages.update(tech_info)

        # Detect languages by extension
        extension_counts = self._count_extensions()
        lang_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "JavaScript",
            ".tsx": "TypeScript",
            ".go": "Go",
            ".rs": "Rust",
            ".java": "Java",
            ".rb": "Ruby",
            ".php": "PHP",
            ".c": "C",
            ".cpp": "C++",
            ".cs": "C#",
        }

        for ext, count in extension_counts.items():
            if count > 2 and ext in lang_map:  # At least 3 files
                languages.add(lang_map[ext])

        # Detect frameworks
        frameworks.update(self._detect_frameworks())

        # Detect databases
        databases.update(self._detect_databases())

        return TechStack(
            languages=sorted(list(languages)),
            frameworks=sorted(list(frameworks)),
            package_managers=sorted(list(package_managers)),
            databases=sorted(list(databases)),
            tools=sorted(list(tools)),
        )

    def _detect_frameworks(self) -> Set[str]:
        """Detect frameworks used."""
        frameworks = set()

        # Check package.json for JS frameworks
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {
                        **data.get("dependencies", {}),
                        **data.get("devDependencies", {}),
                    }

                    if "react" in deps:
                        frameworks.add("React")
                    if "next" in deps:
                        frameworks.add("Next.js")
                    if "vue" in deps:
                        frameworks.add("Vue.js")
                    if "@angular/core" in deps:
                        frameworks.add("Angular")
                    if "express" in deps:
                        frameworks.add("Express")
            except:
                pass

        # Check requirements.txt for Python frameworks
        requirements = self.project_root / "requirements.txt"
        if requirements.exists():
            try:
                with open(requirements) as f:
                    content = f.read().lower()
                    if "django" in content:
                        frameworks.add("Django")
                    if "flask" in content:
                        frameworks.add("Flask")
                    if "fastapi" in content:
                        frameworks.add("FastAPI")
            except:
                pass

        return frameworks

    def _detect_databases(self) -> Set[str]:
        """Detect databases used."""
        databases = set()

        # Check package files
        for db_name, indicators in self.DATABASE_INDICATORS.items():
            for indicator in indicators:
                if self._search_in_files(
                    indicator, ["package.json", "requirements.txt", "Pipfile"]
                ):
                    databases.add(db_name.capitalize())
                    break

        return databases

    def _analyze_patterns(self) -> ProjectPatterns:
        """Analyze code patterns and structure."""
        file_structure = self._analyze_file_structure()
        naming_conventions = self._detect_naming_conventions()
        common_patterns = self._detect_common_patterns()
        test_framework = self._detect_test_framework()

        return ProjectPatterns(
            file_structure=file_structure,
            naming_conventions=naming_conventions,
            common_patterns=common_patterns,
            test_framework=test_framework,
        )

    def _analyze_file_structure(self) -> Dict[str, int]:
        """Analyze directory structure."""
        structure = {}

        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir() and not self._should_ignore(dir_path):
                rel_path = str(dir_path.relative_to(self.project_root))
                file_count = len(list(dir_path.glob("*")))
                structure[rel_path] = file_count

        return dict(sorted(structure.items(), key=lambda x: x[1], reverse=True)[:10])

    def _detect_naming_conventions(self) -> List[str]:
        """Detect naming conventions used."""
        conventions = []

        # Sample some Python/JS files
        sample_files = (
            list(self.project_root.rglob("*.py"))[:10]
            + list(self.project_root.rglob("*.js"))[:10]
        )

        for file_path in sample_files:
            if self._should_ignore(file_path):
                continue

            try:
                with open(file_path) as f:
                    content = f.read()

                    # Check for snake_case
                    if re.search(r"\b[a-z]+_[a-z]+\b", content):
                        conventions.append("snake_case")

                    # Check for camelCase
                    if re.search(r"\b[a-z]+[A-Z][a-z]+\b", content):
                        conventions.append("camelCase")

                    # Check for PascalCase
                    if re.search(r"\b[A-Z][a-z]+[A-Z][a-z]+\b", content):
                        conventions.append("PascalCase")
            except:
                pass

        return list(set(conventions))

    def _detect_common_patterns(self) -> List[str]:
        """Detect common code patterns."""
        patterns = []

        # Check for async/await
        if self._search_in_code(["async ", "await "]):
            patterns.append("Async/Await")

        # Check for classes
        if self._search_in_code(["class "]):
            patterns.append("OOP/Classes")

        # Check for functional patterns
        if self._search_in_code(["map(", "filter(", "reduce("]):
            patterns.append("Functional Programming")

        # Check for type hints
        if self._search_in_code([": str", ": int", ": List", ": Dict"]):
            patterns.append("Type Hints")

        return patterns

    def _detect_test_framework(self) -> Optional[str]:
        """Detect test framework used."""
        # Check for test files/directories
        if (self.project_root / "tests").exists() or (
            self.project_root / "test"
        ).exists():

            # Check for pytest
            if self._search_in_files("pytest", ["requirements.txt", "pyproject.toml"]):
                return "pytest"

            # Check for unittest
            if self._search_in_code(["import unittest"]):
                return "unittest"

            # Check for jest
            if self._search_in_files("jest", ["package.json"]):
                return "jest"

            # Check for mocha
            if self._search_in_files("mocha", ["package.json"]):
                return "mocha"

        return None

    def _infer_architecture(self, patterns: ProjectPatterns) -> str:
        """Infer architecture style from patterns."""
        structure = patterns.file_structure

        # Check for common architecture patterns
        if "src/components" in structure or "components" in structure:
            return "Component-based (likely frontend)"

        if "src/models" in structure and "src/views" in structure:
            return "MVC (Model-View-Controller)"

        if "api" in structure or "routes" in structure:
            return "API/REST architecture"

        if "services" in structure:
            return "Service-oriented"

        return "Monolithic"

    def _infer_project_type(
        self, tech_stack: TechStack, patterns: ProjectPatterns
    ) -> str:
        """Infer project type from tech stack and patterns."""
        # Check for specific project types
        if (
            "React" in tech_stack.frameworks
            or "Vue.js" in tech_stack.frameworks
            or "Angular" in tech_stack.frameworks
        ):
            return "frontend"

        if (
            "Django" in tech_stack.frameworks
            or "Flask" in tech_stack.frameworks
            or "FastAPI" in tech_stack.frameworks
        ):
            return "backend"

        if "Express" in tech_stack.frameworks:
            return "api"

        if tech_stack.databases:
            return "fullstack"

        if patterns.test_framework:
            return "library"

        return "general"

    def _generate_constraints(
        self, tech_stack: TechStack, patterns: ProjectPatterns
    ) -> List[str]:
        """Generate project constraints."""
        constraints = [
            "Maximum 50 lines per change",
            "One feature at a time",
            "No refactoring unless explicitly requested",
        ]

        # Add tech-specific constraints
        if "Python" in tech_stack.languages:
            constraints.append("Follow PEP 8 style guide")
            if patterns.test_framework:
                constraints.append(f"Write tests using {patterns.test_framework}")

        if "TypeScript" in tech_stack.languages:
            constraints.append("Maintain type safety")

        if patterns.test_framework:
            constraints.append("Every change must be testable")

        return constraints

    # Helper methods

    def _file_exists(self, pattern: str) -> bool:
        """Check if file matching pattern exists."""
        return len(list(self.project_root.glob(pattern))) > 0

    def _count_extensions(self) -> Counter:
        """Count files by extension."""
        extensions = Counter()

        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self._should_ignore(file_path):
                extensions[file_path.suffix] += 1

        return extensions

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        ignore_patterns = [
            "node_modules",
            ".git",
            "__pycache__",
            ".qaw",
            "venv",
            ".venv",
            "env",
            "dist",
            "build",
            ".pytest_cache",
            ".mypy_cache",
            "coverage",
        ]

        path_str = str(path)
        return any(pattern in path_str for pattern in ignore_patterns)

    def _search_in_files(self, text: str, filenames: List[str]) -> bool:
        """Search for text in specific files."""
        for filename in filenames:
            file_path = self.project_root / filename
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        if text in f.read():
                            return True
                except:
                    pass
        return False

    def _search_in_code(self, patterns: List[str]) -> bool:
        """Search for patterns in code files."""
        extensions = [".py", ".js", ".ts", ".jsx", ".tsx"]

        for ext in extensions:
            for file_path in list(self.project_root.rglob(f"*{ext}"))[
                :20
            ]:  # Sample 20 files
                if self._should_ignore(file_path):
                    continue

                try:
                    with open(file_path) as f:
                        content = f.read()
                        if any(pattern in content for pattern in patterns):
                            return True
                except:
                    pass

        return False


class ContextManager:
    """Manages project context and steering documents."""

    def __init__(self, workspace_dir: Path):
        """
        Initialize context manager.

        Args:
            workspace_dir: QAW workspace directory (.qaw)
        """
        self.workspace_dir = workspace_dir
        self.context_dir = workspace_dir / "context"
        self.context_dir.mkdir(parents=True, exist_ok=True)

        self.project_root = workspace_dir.parent
        self.analyzer = CodebaseAnalyzer(self.project_root)

    def initialize(self, force: bool = False) -> ProjectContext:
        """
        Initialize context by analyzing project.

        Args:
            force: Force re-analysis even if context exists

        Returns:
            ProjectContext
        """
        context_file = self.context_dir / "project_context.json"

        # Load existing if available and not forcing
        if not force and context_file.exists():
            logger.info("Loading existing project context")
            with open(context_file) as f:
                return ProjectContext.from_dict(json.load(f))

        # Analyze project
        logger.info("Analyzing project to generate context...")
        context = self.analyzer.analyze()

        # Save context
        with open(context_file, "w") as f:
            json.dump(context.to_dict(), f, indent=2)

        # Generate steering documents
        self._generate_steering_documents(context)

        logger.info(f"Project context initialized in {self.context_dir}")
        return context

    def get_context(self) -> Optional[ProjectContext]:
        """Get existing context."""
        context_file = self.context_dir / "project_context.json"
        if context_file.exists():
            with open(context_file) as f:
                return ProjectContext.from_dict(json.load(f))
        return None

    def _generate_steering_documents(self, context: ProjectContext):
        """Generate steering documents from context."""

        # 1. Project Rules
        self._write_project_rules(context)

        # 2. Architecture
        self._write_architecture(context)

        # 3. Coding Standards
        self._write_coding_standards(context)

        # 4. Constraints
        self._write_constraints(context)

        # 5. Verification Rules
        self._write_verification_rules(context)

    def _write_project_rules(self, context: ProjectContext):
        """Write project rules document."""
        content = f"""# Project Rules

## Technology Stack
{self._format_list(context.tech_stack.languages, 'Languages')}
{self._format_list(context.tech_stack.frameworks, 'Frameworks')}
{self._format_list(context.tech_stack.databases, 'Databases')}

## Project Structure
"""

        for dir_name, count in list(context.patterns.file_structure.items())[:5]:
            content += f"- `{dir_name}/` ({count} files)\n"

        content += f"""
## Test Framework
{context.patterns.test_framework or 'Not detected'}

## Architecture
{context.architecture}

## Guidelines
- Follow existing patterns and conventions
- Maintain consistency with current codebase
- Ensure all changes are testable
- Document significant changes
"""

        (self.context_dir / "project_rules.md").write_text(content)

    def _write_architecture(self, context: ProjectContext):
        """Write architecture document."""
        content = f"""# Architecture

## Current Architecture
{context.architecture}

## Directory Structure
"""
        for dir_name, count in context.patterns.file_structure.items():
            content += f"- `{dir_name}/`: {count} files\n"

        content += """
## Patterns Observed
"""
        for pattern in context.patterns.common_patterns:
            content += f"- {pattern}\n"

        content += """
## Guidelines
- Maintain existing architectural patterns
- Don't introduce new layers without discussion
- Keep separation of concerns
- Follow single responsibility principle
"""

        (self.context_dir / "architecture.md").write_text(content)

    def _write_coding_standards(self, context: ProjectContext):
        """Write coding standards document."""
        content = """# Coding Standards

## Naming Conventions
"""
        for convention in context.patterns.naming_conventions:
            content += f"- Use {convention} where appropriate\n"

        if "Python" in context.tech_stack.languages:
            content += """
## Python Standards
- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Keep functions under 50 lines
"""

        if (
            "TypeScript" in context.tech_stack.languages
            or "JavaScript" in context.tech_stack.languages
        ):
            content += """
## JavaScript/TypeScript Standards
- Use const/let, not var
- Prefer arrow functions
- Use async/await over callbacks
- Add JSDoc comments
"""

        content += """
## General
- Clear variable names
- No magic numbers
- Comment complex logic
- Keep files under 300 lines
"""

        (self.context_dir / "coding_standards.md").write_text(content)

    def _write_constraints(self, context: ProjectContext):
        """Write constraints document."""
        content = """# Project Constraints

## Scope Control
"""
        for constraint in context.constraints:
            content += f"- {constraint}\n"

        content += """
## Forbidden Actions
- Don't change files outside task scope
- Don't add dependencies without approval
- Don't modify architecture without discussion
- Don't introduce new patterns

## Required Checks
- Every change must be testable
- Every change must be reversible
- Every change must align with intent
"""

        (self.context_dir / "constraints.md").write_text(content)

    def _write_verification_rules(self, context: ProjectContext):
        """Write verification rules document."""
        content = f"""# Verification Rules

## Alignment Check
- Does the code match the original request?
- Are there any scope creep additions?
- Is the implementation focused and minimal?

## Code Quality Check
- Does code follow project patterns?
- Are naming conventions consistent?
- Is the code style appropriate?

## Test Verification
"""
        if context.patterns.test_framework:
            content += f"- Tests must use {context.patterns.test_framework}\n"

        content += """- All logic changes require tests
- Tests must pass before acceptance
- Test coverage should be maintained

## Success Criteria
- All 3 verification stages pass
- No linting errors
- Tests pass
- Code is reviewable
"""

        (self.context_dir / "verification_rules.md").write_text(content)

    def _format_list(self, items: List[str], title: str) -> str:
        """Format list with title."""
        if not items:
            return f"**{title}**: None detected\n"
        return f"**{title}**: {', '.join(items)}\n"
