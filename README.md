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

# 🚴‍♂️ Smart Ride Matcher - Chennai Daily Commute

An AI & Road Corridor-powered **Bike Ride-Sharing (Bike Pooling) Platform** tailored specifically for daily office commuters across Chennai (OMR, GST Road, 100ft Inner Ring Road, Mount Road, Ambattur & Porur IT Corridors).

---

## 🌟 Key Capabilities & Architecture

- **🗺️ Interactive Chennai Road Maps**: Built with **Leaflet.js + OpenStreetMap**, rendering turn-by-turn road polylines, animated rider GPS tracking, and suggested pickup nodal pins across Chennai.
- **🛣️ OSRM Road Routing Engine**: Real road network routing with exact road distances (km), travel durations (minutes), and GeoJSON geometries (100% free with no API key requirement).
- **🤖 Intelligent Commute Matching (Gemini AI + Geometric Corridor Engine)**:
  - Detects corridor overlaps (e.g., rider going *Maduravoyal ➔ Olympia Tech Park* picking up a passenger at *Vadapalani* with 0 min detour).
  - Calculates compatibility match scores (0–100%), estimated detour minutes, and suggested boarding junctions.
- **💰 Smart Fair-Pricing Engine**:
  - Calculates commute fuel sharing rates based on actual road distance.
  - Automatic peak-hour office commute surcharge (8:00–10:30 AM & 5:00–8:30 PM) and long-distance pooling discounts.
- **🏍️ Dynamic User Roles & Gatekeeping (Passenger vs Rider)**:
  - Any user can switch between **Passenger** (finding rides) and **Rider** (offering rides).
  - **Safety Gatekeeping**: To offer a ride, users **must** have an Admin-approved Driving License (DL) and at least one Admin-approved registered two-wheeler.
  - **Indian Bike Catalog**: Pre-integrated with popular Indian two-wheeler models (Royal Enfield, Honda, TVS, Bajaj, Yamaha, Hero, Ather, Ola, Suzuki, KTM, etc.).
- **🛡️ Dedicated Admin Moderation Portal**:
  - Review submitted Driver Licenses (with document photo preview).
  - Review Two-Wheeler Registrations (with RC & Insurance details).
  - 1-Click Approve / Reject controls with live status updates.

---

## 🔑 Platform Admin Credentials

| Role | Username / Email | Password | Scope |
| :--- | :--- | :--- | :--- |
| **🛡️ System Administrator** | `admin@gmail.com` | `Admin@7781` | Full admin moderation, DL approvals, bike verifications, user management |

---

## 🛠️ Free-Tier Technology Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, Leaflet.js, Lucide Icons | 100% Free deployment on **Vercel / Cloudflare Pages** |
| **Backend** | Python Flask, Flask-RESTX, Flask-JWT-Extended | 100% Free 24/7 deployment on **Hugging Face Spaces / Render** |
| **Database** | Neon Serverless PostgreSQL / SQLAlchemy ORM | **100% Free Forever** (500MB cloud database) |
| **Maps & Routing** | OpenStreetMap (OSM) + OSRM Road Engine | **100% Free & Open** (zero API keys required) |
| **AI / LLM** | Google Gemini API (`gemini-1.5-flash`) | **100% Free Tier** on Google AI Studio |

---

## 🚀 Quick Start (Running Locally)

### 1. Backend Setup
```bash
# Navigate to backend and install dependencies
pip install -r backend/requirements.txt

# Start the Flask API server
python backend/app.py
```
> Backend runs at: `http://localhost:5000` (Swagger docs at `http://localhost:5000/docs/`)

### 2. Frontend Setup
```bash
# Navigate to frontend and install dependencies
cd frontend
npm install

# Start the Vite development server
npm run dev
```
> Frontend runs at: `http://localhost:5173`

---

## 🌐 100% Free Live Deployment Guide

### A. Deploy Frontend to Vercel (100% Free Forever)
1. Push this repository to your GitHub account.
2. Go to [Vercel](https://vercel.com) and click **"Add New Project"**.
3. Select your repository, set **Root Directory** to `frontend`.
4. Add environment variable:
   * `VITE_API_URL`: `https://your-backend-url.hf.space` (or your Render URL)
5. Click **Deploy**.

### B. Deploy Backend to Hugging Face Spaces (24/7 Always-On Free)
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
2. Name it `chennai-bike-share-backend`, choose **Docker** SDK (Blank).
3. Push your backend code or link your GitHub repo.
4. In Space Settings, add your Secrets:
   * `DATABASE_URL`: `postgresql://...` (your Neon Postgres URL)
   * `GEMINI_API_KEY`: `your_gemini_key`
   * `SECRET_KEY`: `chennai_bike_share_secret_key_2026_super_secure_jwt`
   * `JWT_SECRET_KEY`: `chennai_jwt_token_secret_key_2026_safe_auth`
5. Your API is live 24/7 with zero cold starts!

---

## 👨‍💻 Author & Ownership

* **Creator & Lead Architect**: **PARTHIBAKANNAN S**
* **Contact Email**: [parthisivaram45@gmail.com](mailto:parthisivaram45@gmail.com)
* **GitHub**: [@PARTHIBAKANNAN](https://github.com/PARTHIBAKANNAN)

---

## 📄 Copyright & License

```
Copyright (c) 2026 PARTHIBAKANNAN S. All rights reserved.
```
All design, source code, and intellectual property of **SmartRide Chennai** are owned and maintained by **PARTHIBAKANNAN S**.