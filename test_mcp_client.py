
#!/usr/bin/env python3
"""
Simple MCP client to test protocol functionality
"""
import requests
import json

class MCPClient:
    def __init__(self, server_url="http://0.0.0.0:5000"):
        self.server_url = server_url
        self.session = requests.Session()
    
    def call_method(self, method, params=None, request_id=1):
        """Call an MCP method"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}

def test_mcp_methods():
    """Test various MCP methods"""
    client = MCPClient()
    
    test_wallet = "0x742d35Cc6635C0532925a3b8D2C69AaE2b8de59A"
    
    tests = [
        ("defi.chains", {}),
        ("defi.protocols", {}),
        ("defi.portfolio", {"wallet_address": test_wallet, "blockchain": "ethereum"}),
        ("defi.positions", {"wallet_address": test_wallet, "blockchain": "ethereum"}),
        ("defi.swap", {
            "wallet_address": test_wallet,
            "blockchain": "ethereum", 
            "token_in": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "token_out": "0xA0b86a33E6411D426C3d77A6CF0C0DFEcb7fD9A9",
            "amount_in": "0.1"
        })
    ]
    
    print("🧪 Testing MCP Methods")
    print("-" * 40)
    
    for method, params in tests:
        print(f"\n📞 Calling: {method}")
        result = client.call_method(method, params)
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
        elif "result" in result:
            print(f"   ✅ Success: {json.dumps(result['result'], indent=2)[:200]}...")
        else:
            print(f"   ⚠️  Unexpected response: {result}")

if __name__ == "__main__":
    test_mcp_methods()
