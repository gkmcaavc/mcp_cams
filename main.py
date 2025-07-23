#!/usr/bin/env python3
"""
Create Cams Biometrics application for read information
Communicates with Claude AI via MCP protocol
"""

import sys
import json
import logging
import os
from datetime import datetime

# Set environment for UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_cams_biometrics.log', encoding='utf-8'),
        logging.StreamHandler(sys.stderr)
    ]
)

class SimpleMCPCalculator:
    def __init__(self):
        logging.info("Simple MCP Calculator initialized")
    
    def create_response(self, request_id, result=None, error=None):
        """Create a proper MCP JSON-RPC response"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id if request_id is not None else "unknown"
        }
        
        if error:
            response["error"] = {
                "code": error.get("code", -32603),
                "message": error.get("message", "Internal error"),
                "data": error.get("data")
            }
        else:
            response["result"] = result if result is not None else {}
        
        return response
    
    def add_numbers(self, num1, num2):
        """Add two numbers together"""
        try:
            # Convert to float to handle both integers and decimals
            n1 = float(num1)
            n2 = float(num2)
            result = n1 + n2
            
            # If result is a whole number, return as int
            if result.is_integer():
                result = int(result)
            
            return {
                "number1": n1,
                "number2": n2,
                "result": result,
                "operation": "addition",
                "timestamp": datetime.now().isoformat()
            }
            
        except (ValueError, TypeError) as e:
            logging.error(f"Addition error: {str(e)}")
            return {
                "number1": num1,
                "number2": num2,
                "error": f"Invalid numbers provided: {str(e)}",
                "operation": "addition",
                "timestamp": datetime.now().isoformat()
            }
    
    def handle_initialize(self, request_id, params):
        """Handle MCP initialize request"""
        logging.info("Handling initialize request")
        
        protocol_version = params.get("protocolVersion")
        if not protocol_version:
            return self.create_response(request_id, error={
                "code": -32602,
                "message": "Invalid params: protocolVersion is required"
            })
        
        result = {
            "protocolVersion": protocol_version,
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "serverInfo": {
                "name": "Simple MCP Calculator",
                "version": "1.0.0",
                "description": "Simple calculator that adds two numbers"
            }
        }
        
        return self.create_response(request_id, result)
    
    def handle_tools_list(self, request_id, params):
        """Handle tools/list request"""
        logging.info("Handling tools/list request")
        
        tools = [
            {
                "name": "add_numbers",
                "description": "Add two numbers together",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "number1": {
                            "type": "number",
                            "description": "First number to add"
                        },
                        "number2": {
                            "type": "number", 
                            "description": "Second number to add"
                        }
                    },
                    "required": ["number1", "number2"]
                }
            }
        ]
        
        return self.create_response(request_id, {"tools": tools})
    
    def handle_tools_call(self, request_id, params):
        """Handle tools/call request"""
        if not isinstance(params, dict):
            return self.create_response(request_id, error={
                "code": -32602,
                "message": "Invalid params: must be an object"
            })
        
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return self.create_response(request_id, error={
                "code": -32602,
                "message": "Invalid params: 'name' is required"
            })
        
        logging.info(f"Handling tools/call request for: {tool_name}")
        
        try:
            if tool_name == "add_numbers":
                number1 = arguments.get("number1")
                number2 = arguments.get("number2")
                
                if number1 is None or number2 is None:
                    return self.create_response(request_id, error={
                        "code": -32602,
                        "message": "Both number1 and number2 are required"
                    })
                
                calculation_result = self.add_numbers(number1, number2)
                
                if 'error' in calculation_result:
                    result_text = f"""Addition Error:
Number 1: {calculation_result['number1']}
Number 2: {calculation_result['number2']}
Error: {calculation_result['error']}
Timestamp: {calculation_result['timestamp']}"""
                else:
                    result_text = f"""Addition Result:
{calculation_result['number1']} + {calculation_result['number2']} = {calculation_result['result']}
Timestamp: {calculation_result['timestamp']}"""
                
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ],
                    "isError": 'error' in calculation_result
                }
                
                return self.create_response(request_id, result)
            
            else:
                return self.create_response(request_id, error={
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                })
                
        except Exception as e:
            logging.error(f"Error executing tool {tool_name}: {str(e)}")
            return self.create_response(request_id, error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            })
    
    def handle_request(self, request):
        """Handle incoming MCP request"""
        if not isinstance(request, dict):
            return self.create_response(None, error={
                "code": -32700,
                "message": "Parse error: request must be an object"
            })
        
        jsonrpc = request.get("jsonrpc")
        if jsonrpc != "2.0":
            return self.create_response(request.get("id"), error={
                "code": -32600,
                "message": "Invalid Request: jsonrpc must be '2.0'"
            })
        
        method = request.get("method")
        if not method:
            return self.create_response(request.get("id"), error={
                "code": -32600,
                "message": "Invalid Request: 'method' is required"
            })
        
        params = request.get("params", {})
        request_id = request.get("id")
        
        logging.info(f"Processing MCP request: {method} (ID: {request_id})")
        
        try:
            if method == "initialize":
                return self.handle_initialize(request_id, params)
            elif method == "tools/list":
                return self.handle_tools_list(request_id, params)
            elif method == "tools/call":
                return self.handle_tools_call(request_id, params)
            else:
                logging.warning(f"Unknown method: {method}")
                return self.create_response(request_id, error={
                    "code": -32601,
                    "message": f"Method not found: {method}"
                })
        except Exception as e:
            logging.error(f"Error handling request {method}: {str(e)}", exc_info=True)
            return self.create_response(request_id, error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            })

def main():
    """Main client loop"""
    calculator = SimpleMCPCalculator()
    
    logging.info("Simple MCP Calculator Started")
    logging.info("Ready to receive MCP requests from Claude AI...")
    
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                logging.info("EOF received, shutting down")
                break
                
            line = line.strip()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                response = calculator.handle_request(request)
                
                response_json = json.dumps(response, ensure_ascii=False)
                print(response_json, flush=True)
                logging.debug(f"Sent response: {response_json}")
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {str(e)} for input: {line}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
            except Exception as e:
                logging.error(f"Request handling error: {str(e)}", exc_info=True)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        logging.info("MCP Calculator stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        logging.info("MCP Calculator shutdown complete")

if __name__ == "__main__":
    main()