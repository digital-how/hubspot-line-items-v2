import os
import json
import hmac
import hashlib
import base64
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, session, url_for
from flask_cors import CORS
import requests
from urllib.parse import urlencode, parse_qs
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HubSpot OAuth configuration
HUBSPOT_CLIENT_ID = os.environ.get('HUBSPOT_CLIENT_ID')
HUBSPOT_CLIENT_SECRET = os.environ.get('HUBSPOT_CLIENT_SECRET')
HUBSPOT_REDIRECT_URI = os.environ.get('HUBSPOT_REDIRECT_URI')
HUBSPOT_SCOPES = 'crm.objects.companies.read crm.objects.deals.read crm.objects.line_items.read'

# In-memory storage for tokens (use database in production)
token_storage = {}

def verify_hubspot_signature(payload, signature, secret):
    """Verify HubSpot webhook signature"""
    if not signature or not secret:
        return False
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def get_hubspot_access_token(portal_id):
    """Get access token for a portal"""
    token_data = token_storage.get(portal_id)
    if not token_data:
        return None
    
    # Check if token is expired
    if datetime.now() > token_data['expires_at']:
        # Try to refresh token
        refresh_token = token_data.get('refresh_token')
        if refresh_token:
            return refresh_access_token(portal_id, refresh_token)
        return None
    
    return token_data['access_token']

def refresh_access_token(portal_id, refresh_token):
    """Refresh access token using refresh token"""
    token_url = 'https://api.hubapi.com/oauth/v1/token'
    data = {
        'grant_type': 'refresh_token',
        'client_id': HUBSPOT_CLIENT_ID,
        'client_secret': HUBSPOT_CLIENT_SECRET,
        'refresh_token': refresh_token
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        token_storage[portal_id] = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token', refresh_token),
            'expires_at': datetime.now() + timedelta(seconds=token_data['expires_in']),
            'scope': token_data.get('scope', '')
        }
        return token_data['access_token']
    
    logger.error(f"Failed to refresh token for portal {portal_id}: {response.text}")
    return None

