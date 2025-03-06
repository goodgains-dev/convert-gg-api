# Deploying DeepSeek Web Crawler API to Digital Ocean

This guide will walk you through the process of deploying the DeepSeek Web Crawler API to Digital Ocean App Platform.

## Prerequisites

- A Digital Ocean account
- Git repository (GitHub, GitLab, etc.) with your code
- Digital Ocean API token with write access

## Deployment Options

You can deploy the application using one of the following methods:

### Option 1: Using the Deployment Scripts (Recommended)

#### For Windows Users

1. Open PowerShell and navigate to the project directory
2. Run the deployment script:
   ```powershell
   .\deploy_to_digitalocean.ps1
   ```
3. Follow the prompts to complete the deployment

#### For macOS/Linux Users

1. Open Terminal and navigate to the project directory
2. Make the script executable (if needed):
   ```bash
   chmod +x deploy_to_digitalocean.sh
   ```
3. Run the deployment script:
   ```bash
   ./deploy_to_digitalocean.sh
   ```
4. Follow the prompts to complete the deployment

### Option 2: Manual Deployment

1. Install the Digital Ocean CLI (doctl):
   - Windows: Download from [GitHub](https://github.com/digitalocean/doctl/releases)
   - macOS: `brew install doctl`
   - Linux: Follow instructions on [GitHub](https://github.com/digitalocean/doctl#installing-doctl)

2. Authenticate with Digital Ocean:
   ```bash
   doctl auth init
   ```

3. Create the app on Digital Ocean App Platform:
   ```bash
   doctl apps create --spec app.yaml
   ```

4. Set environment variables:
   ```bash
   doctl apps update <APP_ID> --set-env-vars "GROQ_API_KEY=<your_groq_api_key>,API_KEY=<your_api_key>"
   ```

5. Deploy the app:
   ```bash
   doctl apps create deployment <APP_ID>
   ```

## Using the API

Once deployed, you can access your API at the URL provided by Digital Ocean. You'll need to include your API key in the `X-API-Key` header for all requests.

### Example API Requests

#### List Available Configurations

```bash
curl -X GET 'https://your-app-url.ondigitalocean.app/configs' \
  -H 'X-API-Key: your_api_key'
```

#### Crawl a Website Using a Predefined Configuration

```bash
curl -X POST 'https://your-app-url.ondigitalocean.app/crawl' \
  -H 'X-API-Key: your_api_key' \
  -H 'Content-Type: application/json' \
  -d '{
    "config_name": "test"
  }'
```

#### Crawl a Website Using a Custom Configuration

```bash
curl -X POST 'https://your-app-url.ondigitalocean.app/crawl' \
  -H 'X-API-Key: your_api_key' \
  -H 'Content-Type: application/json' \
  -d '{
    "custom_config": {
      "BASE_URL": "https://example.com",
      "CSS_SELECTOR": "div.product-card",
      "REQUIRED_KEYS": ["name", "price"],
      "OPTIONAL_KEYS": ["description", "image_url"],
      "CRAWLER_CONFIG": {
        "MULTI_PAGE": false,
        "HEADLESS": true,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "TIMEOUT": 30000,
        "WAIT_FOR": 1000
      },
      "LLM_CONFIG": {
        "MODEL": "llama3-70b-8192",
        "TEMPERATURE": 0.2,
        "MAX_TOKENS": 1024,
        "INSTRUCTION": "Extract product information from each product card: name and price."
      }
    }
  }'
```

## Troubleshooting

- If you encounter issues with the deployment, check the Digital Ocean App Platform logs for more information.
- Ensure your GitHub repository is public or that you've connected Digital Ocean to your GitHub account.
- Make sure your environment variables are set correctly.
