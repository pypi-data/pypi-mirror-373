# League Analysis MCP Server

A comprehensive Model Context Protocol (MCP) server that provides AI assistants with access to Yahoo Fantasy Sports data, including advanced historical analysis and manager profiling capabilities.

## Features

### 🏈 Multi-Sport Support
- **NFL** (National Football League)
- **NBA** (National Basketball Association) 
- **MLB** (Major League Baseball)
- **NHL** (National Hockey League)

### 📊 Current Season Data
- League information and settings
- Real-time standings
- Team rosters and lineups
- Weekly matchups and scoring
- Transaction history

### 📈 Historical Analysis
- **Multi-season draft analysis** - Track draft patterns and strategies over time
- **Manager performance history** - Comprehensive performance metrics across seasons
- **Transaction pattern analysis** - Trading behavior and partnership identification
- **Season-to-season comparisons** - League evolution and competitive balance trends

### 🧠 Advanced Analytics
- **Draft strategy classification** - Identify RB-heavy, Zero-RB, or balanced approaches
- **Manager skill evaluation** - Comprehensive skill scoring based on multiple metrics
- **Trade likelihood prediction** - Predict trade partnerships based on historical patterns
- **Pattern recognition** - Identify trends in manager behavior and league dynamics

### ⚡ Performance Features
- **Smart caching** - Historical data cached permanently, current data with TTL
- **Rate limiting** - Respects Yahoo API limits
- **Error handling** - Comprehensive error handling and logging
- **Multi-season support** - Access data from 2015+ seasons

## Installation

### Prerequisites
- Python 3.10+
- Yahoo Developer App credentials (setup will guide you)

### 🚀 Easy Installation (PyPI)

**One-Command Install:**
```bash
# Install and run directly with uvx (recommended)
uvx league-analysis-mcp-server

# Or install with pip
pip install league-analysis-mcp-server
league-analysis-mcp-server

# Or run with python
python -m league_analysis_mcp_server
```

**First-time setup:**
After installation, the server will guide you through Yahoo API setup automatically.

### 🔧 Development Installation

**From Source:**
```bash
git clone <repository-url>
cd league-analysis-mcp
uv run python setup_complete.py
```

This automated script will:
- ✅ Install all dependencies  
- ✅ Run comprehensive system tests
- ✅ Guide you through Yahoo OAuth setup
- ✅ Test the complete integration
- ✅ Provide usage instructions

## 🚀 **NEW! Streamlined Authentication Setup**

**No more complex setup scripts!** Authentication is now handled entirely through conversational MCP tools:

### **5-Step Setup Process:**

1. **Install & Connect** - Add server to your MCP client
2. **Check Status** - AI assistant runs `check_setup_status()` 
3. **Create Yahoo App** - AI assistant shows you exactly what to do with `create_yahoo_app()`
4. **Save Credentials** - AI assistant saves them for you with `save_yahoo_credentials(key, secret)`
5. **Complete OAuth** - AI assistant guides you through `start_oauth_flow()` and `complete_oauth_flow(code)`

**That's it!** ✨ Everything happens in your conversation with the AI assistant. No file editing, no command line scripts, no leaving the interface.

### **Example User Experience:**

```
You: "Show me my fantasy league standings"

AI: Let me check that for you. First, I need to check your authentication setup.
    → Runs check_setup_status()
    
AI: I see you need to create a Yahoo Developer app first. Here are the exact steps:
    → Runs create_yahoo_app()
    → Shows step-by-step instructions with exact values to use

You: "I created the app! My key is dj0yJmk9... and secret is abc123..."

AI: Perfect! Let me save those credentials for you.
    → Runs save_yahoo_credentials(key, secret)
    → Automatically saves to your environment

AI: Great! Now let's complete the OAuth authorization. Please visit this URL:
    → Runs start_oauth_flow()
    → Shows authorization URL and clear instructions

You: "I authorized it and got code: xyz789"

AI: Excellent! Let me complete the setup.
    → Runs complete_oauth_flow("xyz789")
    
AI: 🎉 Setup complete! Now let me get your league standings...
    → Runs get_standings() and shows your data
```

