c = open('Frontend/careloop-dashboard.html', encoding='utf-8').read()
print('logout buttons:', c.count('onclick="logout()"'))
print('logout functions:', c.count('async function logout'))
