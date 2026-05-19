f = open('Frontend/careloop-dashboard.html', 'r', encoding='utf-8')
c = f.read()
f.close()

# Fix 1: d.customers -> d.items
c = c.replace('customers=d.customers||[]', 'customers=d.items||[]')

# Fix 2: Add logout function
logout_fn = """async function logout(){
  const token=localStorage.getItem('authToken');
  try{
    await fetch('/api/auth/logout',{
      method:'POST',
      headers:{'Authorization':'Bearer '+token}
    });
  }catch(e){}
  localStorage.removeItem('authToken');
  localStorage.removeItem('cl_user');
  localStorage.removeItem('cl_customers');
  window.location.href='careloop-login.html';
}

// --- START ---"""
c = c.replace('// \u2500\u2500\u2500 START \u2500\u2500\u2500', logout_fn)

# Fix 3: Add logout button to sidebar
logout_btn = """  <button class="nav-item" onclick="logout()" style="color:var(--red);margin-top:8px;">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
      Logout
    </button>
  </div>
</aside>"""
c = c.replace('  </div>\n</aside>', logout_btn)

f = open('Frontend/careloop-dashboard.html', 'w', encoding='utf-8')
f.write(c)
f.close()
print('Done')
