# Gymix API Documentation (Normal User Endpoints)

Base URL: `https://api.gymix.ir`

---

## Users

### GET `/users/info`

- **Description:** Get current user's profile and gyms.
- **Request:** No body required. Auth required.
- **Response:**
  ```json
  {
    "return": {
      "status": 200,
      "message": "تایید شد"
    },
    "data": {
      "status": "active",
      "name": "John",
      "lastname": "Doe",
      "phone": "09123456789",
      "address": "Tehran",
      "gyms": [{ "id": "gym_id", "name": "Gym Name", "location": "Location" }],
      "balance": 100000
    }
  }
  ```

**Errors:**

- `401 Unauthorized`: Missing or invalid authentication token.
  ```json
  {
    "return": {
      "status": 401,
      "message": "هدر احراز هویت گمشده یا نامعتبر"
    },
    "data": {}
  }
  ```
- `403 Forbidden`: User account is deactivated, banned, or API/payment access is restricted.
  ```json
  {
    "return": {
      "status": 403,
      "message": "حساب کاربری غیرفعال است"
    },
    "data": {}
  }
  ```

---

## Gym

### POST `/gym/info`

- **Description:** Get gym details, subscription, and plan info.
- **Request:**
  - `gym_public_key` (form field, required)
- **Response:**
  ```json
  {
    "return": {
      "status": 200,
      "message": "تایید شد"
    },
    "data": {
      "gym_info": {
        "name": "Gym Name",
        "location": "Location",
        "status": "Active",
        "created_at": "2025-08-29T12:00:00Z"
      },
      "subscription_info": {
        "id": "sub_id",
        "name": "Subscription Name",
        "price": 100000,
        "date_of_initiation": "2025-08-01T12:00:00Z",
        "expiration_date": "2025-09-01T12:00:00Z",
        "duration_days": 30,
        "remaining_days": 3,
        "usage_percentage": 90.0,
        "status": "active"
      },
      "plan_info": {
        "id": "plan_id",
        "name": "Plan Name",
        "description": "Plan Description",
        "price": 100000,
        "status": "Active",
        "duration_days": 30,
        "features": {
          "includes_backup": true,
          "includes_support": true,
          "max_backups": 5,
          "backup_expiration_days": 30,
          "max_backups_per_day": 1,
          "support_tier": "premium"
        }
      },
      "subscription_summary": {
        "has_subscription": true,
        "is_active": true,
        "is_expiring_soon": false,
        "is_expired": false,
        "no_subscription": false,
        "days_until_expiration": 3,
        "can_use_services": true
      }
    }
  }
  ```

**Errors:**

- `401 Unauthorized`: Missing or invalid authentication token.
  ```json
  {
    "return": {
      "status": 401,
      "message": "توکن API نامعتبر"
    },
    "data": {}
  }
  ```
- `404 Not Found`: Gym not found or not owned by user.
  ```json
  {
    "return": {
      "status": 404,
      "message": "باشگاه مورد نظر یافت نشد یا شما مالک آن نیستید"
    },
    "data": {}
  }
  ```

---

## Backups

### POST `/backup/create`

- **Description:** Upload a backup ZIP file for a gym.
- **Request:**
  - `gym_public_key` (form field, required)
  - `file` (form file, required, must be `.zip`)
- **Response:**
  ```json
  {
    "return": {
      "status": 200,
      "message": "تایید شد"
    },
    "data": {
      "id": "backup_id",
      "file_name": "backup.zip",
      "created_at": "2025-08-29T12:00:00Z",
      "size": 1048576,
      "plan_info": {
        "plan_name": "Plan Name",
        "max_backups": 5,
        "current_backup_count": 2,
        "backup_expiration_days": 30,
        "max_backups_per_day": 1
      }
    }
  }
  ```

**Errors:**

- `401 Unauthorized`: Missing or invalid authentication token.
  ```json
  {
    "return": {
      "status": 401,
      "message": "توکن API نامعتبر"
    },
    "data": {}
  }
  ```
- `404 Not Found`: Gym not found or not owned by user.
  ```json
  {
    "return": {
      "status": 404,
      "message": "باشگاه مورد نظر یافت نشد یا شما مالک آن نیستید"
    },
    "data": {}
  }
  ```
- `403 Forbidden`: Gym is deactivated, expired, or has no active subscription.
  ```json
  {
    "return": {
      "status": 403,
      "message": "اشتراک باشگاه منقضی شده است"
    },
    "data": {}
  }
  ```
