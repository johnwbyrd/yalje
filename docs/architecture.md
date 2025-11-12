# yalje Architecture

## Overview

yalje is designed as a modular system with clear separation of concerns:

1. **Core** - Authentication, session management, configuration
2. **API Clients** - Download data from LiveJournal
3. **Parsers** - Parse XML/HTML responses
4. **Models** - Pydantic models for data validation
5. **Exporters** - Serialize data to various formats
6. **CLI** - Command-line interface
7. **Utils** - Common utilities

## Data Flow

```
User Input (CLI)
      ↓
   Config
      ↓
Authentication → Session
      ↓
API Clients → HTTP Requests → LiveJournal
      ↓
Raw XML/HTML Responses
      ↓
   Parsers
      ↓
Pydantic Models (validated)
      ↓
  LJExport (unified model)
      ↓
   Exporters
      ↓
Single File (YAML/JSON/XML)
```

## Key Design Decisions

### Single File Export

All data is exported to a single file in YAML, JSON, or XML format containing:
- Export metadata
- Usermap (comment author mappings)
- All posts
- All comments
- All inbox messages

**Rationale**: Simplicity. One file to manage, easy to version control, easy to process. Multiple format options allow users to choose what works best for their workflow.

### Pydantic Models

All data structures use Pydantic for:
- Automatic validation
- Type safety
- Easy serialization/deserialization
- Clear schema definition

### Separation of API Clients and Parsers

- **API Clients**: Handle HTTP requests, pagination, retry logic
- **Parsers**: Parse XML/HTML into Pydantic models

This separation makes testing easier and allows parsers to be reused.

### Pluggable Exporters

Exporters implement a common interface, making it easy to add new formats:
- **YAMLExporter** - Default format, human-readable
- **JSONExporter** - Structured data, machine-readable
- **XMLExporter** - Universal interchange format
- Could add: SQLiteExporter, MarkdownExporter, etc.

All three formats contain identical data with full fidelity.

## Module Relationships

```
yalje/
├── core/          # Foundation (auth, session, config)
├── models/        # Data structures (used by everyone)
├── api/           # Uses: core, models
├── parsers/       # Uses: models
├── exporters/     # Uses: models
├── cli/           # Uses: everything
└── utils/         # Used by: everyone
```

## Extension Points

### Adding a New Export Format

1. Create new exporter class in `exporters/`
2. Implement `export(data, output_path)` and `load(input_path)` methods
3. Add exporter to `exporters/__init__.py`
4. Add format choice to CLI `--format` option in `cli/main.py`
5. Add tests in `tests/unit/test_exporters.py`

### Adding New Data Types

1. Create Pydantic model in `models/`
2. Add field to `LJExport` model
3. Create API client in `api/`
4. Create parser in `parsers/`
5. Update CLI to include in download

## Testing Strategy

- **Unit Tests**: Test individual functions (parsers, models, utils)
- **Integration Tests**: Test API clients with fixture responses
- **CLI Tests**: Test command-line interface with Click's test runner

## Error Handling

All errors inherit from `YaljeError` base exception:
- `AuthenticationError` - Login failures
- `APIError` - HTTP request failures
- `ParsingError` - XML/HTML parsing failures
- `ExportError` - File I/O failures
- `ValidationError` - Data validation failures

## Logging

Structured logging with configurable levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: Progress updates (default)
- `WARNING`: Recoverable issues
- `ERROR`: Serious problems
- `CRITICAL`: Fatal errors

## Future Enhancements

Potential improvements:
- Incremental backups (download only new content)
- Resume interrupted downloads
- Parallel downloading
- SQLite export format
- Web UI for browsing exports
- Import to other platforms (WordPress, etc.)

## See Also

- [README](../README.md) - Getting started
- [API Documentation](api/) - LiveJournal API details
- [Schema](schema.md) - Export format specification