@app.route('/oauth/start')
def oauth_start():
    """Start OAuth flow"""
    params = {
        'client_id': HUBSPOT_CLIENT_ID,
        'redirect_uri': HUBSPOT_REDIRECT_URI,
        'scope': HUBSPOT_SCOPES,
        'response_type': 'code'
    }
    
    auth_url = f"https://app.hubspot.com/oauth/authorize?{urlencode(params)}"
    return redirect(auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    """Handle OAuth callback"""
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400
    
    # Exchange code for tokens
    token_url = 'https://api.hubapi.com/oauth/v1/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': HUBSPOT_CLIENT_ID,
        'client_secret': HUBSPOT_CLIENT_SECRET,
        'redirect_uri': HUBSPOT_REDIRECT_URI,
        'code': code
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        logger.error(f"Token exchange failed: {response.text}")
        return jsonify({'error': 'Failed to exchange code for tokens'}), 400
    
    token_data = response.json()
    
    # Get portal information
    portal_url = 'https://api.hubapi.com/oauth/v1/access-tokens/' + token_data['access_token']
    portal_response = requests.get(portal_url)
    
    if portal_response.status_code != 200:
        logger.error(f"Failed to get portal info: {portal_response.text}")
        return jsonify({'error': 'Failed to get portal information'}), 400
    
    portal_data = portal_response.json()
    portal_id = portal_data['hub_id']
    
    # Store tokens
    token_storage[portal_id] = {
        'access_token': token_data['access_token'],
        'refresh_token': token_data.get('refresh_token'),
        'expires_at': datetime.now() + timedelta(seconds=token_data['expires_in']),
        'scope': token_data.get('scope', '')
    }
    
    return jsonify({
        'message': 'OAuth successful',
        'portal_id': portal_id,
        'access_token': token_data['access_token']
    })

@app.route('/api/company/<company_id>/line-items')
def get_company_line_items(company_id):
    """Get line items for a company through its deals"""
    # Get portal ID from request headers or session
    portal_id = request.headers.get('X-HubSpot-Portal-Id')
    if not portal_id:
        return jsonify({'error': 'Portal ID not provided'}), 400
    
    # Verify HubSpot signature
    signature = request.headers.get('X-HubSpot-Signature-V3')
    if signature:
        # In production, you should get the webhook secret from HubSpot
        webhook_secret = os.environ.get('HUBSPOT_WEBHOOK_SECRET', '')
        if not verify_hubspot_signature(request.get_data(as_text=True), signature, webhook_secret):
            return jsonify({'error': 'Invalid signature'}), 401
    
    # Get access token
    access_token = get_hubspot_access_token(portal_id)
    if not access_token:
        return jsonify({'error': 'No valid access token found'}), 401
    
    try:
        # Get company deals using GraphQL
        line_items = get_company_line_items_graphql(access_token, company_id)
        
        if line_items is None:
            # Fallback to REST API
            line_items = get_company_line_items_rest(access_token, company_id)
        
        return jsonify({
            'company_id': company_id,
            'line_items': line_items
        })
    
    except Exception as e:
        logger.error(f"Error fetching line items: {str(e)}")
        return jsonify({'error': 'Failed to fetch line items'}), 500

def get_company_line_items_graphql(access_token, company_id):
    """Get line items using GraphQL API"""
    query = """
    query GetCompanyLineItems($companyId: ID!) {
      CRM {
        company(uniqueIdentifier: $companyId) {
          associations {
            deals {
              items {
                id
                properties {
                  dealname
                }
                associations {
                  lineItems {
                    items {
                      id
                      properties {
                        name
                        quantity
                        price
                        amount
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    
    variables = {"companyId": company_id}
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        'https://api.hubapi.com/crm/v3/objects/companies/graphql',
        headers=headers,
        json={'query': query, 'variables': variables}
    )
    
    if response.status_code != 200:
        logger.warning(f"GraphQL request failed: {response.text}")
        return None
    
    data = response.json()
    if 'errors' in data:
        logger.warning(f"GraphQL errors: {data['errors']}")
        return None
    
    # Process GraphQL response
    line_items = []
    company_data = data.get('data', {}).get('CRM', {}).get('company', {})
    deals = company_data.get('associations', {}).get('deals', {}).get('items', [])
    
    for deal in deals:
        deal_name = deal.get('properties', {}).get('dealname', 'Unknown Deal')
        line_items_data = deal.get('associations', {}).get('lineItems', {}).get('items', [])
        
        for line_item in line_items_data:
            props = line_item.get('properties', {})
            line_items.append({
                'deal_name': deal_name,
                'line_item_name': props.get('name', 'Unknown Item'),
                'quantity': props.get('quantity', 0),
                'unit_price': props.get('price', 0),
                'amount': props.get('amount', 0)
            })
    
    return line_items

def get_company_line_items_rest(access_token, company_id):
    """Get line items using REST API (fallback)"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get company deals
    deals_url = f'https://api.hubapi.com/crm/v3/objects/companies/{company_id}/associations/deals'
    deals_response = requests.get(deals_url, headers=headers)
    
    if deals_response.status_code != 200:
        logger.error(f"Failed to get deals: {deals_response.text}")
        return []
    
    deals_data = deals_response.json()
    line_items = []
    
    # Get line items for each deal
    for deal_association in deals_data.get('results', []):
        deal_id = deal_association['id']
        
        # Get deal details
        deal_url = f'https://api.hubapi.com/crm/v3/objects/deals/{deal_id}'
        deal_response = requests.get(deal_url, headers=headers)
        
        if deal_response.status_code != 200:
            continue
        
        deal_data = deal_response.json()
        deal_name = deal_data.get('properties', {}).get('dealname', 'Unknown Deal')
        
        # Get line items for this deal
        line_items_url = f'https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/line_items'
        line_items_response = requests.get(line_items_url, headers=headers)
        
        if line_items_response.status_code != 200:
            continue
        
        line_items_data = line_items_response.json()
        
        # Get details for each line item
        for line_item_association in line_items_data.get('results', []):
            line_item_id = line_item_association['id']
            
            line_item_url = f'https://api.hubapi.com/crm/v3/objects/line_items/{line_item_id}'
            line_item_response = requests.get(line_item_url, headers=headers)
            
            if line_item_response.status_code != 200:
                continue
            
            line_item_data = line_item_response.json()
            props = line_item_data.get('properties', {})
            
            line_items.append({
                'deal_name': deal_name,
                'line_item_name': props.get('name', 'Unknown Item'),
                'quantity': props.get('quantity', 0),
                'unit_price': props.get('price', 0),
                'amount': props.get('amount', 0)
            })
    
    return line_items

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
