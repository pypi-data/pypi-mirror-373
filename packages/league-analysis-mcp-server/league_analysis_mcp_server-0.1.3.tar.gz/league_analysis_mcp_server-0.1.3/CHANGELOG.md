# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2025-09-02

### ✨ **MAJOR UX IMPROVEMENT**: Streamlined Authentication Setup

#### Added
- **🚀 NEW: Conversational Authentication Setup** - Complete Yahoo API setup through MCP tools
  - `check_setup_status()` - Check authentication state and get next steps
  - `create_yahoo_app()` - Step-by-step Yahoo Developer app creation guide  
  - `save_yahoo_credentials(consumer_key, consumer_secret)` - Automated credential saving
  - `start_oauth_flow()` - OAuth authorization with clear instructions
  - `complete_oauth_flow(verification_code)` - Complete setup with verification code
  - `test_yahoo_connection()` - API connectivity testing and troubleshooting
  - `reset_authentication()` - Clear all authentication data to start fresh

#### Enhanced
- **OAuth Token Exchange**: Fixed manual OAuth flow with proper Yahoo API token exchange
- **Error Messages**: Updated all authentication errors to guide users to new setup tools
- **Setup Instructions**: Updated `get_setup_instructions()` to showcase new conversational flow
- **Token Management**: Enhanced token status reporting and validation

#### User Experience
- **Setup Time**: Reduced from 10+ manual steps to 5 conversational interactions
- **No File Editing**: Credentials automatically saved to environment
- **No Scripts**: Everything happens through AI assistant conversation
- **Clear Guidance**: Each step provides exact next action to take
- **Error Recovery**: Reset and retry any step without starting over

### Technical Improvements
- **Enhanced OAuth**: Real token exchange implementation (removed placeholder tokens)
- **Smart Validation**: Credential format validation and helpful error messages  
- **Environment Management**: Automated .env file creation and updates
- **Connection Testing**: Built-in API connectivity verification
- **State Management**: Comprehensive setup state tracking and reporting

### Documentation
- **README.md**: Updated with new streamlined setup process and example user flow
- **Authentication Guide**: Clear 5-step setup process with conversation example
- **Troubleshooting**: Updated to prioritize new setup tools over manual methods

## [0.1.2] - 2025-09-02

### Fixed
- GitHub Actions workflow publishing issues
- UV publish command configuration for TestPyPI
- Python environment compatibility in CI/CD pipeline 
- YAML syntax errors in publish workflow
- Package installation wildcard expansion in GitHub Actions

### Changed
- Removed GitHub environment references from workflow for simplified deployment
- Improved error handling in automated publishing pipeline

## [0.1.0] - 2024-09-02

### Added
- Initial release of League Analysis MCP Server
- **Multi-Sport Support**: NFL, NBA, MLB, NHL fantasy sports analysis
- **Current Season Data**: League info, standings, rosters, matchups, transactions
- **Historical Analysis**: Multi-season draft analysis, manager performance tracking
- **Advanced Analytics**: Draft strategy classification, manager skill evaluation, trade predictions
- **Smart Caching**: Permanent historical data cache, TTL-based current data cache
- **Enhanced Authentication**: Automated Yahoo OAuth setup with token refresh
- **FastMCP 2.0 Integration**: Modern Model Context Protocol implementation
- **Comprehensive Testing**: Automated setup validation and testing suite

### Features
- **15+ MCP Tools**: Complete fantasy sports analysis toolkit
- **4 MCP Resources**: League overviews, current week info, historical trends, manager profiles
- **Automated Setup**: One-command installation and OAuth configuration
- **PyPI Distribution**: Install with `uvx league-analysis-mcp-server`
- **Multi-Client Support**: Works with Claude Desktop, Claude Code, Continue.dev, etc.
- **Rate Limiting**: Respects Yahoo API limits with intelligent throttling
- **Error Handling**: Comprehensive error handling with user-friendly messages

### Tools Available
#### Basic League Tools
- `get_server_info()` - Server status and authentication info
- `get_setup_instructions()` - Interactive setup guidance
- `list_available_seasons(sport)` - Historical seasons (2015-2024)
- `get_league_info(league_id, sport, season?)` - League settings
- `get_standings(league_id, sport, season?)` - Current/historical standings
- `get_team_roster(league_id, team_id, sport, season?)` - Team rosters
- `get_matchups(league_id, sport, week?, season?)` - Weekly matchups
- `refresh_yahoo_token()` - Manual token refresh
- `clear_cache(cache_type?)` - Cache management

#### Historical Analysis Tools
- `get_historical_drafts(league_id, sport, seasons?)` - Multi-season drafts
- `get_season_transactions(league_id, sport, season)` - Transaction history
- `analyze_manager_history(league_id, sport, seasons?, team_id?)` - Manager patterns
- `compare_seasons(league_id, sport, seasons)` - Season comparisons

#### Advanced Analytics Tools
- `analyze_draft_strategy(league_id, sport, seasons?, team_id?)` - Draft classification
- `predict_trade_likelihood(league_id, sport, team1_id?, team2_id?, seasons?)` - Trade predictions
- `evaluate_manager_skill(league_id, sport, seasons?, team_id?)` - Skill scoring

### Resources Available
- `league_overview/{sport}/{league_id}` - Comprehensive league overviews
- `current_week/{sport}/{league_id}` - Current week activity summaries
- `league_history/{sport}/{league_id}` - Multi-season trends and insights
- `manager_profiles/{sport}/{league_id}` - Manager tendency analysis

### Technical Details
- **Python**: 3.10+ required
- **Dependencies**: FastMCP 2.0, YFPY 16.0+, Pandas 2.0+
- **Package Manager**: UV (recommended)
- **Authentication**: Yahoo OAuth 2.0 with automatic refresh
- **Transport**: stdio (MCP standard)
- **Caching**: In-memory with configurable TTL

### Installation
```bash
# Easy installation
uvx league-analysis-mcp-server

# Or with pip
pip install league-analysis-mcp-server

# Development setup
git clone <repository>
cd league-analysis-mcp
uv run python setup_complete.py
```

### MCP Client Configuration
```json
{
  "mcpServers": {
    "league-analysis": {
      "command": "uvx",
      "args": ["league-analysis-mcp-server"]
    }
  }
}
```

[Unreleased]: https://github.com/league-analysis-mcp/league-analysis-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/league-analysis-mcp/league-analysis-mcp/releases/tag/v0.1.0