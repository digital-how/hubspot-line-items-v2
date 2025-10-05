// Brand new HubSpot extension - v3.0
console.log('Brand New Line Items Extension v3.0');

const container = document.createElement('div');
container.style.cssText = 'padding: 16px; border: 1px solid #28a745; margin: 8px; background: #d4edda;';
container.innerHTML = '<h3>Brand New Line Items Extension</h3><p>Version 3.0 - Brand New Start</p><button onclick="alert(\'Brand new build successful!\')">Test</button>';

if (typeof window !== 'undefined') {
  document.body.appendChild(container);
}
