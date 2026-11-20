#!/usr/bin/env bash
# Deploy the site to an Azure Storage "static website" ($web blob container).
#
# Usage:
#   ./deploy/deploy-azure-blob.sh <storage-account-name> [resource-group] [location]
#
# If the resource group / storage account don't exist they are created.
# Requires: Azure CLI (`az login` first).
set -euo pipefail

ACCOUNT="${1:?storage account name required (3-24 lowercase letters/digits)}"
RG="${2:-rg-hyperpop-reroll-guide}"
LOCATION="${3:-eastus}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Resource group: $RG ($LOCATION)"
az group create --name "$RG" --location "$LOCATION" --output none

if ! az storage account show --name "$ACCOUNT" --resource-group "$RG" --output none 2>/dev/null; then
  echo "==> Creating storage account $ACCOUNT"
  az storage account create \
    --name "$ACCOUNT" --resource-group "$RG" --location "$LOCATION" \
    --sku Standard_LRS --kind StorageV2 --allow-blob-public-access false \
    --output none
fi

echo "==> Enabling static website"
az storage blob service-properties update \
  --account-name "$ACCOUNT" --auth-mode login \
  --static-website --index-document index.html --404-document index.html \
  --output none 2>/dev/null || \
az storage blob service-properties update \
  --account-name "$ACCOUNT" \
  --static-website --index-document index.html --404-document index.html \
  --output none

echo "==> Uploading site files to \$web"
az storage blob upload-batch \
  --account-name "$ACCOUNT" \
  --destination '$web' \
  --source "$ROOT" \
  --pattern "*" \
  --overwrite \
  --exclude-pattern "deploy/*" --exclude-pattern "tools/*" --exclude-pattern "print/*" --exclude-pattern ".git/*" --exclude-pattern ".github/*" \
  --exclude-pattern "*.md" --exclude-pattern ".gitignore" \
  --output none

URL=$(az storage account show --name "$ACCOUNT" --resource-group "$RG" --query "primaryEndpoints.web" --output tsv)
echo "==> Live at: $URL"
