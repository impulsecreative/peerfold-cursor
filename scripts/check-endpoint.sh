#!/usr/bin/env bash
# Confirms https://app.peerfold.com/api/mcp still answers an anonymous request
# the way an OAuth-capable MCP client needs: 401, a WWW-Authenticate header
# naming the protected-resource metadata, and a metadata document that points
# at the authorization server. Asserts the values observed on 2026-10-13.
set -euo pipefail

MCP_URL="https://app.peerfold.com/api/mcp"
PRM_URL="https://app.peerfold.com/.well-known/oauth-protected-resource/api/mcp"
AS_URL="https://app.peerfold.com/.well-known/oauth-authorization-server"

headers=$(curl -sS -D - -o /dev/null "$MCP_URL")
status=$(printf '%s\n' "$headers" | head -1 | awk '{print $2}')
[ "$status" = "401" ] || { echo "Expected 401 from $MCP_URL, got $status"; exit 1; }
www=$(printf '%s\n' "$headers" | tr -d '\r' | grep -i '^www-authenticate:' || true)
[ -n "$www" ] || { echo "No WWW-Authenticate header on the 401"; exit 1; }
printf '%s\n' "$www" | grep -q 'Bearer realm="Peerfold MCP"' || { echo "Unexpected realm: $www"; exit 1; }
printf '%s\n' "$www" | grep -q "resource_metadata=\"$PRM_URL\"" || { echo "Unexpected resource_metadata: $www"; exit 1; }

prm=$(curl -sS -f "$PRM_URL")
echo "$prm" | grep -q "\"resource\":\"$MCP_URL\"" || { echo "Protected-resource document does not name $MCP_URL: $prm"; exit 1; }
echo "$prm" | grep -q '"authorization_servers":\["https://app.peerfold.com"\]' || { echo "Unexpected authorization_servers: $prm"; exit 1; }
echo "$prm" | grep -q '"bearer_methods_supported":\["header"\]' || { echo "Unexpected bearer_methods_supported: $prm"; exit 1; }

as=$(curl -sS -f "$AS_URL")
for key in '"authorization_endpoint":"https://app.peerfold.com/api/oauth/authorize"' \
           '"token_endpoint":"https://app.peerfold.com/api/oauth/token"' \
           '"registration_endpoint":"https://app.peerfold.com/api/oauth/register"' \
           '"revocation_endpoint":"https://app.peerfold.com/api/oauth/revoke"' \
           '"code_challenge_methods_supported":\["S256"\]'; do
  echo "$as" | grep -q "$key" || { echo "Authorization server document is missing $key: $as"; exit 1; }
done

echo "Endpoint check passed: 401 with resource_metadata, protected-resource and authorization-server documents as expected."
