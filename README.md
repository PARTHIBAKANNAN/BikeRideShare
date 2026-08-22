---
title: SmartRide Chennai - AI Bike Ride Sharing
emoji: 🏍️
colorFrom: green
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

<div align="center">

# 🏍️ SmartRide Chennai
### *AI & Road Corridor-Powered Urban Bike Pooling Platform*

[![Live Demo](https://img.shields.io/badge/Live%20App-Vercel-10b981?style=for-the-badge&logo=vercel&logoColor=white)](https://bike-ride-share.vercel.app)
[![API Docs](https://img.shields.io/badge/Swagger%20API-Live%20Docs-6366f1?style=for-the-badge&logo=swagger&logoColor=white)](https://bike-ride-share.vercel.app)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%7C%20Vite%20%7C%20Tailwind-38bdf8?style=for-the-badge&logo=react&logoColor=white)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Backend-Python%203.11%20%7C%20Flask%20RESTX-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-Neon%20PostgreSQL-00e599?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech/)
[![AI Engine](https://img.shields.io/badge/AI%20Copilot-Google%20Gemini-f59e0b?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/Copyright-PARTHIBAKANNAN%20S-purple?style=for-the-badge)](mailto:parthisivaram45@gmail.com)

<p align="center">
  A state-of-the-art, 100% free-tier daily office commute pooling application engineered specifically for Chennai's dense road corridors (OMR IT Expressway, GST Road, 100ft Inner Ring Road, Mount-Poonamallee, Porur & Ambattur SEZs).
</p>

</div>

---

## 📌 Table of Contents
- [🌟 Executive Overview](#-executive-overview)
- [🏗️ System Architecture](#️-system-architecture)
- [🚀 Key Features & Capabilities](#-key-features--capabilities)
- [🛡️ Safety, Moderation & Blacklisting Engine](#️-safety-moderation--blacklisting-engine)
- [🛠️ Free-Tier Technology Stack](#️-free-tier-technology-stack)
- [🔑 Admin Credentials & Portal](#-admin-credentials--portal)
- [💻 Local Development Quickstart](#-local-development-quickstart)
- [🌐 Cloud Deployment Guide](#-cloud-deployment-guide)
- [📡 API Endpoints Reference](#-api-endpoints-reference)
- [👨‍💻 Author & Ownership](#-author--ownership)
- [📄 Copyright & License](#-copyright--license)

---

## 🌟 Executive Overview

Chennai's tech corridors suffer from extreme single-occupant commuter congestion during morning and evening rush hours. **SmartRide Chennai** solves this by pairing two-wheeler commuters traveling along identical road vectors using **turn-by-turn road geometry, Google Gemini AI reasoning, and real-time corridor indexing**.

Unlike traditional ride-hailing services, SmartRide operates on an **economic fuel-sharing model** compliant with carpooling guidelines, saving commuters up to **₹2,800/month in fuel** while preventing **~1.8 kg CO₂ per trip**.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Client[React 18 + Vite Frontend] -->|REST API / JWT| Backend[Flask RESTX Backend Engine]
    Backend -->|Road Polylines & Geometry| OSRM[OSRM Road Engine / OpenStreetMap]
    Backend -->|Corridor Match Reasoning| Gemini[Google Gemini AI API]
    Backend -->|Persistent Storage & Geospatial Indices| NeonDB[(Neon Serverless PostgreSQL)]
    
    subgraph Core Engines
        Backend --> RouteEngine[Route & Reverse Geocoding Service]
        Backend --> FareEngine[Dynamic Fuel Surcharge Engine]
        Backend --> SafetyEngine[3-Tap SOS & Blacklisting Service]
        Backend --> ModerationEngine[Admin Approval & Incident Queue]
    end
```

---

## 🚀 Key Features & Capabilities

### 1. 🗺️ Real Chennai Road Network Maps & OSRM Engine
- **Turn-by-Turn Navigation Polylines**: Renders precise road trajectories on interactive **Leaflet.js** vector maps instead of naive straight lines.
- **Pre-Seeded Chennai Landmark Graph**: Instant autocomplete for 25+ Chennai tech hubs and nodal junctions (*DLF Cybercity, Olympia Tech Park, Tidel Park, Siruseri SIPCOT, Guindy, Vadapalani, Koyambedu, Porur, Tambaram, Medavakkam*).
- **Free & Open Routing**: 100% open routing powered by OSRM with 0 Google Maps API billing or key dependencies.

### 2. 🤖 Gemini AI & Geometric Corridor Matcher
- **Vector Overlap Detection**: Matches commuters along an ongoing route (e.g. a rider traveling *Maduravoyal ➔ Olympia Tech Park* effortlessly picks up a passenger at *Vadapalani Metro* with a 0-minute detour).
- **Match Compatibility Scores (0–100%)**: Evaluates time alignment, corridor intersection, rider rating, and detours.
- **AI Suggested Boarding Nodes**: Recommends optimal transit junctions for boarding.

### 3. 🌸 Pink Rides Mode (Women-Only Female Commuter Safety)
- Dedicated safe commuting mode tailored for women commuters and female riders.
- Female riders can toggle **"Offer as Pink Ride"** during posting.
- Female commuters can filter with 1-click **"🌸 Pink Rides (Women Only)"** to view exclusively verified female pools.

### 4. 🚨 3-Tap Police Emergency SOS (112)
- Interactive SOS safety button embedded inside active ride dashboards.
- **3-Tap Handshake Mechanism**:
  - `Tap 1`: Activates rapid response timer (`SOS: 1/3`).
  - `Tap 2`: Urgent confirmation alert (`SOS: 2/3`).
  - `Tap 3`: Directly triggers an emergency phone call to **Chennai Police Helpline (`tel:112`)**.
  - Prevents accidental pocket-dialing with a 3.5s auto-reset timeout.

### 5. 👥 Book for a Friend & 1-Click WhatsApp Live Sharing
- Book rides on behalf of colleagues, friends, or family members.
- Generates a **1-Click WhatsApp Pre-formatted Share Link** with verified pickup point, 4-digit boarding OTP, emergency helpline, and real-time tracking links.

### 6. 📌 Pinned Active Booking Tracker & Handshake OTP
- Live active booking card pinned to the dashboard header.
- **4-Digit Boarding OTP**: Handshake authentication between passenger and rider before ride start to ensure passenger safety and prevent unauthorized pickups.

### 7. 📜 Booking History & Safety Review Badges
- Complete archive of all past, completed, and cancelled commutes.
- Commuters can award safety and courtesy compliment badges (*⛑️ Clean ISI Helmet, ⏰ Punctual & On Time, 🏍️ Smooth & Safe Rider, 🤝 Courteous & Friendly*).

### 8. 🏍️ Vehicle Management & Strict Compliance
- Strict document verification rules: **Driving License & Vehicle Insurance must have >30 days future validity**.
- Support for multiple registered bikes with **1 Active Vehicle enforcement** per ride.
- Pre-integrated Indian motorcycle catalog (Royal Enfield, Yamaha, Honda, TVS, Bajaj, Ather, Ola Electric, KTM).

### 9. 💰 Dynamic Fair-Pricing Engine
- Fair-share fuel cost algorithm based on actual road kilometer distance.
- Automatic peak-hour office commute surcharge (8:00–10:30 AM & 5:00–8:30 PM).

### 10. 🏆 Tech Park Green Sustainability Leaderboard
- Real-time CO₂ emissions prevented (kg) and petrol money saved (₹) analytics across major Chennai SEZs.

---

## 🛡️ Safety, Moderation & Blacklisting Engine

| Capability | Scope & Mechanism |
| :--- | :--- |
| **🚨 Incident Reporting** | Commuters and riders can report incidents across 6 categories (*Rash driving, Helmet absence, Plate mismatch, Harassment, Overcharging*). |
| **🛑 User Blacklisting** | Admins can immediately suspend and ban malicious accounts, automatically cancelling active rides and blocking login. |
| **🚫 Vehicle Blacklisting** | Admin capability to blacklist specific motorcycle plate numbers for document fraud or unsafe vehicles. |
| **📑 DL & RC Gatekeeping** | Riders cannot post rides without Admin verification of Driving License and Insurance validity. |
| **⛑️ Helmet Mandate** | Strict compliance checkbox agreeing to carry a clean ISI helmet as per the Motor Vehicles Act. |

---

## 🛠️ Free-Tier Technology Stack

```
Frontend:  React 18 • Vite • Tailwind CSS • Leaflet.js • Lucide Icons
Backend:   Python 3.11 • Flask • Flask-RESTX (Swagger) • Flask-JWT-Extended • SQLAlchemy
Database:  Neon Serverless PostgreSQL (Cloud Free Tier)
Routing:   OpenStreetMap (OSM) • OSRM Road Routing API
AI/LLM:    Google Gemini API (Gemini 1.5 Flash via Google AI Studio)
Hosting:   Vercel (Frontend) • Hugging Face Spaces / Render (Backend) • Docker
```

---

## 🔑 Admin Credentials & Portal

The platform features an isolated Admin Moderation Portal for document verifications, incident review, and user management:

| Attribute | Credential / Details |
| :--- | :--- |
| **Portal Path** | Navbar ➔ `Admin Portal` (or login via modal) |
| **Admin Email** | `admin@gmail.com` |
| **Admin Password** | `Admin@7781` |
| **Admin Scope** | DL approvals, RC & Insurance verification, Incident reports triage, User/Bike blacklisting |

---

## 💻 Local Development Quickstart

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- PostgreSQL or Neon DB URL

### 1. Clone the Repository
```bash
git clone https://github.com/PARTHIBAKANNAN/BikeRideShare.git
cd BikeRideShare
```

### 2. Backend Setup
```bash
# Navigate to backend and install requirements
pip install -r backend/requirements.txt

# Configure environment variables (create backend/.env)
# DATABASE_URL=postgresql://user:pass@host/neondb?sslmode=require
# GEMINI_API_KEY=your_gemini_api_key
# JWT_SECRET_KEY=your_jwt_secret

# Start the Flask API server
python backend/app.py
```
> Backend API runs at `http://localhost:5000` (Swagger UI at `http://localhost:5000/docs/`)

### 3. Frontend Setup
```bash
# In a new terminal, navigate to frontend
cd frontend
npm install

# Start the Vite development server
npm run dev
```
> Frontend app runs at `http://localhost:5173`

---

## 🌐 Cloud Deployment Guide

### A. Deploy Frontend to Vercel (100% Free)
1. Push your repository to GitHub.
2. In [Vercel Dashboard](https://vercel.com), click **Add New Project** and import the repository.
3. Set **Root Directory** to `frontend`.
4. Add Environment Variable:
   - `VITE_API_URL`: `https://your-backend-url.hf.space` (or Render API URL)
5. Click **Deploy**.

### B. Deploy Backend to Hugging Face Spaces (24/7 Always-On Free)
1. In [Hugging Face Spaces](https://huggingface.co/spaces), click **Create new Space**.
2. Select **Docker** SDK (Blank).
3. Connect your GitHub repository or push via Git.
4. In Space Settings, add the following Secrets:
   - `DATABASE_URL`: Your Neon PostgreSQL Connection String
   - `GEMINI_API_KEY`: Your Google AI Studio Gemini API Key
   - `SECRET_KEY`: `super_secure_flask_secret_key`
   - `JWT_SECRET_KEY`: `super_secure_jwt_secret_key`
5. The container will build automatically using the root [Dockerfile](./Dockerfile) and host on port `7860`.

---

## 📡 API Endpoints Reference

### Authentication (`/api/auth`)
- `POST /api/auth/register` — Register commuter account (with gender & corridor preferences)
- `POST /api/auth/login` — JWT login authentication (enforces blacklist check)
- `GET /api/auth/profile` — Get authenticated commuter profile
- `PUT /api/auth/profile` — Update commute corridors and personal info
- `POST /api/auth/upload-license` — Submit Driving License for Admin review

### Rides & Pooling (`/api/rides`)
- `POST /api/rides/search` — Search rides by corridor, date, time, and Pink Ride filter
- `POST /api/rides/post` — Publish a new ride (enforces verified DL, insurance, active bike)
- `POST /api/rides/<id>/join` — Submit join request (supports "Book for a Friend")
- `GET /api/rides/my-requests` — Get commuter bookings and active OTP
- `POST /api/rides/requests/<id>/respond` — Accept / reject join request
- `POST /api/rides/requests/<id>/rate` — Submit post-commute rating and safety badges
- `POST /api/rides/route-preview` — Real-time OSRM road distance, duration, and fare preview
- `POST /api/rides/report` — File safety or conduct incident report

### Vehicle Management (`/api/bikes`)
- `GET /api/bikes/` — Get user's registered two-wheelers
- `POST /api/bikes/register` — Register bike with RC and Insurance (>30 days check)
- `PUT /api/bikes/<id>` — Update vehicle info and renewal documents
- `POST /api/bikes/set-active` — Select active vehicle for commute offers

### Admin Moderation (`/api/admin`)
- `GET /api/admin/dashboard` — Platform-wide metrics and stats
- `GET /api/admin/license-verifications` — Queue of pending driver licenses
- `POST /api/admin/license-verifications/verify` — Approve or reject DL with presets
- `GET /api/admin/incident-reports` — Incident triage queue
- `POST /api/admin/incident-reports/<id>/action` — Action incident report (investigate, blacklist)
- `GET /api/admin/users-directory` — Full user list with 1-click blacklist/reinstate
- `GET /api/admin/bikes-directory` — Full vehicle registry with 1-click plate ban

---

## 👨‍💻 Author & Ownership

* **Creator & Lead Software Architect**: **PARTHIBAKANNAN S**
* **Contact Email**: [parthisivaram45@gmail.com](mailto:parthisivaram45@gmail.com)
* **GitHub**: [@PARTHIBAKANNAN](https://github.com/PARTHIBAKANNAN)
* **LinkedIn**: [linkedin.com/in/parthibakannan-s](https://linkedin.com/in/parthibakannan-s)

---

## 📄 Copyright & License

```
Copyright (c) 2026 PARTHIBAKANNAN S. All rights reserved.
```

All software architecture, source code, design systems, algorithms, and documentation in this repository are owned and maintained by **PARTHIBAKANNAN S**.

---

<div align="center">
  <b>⭐ If you find SmartRide Chennai helpful, please star the repository! ⭐</b>
</div>