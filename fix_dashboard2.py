f = open('Frontend/careloop-dashboard.html', 'r', encoding='utf-8')
c = f.read()
f.close()

# Remove duplicate logout button (keep the one with id="nav-logout")
c = c.replace(
    '  <button class="nav-item" onclick="logout()" style="color:var(--red);margin-top:8px;">\n      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>\n      Logout\n    </button>\n  </div>\n</aside>',
    '  </div>\n</aside>'
)

# Remove duplicate logout function (keep the first one)
duplicate_fn = """
async function logout(){
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
c = c.replace(duplicate_fn, '\n\n// --- START ---')

f = open('Frontend/careloop-dashboard.html', 'w', encoding='utf-8')
f.write(c)
f.close()
print('Done')
