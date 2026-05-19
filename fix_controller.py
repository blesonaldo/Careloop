f = open('app/controllers/auth_controller.py', 'r', encoding='utf-8')
c = f.read()
f.close()

# Add preferred_currency to all UserResponse constructions
c = c.replace(
    "return UserResponse(\n            id=user.id,\n            email=user.email,\n            full_name=user.full_name,\n            business_name=user.business_name,\n            is_active=user.is_active,\n            created_at=user.created_at,\n            updated_at=user.updated_at,\n            last_login_at=user.last_login_at\n        )",
    "return UserResponse(\n            id=user.id,\n            email=user.email,\n            full_name=user.full_name,\n            business_name=user.business_name,\n            is_active=user.is_active,\n            created_at=user.created_at,\n            updated_at=user.updated_at,\n            last_login_at=user.last_login_at,\n            preferred_currency=getattr(user, 'preferred_currency', 'USD')\n        )"
)

f = open('app/controllers/auth_controller.py', 'w', encoding='utf-8')
f.write(c)
f.close()
print('Done:', c.count('preferred_currency'), 'occurrences')
