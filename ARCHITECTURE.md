# Architecture Documentation

## Overview

This application is built with a **modular, non-monolithic architecture** following the principle of **separation of powers**. Each layer has distinct responsibilities and communicates through well-defined interfaces.

## Architectural Principles

### 1. Separation of Concerns
Each module focuses on a single responsibility:
- **Routes** only handle HTTP request/response
- **Services** contain all business logic
- **Middleware** processes requests/responses
- **Models** define data structures
- **Components** handle UI rendering only
- **Stores** manage application state

### 2. Modularity
- No monolithic files
- Each file has a single, well-defined purpose
- Easy to locate, modify, and test individual components
- New features can be added without touching existing code

### 3. Division of Powers

#### Backend Layers
```
Request Flow:
HTTP Request → Middleware → Routes → Services → External API
                   ↓           ↓         ↓
              Validation   Routing   Business
              CORS         HTTP      Logic
              Errors       Layer     AI Calls
```

#### Frontend Layers
```
User Interaction Flow:
User Input → Components → Hooks → Services → API
               ↓           ↓        ↓
            UI Logic   Business   HTTP/SSE
            Rendering  Logic      Communication
                          ↓
                       Store
                    (State Mgmt)
```

## Backend Architecture

### Layer Breakdown

#### 1. API Layer (`/backend/api/`)
**Responsibility**: HTTP request/response handling

- `routes.py` - Route registration and URL mapping
- `chat_routes.py` - Chat endpoint handlers

**Key Principles**:
- Only handles HTTP concerns
- Validates request format
- Delegates business logic to services
- Returns properly formatted responses

#### 2. Service Layer (`/backend/services/`)
**Responsibility**: Business logic and external integrations

- `mistral_service.py` - Mistral AI API integration, SSE streaming
- `conversation_manager.py` - Conversation state management

**Key Principles**:
- No HTTP knowledge
- Pure business logic
- Reusable across different endpoints
- Can be tested independently

#### 3. Middleware Layer (`/backend/middleware/`)
**Responsibility**: Request/response processing

- `error_handler.py` - Centralized error handling
- `request_validator.py` - Request validation
- `cors.py` - CORS configuration

**Key Principles**:
- Processes all requests before routes
- Handles cross-cutting concerns
- No business logic

#### 4. Models Layer (`/backend/models/`)
**Responsibility**: Data structures and validation

- `chat.py` - Message, Conversation, Request models

**Key Principles**:
- Defines data schemas
- Type validation
- Serialization/deserialization
- No business logic

#### 5. Configuration Layer (`/backend/config/`)
**Responsibility**: Application configuration

- `settings.py` - Environment-based configuration

**Key Principles**:
- Centralized configuration
- Environment variable management
- Type-safe settings

#### 6. Utilities Layer (`/backend/utils/`)
**Responsibility**: Shared utilities

- `logger.py` - Logging configuration
- `validators.py` - Input validation functions

**Key Principles**:
- Reusable across layers
- No state
- Pure functions

## Frontend Architecture

### Layer Breakdown

#### 1. Components Layer (`/frontend/src/components/`)
**Responsibility**: UI rendering and user interaction

```
components/
├── sidebar/
│   ├── Sidebar.tsx           # Conversation list container
│   └── ConversationItem.tsx  # Individual conversation item
├── chat/
│   ├── ChatArea.tsx          # Message display area
│   ├── MessageBubble.tsx     # Individual message
│   └── MessageInput.tsx      # Message composition
└── ChatContainer.tsx         # Main layout orchestrator
```

**Key Principles**:
- Presentational components
- Minimal business logic
- Reusable and composable
- Props-driven

#### 2. Hooks Layer (`/frontend/src/hooks/`)
**Responsibility**: Reusable business logic

- `useChatHandler.ts` - Chat operations (send, cancel)

**Key Principles**:
- Encapsulates complex logic
- Reusable across components
- State management integration
- Side effect handling

#### 3. Services Layer (`/frontend/src/services/`)
**Responsibility**: External communication

- `api-client.ts` - Base HTTP client
- `sse-client.ts` - SSE streaming client
- `chat-service.ts` - Chat API operations
- `conversation-service.ts` - Conversation API operations

**Key Principles**:
- Abstracts API details
- Handles network errors
- Type-safe responses
- No UI logic

#### 4. Store Layer (`/frontend/src/store/`)
**Responsibility**: Global state management

- `chat-store.ts` - Chat state (Zustand)

**Key Principles**:
- Single source of truth
- Immutable updates
- Selector-based access
- No side effects in reducers

#### 5. Types Layer (`/frontend/src/types/`)
**Responsibility**: TypeScript type definitions

- `chat.ts` - Chat-related types
- `api.ts` - API-related types

**Key Principles**:
- Type safety
- Shared across application
- Matches backend models
- No logic

## Data Flow

### Chat Message Flow

```
1. User types message → MessageInput component
2. MessageInput calls useChatHandler hook
3. Hook updates store (add user message)
4. Hook calls chat-service.sendMessage()
5. Service uses sse-client to POST to /api/chat/stream
6. Request passes through middleware:
   - CORS middleware (allows request)
   - RequestValidationMiddleware (validates format)
   - ErrorHandlerMiddleware (wraps request)
7. Route handler (chat_routes.stream_chat) receives request
8. Route validates input, gets/creates conversation
9. Route calls mistral_service.stream_chat_completion()
10. Service streams from Mistral AI API
11. Service yields SSE chunks
12. SSE client receives chunks
13. Hook appends chunks to streaming message in store
14. Components re-render with updated state
15. User sees message appear word-by-word
```

