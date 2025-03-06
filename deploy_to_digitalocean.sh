#!/bin/bash

# Bash script to deploy the DeepSeek Web Crawler API to Digital Ocean

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if doctl is installed
if ! command_exists doctl; then
    echo "Digital Ocean CLI (doctl) is not installed. Installing now..."
    
    # Check the operating system
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install doctl
        else
            echo "Homebrew is not installed. Please install Homebrew first:"
            echo "https://brew.sh/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "Downloading doctl..."
        cd /tmp
        wget https://github.com/digitalocean/doctl/releases/download/v1.101.0/doctl-1.101.0-linux-amd64.tar.gz
        tar xf doctl-1.101.0-linux-amd64.tar.gz
        sudo mv doctl /usr/local/bin
        rm doctl-1.101.0-linux-amd64.tar.gz
    else
        echo "Unsupported operating system. Please install doctl manually:"
        echo "https://github.com/digitalocean/doctl#installing-doctl"
        exit 1
    fi
    
    echo "doctl has been installed."
    echo "Please restart your terminal session for the changes to take effect."
    echo "After restarting, run this script again to continue the deployment."
    exit 0
fi

# Authenticate with Digital Ocean
echo "Authenticating with Digital Ocean..."
echo "Please go to https://cloud.digitalocean.com/account/api/tokens and create a new API token with write scope."
read -p "Enter your Digital Ocean API token: " token
doctl auth init -t "$token"

# Check if authentication was successful
if [ $? -ne 0 ]; then
    echo "Authentication failed. Please check your API token and try again."
    exit 1
fi

echo "Authentication successful!"

# Get environment variables
groq_api_key=$(grep GROQ_API_KEY .env | cut -d '=' -f2)
api_key=$(grep API_KEY .env | cut -d '=' -f2)

# Create app.yaml with correct values
echo "Creating app specification..."

# Ask for GitHub repository details
read -p "Enter your GitHub username: " repo_owner
read -p "Enter the GitHub repository name (default: deepseek-web-crawler): " repo_name
repo_name=${repo_name:-deepseek-web-crawler}

# Update app.yaml
sed -i.bak "s|your-github-username/deepseek-web-crawler|$repo_owner/$repo_name|g" app.yaml
rm app.yaml.bak

# Create the app on Digital Ocean
echo "Creating app on Digital Ocean App Platform..."
doctl apps create --spec app.yaml

# Check if app creation was successful
if [ $? -ne 0 ]; then
    echo "App creation failed. Please check the error message above and try again."
    exit 1
fi

# Get the app ID
app_id=$(doctl apps list --format ID,Spec.Name --no-header | grep deepseek-web-crawler-api | awk '{print $1}')

# Set environment variables
echo "Setting environment variables..."
doctl apps update $app_id --set-env-vars "GROQ_API_KEY=$groq_api_key,API_KEY=$api_key"

# Deploy the app
echo "Deploying the app..."
doctl apps create deployment $app_id

# Get the app URL
app_url=$(doctl apps get $app_id --format DefaultIngress | tail -n 1 | awk '{print $1}')

echo "Deployment initiated!"
echo "Your API will be available at: $app_url"
echo "API Key: $api_key"
echo "Use this API Key in the X-API-Key header when making requests to the API."
echo "Example curl command:"
echo "curl -X POST '$app_url/crawl' -H 'X-API-Key: $api_key' -H 'Content-Type: application/json' -d '{\"config_name\": \"test\"}'"
