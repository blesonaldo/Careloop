f = open('Frontend/careloop-dashboard.html', 'r', encoding='utf-8')
c = f.read()
f.close()

# Fix 1: Remove localStorage sales init, replace with empty array
c = c.replace(
    "let sales = JSON.parse(localStorage.getItem('cl_sales')||'[]');",
    "let sales = [];\nlet preferredCurrency = localStorage.getItem('cl_currency') || 'USD';"
)

# Fix 2: Replace submitSale function
old_submit = """function submitSale(){
  const custId=document.getElementById('sale-cust-select').value;
  const amount=parseFloat(document.getElementById('sale-amount').value);
  const product=document.getElementById('sale-product').value.trim();
  if(!custId||isNaN(amount)||amount<=0){alert('Please select a customer and enter a valid amount.');return;}
  const c=customers.find(x=>String(x.id)===String(custId));
  sales.push({customerId:custId,amount,product,date:new Date().toISOString()});
  localStorage.setItem('cl_sales',JSON.stringify(sales));
  if(c) addNotification({type:'cart',title:'Sale Recorded',names:c.name});
  closeModal('sale-modal');
  alert('Sale recorded!');
}"""

new_submit = """async function submitSale(){
  const custId=document.getElementById('sale-cust-select').value;
  const amount=parseFloat(document.getElementById('sale-amount').value);
  const product=document.getElementById('sale-product').value.trim();
  const currency=document.getElementById('sale-currency').value||preferredCurrency;
  if(!custId||isNaN(amount)||amount<=0){alert('Please select a customer and enter a valid amount.');return;}
  const token=localStorage.getItem('authToken');
  try{
    const r=await fetch('/api/sales',{
      method:'POST',
      headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},
      body:JSON.stringify({customer_id:parseInt(custId),amount,currency,product:product||null})
    });
    if(r.ok){
      const saved=await r.json();
      sales.unshift({...saved,customerId:saved.customer_id});
      const c=customers.find(x=>String(x.id)===String(custId));
      if(c) addNotification({type:'cart',title:'Sale Recorded',names:c.name});
      closeModal('sale-modal');
      renderSalesPage();
    } else {
      alert('Failed to record sale.');
    }
  }catch(e){alert('Failed to record sale: '+e.message);}
}"""

c = c.replace(old_submit, new_submit)

# Fix 3: Add loadSales function after loadCustomers
load_sales_fn = """
// --- LOAD SALES ---
async function loadSales(){
  const token=localStorage.getItem('authToken'); if(!token) return;
  try{
    const r=await fetch('/api/sales',{headers:{'Authorization':'Bearer '+token}});
    if(r.ok){
      const d=await r.json();
      sales=d.items.map(s=>({...s,customerId:s.customer_id}));
    }
  }catch(e){sales=[];}
}

// --- LOAD PREFERENCES ---
async function loadPreferences(){
  const token=localStorage.getItem('authToken'); if(!token) return;
  try{
    const r=await fetch('/api/user/profile',{headers:{'Authorization':'Bearer '+token}});
    if(r.ok){
      const u=await r.json();
      if(u.preferred_currency){
        preferredCurrency=u.preferred_currency;
        localStorage.setItem('cl_currency',preferredCurrency);
      }
    }
  }catch(e){}
}

// --- SAVE CURRENCY PREFERENCE ---
async function saveCurrencyPreference(currency){
  preferredCurrency=currency;
  localStorage.setItem('cl_currency',currency);
  const token=localStorage.getItem('authToken');
  try{
    await fetch('/api/sales/preferences',{
      method:'PUT',
      headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},
      body:JSON.stringify({preferred_currency:currency})
    });
  }catch(e){}
}
"""

c = c.replace('// --- LOAD CUSTOMERS ---', load_sales_fn + '\n// --- LOAD CUSTOMERS ---')
# fallback if using unicode dashes
c = c.replace('// \u2500\u2500\u2500 LOAD CUSTOMERS \u2500\u2500\u2500', load_sales_fn + '\n// \u2500\u2500\u2500 LOAD CUSTOMERS \u2500\u2500\u2500')

# Fix 4: Call loadSales and loadPreferences in init
c = c.replace(
    'await loadCustomers();',
    'await loadPreferences();\n  await loadSales();\n  await loadCustomers();'
)

# Fix 5: Add currency selector to sale modal
c = c.replace(
    '<label class="field-label">Amount ($)</label>',
    '<label class="field-label">Currency</label>\n    <select class="field-input" id="sale-currency" style="margin-bottom:16px;cursor:pointer;" onchange="saveCurrencyPreference(this.value)">\n      <option value="USD">USD - US Dollar</option>\n      <option value="EUR">EUR - Euro</option>\n      <option value="GBP">GBP - British Pound</option>\n      <option value="NGN">NGN - Nigerian Naira</option>\n      <option value="GHS">GHS - Ghanaian Cedi</option>\n      <option value="KES">KES - Kenyan Shilling</option>\n      <option value="ZAR">ZAR - South African Rand</option>\n      <option value="CAD">CAD - Canadian Dollar</option>\n      <option value="AUD">AUD - Australian Dollar</option>\n    </select>\n    <label class="field-label">Amount</label>'
)

# Fix 6: Update currency symbols in renderSalesTable and updateRevenueStats
c = c.replace(
    "const fmt = n=>'$'+n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});",
    "const symbols={'USD':'$','EUR':'\\u20ac','GBP':'\\u00a3','NGN':'\\u20a6','GHS':'\\u20b5','KES':'KSh','ZAR':'R','CAD':'CA$','AUD':'A$'};\n  const sym=symbols[preferredCurrency]||preferredCurrency+' ';\n  const fmt = n=>sym+n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});"
)

f = open('Frontend/careloop-dashboard.html', 'w', encoding='utf-8')
f.write(c)
f.close()
print('Done')
