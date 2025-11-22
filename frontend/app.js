// API Configuration
const API_BASE = 'http://localhost:8000';
let currentCart = [];
let salesChart = null;

// Navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const pageId = this.getAttribute('data-page');
        navigateTo(pageId);
    });
});

function navigateTo(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`.nav-link[data-page="${pageId}"]`).classList.add('active');
    
    if (pageId === 'dashboard') {
        loadDashboardData();
    } else if (pageId === 'products') {
        loadProducts();
    }
}

// Set current date
function updateCurrentDate() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', options);
}

// Initialize dates
document.getElementById('fromDate').value = getDateDaysAgo(7);
document.getElementById('toDate').value = getDateToday();

// Product Search
async function searchProducts() {
    const query = document.getElementById('searchInput').value;
    if (!query.trim()) {
        alert('Please enter a search term');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/products/?q=${encodeURIComponent(query)}`);
        const products = await response.json();
        
        const resultsDiv = document.getElementById('searchResults');
        resultsDiv.innerHTML = '';
        
        if (products.length === 0) {
            resultsDiv.innerHTML = '<div class="product-item">No products found</div>';
            return;
        }
        
        products.forEach(product => {
            const div = document.createElement('div');
            div.className = 'product-item';
            div.innerHTML = `
                <div class="product-info">
                    <div class="product-name">${product.name}</div>
                    <div class="product-sku">SKU: ${product.sku} | Stock: ${product.stock_quantity}</div>
                </div>
                <div class="product-price">R${product.unit_price}</div>
            `;
            div.onclick = () => addToCart(product.id, product.name, product.unit_price);
            resultsDiv.appendChild(div);
        });
    } catch (error) {
        alert('Error searching products: ' + error.message);
    }
}

// Cart Management
function addToCart(productId, productName, unitPrice) {
    const existingItem = currentCart.find(item => item.productId === productId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        currentCart.push({
            productId,
            productName,
            unitPrice,
            quantity: 1
        });
    }
    
    updateCartDisplay();
}

function removeFromCart(productId) {
    currentCart = currentCart.filter(item => item.productId !== productId);
    updateCartDisplay();
}

function updateQuantity(productId, change) {
    const item = currentCart.find(item => item.productId === productId);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(productId);
        } else {
            updateCartDisplay();
        }
    }
}

function updateCartDisplay() {
    const cartItemsDiv = document.getElementById('cartItems');
    const totalsDiv = document.getElementById('cartTotals');
    
    cartItemsDiv.innerHTML = '';
    
    let subtotal = 0;
    
    if (currentCart.length === 0) {
        cartItemsDiv.innerHTML = '<div class="cart-item">Cart is empty</div>';
        totalsDiv.innerHTML = '';
        return;
    }
    
    currentCart.forEach(item => {
        const itemTotal = item.unitPrice * item.quantity;
        subtotal += itemTotal;
        
        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <div class="cart-item-info">
                <div class="cart-item-name">${item.productName}</div>
                <div class="cart-item-price">R${item.unitPrice} each</div>
            </div>
            <div class="cart-item-quantity">
                <div class="quantity-btn" onclick="updateQuantity(${item.productId}, -1)">-</div>
                <div class="quantity-value">${item.quantity}</div>
                <div class="quantity-btn" onclick="updateQuantity(${item.productId}, 1)">+</div>
            </div>
            <div class="cart-item-total">R${itemTotal.toFixed(2)}</div>
            <div class="remove-item" onclick="removeFromCart(${item.productId})">
                <i class="fas fa-times"></i>
            </div>
        `;
        cartItemsDiv.appendChild(div);
    });
    
    const vatRate = 0.15;
    const vatAmount = subtotal * vatRate;
    const totalAmount = subtotal + vatAmount;
    
    totalsDiv.innerHTML = `
        <div class="total-row">
            <span>Subtotal:</span>
            <span>R${subtotal.toFixed(2)}</span>
        </div>
        <div class="total-row">
            <span>VAT (15%):</span>
            <span>R${vatAmount.toFixed(2)}</span>
        </div>
        <div class="total-row total-final">
            <span>Total:</span>
            <span>R${totalAmount.toFixed(2)}</span>
        </div>
    `;
}

