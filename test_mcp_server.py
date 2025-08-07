
#!/usr/bin/env python3
"""
Test script to verify MCP server end-to-end functionality
"""
import requests
import json
import time

# Test configuration
MCP_SERVER_URL = "http://0.0.0.0:5000"
TEST_WALLET = "0x742d35Cc6635C0532925a3b8D2C69AaE2b8de59A"

def test_web_interface():
    """Test web interface endpoints"""
    print("🌐 Testing Web Interface...")
    
    endpoints = [
        "/",
        "/dashboard", 
        "/api-docs",
        "/ai-agent"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{MCP_SERVER_URL}{endpoint}")
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"  {endpoint}: {status}")
        except Exception as e:
            print(f"  {endpoint}: ❌ FAIL ({e})")

def test_api_endpoints():
    """Test REST API endpoints"""
    print("\n🔌 Testing REST API...")
    
    # Test portfolio endpoint
    try:
        response = requests.get(f"{MCP_SERVER_URL}/api/v1/portfolio/{TEST_WALLET}")
        if response.status_code == 200:
            print("  Portfolio API: ✅ PASS")
        else:
            print(f"  Portfolio API: ❌ FAIL ({response.status_code})")
    except Exception as e:
        print(f"  Portfolio API: ❌ FAIL ({e})")
    
    # Test swap endpoint (demo mode)
    try:
        swap_data = {
            "wallet_address": TEST_WALLET,
            "blockchain": "ethereum",
            "token_in": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "token_out": "0xA0b86a33E6411D426C3d77A6CF0C0DFEcb7fD9A9",
            "amount_in": "0.1",
            "protocol": "uniswap"
        }
        
        response = requests.post(
            f"{MCP_SERVER_URL}/api/v1/swap",
            json=swap_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("  Swap API: ✅ PASS")
            else:
                print(f"  Swap API: ⚠️  PARTIAL ({result.get('message', 'Unknown')})")
        else:
            print(f"  Swap API: ❌ FAIL ({response.status_code})")
    except Exception as e:
        print(f"  Swap API: ❌ FAIL ({e})")

def test_mcp_protocol():
    """Test MCP JSON-RPC protocol"""
    print("\n🤖 Testing MCP Protocol...")
    
    # Test basic MCP request
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "defi.chains",
        "params": {},
        "id": 1
    }
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp",
            json=mcp_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print("  MCP Protocol: ✅ PASS")
                print(f"    Response: {result['result']}")
            else:
                print(f"  MCP Protocol: ❌ FAIL (No result in response)")
        else:
            print(f"  MCP Protocol: ❌ FAIL ({response.status_code})")
    except Exception as e:
        print(f"  MCP Protocol: ❌ FAIL ({e})")

def test_ai_agent():
    """Test AI Agent functionality"""
    print("\n🧠 Testing AI Agent...")
    
    try:
        # Import and test AI agent locally
        from ai_agent import DeFiAIAgent
        
        agent = DeFiAIAgent(mcp_server_url=MCP_SERVER_URL)
        
        # Test portfolio analysis
        analysis = agent.analyze_portfolio(TEST_WALLET)
        
        if analysis.get("success"):
            print("  AI Portfolio Analysis: ✅ PASS")
            print(f"    Total Value: ${analysis['analysis'].get('total_value', 0):,.2f}")
            print(f"    AI Insights: {analysis['analysis'].get('ai_insights', 'None')[:100]}...")
        else:
            print(f"  AI Portfolio Analysis: ❌ FAIL ({analysis.get('error', 'Unknown')})")
            
    except ImportError:
        print("  AI Agent: ⚠️  SKIP (Module not found)")
    except Exception as e:
        print(f"  AI Agent: ❌ FAIL ({e})")

def test_blockchain_connections():
    """Test blockchain connectivity"""
    print("\n⛓️  Testing Blockchain Connections...")
    
    try:
        from blockchain.ethereum import EthereumClient
        from blockchain.polygon import PolygonClient
        from blockchain.solana import SolanaClient
        
        # Test Ethereum
        try:
            eth_client = EthereumClient()
            if hasattr(eth_client, 'w3') and eth_client.w3:
                print("  Ethereum: ✅ CONNECTED")
            else:
                print("  Ethereum: ❌ DISCONNECTED")
        except Exception as e:
            print(f"  Ethereum: ❌ ERROR ({e})")
        
        # Test Polygon
        try:
            poly_client = PolygonClient()
            if hasattr(poly_client, 'w3') and poly_client.w3:
                print("  Polygon: ✅ CONNECTED")
            else:
                print("  Polygon: ❌ DISCONNECTED")
        except Exception as e:
            print(f"  Polygon: ❌ ERROR ({e})")
        
        # Test Solana
        try:
            sol_client = SolanaClient()
            if hasattr(sol_client, 'client') and sol_client.client:
                print("  Solana: ✅ CONNECTED")
            else:
                print("  Solana: ❌ DISCONNECTED")
        except Exception as e:
            print(f"  Solana: ❌ ERROR ({e})")
            
    except ImportError as e:
        print(f"  Blockchain modules: ❌ IMPORT ERROR ({e})")

def main():
    """Run all tests"""
    print("🔬 DeFi MCP Server End-to-End Test")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    test_web_interface()
    test_api_endpoints()
    test_mcp_protocol()
    test_ai_agent()
    test_blockchain_connections()
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")
    print("\n💡 To fix issues:")
    print("1. Add proper Infura project ID to .env file")
    print("2. Configure API keys for production use")
    print("3. Test with real wallet addresses")

if __name__ == "__main__":
    main()
