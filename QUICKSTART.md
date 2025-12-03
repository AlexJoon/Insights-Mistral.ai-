# Quick Start Guide

Get your Mistral Chat application up and running in under 5 minutes.

## Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- Mistral AI API key (already configured in `.env`)

## Automated Setup (Recommended)

### Option 1: Using the setup script

```bash
./setup.sh
```

This will automatically:
- Create Python virtual environment
- Install backend dependencies
- Install frontend dependencies

### Option 2: Manual Setup

If the automated script doesn't work, follow these steps:

#### Backend Setup (Terminal 1)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Verify .env file has your API key
cat .env
# Should show: MISTRAL_API_KEY=0JXJr9rrzJL5fX4drf29HAAAxwJWYRZy

# Start the backend server
python -m backend.main
```

You should see:
```
============================================================
Starting Mistral Chat API Server
============================================================
Host: 0.0.0.0
Port: 8000
Debug: True
Model: mistral-large-latest
============================================================
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application starting up...
INFO:     Using Mistral model: mistral-large-latest
INFO:     CORS origins: ['http://localhost:3000']
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Frontend Setup (Terminal 2)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

You should see:
```
   ▲ Next.js 14.1.0
   - Local:        http://localhost:3000
   - Environments: .env.local

 ✓ Ready in 2.3s
```

## Verify Installation

### 1. Check Backend Health

Open a new terminal and run:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","service":"mistral-chat-api"}
```

### 2. Test Frontend

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the Mistral Chat interface with:
- Left sidebar with "New Conversation" button
- Welcome message in the center

## First Conversation

1. Click **"New Conversation"** in the sidebar
2. Type a message in the input box at the bottom (e.g., "Hello, tell me about yourself")
3. Press Enter or click **"Send"**
4. Watch the AI response stream in real-time!

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'backend'`
```bash
# Solution: Make sure you're running from the backend directory
cd backend
python -m backend.main
```

**Problem**: `ValueError: MISTRAL_API_KEY environment variable is required`
```bash
# Solution: Check your .env file exists and has the API key
cat backend/.env
# If missing, copy from example:
cp backend/.env.example backend/.env
# Then edit and add your API key
```

**Problem**: Port 8000 already in use
```bash
# Solution: Change the port in backend/.env
echo "SERVER_PORT=8001" >> backend/.env
# Also update frontend/.env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > frontend/.env.local
```

### Frontend Issues

**Problem**: `Module not found: Can't resolve '@/...'`
```bash
# Solution: Delete node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem**: "Failed to fetch" error when sending messages
```bash
# Solution: Ensure backend is running and CORS is configured
# Check frontend/.env.local has correct API URL
cat frontend/.env.local
# Should show: NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Problem**: Port 3000 already in use
```bash
# Solution: Use a different port
PORT=3001 npm run dev
```

### SSE Streaming Issues

**Problem**: Messages not streaming, appearing all at once
- Check browser DevTools Network tab
- Look for `/api/chat/stream` request
- Verify it's using EventStream
- Check for any proxy/reverse proxy buffering issues

## Directory Structure Quick Reference

```
.
├── backend/                    # Python backend
│   ├── api/                   # Route handlers
│   ├── services/              # Business logic
│   ├── middleware/            # Request processing
│   ├── models/                # Data models
│   ├── config/                # Configuration
│   ├── utils/                 # Utilities
│   ├── main.py               # Entry point
│   ├── app.py                # App factory
│   └── requirements.txt      # Python dependencies
│
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   ├── services/         # API clients
│   │   ├── hooks/            # Custom hooks
│   │   ├── store/            # State management
│   │   └── types/            # TypeScript types
│   └── package.json          # Node dependencies
│
├── README.md                  # Main documentation
├── ARCHITECTURE.md            # Architecture details
├── QUICKSTART.md             # This file
└── setup.sh                  # Automated setup
```

## Next Steps

1. **Explore the Code**
   - Read [ARCHITECTURE.md](ARCHITECTURE.md) for design details
   - Check out the modular structure
   - Review the separation of concerns

2. **Customize**
   - Modify the UI theme in `frontend/tailwind.config.js`
   - Add new endpoints in `backend/api/`
   - Create new components in `frontend/src/components/`

3. **Deploy**
   - Backend: Deploy to Heroku, Railway, or AWS
   - Frontend: Deploy to Vercel, Netlify, or Cloudflare Pages

## Key Commands Reference

### Backend
```bash
# Start server
python -m backend.main

# Install new dependency
pip install <package>
pip freeze > requirements.txt

# Check code
python -m pylint backend/

# Run tests (when implemented)
pytest
```

### Frontend
```bash
# Development server
npm run dev

# Production build
npm run build
npm start

# Install new dependency
npm install <package>

# Lint
npm run lint
```

## Support

- For detailed architecture: See [ARCHITECTURE.md](ARCHITECTURE.md)
- For full documentation: See [README.md](README.md)
- For issues: Check the troubleshooting section above

## Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Health check returns healthy status
- [ ] Can create new conversation
- [ ] Can send message and see streaming response
- [ ] Sidebar shows conversation list
- [ ] Can switch between conversations
- [ ] Can delete conversations

If all boxes are checked, you're ready to go! 🚀
