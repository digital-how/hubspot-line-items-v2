# HubSpot Company Line Items App

A full-stack HubSpot public app that adds a custom sidebar card to Company records, displaying all Line Items from that Company's associated Deals.

## Features

- **Custom Sidebar Card**: Displays line items in a clean, organized table format
- **Real-time Data**: Fetches live data from HubSpot CRM via GraphQL and REST APIs
- **OAuth 2.0 Integration**: Secure authentication with HubSpot
- **Responsive Design**: Built with HubSpot UI Extensions SDK
- **Error Handling**: Loading states, error messages, and empty state handling
- **Refresh Functionality**: Manual refresh button for updated data

## Architecture

### Backend (Python Flask)
- **OAuth 2.0 Flow**: Handles HubSpot authentication
- **API Endpoints**: RESTful API for line items data
- **GraphQL Integration**: Primary data fetching method with REST fallback
- **Token Management**: Automatic token refresh and storage
- **Security**: HubSpot signature verification

### Frontend (React + HubSpot UI Extensions)
- **Sidebar Card**: Renders in Company record sidebar
- **Data Table**: Displays Deal Name, Line Item Name, Quantity, Unit Price, Amount
- **Interactive UI**: Loading spinners, refresh button, error states
- **Responsive Design**: Optimized for HubSpot's UI

## Project Structure

```
hubspot-company-line-items-app/
├── backend/                    # Python Flask backend
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── Dockerfile            # Docker configuration
├── hubspot/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── CompanyLineItemsCard.jsx
│   │   ├── index.js          # Entry point
│   │   └── index.html        # HTML template
│   ├── package.json          # Node.js dependencies
│   ├── webpack.config.js     # Webpack configuration
│   └── Dockerfile            # Docker configuration
├── app-hsmeta.json           # HubSpot app metadata
├── company-line-items-card-hsmeta.json  # Card metadata
├── docker-compose.yml        # Docker Compose configuration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- HubSpot Developer Account
- HubSpot CLI (for local development)

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <your-repo-url>
cd hubspot-company-line-items-app

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd hubspot
npm install
cd ..
```

### 2. HubSpot App Configuration

1. **Create a HubSpot App**:
   - Go to [HubSpot Developer Portal](https://developers.hubspot.com/)
   - Create a new app
   - Note your Client ID and Client Secret

2. **Configure OAuth**:
   - Set Redirect URI: `http://localhost:5000/oauth/callback`
   - Add required scopes:
     - `crm.objects.companies.read`
     - `crm.objects.deals.read`
     - `crm.objects.line_items.read`

3. **Update Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your HubSpot credentials
   ```

### 3. Local Development

#### Option A: Manual Setup

**Start Backend**:
```bash
cd backend
python app.py
# Backend runs on http://localhost:5000
```

**Start Frontend** (in new terminal):
```bash
cd hubspot
npm run dev
# Frontend runs on http://localhost:3000
```

#### Option B: Docker Compose

```bash
docker-compose up --build
```

### 4. HubSpot CLI Development

1. **Install HubSpot CLI**:
   ```bash
   npm install -g @hubspot/cli
   ```

2. **Login to HubSpot**:
   ```bash
   hs auth login
   ```

3. **Create Development App**:
   ```bash
   hs create app
   ```

4. **Upload App Files**:
   ```bash
   # Build frontend
   cd hubspot
   npm run build
   cd ..
   
   # Upload to HubSpot
   hs upload hubspot/dist/bundle.js
   ```

5. **Test in HubSpot**:
   - Go to your HubSpot portal
   - Navigate to a Company record
   - Look for the "Line Items" card in the sidebar

## API Endpoints

### Backend Endpoints

- `GET /oauth/start` - Initiates OAuth flow
- `GET /oauth/callback` - Handles OAuth callback
- `GET /api/company/<company_id>/line-items` - Fetches line items for a company
- `GET /health` - Health check endpoint

### Frontend Integration

The React component automatically:
- Detects the current company ID from HubSpot context
- Calls the backend API to fetch line items
- Displays data in a formatted table
- Handles loading states and errors

## Data Flow

1. **User opens Company record** in HubSpot
2. **Sidebar card loads** and gets company ID from context
3. **Frontend calls backend** `/api/company/<id>/line-items`
4. **Backend authenticates** using stored OAuth tokens
5. **Backend fetches data** from HubSpot via GraphQL (with REST fallback)
6. **Data is returned** and displayed in the sidebar card

## Deployment

### 1. Production Environment Setup

1. **Deploy Backend**:
   - Deploy Flask app to your preferred platform (Heroku, AWS, etc.)
   - Set environment variables in production
   - Update `HUBSPOT_REDIRECT_URI` to production URL

2. **Deploy Frontend**:
   - Build production bundle: `npm run build`
   - Upload `dist/bundle.js` to your CDN or static hosting
   - Update `app-hsmeta.json` with production URLs

### 2. HubSpot App Marketplace

1. **Prepare for Submission**:
   - Complete app testing in development
   - Prepare app screenshots and descriptions
   - Ensure all security requirements are met

2. **Submit to Marketplace**:
   - Go to HubSpot Developer Portal
   - Submit your app for review
   - Provide required documentation and screenshots

3. **App Store Listing**:
   - App name: "Company Line Items"
   - Description: "View all line items from company deals in a convenient sidebar card"
   - Category: CRM Tools
   - Pricing: Free

## Configuration

### Environment Variables

```bash
# HubSpot OAuth
HUBSPOT_CLIENT_ID=your_client_id
HUBSPOT_CLIENT_SECRET=your_client_secret
HUBSPOT_REDIRECT_URI=http://localhost:5000/oauth/callback
HUBSPOT_WEBHOOK_SECRET=your_webhook_secret

# Flask
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=development

# Backend URL
BACKEND_URL=http://localhost:5000
```

### HubSpot Scopes Required

- `crm.objects.companies.read` - Read company data
- `crm.objects.deals.read` - Read deal data
- `crm.objects.line_items.read` - Read line item data

## Troubleshooting

### Common Issues

1. **OAuth Errors**:
   - Verify Client ID and Secret are correct
   - Check redirect URI matches exactly
   - Ensure scopes are properly configured

2. **API Errors**:
   - Check if company has associated deals
   - Verify line items exist in deals
   - Check HubSpot API rate limits

3. **Frontend Issues**:
   - Ensure backend is running and accessible
   - Check browser console for errors
   - Verify HubSpot context is available

### Debug Mode

Enable debug logging:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
```

## Security Considerations

- **Token Storage**: Currently uses in-memory storage (use database in production)
- **Signature Verification**: Implements HubSpot webhook signature verification
- **CORS**: Properly configured for HubSpot domains
- **Environment Variables**: Sensitive data stored in environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions:
- Create an issue in this repository
- Contact: support@yourcompany.com
- Documentation: [HubSpot Developer Docs](https://developers.hubspot.com/)

## Changelog

### v1.0.0
- Initial release
- Basic line items display functionality
- OAuth 2.0 integration
- GraphQL and REST API support
- Responsive UI design