**Total time: ~2 minutes.** No technical knowledge required!

### 🔧 **Fallback: Manual Setup (Advanced Users)**

If you prefer the traditional approach, you can still use the manual setup scripts. But most users will love the new conversational setup!

## Usage

### Starting the Server
```bash
# PyPI Installation (recommended):
uvx league-analysis-mcp-server

# Or if installed with pip:
league-analysis-mcp-server

# Development/Source:
uv run python -m src.server
```

## 🔌 MCP Client Configuration

### Claude Desktop

Add this to your Claude Desktop `claude_desktop_config.json`:

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

**Configuration file locations:**
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### Claude Code

Add this to your Claude Code MCP configuration:

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

### Continue.dev

Add this to your Continue config:

```json
{
  "mcpServers": [
    {
      "name": "league-analysis",
      "command": ["uvx", "league-analysis-mcp-server"]
    }
  ]
}
```

### Other MCP Clients

For any MCP-compatible client, use these connection details:
- **Command:** `uvx`
- **Args:** `["league-analysis-mcp-server"]`
- **Transport:** stdio (default)
- **No working directory needed!**

### 🔧 Testing Your Connection

After adding to your MCP client:

1. **Restart your MCP client** (Claude Desktop, etc.)
2. **Test the connection** by asking:
   - "Can you get server info for the league analysis server?"
   - "List available seasons for NFL"
   - "What fantasy sports tools are available?"
3. **Check server status** with: `get_server_info()`

### 🚨 Troubleshooting MCP Connection

**Common issues:**

1. **Server not found:**
   - Check the file path in your config
   - Ensure UV is installed and in PATH
   - Verify the server starts manually: `uv run python -m src.server`

2. **Authentication errors:**
   - Use the new streamlined setup: Ask your AI assistant to run `check_setup_status()`
   - For advanced users: Run `uv run python utils/setup_yahoo_auth.py`
   - Check your Yahoo Developer app settings

3. **Permission issues:**
   - Ensure your MCP client has permission to execute UV
   - Check working directory permissions

4. **Environment variables:**
   - MCP clients may not inherit your shell environment
   - Create `.env` file in project root with credentials

### Available Tools

#### **🔐 Streamlined Authentication Tools** ✨ **NEW!**
- `check_setup_status()` - Check current authentication state and get next steps
- `create_yahoo_app()` - Step-by-step Yahoo Developer app creation guide
- `save_yahoo_credentials(consumer_key, consumer_secret)` - Save Yahoo app credentials
- `start_oauth_flow()` - Begin OAuth authorization with clear instructions  
- `complete_oauth_flow(verification_code)` - Complete setup with verification code
- `test_yahoo_connection()` - Test API connectivity and troubleshoot issues
- `reset_authentication()` - Clear all auth data to start fresh

#### Basic League Tools
- `get_server_info()` - Server status and configuration
- `get_setup_instructions()` - Comprehensive setup help (includes new tools guidance)
- `list_available_seasons(sport)` - Available historical seasons
- `get_league_info(league_id, sport, season?)` - League settings and metadata
- `get_standings(league_id, sport, season?)` - Current or historical standings
- `get_team_roster(league_id, team_id, sport, season?)` - Team roster information
- `get_matchups(league_id, sport, week?, season?)` - Weekly matchup data

#### Historical Analysis Tools
- `get_historical_drafts(league_id, sport, seasons?)` - Draft results across seasons
- `get_season_transactions(league_id, sport, season)` - Transaction history for season
- `analyze_manager_history(league_id, sport, seasons?, team_id?)` - Manager performance patterns
- `compare_seasons(league_id, sport, seasons)` - Season-to-season analysis

#### Advanced Analytics Tools
- `analyze_draft_strategy(league_id, sport, seasons?, team_id?)` - Draft pattern analysis
- `predict_trade_likelihood(league_id, sport, team1_id?, team2_id?, seasons?)` - Trade predictions
- `evaluate_manager_skill(league_id, sport, seasons?, team_id?)` - Comprehensive skill evaluation

