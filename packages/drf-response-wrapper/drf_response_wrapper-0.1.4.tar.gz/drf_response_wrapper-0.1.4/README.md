# DRF Response Wrapper

A Django REST Framework middleware that automatically wraps **all API responses** into a consistent format.  
No need to modify your views or APIView classes.

---

## 🚀 Features

- Standardized success & error responses
- Works with all DRF APIViews
- Simple integration: just add middleware
- No changes needed in your views

---

## 📦 Installation

Install the package from PyPI:

```bash
pip install drf-response-wrapper
```

---

## ⚙️ Usage / User Guide

### 1️⃣ Add Middleware

Open your Django project's `settings.py` and add the middleware:

```python
MIDDLEWARE = [
    # Other middlewares
    "drf_response_wrapper.middleware.APIResponseWrapperMiddleware",
]
```

> This middleware automatically wraps all DRF API responses, so you don't need to manually call `success_response()` or `error_response()` in your views.

---

### 2️⃣ Example API Responses

**Success response example:**

```json
{
  "success": true,
  "message": "Request successful",
  "status": 200,
  "data": {
    "id": 1,
    "name": "Example Item"
  }
}
```

**Error response example:**

```json
{
  "success": false,
  "message": "Something went wrong",
  "status": 400,
  "data": {}
}
```

---

### 3️⃣ Notes / Tips

- Works with any DRF APIView returning `Response`.
- Can be used with `BaseAPIView` or standard `APIView`.
- Ensures all API responses follow the same structure automatically.
- No changes needed in your existing views.
- Compatible with existing DRF projects—just add middleware.
- Ideal for projects where consistent API response format is required.

---

## 📝 License

MIT License