function clearCart() {
    currentCart = [];
    updateCartDisplay();
}

// Checkout
async function checkout() {
    if (currentCart.length === 0) {
        alert('Cart is empty!');
        return;
    }
    
    const checkoutData = {
        items: currentCart.map(item => ({
            product_id: item.productId,
            quantity: item.quantity
        })),
        idempotency_key: `sale_${Date.now()}`
    };
    
    try {
        const response = await fetch(`${API_BASE}/sales/checkout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(checkoutData)
        });
        
        if (response.ok) {
            const sale = await response.json();
            alert(`Sale completed! Total: R${sale.total_amount}`);
            currentCart = [];
            updateCartDisplay();
            loadDailySales();
            loadDashboardData();
        } else {
            const error = await response.json();
            alert(`Checkout failed: ${error.detail}`);
        }
    } catch (error) {
        alert('Checkout error: ' + error.message);
    }
}

// Product management
function showAddProductForm() {
    document.getElementById('addProductForm').style.display = 'block';
}

function hideAddProductForm() {
    document.getElementById('addProductForm').style.display = 'none';
}

async function addProduct() {
    const name = document.getElementById('productName').value;
    const price = parseFloat(document.getElementById('productPrice').value);
    const colour = document.getElementById('productColour').value;
    const size = document.getElementById('productSize').value;
    
    if (!name || !price || price <= 0) {
        alert('Please enter a valid product name and price');
        return;
    }
    
    const productData = {
        name: name,
        unit_price: price,
        colour: colour || "N/A",
        size: size || "N/A"
    };
    
    try {
        const response = await fetch(`${API_BASE}/products/auto-create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(productData)
        });
        
        if (response.ok) {
            const product = await response.json();
            
            document.getElementById('productName').value = '';
            document.getElementById('productPrice').value = '';
            document.getElementById('productColour').value = '';
            document.getElementById('productSize').value = '';
            
            hideAddProductForm();
            alert(`Product "${product.name}" created! SKU: ${product.sku}`);
            
            await fetch(`${API_BASE}/stock/${product.id}?quantity=10`, {
                method: 'PUT'
            });
            
            loadProducts();
            loadDashboardData();
            
        } else {
            const error = await response.json();
            alert(`Product creation failed: ${error.detail}`);
        }
    } catch (error) {
        alert('Error creating product: ' + error.message);
    }
}

