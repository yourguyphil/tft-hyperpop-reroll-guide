# Deploy the site to an Azure Storage "static website" ($web blob container).
#
# Usage:
#   .\deploy\deploy-azure-blob.ps1 -Account <storage-account-name> [-ResourceGroup rg] [-Location eastus]
#
# Requires: Azure CLI (run `az login` first).
param(
  [Parameter(Mandatory = $true)][string]$Account,
  [string]$ResourceGroup = "rg-hyperpop-reroll-guide",
  [string]$Location = "eastus"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "==> Resource group: $ResourceGroup ($Location)"
az group create --name $ResourceGroup --location $Location --output none

az storage account show --name $Account --resource-group $ResourceGroup --output none 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "==> Creating storage account $Account"
  az storage account create --name $Account --resource-group $ResourceGroup --location $Location `
    --sku Standard_LRS --kind StorageV2 --allow-blob-public-access false --output none
}

Write-Host "==> Enabling static website"
az storage blob service-properties update --account-name $Account `
  --static-website --index-document index.html --404-document index.html --output none

Write-Host "==> Uploading site files to `$web"
az storage blob upload-batch --account-name $Account --destination '$web' --source $Root `
  --overwrite `
  --exclude-pattern "deploy/*" --exclude-pattern "tools/*" --exclude-pattern "print/*" --exclude-pattern ".git/*" --exclude-pattern ".github/*" `
  --exclude-pattern "*.md" --exclude-pattern ".gitignore" --output none

$url = az storage account show --name $Account --resource-group $ResourceGroup --query "primaryEndpoints.web" --output tsv
Write-Host "==> Live at: $url"