- `403 Forbidden`: Plan does not include backup feature.
  ```json
  {
    "return": {
      "status": 403,
      "message": "سرویس بکاپ در پلن فعلی شما موجود نیست"
    },
    "data": {}
  }
  ```
- `429 Too Many Requests`: Daily backup limit reached.
  ```json
  {
    "return": {
      "status": 429,
      "message": "محدودیت روزانه بکاپ: 1 بکاپ در روز"
    },
    "data": {}
  }
  ```
- `400 Bad Request`: Invalid file type (must be `.zip`).
  ```json
  {
    "return": {
      "status": 400,
      "message": "فایل معتبر نیست"
    },
    "data": {}
  }
  ```
- `500 Internal Server Error`: S3 upload failed.
  ```json
  {
    "return": {
      "status": 500,
      "message": "خطا در آپلود فایل"
    },
    "data": {}
  }
  ```

---

### GET `/backup/plan`

- **Description:** Get backup plan info and usage for a gym.
- **Request:**
  - `data` (query/body, must include `gym_public_key`)
- **Response:**
  ```json
  {
    "return": {
      "status": 200,
      "message": "تایید شد"
    },
    "data": {
      "plan_info": {
        "plan_name": "Plan Name",
        "includes_backup": true,
        "max_backups": 5,
        "backup_expiration_days": 30,
        "max_backups_per_day": 1
      },
      "current_usage": {
        "backup_count": 2,
        "today_backup_count": 1,
        "can_create_more_today": true,
        "will_delete_old_backup": false
      },
      "subscription_info": {
        "subscription_expiration": "2025-09-01T12:00:00Z",
        "duration_days": 30
      }
    }
  }
  ```

**Errors:**

- `401 Unauthorized`: Missing or invalid authentication token.
  ```json
  {
    "return": {
      "status": 401,
      "message": "توکن API نامعتبر"
    },
    "data": {}
  }
  ```
- `404 Not Found`: Gym not found or not owned by user.
  ```json
  {
    "return": {
      "status": 404,
      "message": "باشگاه مورد نظر یافت نشد یا شما مالک آن نیستید"
    },
    "data": {}
  }
  ```
- `403 Forbidden`: Gym is deactivated, expired, or has no active subscription.
  ```json
  {
    "return": {
      "status": 403,
      "message": "اشتراک باشگاه منقضی شده است"
    },
    "data": {}
  }
  ```

---

### GET `/backup/list`

- **Description:** List all backups for a gym.
- **Request:**
  - `data` (query/body, must include `gym_public_key`, optional `verified`)
- **Response:**
  ```json
  {
    "return": {
      "status": 200,
      "message": "تایید شد"
    },
    "data": {
      "backups": [
        {
          "id": "backup_id",
          "file_name": "backup.zip",
          "created_at": "2025-08-29T12:00:00Z",
          "s3_key": "s3_key",
          "bucket_slug": "bucket_slug"
        }
      ],
      "total_count": 1,
      "verified": false
    }
  }
  ```

**Errors:**

- `401 Unauthorized`: Missing or invalid authentication token.
  ```json
  {
    "return": {
      "status": 401,
      "message": "توکن API نامعتبر"
    },
    "data": {}
  }
  ```
- `404 Not Found`: Gym not found or not owned by user.
  ```json
  {
    "return": {
      "status": 404,
      "message": "باشگاه مورد نظر یافت نشد یا شما مالک آن نیستید"
    },
    "data": {}
  }
  ```
- `403 Forbidden`: Gym is deactivated, expired, or has no active subscription.
  ```json
  {
    "return": {
      "status": 403,
      "message": "اشتراک باشگاه منقضی شده است"
    },
    "data": {}
  }
  ```

---

### POST `/backup/download/{backup_id}`

- **Description:** Get a signed download URL for a backup file.
- **Request:**
  - `backup_id` (path param, required)
  - `gym_public_key` (form field, required)
- **Response:**
  ```json
  {
    "return": {
      "status": 200,
      "message": "تایید شد"
    },
    "data": {
      "backup_id": "backup_id",
      "file_name": "backup.zip",
      "download_url": "https://s3-url",
      "expires_in": "24 hours",
      "created_at": "2025-08-29T12:00:00Z",
      "cached": false
    }
  }
  ```

**Errors:**

- `401 Unauthorized`: Missing or invalid authentication token.
  ```json
  {
    "return": {
      "status": 401,
      "message": "توکن API نامعتبر"
    },
    "data": {}
  }
  ```
