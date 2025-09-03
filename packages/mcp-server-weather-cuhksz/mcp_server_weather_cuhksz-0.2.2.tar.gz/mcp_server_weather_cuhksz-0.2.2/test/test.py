import asyncio
from fastmcp import Client
import logging
import os
import sys
from dotenv import load_dotenv
import json

# --- 1. Setup Environment and Logging ---

# Configure logging to be clear and informative
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger("WeatherTestClient")

# Add project root to path to allow importing the non-tool functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from src.mcp_server_weather_cuhksz.mcp_weather import get_request_volume_stats, get_finance_summary
except ImportError as e:
    logger.error(f"Failed to import console API functions: {e}")
    get_request_volume_stats = None
    get_finance_summary = None

# Define the server URL, matching docker-compose.yml and __main__.py defaults
MCP_SERVER_URL = "http://localhost:3003/sse"

# --- 2. Define Default Inputs for Tools ---
# Set default parameters for tools that require them.
# The 'get_location_id' tool is called first, and its output is used to dynamically
# populate the 'location' for the other tools.
DEFAULT_INPUTS = {
    'get_location_id': {"location": "beijing", "number": 1},
    'get_daily_weather': {'days': '3d', 'location': "101010100"},  # Fallback Beijing ID
    'get_hourly_weather': {'hours': '24h', 'location': "101010100"},
    'get_weather_warning_now': {'location': "101010100"},
    'get_weather_indices': {'days': '1d', 'location': "101010100"},
}

async def run_full_test():
    """
    Connects to the running MCP server, tests all discoverable tools via the client,
    and then directly tests the console-specific API functions.
    """
    logger.info(f"🚀 Starting full test suite, attempting to connect to: {MCP_SERVER_URL}")
    load_dotenv()

    # --- 3. Test MCP Tools via Client ---
    try:
        client = Client(MCP_SERVER_URL)
        async with client:
            tools = await client.list_tools()
            if not tools:
                logger.warning("❌ No MCP tools found on the server. Aborting tool test section.")
                return

            logger.info(f"\n✅ Connection successful! Found {len(tools)} available tools. Will now call them...\n")

            # Step 3.1: Call get_location_id first to get a dynamic ID for other tests
            location_id = DEFAULT_INPUTS['get_daily_weather']['location'] # Start with fallback
            location_tool_name = "get_location_id"

            if any(t.name == location_tool_name for t in tools):
                logger.info(f"--- Calling prerequisite tool: {location_tool_name} ---")
                try:
                    params = DEFAULT_INPUTS[location_tool_name]
                    logger.info(f"   Parameters: {params}")
                    result = await client.call_tool(location_tool_name, params, timeout=120.0)
                    
                    # The tool result is in `structured_content`. We can get the text from it.
                    # Use .get('text', '') for safe access in case 'text' key is missing.
                    result_text = str(result.structured_content.get('text', result.structured_content))
                    logger.info(f"\n✅ {location_tool_name} call successful! Full Result:\n---\n{result_text}\n---")

                    # Try to parse the result for the location ID
                    try:
                        location_id = result_text.split("｜地区/城市ID:")[1].split("｜")[0].strip()
                        logger.info(f"Successfully extracted Location ID for subsequent tests: {location_id}")
                        # Update other tools to use the new dynamic location ID
                        for tool_name in ['get_daily_weather', 'get_hourly_weather', 'get_weather_warning_now', 'get_weather_indices']:
                            if tool_name in DEFAULT_INPUTS:
                                DEFAULT_INPUTS[tool_name]['location'] = location_id
                    except IndexError:
                        logger.warning(f"Could not parse Location ID from result, will use fallback ID: {location_id}")
                
                except Exception as e:
                    logger.error(f"⚠️ Error calling '{location_tool_name}': {e}. Using fallback ID for subsequent tests.", exc_info=True)
            else:
                logger.warning(f"❌ Critical tool '{location_tool_name}' not found! Using fallback ID.")

            # Step 3.2: Test all other tools
            for tool in tools:
                if tool.name not in DEFAULT_INPUTS:
                    logger.info(f"--- Skipping tool: {tool.name} (no test parameters defined) ---")
                    continue

                logger.info(f"--- Calling tool: {tool.name} ---")
                try:
                    params = DEFAULT_INPUTS[tool.name]
                    logger.info(f"   Parameters: {params}")
                    result = await client.call_tool(tool.name, params, timeout=120.0)
                    
                    # Convert the structured_content dict to a formatted string for preview.
                    result_text = json.dumps(result.structured_content, indent=2, ensure_ascii=False)
                    preview = (result_text[:700] + '...') if len(result_text) > 700 else result_text
                    logger.info(f"\n✅ {tool.name} call successful! Result Preview:\n---\n{preview}\n---")
                
                except Exception as e:
                    logger.error(f"⚠️ Error calling tool '{tool.name}': {e}", exc_info=True)

            logger.info("🏁 All available MCP tools have been tested.")

    except Exception as e:
        logger.error(f"❌ MCP tool testing failed. Could not connect to the server at {MCP_SERVER_URL}: {e}", exc_info=True)
        logger.error("\nPlease ensure that:")
        logger.error("1. The weather server is running (e.g., via 'docker-compose up').")
        logger.error("2. The server URL and port are correct.")
        return # Stop if we can't even test the tools

    # --- 4. Test Console API Functions Directly ---
    logger.info("\n--- Starting Console API Function Tests ---\n")

    # Check the server's running mode. These tests are only for Direct API mode.
    is_unified_mode = os.getenv("IS_UNIFIED_API", "false").lower() == "true"
    if is_unified_mode:
        logger.info("MCP server is in Unified API mode. Skipping direct function call tests.")
    else:
        logger.info("MCP server is in Direct API mode. Proceeding with direct function call tests.")
        if not all([get_request_volume_stats, get_finance_summary]):
            logger.error("Could not import console API functions. Skipping these tests.")
            return

        # Check for credentials needed for direct function calls
        if not all([os.getenv("QWEATHER_KEY_ID"), os.getenv("QWEATHER_PROJECT_ID"), os.getenv("QWEATHER_PRIVATE_KEY")]):
            logger.error("FATAL: Environment variables for QWeather are not set for Direct API mode. Cannot run console API tests.")
            return

        # Test get_request_volume_stats
        logger.info("==> Testing function: get_request_volume_stats")
        try:
            stats = await get_request_volume_stats()
            logger.info(f"Result from get_request_volume_stats:\n{json.dumps(stats, indent=2, ensure_ascii=False)}\n")
        except Exception as e:
            logger.error(f"Error testing get_request_volume_stats: {e}", exc_info=True)

        # Test get_finance_summary
        logger.info("==> Testing function: get_finance_summary")
        try:
            summary = await get_finance_summary()
            logger.info(f"Result from get_finance_summary:\n{json.dumps(summary, indent=2, ensure_ascii=False)}\n")
        except Exception as e:
            logger.error(f"Error testing get_finance_summary: {e}", exc_info=True)
        
    logger.info("🏁 Full test suite finished!")


if __name__ == "__main__":
    asyncio.run(run_full_test())
