# qtuidoctools Modernization Plan

## Project Overview and Objectives

This plan addresses the modernization of the qtuidoctools project to ensure Python 3.11+ compliance, modern packaging standards, and best development practices. The project is a Qt UI documentation tool that extracts widgets from .ui files and generates YAML documentation and JSON help files.

**Critical Constraint**: The code currently works and MUST remain functional. All changes are surgical improvements, not refactoring.

## Current State Analysis

### Issues Identified from issue101.txt
- **F403**: Star imports (`from .qtui import *`, `from .qtuibuild import *`) causing undefined name detection issues
- **F405**: Undefined names due to star imports (`getUiPaths`, `sys`, `UIDoc`, `OrderedDict`, `UIBuild`)
- **F811**: Function redefinition (duplicate `update` function at lines 131 and 233)
- **Missing Tests**: No test files found, pytest collecting 0 items
- **Deprecated setup.py**: Currently using setup.py instead of modern pyproject.toml

### Current Project Structure
```
qtuidoctools/
├── qtuidoctools/
│   ├── __init__.py          # Package metadata, version 0.8.3
│   ├── __main__.py          # CLI interface with Click
│   ├── qtui.py              # Core UI processing logic
│   ├── qtuibuild.py         # Build system for YAML→JSON
│   ├── textutils.py         # Text processing utilities
│   └── keymap_db.py         # Keyboard mapping utilities
├── setup.py                 # Legacy packaging (to be replaced)
├── README.md               # Project documentation
└── CLAUDE.md               # Project instructions
```

## Technical Architecture Decisions

### 1. Packaging System Migration
- **From**: setup.py with setuptools
- **To**: pyproject.toml with hatch build backend
- **Rationale**: Modern Python packaging standards, better dependency management, unified configuration

### 2. Linting and Formatting
- **Linter**: Ruff (replacing flake8, isort, pyupgrade)
- **Formatter**: Ruff format (replacing black)
- **Type Checker**: Keep existing type hints, add mypy configuration
- **Rationale**: Fast, comprehensive, single tool approach

### 3. Dependency Management
- **Tool**: uv for fast package installation
- **Virtual Environment**: uv venv for project isolation
- **Lock Files**: uv.lock for reproducible builds

### 4. Testing Framework
- **Framework**: pytest (add comprehensive test suite)
- **Coverage**: pytest-cov for code coverage reporting
- **Structure**: tests/ directory with unit tests for each module

### 5. CLI Framework Migration
- **From**: Click-based command-line interface
- **To**: Fire-based CLI for simpler, more pythonic interface
- **Rationale**: Fire automatically generates CLI from Python functions, reducing boilerplate and improving maintainability
- **Benefits**: Less code to maintain, automatic help generation, better Python integration

## Outstanding Implementation Plan

### Phase 3: Testing Infrastructure
**Objective**: Add comprehensive test coverage for existing functionality

#### 3.1 Test Structure Setup
- **Directory**: tests/ with proper structure
- **Configuration**: pytest configuration in pyproject.toml
- **Coverage**: pytest-cov integration for coverage reporting

#### 3.2 Core Module Tests
- **qtui.py tests**: Test UIDoc class, widget extraction, YAML processing
- **qtuibuild.py tests**: Test UIBuild class, JSON compilation, text processing
- **textutils.py tests**: Test text processing utilities
- **CLI tests**: Test command-line interface with Click testing utilities

#### 3.3 Integration Tests
- **Full workflow tests**: End-to-end testing with sample .ui files
- **YAML↔JSON roundtrip**: Verify data integrity through processing pipeline
- **Error handling**: Test edge cases and error conditions

### Phase 4: CLI Framework Migration
**Objective**: Migrate from Click to Fire for simplified CLI interface

#### 4.1 Fire Framework Integration
- **Remove Click dependency**: Replace click with fire in dependencies
- **Simplify CLI structure**: Convert Click decorators to simple Python functions
- **Maintain command compatibility**: Ensure all existing commands work identically
- **Update help system**: Leverage Fire's automatic help generation

#### 4.2 CLI Code Refactoring
- **Function-based approach**: Convert Click commands to plain Python functions
- **Argument handling**: Use Fire's automatic argument parsing
- **Error handling**: Maintain existing error handling patterns
- **Testing updates**: Update CLI tests to work with Fire

### Phase 5: Code Organization and Documentation
**Objective**: Improve code organization while maintaining functionality

#### 5.1 Import Structure Refinement
- **Explicit imports**: Replace all star imports with specific function imports
- **Module interfaces**: Clean up __all__ exports in each module
- **Type hints**: Enhance existing type annotations where beneficial

