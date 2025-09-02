import asyncio, sys, importlib, json, traceback
from starlette.testclient import TestClient


def main():
    """Main entry point for the ASGI runner"""
    if len(sys.argv) < 2:
        print("Usage: python mcp_runner.py <module:app>", file=sys.stderr)
        sys.exit(1)
    
    app_path = sys.argv[1]
    root_path = sys.argv[2] if len(sys.argv) > 2 else "/mcp/httmcp"

    try:
        # Import the ASGI application
        module_path, app_name = app_path.split(":", 1)
        module = importlib.import_module(module_path)
        app = getattr(module, app_name)

        # create a test client
        client = TestClient(app)
        
        print("app", app.routes)
        print("MCP Server started, waiting for requests from stdin...", file=sys.stderr)
        
        # Handle requests until EOF
        while True:
            try:
                line = sys.stdin.readline()
                if not line:  # EOF
                    break
                
                # Check if the input is valid JSON
                try:
                    request_data = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON input: {str(e)}", file=sys.stderr)
                    continue
                
                print(f"Received request: {request_data}", file=sys.stderr)
                # Construct the path
                jsonrpc_method = request_data.get("method")
                path = f"{root_path}/{jsonrpc_method}"

                # Send the request to the ASGI application
                try:
                    response = client.post(path, json=request_data)
                    response_data = response.json()
                    
                    # Send the response back to the client
                    print(json.dumps(response_data, ensure_ascii=False))
                    sys.stdout.flush()
                except Exception as e:
                    # Send the error message to stderr
                    print(f"Error processing request: {str(e)}", file=sys.stderr)
                    print(traceback.format_exc(), file=sys.stderr)
                    sys.stderr.flush()
                
            except Exception as e:
                # Send the error message to stderr
                print(f"Unexpected error: {str(e)}", file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)
                sys.stderr.flush()
    except Exception as e:
        # Startup error
        print(f"Startup error: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