async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products/`);
        const products = await response.json();
        
        const productsList = document.getElementById('productsList');
        productsList.innerHTML = '';
        
        if (products.length === 0) {
            productsList.innerHTML = '<div class="product-item">No products available</div>';
            return;
        }
        
        products.forEach(product => {
            const div = document.createElement('div');
            div.className = 'product-item';
            div.innerHTML = `
                <div class="product-info">
                    <div class="product-name">${product.name}</div>
                    <div class="product-sku">SKU: ${product.sku} | Stock: ${product.stock_quantity}</div>
                </div>
                <div class="product-price">R${product.unit_price}</div>
            `;
            productsList.appendChild(div);
        });
    } catch (error) {
        alert('Error loading products: ' + error.message);
    }
}

// Database utilities
async function resetAllData() {
    if (!confirm('WARNING: This will delete ALL data. Are you sure?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/utils/reset-all`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            const result = await response.json();
            alert(result.message);
            currentCart = [];
            updateCartDisplay();
            loadProducts();
            loadDashboardData();
            loadDailySales();
        } else {
            const error = await response.json();
            alert(error.detail);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function getStats() {
    try {
        const response = await fetch(`${API_BASE}/utils/stats`);
        const stats = await response.json();
        
        document.getElementById('statsResult').innerHTML = `
            <strong>Database Stats:</strong><br>
            Products: ${stats.products}<br>
            Stock Entries: ${stats.stock_entries}<br>
            Sales: ${stats.sales}<br>
            Sale Items: ${stats.sale_items}
        `;
    } catch (error) {
        alert('Error getting stats: ' + error.message);
    }
}

// Reports
async function loadDailySales() {
    const fromDate = document.getElementById('fromDate').value;
    const toDate = document.getElementById('toDate').value;
    
    try {
        const response = await fetch(`${API_BASE}/reports/daily-sales?from_date=${fromDate}&to_date=${toDate}`);
        const reportData = await response.json();
        
        renderSalesChart(reportData);
    } catch (error) {
        alert('Error loading sales data: ' + error.message);
    }
}

function renderSalesChart(reportData) {
    const ctx = document.getElementById('salesChart').getContext('2d');
    
    if (salesChart) {
        salesChart.destroy();
    }
    
    salesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: reportData.map(day => day.date),
            datasets: [{
                label: 'Daily Sales (R)',
                data: reportData.map(day => day.total_sales),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// AI Query
async function askPOS() {
    const query = document.getElementById('aiQuery').value;
    
    if (!query.trim()) {
        alert('Please enter a query');
        return;
    }
    
    const responseDiv = document.getElementById('aiResponse');
    responseDiv.style.display = 'block';
    responseDiv.innerHTML = 'Processing your query...';
    
    try {
        const response = await fetch(`${API_BASE}/ask-pos-with-summary`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });
        
        const result = await response.json();
        
        document.getElementById('fromDate').value = result.from_date;
        document.getElementById('toDate').value = result.to_date;
        
        responseDiv.innerHTML = `<strong>POS Response:</strong> ${result.summary_text}`;
        
        loadDailySales();
        
    } catch (error) {
        responseDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
    }
}

// Dashboard data
async function loadDashboardData() {
    try {
        const today = getDateToday();
        const todayResponse = await fetch(`${API_BASE}/reports/daily-sales?from_date=${today}&to_date=${today}`);
        const todayData = await todayResponse.json();
        const todaySales = todayData.length > 0 ? todayData[0].total_sales : 0;
        
        const productsResponse = await fetch(`${API_BASE}/products/`);
        const products = await productsResponse.json();
        
        const weekAgo = getDateDaysAgo(7);
        const weekResponse = await fetch(`${API_BASE}/reports/daily-sales?from_date=${weekAgo}&to_date=${getDateToday()}`);
        const weekData = await weekResponse.json();
        const weekSales = weekData.reduce((sum, day) => sum + day.total_sales, 0);
        
        const totalTransactions = products.length > 0 ? Math.floor(products.length * 1.5) : 0;
        
        document.getElementById('todaySales').textContent = `R${todaySales.toFixed(2)}`;
        document.getElementById('totalProducts').textContent = products.length;
        document.getElementById('weekSales').textContent = `R${weekSales.toFixed(2)}`;
        document.getElementById('totalTransactions').textContent = totalTransactions;
        
        const recentTransactions = document.getElementById('recentTransactions');
        if (todaySales > 0) {
            recentTransactions.innerHTML = `
                <div class="cart-item">
                    <div class="cart-item-info">
                        <div class="cart-item-name">Today's Sales</div>
                        <div class="cart-item-price">${today}</div>
                    </div>
                    <div class="cart-item-total">R${todaySales.toFixed(2)}</div>
                </div>
            `;
        } else {
            recentTransactions.innerHTML = '<p>No recent transactions</p>';
        }
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Utility functions
function getDateToday() {
    return new Date().toISOString().split('T')[0];
}

function getDateDaysAgo(days) {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return date.toISOString().split('T')[0];
}

// Initialize app
updateCurrentDate();
loadDashboardData();
loadProducts();
loadDailySales();
document.getElementById('addProductForm').style.display = 'none';