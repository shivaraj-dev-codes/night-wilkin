# Night Wilkin - Women's Safety Platform

A comprehensive mobile-first platform designed to empower women with real-time safety monitoring, emergency alerts, and community protection features.

## 🌟 Features

### For Walkers (Women Users)
- **Real-time Location Sharing**: Share your location with trusted guardians during walks
- **SOS Emergency Alert**: One-click emergency notification to all guardians
- **Fake Call Generator**: Simulate incoming calls to help escape uncomfortable situations
- **Check-in Reminders**: Periodic check-ins to confirm your safety
- **Danger Zone Reports**: Report and view dangerous areas in real-time
- **Evidence Recording**: Safely record audio/video evidence (encrypted)
- **Safe Location Finder**: Locate nearby police stations, hospitals, and safe zones
- **Session Management**: Track walk sessions with destination and expected return time

### For Guardians (Support Contacts)
- **Walker Monitoring**: Real-time location tracking of assigned walkers
- **SOS Response**: Quick response system for emergency alerts
- **Alert Management**: Acknowledge and resolve safety incidents
- **Location History**: Access to historical location data
- **Multiple Walker Tracking**: Monitor multiple walkers simultaneously

## 🏗️ Architecture

### Backend Stack
- **Framework**: Django REST Framework
- **Real-time Communication**: Django Channels (WebSocket)
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL
- **API Documentation**: drf-spectacular (Swagger)
- **Authentication**: JWT (SimpleJWT)

### Frontend Stack
- **Framework**: React 18
- **Build Tool**: Vite
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **UI Framework**: Tailwind CSS
- **Map**: React Leaflet
- **Notifications**: React Hot Toast

## 📁 Project Structure

```
night-wilkin/
├── backend/
│   ├── nightwilkin/          # Project settings
│   ├── core/                 # Main app
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/            # Page components
│   │   ├── components/       # Reusable components
│   │   ├── api/              # API endpoints
│   │   ├── store/            # Zustand stores
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 16+
- Python 3.11+

### Backend Setup

```bash
cd backend

# Create .env file
cp .env.example .env

# Update .env with your credentials

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Access services
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Admin Panel: http://localhost:8000/admin
- API Docs: http://localhost:8000/api/docs
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/token/refresh/` - Refresh access token

### Walkers
- `GET/POST /api/walk-sessions/` - Manage walk sessions
- `POST /api/location-updates/` - Update location
- `POST /api/sos-alerts/` - Trigger SOS
- `GET /api/danger-zones/nearby/` - Get nearby danger zones

### Guardians
- `GET /api/users/my_walkers/` - List assigned walkers
- `POST /api/sos-alerts/{id}/acknowledge/` - Acknowledge SOS

## 🔐 Security Features

- **End-to-End Encryption**: Evidence files are encrypted
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Separate permissions for walkers and guardians
- **Data Privacy**: Automatic anonymization of old location data
- **HTTPS Ready**: Production-ready SSL configuration

## 📱 Real-time Features

### WebSocket Communication
- Live location tracking
- Instant SOS notifications
- Real-time check-in requests
- Guardian alerts

### Background Tasks (Celery)
- Periodic check-in reminders
- SOS notification delivery
- Danger zone monitoring
- Session auto-termination
- Location data anonymization

## 🌍 External Integrations

- **Google Maps API**: For safe location finder and directions
- **Twilio**: SMS notifications for SOS and check-ins
- **OpenAI**: For danger analysis and safe route suggestions

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] AI-powered danger prediction
- [ ] Community safety ratings
- [ ] Integration with law enforcement
- [ ] Multi-language support
- [ ] Offline mode with sync
- [ ] Advanced analytics dashboard

## 📞 Support

For issues or questions, please open an issue on GitHub or contact support@nightwilkin.com

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

---

**Stay Safe, Stay Connected** 🛡️
