# Claude Code Indexer - AI Assistant Configuration

## 🤖 Tool Catalog for LLM/Agents

### Core Tools (Must Use First)
```yaml
cci_init:
  description: Initialize project with CLAUDE.md configuration
  usage: cci init
  when_to_use: First time in any project
  output: Creates CLAUDE.md and database

cci_index:
  description: Index all source code into graph database
  usage: cci index [path]
  when_to_use: After init or when code changes significantly
  parameters:
    - path: Directory to index (default: current)
    - --force: Re-index all files ignoring cache
  output: Graph with nodes (entities) and edges (relationships)
  performance: ~50 files/sec with cache
```

### Query Tools (For Understanding Code)
```yaml
cci_query:
  description: Query indexed code entities with filters
  usage: cci query [options]
  parameters:
    - --important: Show most critical components (PageRank)
    - --type [class|function|method]: Filter by entity type
    - --limit N: Limit results
  when_to_use: To understand project structure
  output: Table of entities with importance scores

cci_search:
  description: Full-text search across codebase
  usage: cci search <keywords>
  parameters:
    - keywords: Space-separated terms (OR search)
    - --mode all: Require all keywords (AND search)
  when_to_use: Finding specific code/functions
  output: Matching entities with file paths

cci_critical:
  description: Find most critical components
  usage: cci critical [--limit N]
  when_to_use: Identify key files to focus on
  output: Critical paths and dependencies
```

### Analysis Tools (For Insights)
```yaml
cci_stats:
  description: Show project statistics
  usage: cci stats
  when_to_use: Quick project overview
  output: File counts, languages, cache stats

cci_insights:
  description: Architectural analysis and health check
  usage: cci insights
  when_to_use: Assess code quality and structure
  output: Health score, layer distribution, recommendations

cci_enhanced:
  description: Query AI-enhanced metadata
  usage: cci enhanced [filters]
  parameters:
    - --layer [service|controller|model]: Filter by architecture
    - --complexity '>0.7': Filter by complexity score
    - --domain [auth|payment|etc]: Filter by business domain
  when_to_use: After running cci enhance
  output: Entities with AI-generated metadata
```

### Enhancement Tools (Use Carefully)
```yaml
cci_enhance:
  description: Add AI-powered metadata (requires API)
  usage: cci enhance . --limit N
  when_to_use: For deeper architectural understanding
  warnings:
    - NO sensitive data/API keys in code
    - Start with --limit 5-10 to test
    - Costs API credits
  output: Adds layer, domain, complexity metadata
```

### State Management (For Memory)
```yaml
cci_state_capture:
  description: Save current codebase snapshot
  usage: cci state capture
  when_to_use: Before major changes or milestones
  output: Timestamped state in database

cci_state_diff:
  description: Show changes since last capture
  usage: cci state diff
  when_to_use: Review what changed
  output: Added/modified/deleted files

cci_state_tasks:
  description: List development task history
  usage: cci state tasks
  when_to_use: Track project evolution
  output: Task timeline with changes
```

### Performance Tools
```yaml
cci_cache:
  description: Manage indexing cache
  usage: cci cache [clean|stats]
  subcommands:
    - clean: Remove old cache entries
    - stats: Show cache performance
  when_to_use: Optimize re-indexing speed

cci_benchmark:
  description: Run performance tests
  usage: cci benchmark
  when_to_use: Test indexing speed
  output: Performance metrics
```

### MCP Integration (For Claude Desktop/Code)
```yaml
cci_mcp_install:
  description: Setup MCP server for Claude
  usage: cci mcp install
  when_to_use: Enable real-time code queries
  output: Updates Claude config files

cci_mcp_daemon:
  description: Background service for instant queries
  usage: cci mcp-daemon [start|stop|status]
  when_to_use: For zero-latency responses
  benefits: 100x faster than CLI
```

## 🚀 Quick Start Workflow

```bash
# 1. Initialize and index (one-time setup)
cci init
cci index .

# 2. Understand the codebase
cci stats                    # Overview
cci query --important        # Key components
cci insights                 # Architecture

# 3. Navigate and search
cci search "authentication"  # Find auth code
cci critical --limit 5       # Critical paths

# 4. Optional: Add AI insights (if no secrets)
cci enhance . --limit 10
cci enhanced --layer service
```

## 📊 Performance Expectations

| Operation | First Run | With Cache | Notes |
|-----------|-----------|------------|-------|
| init      | 1-2s      | N/A        | One-time |
| index     | 5-10s     | 0.5-1s     | 95%+ cache hit |
| query     | 0.1-0.5s  | 0.05s      | Database query |
| search    | 0.2-1s    | 0.1s       | Full-text search |
| enhance   | 2-5s/node | N/A        | API calls |

## ⚠️ Security Guidelines

1. **NEVER index sensitive data**:
   - Check for .env files: `find . -name "*.env"`
   - Exclude secrets: Add to .gitignore
   
2. **Safe for**:
   - Open source projects
   - Development code
   - Documentation

3. **Not safe for**:
   - Production configs
   - API keys/tokens
   - Customer data

## 🐛 Error Reporting

If CCI encounters errors, report them:
```bash
gh issue create --repo tuannx/claude-prompts \
  --title "[CCI] Error: <description>" \
  --body "Command: <command>\nError: <error message>" \
  --label bug,cci
```

## 📚 Advanced Usage

### Custom Filters
```bash
# Complex queries
cci query --type class --important --limit 10
cci enhanced --complexity '>0.8' --layer service

# Multiple searches
cci search auth login user --mode all
```

### Project Management
```bash
# List all indexed projects
cci projects

# Remove old project
cci remove <project-path>

# Clean orphaned indexes
cci clean
```

## 💡 Tips for LLM Agents

1. **Always start with**: `cci init && cci index .`
2. **For navigation**: Use `cci query --important` first
3. **For specific code**: Use `cci search` with keywords
4. **For architecture**: Use `cci insights`
5. **Save state regularly**: `cci state capture`
6. **Use cache**: Don't force re-index unless needed

---
*Generated by Claude Code Indexer v{{VERSION}}*