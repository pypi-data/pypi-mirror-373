#!/usr/bin/env python3
"""Test script for show2user MCP server"""

import asyncio
import json
from mcp_show2user.server import serve

async def test_show_report():
    """Simple test to verify the tool schema works"""
    from mcp_show2user.server import ShowReport
    
    # Test valid parameters
    test_cases = [
        {
            "title": "Sales Report",
            "type": "html", 
            "content": "https://example.com/report.html",
            "content_type": "url"
        },
        {
            "title": "Analysis Report",
            "type": "md",
            "content": "# Analysis\n\nThis is a markdown report.",
            "content_type": "text"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            # Validate the model
            report = ShowReport(**test_case)
            print(f"✅ Test case {i} passed: {report.title}")
            
            # Show what the JSON output would look like
            output = {
                "title": report.title,
                "type": report.type,
                "content": report.content,
                "content_type": report.content_type
            }
            print(f"   Output: {json.dumps(output, indent=2)}")
            
        except Exception as e:
            print(f"❌ Test case {i} failed: {e}")
    
    # Test invalid cases
    invalid_cases = [
        {"title": "Test", "type": "invalid", "content": "test", "content_type": "text"},
        {"title": "Test", "type": "html", "content": "test", "content_type": "invalid"}
    ]
    
    print("\nTesting invalid cases:")
    for i, invalid_case in enumerate(invalid_cases, 1):
        try:
            report = ShowReport(**invalid_case)
            print(f"❌ Invalid case {i} should have failed but passed")
        except Exception as e:
            print(f"✅ Invalid case {i} correctly failed: validation working")

if __name__ == "__main__":
    print("Testing Show2User MCP Server")
    print("=" * 40)
    asyncio.run(test_show_report())