### Error Flow

```
1. Error occurs in any layer
2. Error bubbles up to ErrorHandlerMiddleware (backend)
3. Middleware catches error, logs it
4. Middleware returns formatted JSON error
5. Frontend service receives error response
6. Service returns { error: {...} }
7. Hook/component checks for error
8. Store.setError() updates error state
9. ChatContainer displays error banner
10. User sees error message
```

## SSE Streaming Implementation

### Why SSE over WebSockets?

1. **Simpler Protocol**: Unidirectional, no handshake complexity
2. **HTTP-based**: Works with standard HTTP infrastructure
3. **Auto-reconnection**: Built-in reconnection logic
4. **Text-based**: Perfect for chat streaming
5. **No Additional Server Setup**: Works with standard HTTP servers

### SSE Implementation Details

#### Backend (Python)
```python
# In mistral_service.py
async for line in response.aiter_lines():
    if line.startswith("data: "):
        data = line[6:]  # Remove "data: " prefix
        chunk = json.loads(data)
        yield StreamChunk(content=chunk.content, ...)
```

#### Frontend (TypeScript)
```typescript
// In sse-client.ts
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    // Parse SSE format and extract data
    options.onChunk(parsedChunk);
}
```

## State Management

### Zustand Store Design

```typescript
interface ChatState {
  // Data
  currentConversation: Conversation | null;
  conversations: Conversation[];

  // UI State
  isStreaming: boolean;
  currentStreamingMessage: string;
  error: string | null;

  // Actions
  setCurrentConversation: (conv) => void;
  addMessage: (convId, msg) => void;
  // ... more actions
}
```

**Why Zustand?**
1. **Minimal Boilerplate**: No providers, no reducers
2. **TypeScript Support**: Full type safety
3. **DevTools**: Redux DevTools integration
4. **Performance**: Selector-based subscriptions
5. **Small Bundle**: ~1KB gzipped

## Scalability Considerations

### Horizontal Scaling
- **Backend**: Stateless design allows multiple instances
- **Frontend**: Static generation enables CDN distribution
- **State**: In-memory storage can be replaced with Redis

### Vertical Scaling
- **Backend**: Async/await for concurrent request handling
- **Frontend**: Code splitting, lazy loading
- **SSE**: Connection pooling, event-driven architecture

### Database Integration
Current: In-memory storage (`ConversationManager`)

Future: Replace with database layer
```python
# backend/services/database_service.py
class DatabaseService:
    async def get_conversation(self, conv_id: str):
        # PostgreSQL, MongoDB, etc.
        pass
```

No other code needs to change due to modular design.

## Security

### Current Measures
1. **CORS**: Configurable allowed origins
2. **Input Validation**: Multi-layer validation
3. **Error Messages**: No sensitive data exposure
4. **API Key**: Server-side only, never exposed to client

### Production Recommendations
1. Add authentication/authorization
2. Rate limiting middleware
3. Request size limits
4. SQL injection protection (when using DB)
5. XSS protection headers
6. HTTPS enforcement

## Testing Strategy

### Backend Testing
```python
# Unit Tests
- Test services independently
- Mock external APIs
- Test validators

# Integration Tests
- Test route handlers
- Test middleware chain
- Test error handling
```

### Frontend Testing
```typescript
// Unit Tests
- Test components with React Testing Library
- Test hooks independently
- Test services with mocked fetch

// E2E Tests
- Test full user flows
- Test SSE streaming
- Test error scenarios
```

## Performance Optimizations

### Backend
1. **Async I/O**: Non-blocking HTTP calls
2. **Streaming**: Memory-efficient SSE
3. **Connection Pooling**: Reuse HTTP connections

### Frontend
1. **Code Splitting**: Lazy load routes
2. **Memoization**: React.memo, useMemo
3. **Virtual Scrolling**: For long message lists
4. **Debouncing**: Input handling

## Deployment

### Backend Deployment
```bash
# Docker
docker build -t mistral-chat-backend .
docker run -p 8000:8000 --env-file .env mistral-chat-backend

# Kubernetes
kubectl apply -f k8s/backend-deployment.yaml
```

### Frontend Deployment
```bash
# Static Export
npm run build
# Deploy to Vercel, Netlify, CloudFront, etc.

# Docker
docker build -t mistral-chat-frontend .
docker run -p 3000:3000 mistral-chat-frontend
```

## Monitoring and Logging

### Current Implementation
- Structured logging with Python logging module
- Request/response logging in middleware
- Error tracking in ErrorHandlerMiddleware

### Production Recommendations
1. **Application Monitoring**: Datadog, New Relic
2. **Error Tracking**: Sentry
3. **Logging**: ELK Stack, CloudWatch
4. **Metrics**: Prometheus + Grafana
5. **Tracing**: OpenTelemetry

## Future Enhancements

### Short-term
1. User authentication (JWT)
2. Conversation search
3. Message editing/deletion
4. File uploads
5. Code syntax highlighting

### Long-term
1. Multi-model support (OpenAI, Anthropic, etc.)
2. Conversation sharing
3. Real-time collaboration
4. Voice input/output
5. Mobile app (React Native)

## Conclusion

This architecture prioritizes:
- **Maintainability**: Easy to understand and modify
- **Scalability**: Can grow with usage
- **Testability**: Each layer can be tested independently
- **Developer Experience**: Clear structure, type safety
- **Performance**: Efficient streaming, minimal overhead

The modular design ensures that changes in one layer don't cascade to others, making the application resilient to change and easy to extend.
