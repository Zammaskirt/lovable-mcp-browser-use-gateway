# Fly.io Deployment Script for Lovable MCP Gateway
# Usage: .\deploy.ps1

param(
    [string]$AppName = "lovable-mcp-gateway",
    [string]$Region = "iad",
    [switch]$FirstTime = $false
)

Write-Host "🚀 Lovable MCP Gateway - Fly.io Deployment" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "auth.json")) {
    Write-Host "❌ auth.json file not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "fly.toml")) {
    Write-Host "❌ fly.toml file not found" -ForegroundColor Red
    exit 1
}

Write-Host "✅ All files present" -ForegroundColor Green
Write-Host ""

# Check Fly CLI
Write-Host "🔍 Checking Fly CLI..." -ForegroundColor Yellow
try {
    $flyVersion = fly --version
    Write-Host "✅ Fly CLI installed: $flyVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Fly CLI not found. Install from https://fly.io/docs/hands-on/install-flyctl/" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check authentication
Write-Host "🔐 Checking Fly authentication..." -ForegroundColor Yellow
try {
    $whoami = fly auth whoami
    Write-Host "✅ Authenticated as: $whoami" -ForegroundColor Green
} catch {
    Write-Host "❌ Not authenticated. Run: fly auth login" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Extract secrets from .env
Write-Host "🔑 Extracting secrets from .env..." -ForegroundColor Yellow
$bearerToken = (Select-String -Path ".env" -Pattern "^MCP_BEARER_TOKEN=" | ForEach-Object { $_.Line -split "=" | Select-Object -Last 1 }).Trim()
$openrouterKey = (Select-String -Path ".env" -Pattern "^MCP_LLM_OPENROUTER_API_KEY=" | ForEach-Object { $_.Line -split "=" | Select-Object -Last 1 }).Trim()

if (-not $bearerToken -or -not $openrouterKey) {
    Write-Host "❌ Missing required secrets in .env" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Secrets extracted" -ForegroundColor Green
Write-Host ""

# First time setup
if ($FirstTime) {
    Write-Host "🚀 First-time setup: Creating Fly app..." -ForegroundColor Yellow
    fly launch --name $AppName --region $Region --no-deploy
    Write-Host "✅ Fly app created" -ForegroundColor Green
    Write-Host ""
}

# Set secrets
Write-Host "🔐 Setting secrets on Fly.io..." -ForegroundColor Yellow
fly secrets set MCP_BEARER_TOKEN=$bearerToken
fly secrets set MCP_LLM_OPENROUTER_API_KEY=$openrouterKey
fly secrets set MCP_LLM_MODEL_NAME="anthropic/claude-3.5-sonnet-20241022"
Write-Host "✅ Secrets set" -ForegroundColor Green
Write-Host ""

# Deploy
Write-Host "📦 Deploying to Fly.io..." -ForegroundColor Yellow
fly deploy
Write-Host "✅ Deployment complete" -ForegroundColor Green
Write-Host ""

# Get app info
Write-Host "📊 App Information:" -ForegroundColor Cyan
fly info
Write-Host ""

# Test health endpoint
Write-Host "🧪 Testing health endpoint..." -ForegroundColor Yellow
$appUrl = (fly info | Select-String "Hostname" | ForEach-Object { $_.Line -split ":" | Select-Object -Last 1 }).Trim()
if ($appUrl) {
    try {
        $response = Invoke-WebRequest -Uri "https://$appUrl/health" -UseBasicParsing
        Write-Host "✅ Health check passed" -ForegroundColor Green
        Write-Host $response.Content
    } catch {
        Write-Host "⚠️  Health check failed (may be starting up)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 Deployment complete!" -ForegroundColor Green
Write-Host "📍 App URL: https://$appUrl" -ForegroundColor Cyan
Write-Host "📋 View logs: fly logs" -ForegroundColor Cyan