#### Cache Management
- `clear_cache(cache_type?)` - Clear cached data ('all', 'current', 'historical')

### Available Resources

Access read-only data through these resource URIs:

- `league_overview://sport/league_id[/season]` - Comprehensive league overview
- `current_week://sport/league_id` - Current week activity and focus areas
- `league_history://sport/league_id` - Multi-season history and trends
- `manager_profiles://sport/league_id[/team_id]` - Manager profiling information

## Example Usage

```python
# Get basic league info
result = get_league_info("123456", "nfl")

# Analyze manager performance across last 3 seasons  
analysis = analyze_manager_history("123456", "nfl", ["2022", "2023", "2024"])

# Get draft strategies for all managers
draft_analysis = analyze_draft_strategy("123456", "nfl", ["2022", "2023", "2024"])

# Evaluate manager skill levels
skill_eval = evaluate_manager_skill("123456", "nfl", ["2022", "2023", "2024"])

# Predict trade likelihood between specific managers
trade_pred = predict_trade_likelihood("123456", "nfl", "team1", "team2")
```

## Configuration

### Game IDs
The server includes game ID mappings for seasons 2015-2024 across all supported sports. These are automatically used when specifying historical seasons.

### Caching Strategy
- **Historical data**: Cached permanently (TTL = -1)
- **Current season data**: Cached for 5 minutes (TTL = 300)
- **Cache size**: Limited to 100MB by default

### Rate Limiting
- **Default**: 60 requests per minute
- **Burst limit**: 10 requests
- Automatically handled by the server

## Architecture

### Core Components
- **FastMCP 2.0**: High-level MCP framework for rapid development
- **YFPY**: Yahoo Fantasy Sports API wrapper
- **Caching Layer**: Smart caching for performance optimization
- **Authentication Manager**: OAuth handling for Yahoo API access
- **Analytics Engine**: Advanced pattern recognition and predictions

### Data Flow
1. **Request** → Authentication → Cache Check → Yahoo API → Response Processing → Cache Storage → **Response**
2. **Historical Data**: Cached permanently after first fetch
3. **Current Data**: Cached with TTL, automatically refreshed

### Error Handling
- Comprehensive error logging
- Graceful degradation for missing data
- Cache fallback for API failures
- User-friendly error messages

## Supported Analysis Types

### Manager Profiling
- **Performance Tiers**: Elite, Above Average, Average, Below Average, Needs Improvement
- **Consistency Scoring**: Win rate, scoring, and ranking consistency
- **Success Patterns**: Championship rate, playoff appearances, trajectory analysis

### Draft Strategy Classification
- **RB-Heavy**: Prioritizes running backs in early rounds
- **Zero-RB**: Waits on running backs, focuses on WR/other positions
- **Balanced**: Even distribution across position types
- **Auction Analysis**: Spending patterns and value identification

### Trade Pattern Analysis
- **Partnership Identification**: Historical trade frequency between managers
- **Likelihood Scoring**: Probability of future trades based on history
- **Trade Timing**: Seasonal patterns and deadline behavior

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - **NEW**: Use streamlined setup by asking AI to run `check_setup_status()`
   - Try `reset_authentication()` to start fresh
   - For manual setup: Verify Yahoo Consumer Key/Secret in .env
   - Check app configuration in Yahoo Developer Console
   - Run `get_setup_instructions()` for detailed setup help

2. **No Historical Data**
   - Ensure league has existed for multiple seasons
   - Verify correct league ID and sport combination
   - Check game ID mappings in config/game_ids.json

3. **Cache Issues**
   - Use `clear_cache("all")` to reset all cached data
   - Check cache statistics with `get_server_info()`

4. **Rate Limiting**
   - Server automatically handles rate limits
   - Historical data queries may take longer due to multiple API calls
   - Use caching to minimize repeated requests

### Support

For issues and feature requests, please check the documentation or create an issue in the project repository.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read the contributing guidelines and submit pull requests for any improvements.