#### 5.2 Documentation Improvements
- **Docstrings**: Ensure all public functions have clear docstrings
- **README updates**: Reflect new build system and development workflow
- **CHANGELOG**: Document all changes made during modernization

#### 5.3 Development Workflow
- **Scripts**: Hatch scripts for common tasks (test, lint, build, publish)
- **Pre-commit hooks**: Optional git hooks for code quality
- **CI/CD ready**: Configuration that supports automated testing

## Outstanding Implementation Steps

### Step 4: CLI Framework Migration
1. **Update dependencies**:
   - Remove click from project.dependencies in pyproject.toml
   - Add fire to project.dependencies
2. **Refactor __main__.py**:
   - Remove all Click decorators (@click.command, @click.option, etc.)
   - Convert commands to simple Python functions
   - Replace Click context handling with direct arguments
   - Update entry point to use fire.Fire()
3. **Maintain command compatibility**:
   - Ensure update, build, cleanup commands work identically
   - Test all argument combinations work as before
4. **Update tests**:
   - Modify test_cli.py to work with Fire instead of Click's CliRunner

### Step 5: Add Testing
1. Create tests/ directory structure
2. Add test_qtui.py with UIDoc tests
3. Add test_qtuibuild.py with UIBuild tests  
4. Add test_cli.py with CLI tests
5. Configure pytest in pyproject.toml
6. Test: `pytest` should pass

### Step 6: Verification and Documentation
1. Run full lint: `ruff check --fix .`
2. Run full format: `ruff format .`
3. Run tests: `pytest --cov=qtuidoctools`
4. Build package: `hatch build`
5. Test installation: `uv pip install dist/*.whl`
6. Update CHANGELOG.md with all changes

## Testing and Validation Criteria

### Functionality Preservation
- **CLI Commands**: All existing commands work identically
- **File Processing**: .ui files process correctly to YAML
- **Build Process**: YAML files compile correctly to JSON
- **Output Format**: Generated files maintain same structure and content

### Code Quality Standards
- **Ruff Clean**: `ruff check .` reports no errors
- **Format Consistent**: `ruff format .` makes no changes
- **Tests Pass**: `pytest` passes with high coverage (>90%)
- **Build Success**: `hatch build` creates valid wheel and sdist

### Modern Standards Compliance
- **Python 3.11+**: Code uses modern Python features appropriately
- **PEP 517**: Build system follows modern packaging standards
- **Type Hints**: Existing type annotations are preserved and enhanced
- **Documentation**: All public APIs are documented

## Risk Assessment and Mitigation

### High Risk Items
1. **Star Import Replacement**: May break if imports are missed
   - **Mitigation**: Careful analysis of what each star import provides
   - **Testing**: Thorough CLI testing after changes

2. **Function Redefinition Fix**: Duplicate `update` functions need careful handling
   - **Mitigation**: Analyze both functions to understand intended behavior
   - **Testing**: Test both CLI commands that use these functions

3. **Dependency Changes**: Moving from setup.py to pyproject.toml dependencies
   - **Mitigation**: Verify all dependencies are correctly specified
   - **Testing**: Fresh virtual environment installation test

### Medium Risk Items
1. **Ruff Configuration**: Too aggressive linting rules might require code changes
   - **Mitigation**: Start with conservative rules, enable incrementally
   - **Rollback**: Can adjust configuration if issues arise

2. **Test Coverage**: Adding tests might reveal existing bugs
   - **Mitigation**: Focus on testing current behavior, not ideal behavior
   - **Documentation**: Document any discovered limitations

## Future Considerations

### Post-Modernization Improvements (Out of Scope)
- **Async Support**: Consider async file processing for large projects
- **Plugin System**: Extensible text processing plugins
- **Configuration Files**: User-configurable processing options
- **Performance Optimization**: Profile and optimize for large UI projects

### Maintenance Strategy
- **Regular Updates**: Keep dependencies updated with dependabot
- **Monitoring**: Set up basic CI/CD for automated testing
- **Documentation**: Maintain clear development setup instructions
- **Version Management**: Use semantic versioning for releases

## Success Metrics

1. **Zero Functional Regressions**: All existing functionality works identically
2. **Clean Linting**: No ruff errors or warnings
3. **High Test Coverage**: >90% line coverage with meaningful tests
4. **Fast Development**: Modern tooling speeds up development workflow
5. **Easy Onboarding**: New developers can quickly understand and contribute
6. **Maintainable Codebase**: Clear imports, documented functions, organized structure

This plan ensures qtuidoctools evolves to modern Python standards while maintaining its proven functionality and reliability.