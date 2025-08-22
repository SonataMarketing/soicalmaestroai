#!/bin/bash

# SocialMaestro - Create Admin User Example
# This script demonstrates how to create the first admin user via API

set -e  # Exit on any error

API_BASE="http://localhost:8000/api"

echo "🚀 SocialMaestro - Admin Setup"
echo "========================================"

# Check if bootstrap is needed
echo "📋 Checking bootstrap status..."
BOOTSTRAP_STATUS=$(curl -s "${API_BASE}/auth/bootstrap/status")
echo "Response: $BOOTSTRAP_STATUS"

# Parse the JSON response to check if bootstrap is needed
BOOTSTRAP_NEEDED=$(echo $BOOTSTRAP_STATUS | grep -o '"bootstrap_needed":[^,]*' | cut -d: -f2)

if [[ "$BOOTSTRAP_NEEDED" == "true" ]]; then
    echo "✅ Bootstrap needed - creating admin user..."

    # Create admin user
    echo "🔑 Creating admin user..."

    ADMIN_DATA='{
        "email": "admin@example.com",
        "full_name": "Admin User",
        "password": "AdminPass123!",
        "confirm_password": "AdminPass123!"
    }'

    ADMIN_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/bootstrap" \
        -H "Content-Type: application/json" \
        -d "$ADMIN_DATA")

    echo "Admin user created:"
    echo "$ADMIN_RESPONSE" | python3 -m json.tool

    # Login to get token
    echo ""
    echo "🔐 Logging in as admin..."

    LOGIN_DATA='{
        "email": "admin@example.com",
        "password": "AdminPass123!"
    }'

    TOKEN_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/login" \
        -H "Content-Type: application/json" \
        -d "$LOGIN_DATA")

    # Extract access token
    ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

    if [[ -n "$ACCESS_TOKEN" ]]; then
        echo "✅ Login successful!"
        echo "Access token: ${ACCESS_TOKEN:0:50}..."

        # Test authenticated endpoint
        echo ""
        echo "🔍 Testing authenticated endpoint..."

        USER_INFO=$(curl -s -X GET "${API_BASE}/auth/me" \
            -H "Authorization: Bearer $ACCESS_TOKEN")

        echo "User info:"
        echo "$USER_INFO" | python3 -m json.tool

        echo ""
        echo "🎉 Setup complete!"
        echo ""
        echo "Next steps:"
        echo "1. Save your admin credentials securely"
        echo "2. Configure social media API keys in .env"
        echo "3. Create additional users via: POST ${API_BASE}/auth/register"
        echo "4. Access API docs at: http://localhost:8000/docs"

        # Save token to file for convenience
        echo "$ACCESS_TOKEN" > .admin_token
        echo ""
        echo "💡 Admin token saved to .admin_token file"
        echo "   Use it like: curl -H \"Authorization: Bearer \$(cat .admin_token)\" ..."

    else
        echo "❌ Login failed"
        echo "Response: $TOKEN_RESPONSE"
        exit 1
    fi

else
    echo "❌ Bootstrap not needed - users already exist"
    echo "Use regular login instead:"
    echo ""
    echo "curl -X POST \"${API_BASE}/auth/login\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"email\": \"your-email\", \"password\": \"your-password\"}'"
fi

echo ""
echo "📚 For more examples, see:"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Setup Guide: SETUP.md"
echo "   - README: README.md"
