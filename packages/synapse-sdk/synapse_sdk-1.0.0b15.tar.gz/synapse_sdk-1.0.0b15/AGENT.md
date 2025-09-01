# Synapse SDK Development Guide

Always follow the instructions in plan.md. When I say "go", find the next unmarked test in plan.md, implement the test, then implement only enough code to make that test pass.

## Overall Engineering Principle

### ROLE AND EXPERTISE

You are a senior software engineer who follows Kent Beck's Test-Driven Development (TDD) and Tidy First principles. Your purpose is to guide development following these methodologies precisely.

### CORE DEVELOPMENT PRINCIPLES

- Always follow the TDD cycle: Red → Green → Refactor
- Write the simplest failing test first
- Implement the minimum code needed to make tests pass
- Refactor only after tests are passing
- Follow Beck's "Tidy First" approach by separating structural changes from behavioral changes
- Maintain high code quality throughout development

### TDD METHODOLOGY GUIDANCE

- Start by writing a failing test that defines a small increment of functionality
- Use meaningful test names that describe behavior (e.g., "shouldSumTwoPositiveNumbers")
- Make test failures clear and informative
- Write just enough code to make the test pass - no more
- Once tests pass, consider if refactoring is needed
- Repeat the cycle for new functionality
- When fixing a defect, first write an API-level failing test then write the smallest possible test that replicates the problem then get both tests to pass.

### TIDY FIRST APPROACH

- Separate all changes into two distinct types:
  1. STRUCTURAL CHANGES: Rearranging code without changing behavior (renaming, extracting methods, moving code)
  2. BEHAVIORAL CHANGES: Adding or modifying actual functionality
- Never mix structural and behavioral changes in the same commit
- Always make structural changes first when both are needed
- Validate structural changes do not alter behavior by running tests before and after

### COMMIT DISCIPLINE

- Only commit when:
  1. ALL tests are passing
  2. ALL compiler/linter warnings have been resolved
  3. The change represents a single logical unit of work
  4. Commit messages clearly state whether the commit contains structural or behavioral changes
- Use small, frequent commits rather than large, infrequent ones

### CODE QUALITY STANDARDS

- Eliminate duplication ruthlessly
- Express intent clearly through naming and structure
- Make dependencies explicit
- Keep methods small and focused on a single responsibility
- Minimize state and side effects
- Use the simplest solution that could possibly work

### REFACTORING GUIDELINES

- Refactor only when tests are passing (in the "Green" phase)
- Use established refactoring patterns with their proper names
- Make one refactoring change at a time
- Run tests after each refactoring step
- Prioritize refactorings that remove duplication or improve clarity

### EXAMPLE WORKFLOW

When approaching a new feature:

1. Write a simple failing test for a small part of the feature
2. Implement the bare minimum to make it pass
3. Run tests to confirm they pass (Green)
4. Make any necessary structural changes (Tidy First), running tests after each change
5. Commit structural changes separately
6. Add another test for the next small increment of functionality
7. Repeat until the feature is complete, committing behavioral changes separately from structural ones

Follow this process precisely, always prioritizing clean, well-tested code over quick implementation.

Always write one test at a time, make it run, then improve structure. Always run all the tests (except long-running tests) each time.

## Project Core Features

## Synapse SDK Overview

A Python SDK for building and managing ML plugins, data annotation workflows, and AI agents.

## Core Features

- **🔌 Plugin System**: Create and manage ML plugins with categories like neural networks, data validation, and export tools
- **🤖 Agent Management**: Backend and Ray-based agent clients for distributed AI workflows  
- **🔄 Data Converters**: Convert between formats (COCO, Pascal VOC, YOLO) and annotation schemas
- **🛠️ Development Tools**: Interactive web dashboard for monitoring and debugging
- **⚡ CLI Interface**: Command-line tool for configuration, plugin management, and development

## 🔌 Plugin System (`synapse_sdk/plugins`)

The plugin system provides a comprehensive framework for building and managing ML plugins across different categories and execution methods.

### Plugin Categories

1. **Neural Networks** (`neural_net/`)
   - Actions: `deployment`, `gradio`, `inference`, `test`, `train`, `tune`
   - Base classes for inference operations
   - Template generation for ML model plugins

2. **Export** (`export/`)
   - Actions: `export`
   - Data export functionality with configurable formats
   - Template-based plugin generation

3. **Upload** (`upload/`)
   - Actions: `upload`
   - File and data upload capabilities
   - Integration with various storage providers

