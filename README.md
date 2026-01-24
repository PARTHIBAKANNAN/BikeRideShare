# 🚴‍♂️ Smart Ride Matcher - Chennai Daily Commute

A bike ride-sharing platform for Chennai commuters with AI-powered route matching.

## 🎯 Features

### Core Functionality
- **User Authentication** - Secure registration/login with JWT
- **Bike Management** - Register multiple bikes, admin verification
- **Ride Posting** - Offer or seek rides with flexible timing
- **AI Route Matching** - GPT-powered intelligent route overlap detection
- **Safety Features** - User ratings, reports, verified profiles

### AI-Powered Matching
- Analyzes any Chennai route (e.g., Pallavaram → Perungalathur vs Tambaram → Vandalur)
- Finds overlapping segments and nodal points
- Suggests optimal pickup/drop locations
- Calculates fair cost sharing

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **JWT** - Authentication
- **Flask-RESTX** - Swagger API documentation

### AI Integration
- **Azure OpenAI** - GPT-4 for route analysis
- **Fallback System** - Works without GPT using Chennai knowledge

### Frontend (Planned)
- **React** - User interface
- **Material-UI** - Modern design

## 📁 Project Structure

```
BikeRideApp/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── models/             # Database models
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   ├── config/             # Configuration
│   └── requirements.txt    # Dependencies
├── frontend/               # React application (future)
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js (for frontend)
- Azure OpenAI account (optional)

### Installation
1. Clone the repository
2. Set up virtual environment
3. Install dependencies
4. Configure environment variables
5. Run the application

## 🎯 Development Phases

### Phase 1: Core Backend ✅
- [x] User authentication
- [x] Database models
- [x] API endpoints
- [x] Swagger documentation

### Phase 2: Bike & Ride Management 🔄
- [ ] Bike registration
- [ ] Ride posting/searching
- [ ] Basic matching

### Phase 3: AI Integration 🔄
- [ ] GPT route analysis
- [ ] Intelligent matching
- [ ] Cost calculation

### Phase 4: Frontend 📋
- [ ] React application
- [ ] User dashboard
- [ ] Mobile responsive

### Phase 5: Production 📋
- [ ] Deployment
- [ ] Testing
- [ ] Documentation

## 📝 API Documentation

Once running, visit: `http://localhost:5000/docs/`

## 🌟 Example Use Case

**User A**: Daily commute Pallavaram → Perungalathur (8:30 AM)
**User B**: Occasional travel Tambaram → Vandalur (flexible timing)

**AI Analysis**: 
- Finds GST Road overlap
- Suggests Tambaram Railway Station as pickup point
- Calculates 60% route match
- Enables cost sharing and coordination

## 📞 Contact

Built for Chennai commuters by Chennai developers! 🚗🌟 