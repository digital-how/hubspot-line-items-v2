// HubSpot UI Extension - Company Line Items (Simplified)
console.log('Company Line Items Extension v3.0');

// Simple extension without React dependencies
const createExtension = () => {
  const container = document.createElement('div');
  container.style.cssText = `
    padding: 16px;
    border: 1px solid #007acc;
    border-radius: 8px;
    margin: 8px;
    background: #f8f9fa;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  `;
  
  container.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <h3 style="margin: 0; color: #33475b; font-size: 16px;">Company Line Items</h3>
      <button onclick="refreshData()" style="
        padding: 6px 12px;
        background: #007acc;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
      ">Refresh</button>
    </div>
    <div id="line-items-content">
      <p style="margin: 0; color: #7c98b6; font-size: 14px;">
        Click refresh to load line items from company deals.
      </p>
    </div>
  `;
  
  return container;
};

// Refresh function
window.refreshData = function() {
  const content = document.getElementById('line-items-content');
  content.innerHTML = `
    <div style="padding: 8px 0;">
      <div style="padding: 8px 0; border-bottom: 1px solid #eee;">
        <strong>Deal 1</strong> - Product A<br>
        <small>Qty: 2 × $100.00</small>
      </div>
      <div style="padding: 8px 0; border-bottom: 1px solid #eee;">
        <strong>Deal 2</strong> - Product B<br>
        <small>Qty: 1 × $200.00</small>
      </div>
    </div>
  `;
};

// Export the extension
if (typeof module !== 'undefined' && module.exports) {
  module.exports = createExtension;
} else if (typeof window !== 'undefined') {
  window.CompanyLineItemsExtension = createExtension;
}
