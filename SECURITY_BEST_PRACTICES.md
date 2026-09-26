# EMS Frontend Security & Best Practices Guide

## 🔒 Security Features Implemented

### 1. CSRF Protection
**Function**: `getCSRFToken()`
- Retrieves CSRF token from meta tag
- Automatically added to all API requests
- Prevents cross-site request forgery attacks

**Usage**:
```javascript
const token = getCSRFToken();
// Automatically added to fetch requests
```

### 2. XSS Prevention
**Functions**: `escapeHTML()`, `sanitizeHTML()`

**Methods**:
- All user input is HTML-escaped before display
- Special characters converted to HTML entities
- Prevents script injection attacks

**Examples**:
```javascript
// Escape HTML
const safeText = escapeHTML(userInput);
showToast('Title', safeText, 'info');

// Sanitize HTML
const div = document.createElement('div');
div.textContent = userInput;
const safe = div.innerHTML;
```

### 3. Secure Form Validation

**Client-Side Validation**:
- Email format validation using regex
- Password strength requirements
- Required field checking
- Real-time feedback

**Password Requirements**:
- Minimum 8 characters = 1 point
- 12+ characters = 1 point
- Lowercase letters = 1 point
- Uppercase letters = 1 point
- Numbers = 1 point
- Special characters = 1 point

**Strength Levels**:
- 0-1 points: Very Weak (Red)
- 2 points: Weak (Orange)
- 3 points: Fair (Orange)
- 4 points: Good (Blue)
- 5+ points: Strong (Green)

### 4. API Security

**Enhanced Fetch Wrapper**:
```javascript
async function apiCall(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };

    // Auto-add CSRF token
    const csrfToken = getCSRFToken();
    if (csrfToken) {
        defaultOptions.headers['X-CSRF-Token'] = csrfToken;
    }
    
    // Error handling
    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Call Error:', error);
        throw error;
    }
}
```

### 5. Error Handling

**Global Error Handlers**:
```javascript
// Handle JavaScript errors
window.addEventListener('error', (event) => {
    console.error('Global Error:', event.error);
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection:', event.reason);
});
```

---

## 🛡️ Frontend Security Best Practices

### 1. Input Validation
- ✅ Always validate on both client and server
- ✅ Use regex for email validation
- ✅ Escape special characters
- ✅ Check for required fields
- ✅ Validate file uploads (size, type)

### 2. Output Encoding
- ✅ Use `escapeHTML()` for user content
- ✅ Use `textContent` instead of `innerHTML` when possible
- ✅ Sanitize data from external sources
- ✅ Never insert user input directly into DOM

### 3. Authentication & Sessions
- ✅ Store JWT tokens securely
- ✅ Use HttpOnly cookies for sensitive data
- ✅ Implement session timeout warnings
- ✅ Clear sensitive data on logout
- ✅ Validate tokens server-side

### 4. HTTPS & Transport
- ✅ Always use HTTPS in production
- ✅ Add Security Headers (CSP, X-Frame-Options, etc.)
- ✅ Use SameSite cookie attribute
- ✅ Enable HSTS

### 5. Content Security Policy
**Recommended CSP Header**:
```
Content-Security-Policy: 
  default-src 'self'; 
  script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; 
  style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; 
  img-src 'self' data:; 
  font-src 'self' cdn.jsdelivr.net;
```

### 6. DOM-based Security
- ✅ Use `textContent` instead of `innerHTML`
- ✅ Use `.setAttribute()` for dynamic attributes
- ✅ Validate before inserting into DOM
- ✅ Use template literals carefully

---

## 🔐 Recommended Server-Side Security

### Flask/Python Security Configuration
```python
# app.py

from flask_talisman import Talisman
from flask_limiter import Limiter

# CSRF Protection
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# Session Configuration
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Security Headers
Talisman(app)

# Rate Limiting
limiter = Limiter(app)
```

### Login Endpoint Protection
```python
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Check CSRF token
    # Validate credentials
    # Hash passwords (never store plain)
    # Log authentication attempts
    # Implement account lockout
    pass
```

---

## 🧪 Security Testing Checklist

### Before Deployment
- [ ] Run security headers check
- [ ] Test XSS vulnerabilities
- [ ] Check CSRF protection
- [ ] Verify HTTPS enforcement
- [ ] Test SQL injection (if applicable)
- [ ] Check password requirements
- [ ] Test rate limiting
- [ ] Verify session security
- [ ] Check for hardcoded secrets
- [ ] Test error message privacy
- [ ] Verify log security
- [ ] Check authentication flows

### Browser Security Tools
- [ ] Check with OWASP ZAP
- [ ] Run Lighthouse security audit
- [ ] Test with Mozilla Observatory
- [ ] Check SSL Labs score
- [ ] Use browser developer tools
- [ ] Test network requests

---

## 📊 Security Metrics

### Current Implementation
- **CSRF Protection**: ✅ Enabled
- **XSS Prevention**: ✅ HTML escaping
- **Input Validation**: ✅ Client-side
- **Error Handling**: ✅ Implemented
- **HTTPS Ready**: ✅ Yes
- **Password Strength**: ✅ Enforced

### Recommended Additions
- [ ] Add server-side rate limiting
- [ ] Implement 2FA/MFA
- [ ] Add security audit logging
- [ ] Implement API key management
- [ ] Add data encryption at rest
- [ ] Implement CORS properly

---

## 🚨 Common Vulnerabilities to Watch For

### 1. XSS (Cross-Site Scripting)
**Prevention**:
```javascript
// ❌ WRONG
element.innerHTML = userInput;

// ✅ CORRECT
element.textContent = userInput;
element.innerHTML = escapeHTML(userInput);
```

### 2. CSRF (Cross-Site Request Forgery)
**Prevention**:
- Always include CSRF token
- Use `getCSRFToken()` function
- Server validates token on POST/PUT/DELETE

### 3. SQL Injection
**Prevention** (Server-side):
- Use parameterized queries
- Never concatenate user input in SQL
- Use ORM (SQLAlchemy)

### 4. Insecure Deserialization
**Prevention**:
- Use JSON only
- Validate data types
- Use strict parsing

### 5. Sensitive Data Exposure
**Prevention**:
- Never log passwords
- Use HTTPS
- Clear sensitive data
- Don't store unnecessary data

---

## 📝 Security Headers Configuration

### For Flask/Python
```python
from flask import Flask

app = Flask(__name__)

@app.after_request
def set_security_headers(response):
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Enforce HTTPS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    
    return response
```

---

## 🔗 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Flask Security](https://flask.palletsprojects.com/en/2.0.x/security/)

---

## 💡 Quick Security Checklist

**Before Every Release**:
- [ ] Run security audit
- [ ] Update dependencies
- [ ] Check for known vulnerabilities
- [ ] Test authentication flows
- [ ] Verify CSRF protection
- [ ] Check for hardcoded secrets
- [ ] Review error messages
- [ ] Test with outdated browser
- [ ] Check password policies
- [ ] Verify access controls

**After Deployment**:
- [ ] Monitor error logs
- [ ] Check failed login attempts
- [ ] Review security headers
- [ ] Monitor for unusual activity
- [ ] Test recovery procedures
- [ ] Update security documentation

---

## 📞 Reporting Security Issues

If you discover a security vulnerability, please:
1. **DO NOT** post it publicly
2. Email security@example.com with details
3. Include steps to reproduce
4. Allow time for fixes before disclosure
5. Expect acknowledgment within 48 hours

---

**Last Updated**: January 2026
**Status**: Ready for Production
**Compliance**: OWASP Top 10 Best Practices
