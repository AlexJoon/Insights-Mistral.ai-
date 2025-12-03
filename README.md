# Mistral Chat Application

A modern, modular chat application powered by Mistral AI with real-time streaming responses. Built with a clean separation of concerns across frontend, backend, and middleware layers.

## Architecture Overview

This project follows a **non-monolithic architecture** with clear separation of powers:

### Backend (Python)
- **`/backend/api/`** - REST API route handlers
- **`/backend/services/`** - Business logic layer (Mistral AI integration, conversation management)
- **`/backend/middleware/`** - Request processing, validation, error handling, CORS
- **`/backend/models/`** - Data models and type definitions
- **`/backend/config/`** - Configuration management
- **`/backend/utils/`** - Utility functions (logging, validation)

### Frontend (Next.js + TypeScript)
- **`/frontend/src/components/`** - Modular React components
  - `/sidebar/` - Conversation list components
  - `/chat/` - Chat interface components
- **`/frontend/src/services/`** - API communication layer
- **`/frontend/src/hooks/`** - Custom React hooks
- **`/frontend/src/store/`** - State management (Zustand)
- **`/frontend/src/types/`** - TypeScript type definitions
- **`/frontend/src/utils/`** - Frontend utilities

## Features

- **Real-time Streaming**: SSE (Server-Sent Events) implementation for ChatGPT-like streaming responses
- **Conversation Management**: Create, view, and delete conversation threads
- **Modular Architecture**: Clean separation of concerns, no monolithic files
- **Type Safety**: Full TypeScript implementation on frontend
- **Modern UI**: Tailwind CSS with a sleek, dark theme
- **Error Handling**: Comprehensive error handling at every layer
- **State Management**: Zustand for lightweight, efficient state management

## Technology Stack

### Backend
- **Starlette** - Lightweight ASGI framework
- **Uvicorn** - ASGI server with WebSocket support
- **httpx** - Async HTTP client for Mistral AI API
- **Python 3.8+**

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and better developer experience
- **Zustand** - State management
- **Tailwind CSS** - Utility-first CSS framework

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Node.js 18 or higher
- Mistral AI API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your Mistral API key
```

5. Start the backend server:
```bash
python -m backend.main
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
# Create .env.local file with:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Health Check
- `GET /health` - Check API status

### Chat
- `POST /api/chat/stream` - Stream a chat completion (SSE)

### Conversations
- `GET /api/conversations` - Get all conversations
- `POST /api/conversations` - Create a new conversation
- `GET /api/conversations/{id}` - Get a specific conversation
- `PUT /api/conversations/{id}` - Update conversation title
- `DELETE /api/conversations/{id}` - Delete a conversation

## Project Structure

```
.
├── backend/
│   ├── api/              # API route handlers
│   │   ├── chat_routes.py
│   │   └── routes.py
│   ├── services/         # Business logic
│   │   ├── mistral_service.py
│   │   └── conversation_manager.py
│   ├── middleware/       # Request/response processing
│   │   ├── error_handler.py
│   │   ├── request_validator.py
│   │   └── cors.py
│   ├── models/           # Data models
│   │   └── chat.py
│   ├── config/           # Configuration
│   │   └── settings.py
│   ├── utils/            # Utilities
│   │   ├── logger.py
│   │   └── validators.py
│   ├── app.py            # Application factory
│   ├── main.py           # Entry point
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/   # React components
│   │   │   ├── sidebar/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── ConversationItem.tsx
│   │   │   ├── chat/
│   │   │   │   ├── ChatArea.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   └── MessageInput.tsx
│   │   │   └── ChatContainer.tsx
│   │   ├── services/     # API clients
│   │   │   ├── api-client.ts
│   │   │   ├── sse-client.ts
│   │   │   ├── chat-service.ts
│   │   │   └── conversation-service.ts
│   │   ├── hooks/        # Custom hooks
│   │   │   └── useChatHandler.ts
│   │   ├── store/        # State management
│   │   │   └── chat-store.ts
│   │   ├── types/        # TypeScript types
│   │   │   ├── chat.ts
│   │   │   └── api.ts
│   │   └── styles/       # Global styles
│   │       └── globals.css
│   ├── package.json
│   └── tsconfig.json
│
└── README.md
```

## Design Principles

### Modularity
Each module has a single, well-defined responsibility. No monolithic files.

### Separation of Concerns
- **Routes** handle HTTP requests/responses
- **Services** contain business logic
- **Middleware** processes requests/responses
- **Models** define data structures
- **Components** handle UI rendering
- **Stores** manage state

### Type Safety
Full TypeScript implementation ensures type safety across the frontend.

### Error Handling
Comprehensive error handling at every layer with user-friendly error messages.

### Scalability
Architecture designed to scale - easy to add new features, services, or components.

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python -m backend.main
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Building for Production

Backend:
```bash
# Install dependencies
pip install -r requirements.txt

# Run with production settings
DEBUG=false python -m backend.main
```

Frontend:
```bash
npm run build
npm start
```

## Environment Variables

### Backend (.env)
```env
MISTRAL_API_KEY=your_api_key_here
MISTRAL_API_BASE_URL=https://api.mistral.ai/v1
MISTRAL_MODEL=mistral-large-latest
MISTRAL_MAX_TOKENS=4096
MISTRAL_TEMPERATURE=0.7
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Contributing

When adding new features, maintain the modular architecture:

1. **Backend**: Create new services in `/backend/services/`, add routes in `/backend/api/`
2. **Frontend**: Create new components in `/frontend/src/components/`, add services in `/frontend/src/services/`
3. **Keep files focused** - one responsibility per file
4. **Use types** - define TypeScript types for all data structures
5. **Handle errors** - comprehensive error handling at every layer

## License

MIT

## Support

For issues or questions, please open an issue on the repository.
