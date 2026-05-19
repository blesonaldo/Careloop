f = open('Frontend/careloop-dashboard.html', 'r', encoding='utf-8')
c = f.read()
f.close()

old = '''    <button class="nav-item" id="nav-logout" onclick="logout()" style="color:var(--red);margin-top:8px;">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
      Logout
    </button>'''

new = '''    <button onclick="logout()" style="width:100%;display:flex;align-items:center;gap:10px;padding:10px 16px;border-radius:50px;border:none;background:#FCEBEB;color:#A32D2D;font-size:14px;font-weight:500;cursor:pointer;margin-top:8px;font-family:inherit;transition:background 0.15s;" onmouseover="this.style.background='#F7C1C1'" onmouseout="this.style.background='#FCEBEB'">
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
      Logout
    </button>'''

c = c.replace(old, new)
f = open('Frontend/careloop-dashboard.html', 'w', encoding='utf-8')
f.write(c)
f.close()
print('Done')
