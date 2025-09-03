# qtuidoctools Modernization TODO

## Important: Parallelization

### Phase A: Core Parallel Processing
- [ ] Refactor UIDoc.updateXmlAndYaml() to be process-safe
- [ ] Implement parallel file discovery and batching  
- [ ] Create worker function for independent file processing
- [ ] Add process pool management with configurable worker count
- [ ] Add --workers CLI option to control parallelization level

### Phase B: Shared Resource Management  
- [ ] Implement TOC accumulation strategy using process-safe data structures
- [ ] Add file locking mechanisms for shared YAML/TOC files
- [ ] Create result consolidation pipeline in main process
- [ ] Ensure atomic operations for critical file updates
- [ ] Add graceful fallback to sequential processing on errors

### Phase C: Optimization and Monitoring
- [ ] Add progress reporting with file counts and timing information
- [ ] Implement adaptive batch sizing based on file sizes
- [ ] Add memory usage monitoring and limits
- [ ] Create performance profiling and benchmarking tools
- [ ] Add --benchmark flag for performance testing

### Phase D: Testing and Validation
- [ ] Create comprehensive tests with large UI file sets
- [ ] Add race condition and concurrency testing
- [ ] Implement performance benchmarking across different configurations
- [ ] Validate backwards compatibility with existing workflows
- [ ] Test error handling and recovery scenarios



## Testing Infrastructure

- [ ] Create tests/ directory structure
- [ ] Add pytest configuration to pyproject.toml
- [ ] Create test_qtui.py with UIDoc class tests
- [ ] Create test_qtuibuild.py with UIBuild class tests
- [ ] Create test_textutils.py with utility function tests
- [ ] Create test_cli.py with Fire CLI tests
- [ ] Add integration tests for full workflow
- [ ] Configure pytest-cov for coverage reporting
- [ ] Ensure >90% test coverage
- [ ] Run `pytest --cov=src/qtuidoctools` successfully

## Code Organization and Documentation

- [ ] Enhance docstrings for all public functions
- [ ] Update README.md with new build system and Fire CLI
- [ ] Update CLAUDE.md with new development workflow
- [ ] Add type hints where beneficial
- [ ] Create CHANGELOG.md with modernization changes
- [ ] Configure hatch scripts for common tasks
- [ ] Update this_file paths in all source files

## Final Verification and Testing

- [ ] Run full lint check: `ruff check .` (no errors)
- [ ] Run full format check: `ruff format .` (no changes)
- [ ] Run complete test suite: `pytest` (all pass)
- [ ] Build package: `hatch build` (success)
- [ ] Test fresh installation in new venv
- [ ] Verify all CLI commands work identically with Fire
- [ ] Test .ui file processing workflow
- [ ] Test YAML to JSON compilation
- [ ] Run post-edit Python commands from CLAUDE.md
- [ ] Verify no functionality regressions

## Critical Requirements

- [ ] Code must remain Python 3.11+ compliant
- [ ] Must use pyproject.toml with hatch-vcs
- [ ] Must use hatch for build system with src layout
- [ ] Must use ruff for linting and formatting
- [ ] Must use uv for dependency management
- [ ] Must use fire for CLI instead of click
- [ ] Code must remain clean and well-organized
- [ ] Code must be well-documented
- [ ] Code must be well-tested
- [ ] Code must be well-maintained
- [ ] MUST NOT break existing functionality
- [ ] Keep all changes surgical and minimal