$ErrorActionPreference = "Stop"

$apiKey = [Environment]::GetEnvironmentVariable("STITCH_API_KEY", "User")
if (-not $apiKey) {
    throw "STITCH_API_KEY is missing from the Windows user environment."
}

$env:STITCH_API_KEY = $apiKey
$proxyUrl = [Environment]::GetEnvironmentVariable("STITCH_PROXY_URL", "User")
if ($proxyUrl) {
    $env:STITCH_PROXY_URL = $proxyUrl
}

$scriptPath = Join-Path $PSScriptRoot "stitch_mcp_proxy.mjs"

node $scriptPath
