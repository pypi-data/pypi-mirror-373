#!/bin/bash
# Quick test script for apartment-trade MCP server

echo "Testing apartment-trade MCP server..."
echo "======================================="

# Test server startup with dummy API key
export API_KEY="test-key-12345"

# Test that the server can start
echo "1. Testing server startup..."
timeout 2 python -m data_go_mcp.apartment_trade.server 2>&1 | head -20 || true

echo ""
echo "2. Running unit tests..."
python -m pytest tests/test_models.py -v --tb=short

echo ""
echo "======================================="
echo "Test completed!"