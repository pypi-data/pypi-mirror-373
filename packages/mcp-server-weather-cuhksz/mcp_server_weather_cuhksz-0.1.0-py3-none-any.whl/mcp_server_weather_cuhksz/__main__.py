import argparse
import os
import sys
import logging
import dotenv
from .mcp_weather import mcp

def main():
    """Main entry point for the package."""
    # Load environment variables from .env file first.
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Start MCP Weather Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=3003, help="Port to listen on (default: 3003)")
    parser.add_argument("--transport", type=str, default="stdio", help="Transport type (default: stdio)")
    
    # Set default values from environment variables. CLI arguments will override them.
    parser.add_argument("--api-host", type=str, default=os.getenv("WEATHER_API_HOST", "https://api.qweather.com"), help="Weather API Host")
    parser.add_argument("--key-id", type=str, default=os.getenv("QWEATHER_KEY_ID"), help="QWeather Key ID")
    parser.add_argument("--project-id", type=str, default=os.getenv("QWEATHER_PROJECT_ID"), help="QWeather Project ID")
    parser.add_argument("--private-key", type=str, default=os.getenv("QWEATHER_PRIVATE_KEY"), help="QWeather Private Key")

    args = parser.parse_args()

    # Validate that credentials and directory are set.
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
    os.environ['WEATHER_API_HOST'] = args.api_host
    os.environ['QWEATHER_KEY_ID'] = args.key_id
    os.environ['QWEATHER_PROJECT_ID'] = args.project_id
    os.environ['QWEATHER_PRIVATE_KEY'] = args.private_key
    
    logger = logging.getLogger('mcp_weather_server')
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting MCP Weather Server...")
    logger.info(f"Transport: {args.transport}")
    if args.transport != 'stdio':
        logger.info(f"Host: {args.host}")
        logger.info(f"Port: {args.port}")

    # Run the server
    if args.transport == 'stdio':
        mcp.run(transport='stdio')
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