4. **Smart Tools** (`smart_tool/`)
   - Actions: `auto_label`
   - Automated labeling and annotation tools
   - AI-powered data processing

5. **Pre-annotation** (`pre_annotation/`)
   - Actions: `pre_annotation`, `to_task`
   - Data preparation before annotation
   - Task conversion utilities

6. **Post-annotation** (`post_annotation/`)
   - Actions: `post_annotation`
   - Data processing after annotation
   - Quality assurance and validation

7. **Data Validation** (`data_validation/`)
   - Actions: `validation`
   - Data quality checks and validation rules
   - Schema validation and integrity checks

### Plugin Execution Methods

- **Job**: Ray Job-based execution for distributed processing
- **Task**: Ray Task-based execution for simple operations  
- **REST API**: Ray Serve-based execution for web API endpoints

### Key Components

- **Plugin Models**: `PluginRelease` and `Run` classes for plugin lifecycle management
- **Action Base Class**: Unified interface for all plugin actions with validation, logging, and execution
- **Template System**: Cookiecutter-based plugin generation with standardized structure
- **Registry System**: Dynamic plugin discovery and registration
- **Upload System**: Automated packaging and deployment to storage backends

### Plugin Configuration

Each plugin includes:

- `config.yaml`: Plugin metadata, actions, and dependencies
- `plugin/`: Source code with action implementations
- `requirements.txt`: Python dependencies
- Template-based scaffolding for rapid development

## 📚 Documentation Management

The project uses **Docusaurus** for documentation with a structured approach:

### Documentation Structure

- **Implementation**: `synapse_sdk/devtools/docs/` - Docusaurus application
- **Content**: `docs/` - Markdown documentation files
- **Configuration**: `synapse_sdk/devtools/docs/docusaurus.config.ts`

### Key Directories

```
synapse_sdk/devtools/docs/    # Docusaurus implementation
├── package.json              # Dependencies and scripts
├── docusaurus.config.ts      # Main configuration
├── sidebars.ts               # Navigation structure
├── src/                      # React components and styling
└── static/                   # Static assets (images, logos)

docs/                         # Documentation content
├── introduction.md           # Main landing page
├── installation.md           # Setup instructions
├── quickstart.md            # Getting started guide
├── api/                     # API reference docs
├── features/                # Feature documentation
├── concepts/                # Core concepts
├── examples/                # Code examples
├── tutorial-basics/         # Basic tutorials
├── tutorial-extras/        # Advanced tutorials
└── i18n/                    # Internationalization (Korean)
```

### Available Commands

From `synapse_sdk/devtools/docs/`:

```bash
# Development server
npm start

# Build static site
npm run build

# Serve built site
npm run serve

# Clear cache
npm run clear

# Type checking
npm run typecheck
```

### Documentation Workflow

1. **Content Creation**: Add/edit `.md` files in `docs/`
2. **Navigation**: Update `sidebars.ts` for new sections
3. **Testing**: Run `npm start` to preview changes
4. **Building**: Use `npm run build` for production builds

### Configuration Features

- **Multi-language**: English (default) and Korean support
- **Custom Styling**: Located in `src/css/custom.css`
- **GitHub Integration**: Links to repository
- **Search**: Built-in documentation search
- **Responsive Design**: Mobile-friendly navigation

### Content Guidelines

- Use frontmatter for metadata:
  ```yaml
  ---
  id: page-id
  title: Page Title
  sidebar_position: 1
  ---
  ```
- Follow existing structure for API docs in `docs/api/`
- Add code examples in appropriate language blocks
- Include cross-references using relative paths

### Multi-Language Documentation Requirements

**All documentation must be maintained in both English and Korean:**

1. **Primary Language**: English is the primary language for all documentation
2. **Required Translation**: Every new document must have a corresponding Korean translation
3. **File Structure**: 
   - English documents: `docs/[file].md`
   - Korean documents: `docs/i18n/ko/docusaurus-plugin-content-docs/current/[file].md`
4. **Content Consistency**: Korean translations must maintain the same structure, sections, and information as English versions
5. **Technical Terms**: Keep technical terms like "Synapse SDK", "API", "CLI", "GitHub" in English within Korean documents
6. **Code Examples**: All code examples, commands, and file paths must remain unchanged in Korean versions
7. **Update Process**: When updating documentation:
   - Update the English version first
   - Update the corresponding Korean version immediately after
   - Ensure both versions maintain content parity
