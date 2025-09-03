import argparse
import os
import sys
import logging
import dotenv
from .mcp_weather import mcp

# --- Configuration ---
# Find the directory of the current script to locate the .env file reliably.
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ENV_PATH = os.path.join(_CURRENT_DIR, '.env')

# --- Logging Setup ---x w
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mcp_weather_server')

def main():
    """Main entry point for the package."""
    # Load environment variables from a specific .env file if it exists.
    # This supports local development without interfering with Docker's environment injection.
    dotenv.load_dotenv(dotenv_path=_ENV_PATH)

    parser = argparse.ArgumentParser(description="Start MCP Weather Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=3003, help="Port to listen on (default: 3003)")
    parser.add_argument("--transport", type=str, default="stdio", help="Transport type (default: stdio)")
    
    # Set default values from environment variables. CLI arguments will override them.
    parser.add_argument("--is-unified-api", type=lambda x: (str(x).lower() == 'true'), default=os.getenv("IS_UNIFIED_API", 'false').lower() == 'true', help="Use Unified API Proxy")
    parser.add_argument("--unified-api-host", type=str, default=os.getenv("UNIFIED_API_HOST"), help="Unified API Proxy Host")
    parser.add_argument("--api-host", type=str, default=os.getenv("WEATHER_API_HOST", "https://api.qweather.com"), help="Weather API Host")
    parser.add_argument("--key-id", type=str, default=os.getenv("QWEATHER_KEY_ID"), help="QWeather Key ID")
    parser.add_argument("--project-id", type=str, default=os.getenv("QWEATHER_PROJECT_ID"), help="QWeather Project ID")
    parser.add_argument("--private-key", type=str, default=os.getenv("QWEATHER_PRIVATE_KEY"), help="QWeather Private Key")
    parser.add_argument("--gateway-host", type=str, default=os.getenv("GATEWAY_HOST", "https://gateway.qweather.com"), help="Gateway Host")
    parser.add_argument("--gateway-port", type=int, default=os.getenv("GATEWAY_PORT", 443), help="Gateway Port")

    args = parser.parse_args()

    # --- Unified API Mode Check ---
    is_unified_mode = args.is_unified_api
    final_api_host = args.api_host

    if is_unified_mode:
        if args.unified_api_host:
            logger.info("Running in Unified API mode.")
            final_api_host = args.unified_api_host
            # In unified mode, JWT credentials are not needed on the MCP side.
            # We can skip the credential checks.
        else:
            logger.warning("IS_UNIFIED_API is true, but UNIFIED_API_HOST is not provided. Falling back to direct API mode.")
            is_unified_mode = False
            # Proceed with direct mode credential checks
    
    if not is_unified_mode:
        logger.info("Running in Direct API mode.")
        # Validate that credentials and directory are set for direct mode.
        if not args.api_host:
            print("Error: API Host must be provided.", file=sys.stderr)
            sys.exit(1)

        if not args.key_id:
            print("Error: Key ID must be provided.", file=sys.stderr)
            sys.exit(1)
    
        if not args.project_id:
            print("Error: Project ID must be provided.", file=sys.stderr)
            sys.exit(1)
    
        if not args.private_key:
            print("Error: Private Key must be provided.", file=sys.stderr)
            sys.exit(1)

    # Set the final resolved values back into the environment for the tools to use
    os.environ['IS_UNIFIED_API'] = str(is_unified_mode)
    os.environ['WEATHER_API_HOST'] = final_api_host
    os.environ['QWEATHER_KEY_ID'] = args.key_id or ""
    os.environ['QWEATHER_PROJECT_ID'] = args.project_id or ""
    os.environ['QWEATHER_PRIVATE_KEY'] = args.private_key or ""
    os.environ['GATEWAY_HOST'] = args.gateway_host
    os.environ['GATEWAY_PORT'] = str(args.gateway_port)

    logger.info("Starting MCP Weather Server...")
    logger.info(f"Transport: {args.transport}")
    if args.transport != 'stdio':
        logger.info(f"Host: {args.host}")
        logger.info(f"Port: {args.port}")

    logger.info(f"Gateway Host: {args.gateway_host}")
    logger.info(f"Gateway Port: {args.gateway_port}")

    # Run the server
    if args.transport == 'stdio':
        mcp.run(transport='stdio')
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
