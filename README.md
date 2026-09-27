# 📢 NMC College WhatsApp Broadcast Notification System

A full-stack, enterprise-grade WhatsApp broadcast communication portal built with **Django REST Framework** (Backend), **React + Tailwind CSS** (Frontend), and integrated with the official **Meta WhatsApp Cloud API**.

Designed specifically for college management to communicate with **Students, Staff, Heads of Department (HODs), Parents, and other personnel**.

---

## 🌟 Features

- **Multi-Role Audience Segmentation**: Organize contacts by role (`STUDENT`, `STAFF`, `HOD`, `PARENT`) or department (`CS`, `EC`, `ME`, etc.).
- **Smart Contact Groups**: Create custom or automated groups (e.g. *All Students*, *CS Department*, *1st Year*).
- **Meta WhatsApp Template Integration**: Supports pre-approved Meta message templates with dynamic parameter substitution (`{{1}}`, `{{2}}`, etc.).
- **Live Broadcast Composer**:
  - Live preview with college branding and formatted placeholders.
  - Multi-group audience selection with instant recipient count calculation.
  - One-click asynchronous broadcast dispatch.
- **Real-Time Delivery Tracker**:
  - Track individual message lifecycle: `PENDING` ➔ `SENT` ➔ `DELIVERED` ➔ `READ` ➔ `FAILED`.
  - Detailed error messages per recipient (e.g., invalid phone number, rate limit).
  - One-click **Retry Failed Messages**.
- **Interactive Dashboard**:
  - High-level KPIs: Total contacts, sent messages, delivered, read, and failed counts.
  - Contact distribution breakdown by role.
  - Recent broadcast history and delivery performance.
- **Official Meta Webhook Support**: Receiver endpoint ready for Meta message delivery & read receipts.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│       React 18 + Tailwind CSS (Port 3000)     │
│  - Dashboard & Analytics                     │
│  - Contacts & Groups Manager                 │
│  - Message Template Browser                  │
│  - Interactive Broadcast Composer            │
│  - Delivery Status Tracker                   │
└──────────────────────┬───────────────────────┘
                       │ REST API Proxy
                       ▼
┌──────────────────────────────────────────────┐
│     Django REST Framework (Port 8000)         │
│  - Contacts API (/api/contacts/)             │
│  - Groups API (/api/groups/)                 │
│  - Templates API (/api/templates/)           │
│  - Broadcast Engine (/api/broadcasts/)       │
│  - Status Webhook (/api/webhooks/whatsapp/)  │
└──────────────────────┬───────────────────────┘
                       │ HTTPS API Calls
                       ▼
┌──────────────────────────────────────────────┐
│        Meta WhatsApp Cloud API (v21.0)       │
│        (Official Business Platform)          │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
           📱 WhatsApp Delivery
        Students / Staff / HODs
```

---

## 🚀 Quick Start

### 1. Backend (Django)

```powershell
cd e:\nmc_project\backend

# Run migrations (already executed)
python manage.py migrate

# Start backend server
python manage.py runserver 8000
```

- **API Base URL**: `http://localhost:8000/api/`
- **Django Admin**: `http://localhost:8000/admin/`  
  - *Username*: `admin`  
  - *Password*: `admin123`

---

### 2. Frontend (React + Vite)

```powershell
cd e:\nmc_project\frontend

# Start frontend dev server
npm run dev
```

- **Web Portal**: `http://localhost:3000/`

---

## 🔑 Connecting Your Meta WhatsApp Business Account

To send real messages via WhatsApp, configure your Meta Developer credentials in `e:\nmc_project\backend\.env`:

```env
WHATSAPP_API_VERSION=v21.0
WHATSAPP_PHONE_NUMBER_ID=your_actual_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_meta_system_user_token
WHATSAPP_BUSINESS_ACCOUNT_ID=your_waba_account_id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=nmc_college_webhook_secret_2026
```

### Where to get these credentials:
1. Log in to **[developers.facebook.com](https://developers.facebook.com/)**.
2. Select your Business App ➔ Go to **WhatsApp** ➔ **API Setup**.
3. Copy the **Phone number ID** and temporary/permanent **Access Token**.
4. In **WhatsApp Manager** ➔ **Account Tools** ➔ **Message Templates**, create matching templates (e.g. `exam_schedule`, `fee_reminder`, `general_announcement`).
5. Set up your Webhook: Point Meta Webhooks to `https://your-public-url.com/api/webhooks/whatsapp/` with verify token `nmc_college_webhook_secret_2026`.

---

## 📁 Project Structure

```
e:\nmc_project\
├── backend\
│   ├── nmc_college\             # Core settings, routing & celery config
│   ├── contacts\                # Contacts, Groups & CSV bulk-import
│   ├── wa_templates\            # WhatsApp approved message templates
│   ├── broadcasts\              # Broadcast campaign engine & delivery tracking
│   ├── whatsapp_integration\    # Meta Graph API client & Webhook receiver
│   ├── db.sqlite3               # SQLite database (pre-seeded)
│   └── manage.py
│
├── frontend\
│   ├── src\
│   │   ├── components\          # Navigation Layout & badges
│   │   ├── pages\               # Dashboard, Contacts, Groups, Templates, Composer, Detail
│   │   ├── services\api.js      # Axios client connected to Django API
│   │   ├── App.jsx              # Routing & toast provider
│   │   └── main.jsx
│   └── vite.config.js           # Vite configuration with API reverse proxy
│
└── README.md
```