8. **Review Requirement**: Both English and Korean versions must be reviewed for accuracy and consistency

## 🔧 Code Formatting with Ruff

Claude Code should format all Python code changes using **Ruff** to maintain consistent code style across the project.

### When to Format Code

- **Before committing**: Always format code before creating commits
- **After code changes**: Format immediately after writing or modifying Python code
- **During code reviews**: Ensure all code follows consistent formatting standards

### Ruff Commands

```bash
# Format all Python files in the project
ruff format .

# Format specific file
ruff format path/to/file.py

# Check for formatting issues without applying changes
ruff format --check .

# Check and fix linting issues
ruff check --fix .

# Check linting without fixing
ruff check .
```

### Formatting Workflow

1. **Make code changes** - Write or modify Python code
2. **Format with Ruff** - Run `ruff format .` to apply consistent formatting
3. **Fix linting issues** - Run `ruff check --fix .` to resolve code quality issues
4. **Verify changes** - Review the formatted code to ensure it's correct
5. **Commit changes** - Create commits with properly formatted code

### Integration with Development

- **IDE Setup**: Configure your IDE to run Ruff on save
- **Pre-commit Hooks**: Use Ruff in pre-commit hooks to enforce formatting
- **CI/CD Pipeline**: Include Ruff checks in continuous integration

### Ruff Configuration

The project uses Ruff configuration defined in `pyproject.toml`:

- **Line length**: Follow project-specific line length settings
- **Import sorting**: Automatic import organization and sorting
- **Code style**: Consistent formatting rules across the codebase
- **Linting rules**: Comprehensive code quality checks

### Best Practices

- **Run before commit**: Always run `ruff format .` and `ruff check --fix .` before committing
- **Review changes**: Check that Ruff's changes don't alter code logic
- **Consistent style**: Let Ruff handle formatting so you can focus on functionality
- **Team consistency**: Ensures all contributors follow the same code style

## Code Review Rules

Code review rules are organized by priority level and stored in separate files for better maintainability and modularity.

### Priority Levels

- **[P1_rules.md](P1_rules.md)** - Security and Stability (Critical)
- **[P2_rules.md](P2_rules.md)** - Core Functionality (High)  
- **[P3_rules.md](P3_rules.md)** - Best Practices (Medium)
- **[P4_rules.md](P4_rules.md)** - Code Style (Low)

### Using the Review Rules

1. **Start with P1**: Address security and stability issues first
2. **Progress through priorities**: P1 → P2 → P3 → P4
3. **Use review-pr command**: `synapse review pr` loads and displays all rules automatically
4. **Reference specific files**: Review individual priority files as needed

### Required Checklist Before Review

**Before submitting for review, ensure:**

```bash
# 1. Format all Python code
ruff format .

# 2. Fix linting issues
ruff check --fix .

# 3. Verify no remaining issues
ruff check .

# 4. Run all tests
pytest

# 5. Check test coverage
pytest --cov=synapse_sdk
```

**Pull Request Requirements:**
- [ ] Clear, descriptive title
- [ ] Detailed description with motivation
- [ ] Reference to related GitHub issues
- [ ] All tests pass locally
- [ ] Code formatted with Ruff
- [ ] Documentation updated for user-facing changes
- [ ] Changelog entry added for significant changes

### Review Process

1. **Automated Checks** - CI/CD pipeline validates formatting, linting, and tests
2. **P1 Review** - Focus on security and critical stability issues first
3. **P2 Review** - Verify functionality, architecture, and performance
4. **P3 Review** - Check best practices and maintainability
5. **P4 Review** - Final style and formatting verification

### Review Response Guidelines

- Address all reviewer comments
- Ask for clarification if feedback is unclear
- Make requested changes promptly
- Re-run formatting and tests after changes
- Update documentation as needed

## 🌐 Synapse Backend API Reference

This section documents the Synapse Backend API endpoints and data structures discovered through exploration and implementation.

### API Root Endpoints

The API root (`https://api.test.synapse.sh/`) returns a comprehensive list of available endpoints:

```json
{
    "agents": "https://api.test.synapse.sh/agents/",
    "jobs": "https://api.test.synapse.sh/jobs/",
    "serve_applications": "https://api.test.synapse.sh/serve_applications/",
    "plugins": "https://api.test.synapse.sh/plugins/",
    "plugin_releases": "https://api.test.synapse.sh/plugin_releases/",
    "storages": "https://api.test.synapse.sh/storages/",
    "data_collections": "https://api.test.synapse.sh/data_collections/",
    // ... and many more
}
```

