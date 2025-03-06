# PowerShell script to deploy the DeepSeek Web Crawler API to Digital Ocean

# Function to check if a command exists
function Test-CommandExists {
    param ($command)
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    return $exists
}

# Check if doctl is installed
if (-not (Test-CommandExists "doctl")) {
    Write-Host "Digital Ocean CLI (doctl) is not installed. Installing now..." -ForegroundColor Yellow
    
    # Create a temporary directory
    $tempDir = Join-Path $env:TEMP "doctl-install"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    # Download doctl
    $doctlZip = Join-Path $tempDir "doctl.zip"
    $downloadUrl = "https://github.com/digitalocean/doctl/releases/download/v1.101.0/doctl-1.101.0-windows-amd64.zip"
    Write-Host "Downloading doctl from $downloadUrl..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $downloadUrl -OutFile $doctlZip
    
    # Extract doctl
    Write-Host "Extracting doctl..." -ForegroundColor Yellow
    Expand-Archive -Path $doctlZip -DestinationPath $tempDir -Force
    
    # Move doctl to a directory in PATH
    $doctlPath = Join-Path $tempDir "doctl.exe"
    $destPath = Join-Path $env:USERPROFILE "AppData\Local\Microsoft\WindowsApps"
    Copy-Item -Path $doctlPath -Destination $destPath -Force
    
    # Clean up
    Remove-Item -Path $tempDir -Recurse -Force
    
    Write-Host "doctl has been installed to $destPath" -ForegroundColor Green
    Write-Host "Please restart your terminal session for the changes to take effect." -ForegroundColor Yellow
    Write-Host "After restarting, run this script again to continue the deployment." -ForegroundColor Yellow
    exit
}

# Authenticate with Digital Ocean
Write-Host "Authenticating with Digital Ocean..." -ForegroundColor Yellow
Write-Host "Please go to https://cloud.digitalocean.com/account/api/tokens and create a new API token with write scope." -ForegroundColor Yellow
$token = Read-Host "Enter your Digital Ocean API token"
doctl auth init -t $token

# Check if authentication was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "Authentication failed. Please check your API token and try again." -ForegroundColor Red
    exit 1
}

Write-Host "Authentication successful!" -ForegroundColor Green

# Get environment variables
$groqApiKey = Get-Content .env | Where-Object { $_ -match "GROQ_API_KEY=" } | ForEach-Object { $_ -replace "GROQ_API_KEY=", "" }
$apiKey = Get-Content .env | Where-Object { $_ -match "API_KEY=" } | ForEach-Object { $_ -replace "API_KEY=", "" }

# Create app.yaml with correct values
Write-Host "Creating app specification..." -ForegroundColor Yellow

# Ask for GitHub repository details
$repoOwner = Read-Host "Enter your GitHub username"
$repoName = Read-Host "Enter the GitHub repository name (default: deepseek-web-crawler)"
if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "deepseek-web-crawler"
}

$appYaml = Get-Content app.yaml -Raw
$appYaml = $appYaml -replace "your-github-username/deepseek-web-crawler", "$repoOwner/$repoName"
Set-Content -Path app.yaml -Value $appYaml

# Create the app on Digital Ocean
Write-Host "Creating app on Digital Ocean App Platform..." -ForegroundColor Yellow
doctl apps create --spec app.yaml

# Check if app creation was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "App creation failed. Please check the error message above and try again." -ForegroundColor Red
    exit 1
}

# Get the app ID
$apps = doctl apps list --format ID,Spec.Name --no-header | Where-Object { $_ -match "deepseek-web-crawler-api" }
$appId = ($apps -split '\s+')[0]

# Set environment variables
Write-Host "Setting environment variables..." -ForegroundColor Yellow
doctl apps update $appId --set-env-vars "GROQ_API_KEY=$groqApiKey,API_KEY=$apiKey"

# Deploy the app
Write-Host "Deploying the app..." -ForegroundColor Yellow
doctl apps create deployment $appId

# Get the app URL
$appInfo = doctl apps get $appId --format DefaultIngress
$appUrl = ($appInfo -split '\s+')[-1]

Write-Host "Deployment initiated!" -ForegroundColor Green
Write-Host "Your API will be available at: $appUrl" -ForegroundColor Green
Write-Host "API Key: $apiKey" -ForegroundColor Green
Write-Host "Use this API Key in the X-API-Key header when making requests to the API." -ForegroundColor Yellow
Write-Host "Example curl command:" -ForegroundColor Yellow
Write-Host "curl -X POST '$appUrl/crawl' -H 'X-API-Key: $apiKey' -H 'Content-Type: application/json' -d '{\"config_name\": \"test\"}'" -ForegroundColor Cyan