- `404 Not Found`: Gym not found or not owned by user.
  ```json
  {
    "return": {
      "status": 404,
      "message": "باشگاه مورد نظر یافت نشد یا شما مالک آن نیستید"
    },
    "data": {}
  }
  ```
- `403 Forbidden`: Gym is deactivated, expired, or has no active subscription.
  ```json
  {
    "return": {
      "status": 403,
      "message": "اشتراک باشگاه منقضی شده است"
    },
    "data": {}
  }
  ```
- `404 Not Found`: Backup not found.
  ```json
  {
    "return": {
      "status": 404,
      "message": "بکاپ مورد نظر یافت نشد"
    },
    "data": {}
  }
  ```
- `400 Bad Request`: Backup missing bucket info.
  ```json
  {
    "return": {
      "status": 400,
      "message": "اطلاعات bucket برای این بکاپ موجود نیست"
    },
    "data": {}
  }
  ```
- `404 Not Found`: Backup file not found in storage.
  ```json
  {
    "return": {
      "status": 404,
      "message": "فایل بکاپ در فضای ذخیره‌سازی یافت نشد یا دردسترس نیست"
    },
    "data": {}
  }
  ```
- `500 Internal Server Error`: S3 file check or download URL generation failed.
  ```json
  {
    "return": {
      "status": 500,
      "message": "خطا در تولید لینک دانلود"
    },
    "data": {}
  }
  ```

---

### DELETE `/backup/delete/{backup_id}`

- **Description:** Delete a backup file from S3 and database.
- **Request:**
  - `backup_id` (path param, required)
  - `gym_public_key` (form field, required)
- **Response:**
  ```json
  {
    "return": {
      "status": 200,
      "message": "تایید شد"
    },
    "data": {
      "backup_id": "backup_id",
      "message": "بکاپ با موفقیت حذف شد"
    }
  }
  ```

**Errors:**

- `401 Unauthorized`: Missing or invalid authentication token.
  ```json
  {
    "return": {
      "status": 401,
      "message": "توکن API نامعتبر"
    },
    "data": {}
  }
  ```
- `404 Not Found`: Gym not found or not owned by user.
  ```json
  {
    "return": {
      "status": 404,
      "message": "باشگاه مورد نظر یافت نشد یا شما مالک آن نیستید"
    },
    "data": {}
  }
  ```
- `403 Forbidden`: Gym is deactivated, expired, or has no active subscription.
  ```json
  {
    "return": {
      "status": 403,
      "message": "اشتراک باشگاه منقضی شده است"
    },
    "data": {}
  }
  ```
- `404 Not Found`: Backup not found.
  ```json
  {
    "return": {
      "status": 404,
      "message": "بکاپ مورد نظر یافت نشد"
    },
    "data": {}
  }
  ```
- `400 Bad Request`: Backup missing bucket info.
  ```json
  {
    "return": {
      "status": 400,
      "message": "اطلاعات bucket برای این بکاپ موجود نیست"
    },
    "data": {}
  }
  ```

---

## Health

### GET `/health`

- **Description:** Check API health status and basic system information.
- **Request:** No authentication required.
- **Response:**
  ```json
  {
    "return": {
      "status": 200,
      "message": "تایید شد"
    },
    "data": {
      "status": "healthy",
      "timestamp": "2025-08-29T12:00:00Z",
      "version": "1.0.0",
      "uptime": "5 days, 12 hours",
      "database": "connected",
      "storage": "operational"
    }
  }
  ```

**Errors:**

- `503 Service Unavailable`: API is temporarily unavailable.
  ```json
  {
    "return": {
      "status": 503,
      "message": "سرویس موقتاً در دسترس نیست"
    },
    "data": {
      "status": "unhealthy",
      "timestamp": "2025-08-29T12:00:00Z"
    }
  }
  ```

---

## Notes

- All endpoints require authentication (Bearer token in Authorization header) except for the health endpoint.
- All responses follow the `create_response()` format with `return` (status info) and `data` (actual content) keys.
- All requests for gym-related endpoints require a valid `gym_public_key` for access control.
- Admin-only endpoints (user creation, listing all users, adding gyms to users, bucket status, etc.) are not included in this documentation.
- Error messages are provided in Persian (Farsi) language.
- File uploads must be in ZIP format for backup endpoints.
- Download URLs for backups expire after 24 hours.

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_API_TOKEN
```

Example authentication error responses:

- Missing header: `"هدر احراز هویت گمشده یا نامعتبر"`
- Invalid token: `"توکن API نامعتبر"`
- Account restrictions: `"حساب کاربری غیرفعال است"`, `"دسترسی API محدود شده است"`, etc.