### Authentication

All API requests require authentication using the `SYNAPSE-Access-Token` header:

```bash
curl -H "SYNAPSE-Access-Token: Token YOUR_TOKEN_HERE" \
     -H "Accept: application/json" \
     https://api.test.synapse.sh/endpoint/
```

### Key API Endpoints

#### 1. Agents API (`/agents/`)

**GET /agents/{id}/** - Retrieve agent details

Response structure:
```json
{
    "id": 1,
    "name": "기본 에이전트",
    "url": "http://10.0.22.1:8000",
    "status": "connected",
    "status_display": "Connected",
    "is_connected": true,
    "is_active": true,
    "service_provider": "datamaker",
    "service_provider_display": "datamaker cloud",
    "last_connected": "2025-08-04T13:29:08.106889+09:00",
    "nodes": [
        {
            "id": "node_id",
            "status": "ALIVE",
            "host_name": "synapse-agent-test",
            "ip": "10.0.22.1",
            "cpu": {...},
            "memory": {...},
            "disk": {...},
            "gpus": [...]
        }
    ]
}
```

#### 2. Plugin Releases API (`/plugin_releases/`)

**GET /plugin_releases/{id}/** - Retrieve plugin release details

Response structure:
```json
{
    "id": 26,
    "plugin": 20,  // References the plugin ID
    "version": "0.1.3",
    "config": {
        "code": "yolov8",
        "name": "yolov8",
        "tasks": ["image.object_detection"],
        "actions": {...},
        "category": "neural_net",
        // ... other config fields
    },
    "readme": "# Plugin documentation...",
    "created": "2025-06-10T10:51:52.814743+09:00"
}
```

#### 3. Plugins API (`/plugins/`)

**GET /plugins/** - List all plugins

Response structure:
```json
{
    "count": 33,
    "next": "https://api.test.synapse.sh/plugins/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "익스포트 기본 테스트",
            "code": "test_export2",
            "category": "export",
            "category_display": "내보내기",
            "latest_version": "0.3.0",
            "is_public": true,
            "is_active": true,
            "maintainers": [...],
            "created": "2025-06-10T10:51:52.814743+09:00"
        }
    ]
}
```

**GET /plugins/{id}/** - Retrieve specific plugin details

#### 4. Jobs API (`/jobs/`)

**GET /jobs/** - List jobs with optional filtering

Query parameters:
- `agent`: Filter by agent ID

Response includes job details with plugin_release reference.

#### 5. Serve Applications API (`/serve_applications/`)

**GET /serve_applications/** - List serve applications

Query parameters:
- `agent`: Filter by agent ID

Response includes deployment details with plugin_release and agent references.

### Data Enrichment Pattern

When displaying plugin and agent information in the UI, follow this enrichment pattern:

1. **Fetch primary data** (jobs, serve applications, etc.)
2. **For each plugin_release ID**:
   - Fetch `/plugin_releases/{id}/` to get version and plugin ID
   - Fetch `/plugins/{plugin_id}/` to get plugin name and code
3. **For each agent ID**:
   - Fetch `/agents/{id}/` to get agent name and URL

### Configuration Storage

The SDK stores configuration in `~/.config/synapse/devtools.json`:

```json
{
    "backend": {
        "host": "https://api.test.synapse.sh",
        "token": "syn_xxx"
    },
    "agent": {
        "id": 1,
        "name": "기본 에이전트",
        "url": "http://10.0.22.1:8000",
        "token": "xxx"
    },
    "plugin_storage": "s3://..."
}
```

### Implementation Notes

1. **API Response Handling**:
   - Most endpoints return paginated responses with `count`, `next`, `previous`, and `results` fields
   - Handle both direct array responses and paginated responses
   - Korean text is common in responses (내보내기, 기본 에이전트, etc.)

2. **Error Handling**:
   - 404 responses return `{"detail": "찾을 수 없습니다."}` (Not found in Korean)
   - Always wrap API calls in try-except blocks for resilience

3. **Performance Optimization**:
   - Cache frequently accessed data (plugins, agents) to reduce API calls
   - Use batch fetching where possible
   - Consider implementing local caching for plugin and agent metadata

4. **Display Patterns**:
   - Plugins: Show `{name} (v{version})` when available
   - Agents: Show `{name} @ {url}` when available
   - Always provide fallbacks when names aren't available