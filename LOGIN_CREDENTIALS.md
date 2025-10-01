# 🔐 WAF System Login Credentials

## ✅ **CORRECT LOGIN INFORMATION:**

### **Admin Panel Login:**
- **URL**: http://localhost:8000/admin/
- **Username/Email**: `admin@waf.local`
- **Password**: `admin123`

### **Main Application Login:**
- **URL**: http://localhost:8000/accounts/login/
- **Username/Email**: `admin@waf.local`
- **Password**: `admin123`

### **Analytics Dashboard:**
- **URL**: http://localhost:5601
- **Access**: Direct (no login required)

## ⚠️ **IMPORTANT NOTES:**

### **Custom User Model:**
- This WAF system uses **email as the username field**
- You must use the **email address** (`admin@waf.local`) to login
- Do NOT use just `admin` as the username

### **Login Process:**
1. Go to http://localhost:8000/admin/
2. Enter `admin@waf.local` in the username field
3. Enter `admin123` in the password field
4. Click "Log in"

## 🚀 **QUICK ACCESS:**

| Service | URL | Login Method |
|---------|-----|--------------|
| **Admin Panel** | http://localhost:8000/admin/ | Email: `admin@waf.local` |
| **Main App Login** | http://localhost:8000/accounts/login/ | Email: `admin@waf.local` |
| **Main App** | http://localhost:8000/ | After login |
| **Analytics** | http://localhost:5601 | Direct access |

## 🆘 **TROUBLESHOOTING:**

### **If Login Still Fails:**
```bash
# Check user exists
docker-compose exec django python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print([f'{u.email} - {u.is_staff}' for u in User.objects.all()])"

# Test authentication
docker-compose exec django python manage.py shell -c "from django.contrib.auth import authenticate; print(authenticate(email='admin@waf.local', password='admin123'))"
```

### **If You Need to Reset Password:**
```bash
# Run the fix script
docker-compose exec django python fix-superuser.py
```

---

## 🎯 **SUMMARY:**

**Use `admin@waf.local` as your username/email to login!**

The system uses email-based authentication, so you need to enter the full email address, not just the username part.

**Happy logging in!** 🚀