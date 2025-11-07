# SafeChild Backend Integration Contracts

## 1. Database Schema (MongoDB)

### Collections:

#### 1.1 clients
```javascript
{
  _id: ObjectId,
  clientNumber: String (unique, format: "SC2025XXX"),
  firstName: String,
  lastName: String,
  email: String,
  phone: String,
  country: String,
  caseType: String, // "hague_convention", "child_abduction", "custody_rights"
  status: String, // "active", "closed", "pending"
  createdAt: Date,
  updatedAt: Date
}
```

#### 1.2 documents
```javascript
{
  _id: ObjectId,
  documentNumber: String (unique, format: "DOC2025XXX"),
  clientNumber: String (reference to clients),
  fileName: String,
  fileSize: Number,
  fileType: String,
  filePath: String,
  uploadedBy: String, // "client" or "lawyer"
  uploadedAt: Date,
  status: String // "pending", "reviewed", "approved"
}
```

#### 1.3 consents
```javascript
{
  _id: ObjectId,
  sessionId: String,
  ipAddress: String,
  userAgent: String,
  location: Object {
    latitude: Number,
    longitude: Number,
    country: String,
    city: String
  },
  permissions: Object {
    location: Boolean,
    browser: Boolean,
    camera: Boolean,
    files: Boolean,
    forensic: Boolean
  },
  timestamp: Date,
  clientNumber: String (optional, if client is registered)
}
```

#### 1.4 chat_messages
```javascript
{
  _id: ObjectId,
  sessionId: String,
  clientNumber: String (optional),
  sender: String, // "client" or "bot" or "lawyer"
  message: String,
  timestamp: Date,
  isRead: Boolean
}
```

#### 1.5 landmark_cases (read-only reference data)
```javascript
{
  _id: ObjectId,
  caseNumber: String,
  year: Number,
  countries: Object { de: String, en: String },
  title: Object { de: String, en: String },
  description: Object { de: String, en: String },
  outcome: Object { de: String, en: String },
  facts: Object { de: String, en: String },
  legalPrinciple: Object { de: String, en: String },
  impact: Object { de: String, en: String }
}
```

## 2. API Endpoints

### 2.1 Client Management

**POST /api/clients**
- Create new client
- Auto-generate client number
- Request body: { firstName, lastName, email, phone, country, caseType }
- Response: { clientNumber, message }

**GET /api/clients/:clientNumber**
- Get client details
- Auth: Client number validation
- Response: Client object

**GET /api/clients/:clientNumber/validate**
- Validate client number
- Response: { valid: Boolean, client: Object }

### 2.2 Document Management

**POST /api/documents/upload**
- Upload document(s)
- Requires: clientNumber (validated)
- Request: multipart/form-data with files
- Auto-generate document number
- Store in /uploads directory
- Response: { documentNumber, fileName, uploadedAt }

**GET /api/documents/:documentNumber/download**
- Download document
- Requires: document number validation
- Response: File stream

**GET /api/documents/client/:clientNumber**
- List all documents for a client
- Response: Array of document objects

### 2.3 Consent Management

**POST /api/consent**
- Log user consent
- Request body: { sessionId, permissions, location, userAgent, ipAddress }
- Response: { consentId, timestamp }

**GET /api/consent/:sessionId**
- Get consent details for a session
- Response: Consent object

### 2.4 Chat Management

**POST /api/chat/message**
- Send chat message
- Request body: { sessionId, sender, message, clientNumber? }
- Response: { messageId, timestamp }

**GET /api/chat/:sessionId**
- Get chat history for session
- Response: Array of messages

### 2.5 Landmark Cases

**GET /api/cases/landmark**
- Get all landmark cases
- Response: Array of case objects

**GET /api/cases/landmark/:caseNumber**
- Get specific landmark case
- Response: Case object

## 3. Frontend-Backend Integration

### 3.1 Mock Data to Remove
- mockClientNumbers from mock.js
- mockFileNumbers from mock.js
- Mock client/file validation in Documents.jsx
- Mock chat responses in LiveChat.jsx

### 3.2 Frontend Updates Required

**Documents.jsx:**
- Replace mock validation with API call to /api/clients/:clientNumber/validate
- Implement actual file upload to /api/documents/upload
- Implement actual file download from /api/documents/:documentNumber/download
- Show toast messages based on API responses

**LiveChat.jsx:**
- Replace mock messages with API calls to /api/chat/message
- Fetch chat history from /api/chat/:sessionId
- Send consent data to /api/consent

**ConsentModal.jsx:**
- Collect browser data (navigator.userAgent, navigator.geolocation)
- Send to /api/consent endpoint after user accepts

**New Component: CasesShowcase.jsx (optional)**
- Display landmark cases from /api/cases/landmark
- Show on About or Services page

## 4. Environment Variables

**Backend (.env):**
```
MONGO_URL=mongodb://127.0.0.1:27017/safechild
DB_NAME=safechild
UPLOAD_DIR=/app/backend/uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt
```

## 5. File Upload Strategy

- Store files in /app/backend/uploads/{clientNumber}/{documentNumber}_filename
- Validate file types and sizes on backend
- Generate unique document numbers: DOC + YYYY + sequential number
- Store file metadata in documents collection

## 6. Security Considerations

- Validate all client numbers before allowing operations
- Sanitize file names to prevent path traversal
- Limit file upload size to 10MB
- Verify file types both on client and server
- Store IP addresses and consent logs for legal compliance
- Implement rate limiting on API endpoints

## 7. Testing Strategy

- Test client registration flow
- Test document upload with valid/invalid client numbers
- Test document download with valid/invalid document numbers
- Test consent logging with various permissions
- Test chat message storage and retrieval
- Test landmark cases display

## 8. Implementation Order

1. ✅ Create MongoDB schemas and models
2. ✅ Implement client management endpoints
3. ✅ Implement document upload/download with file storage
4. ✅ Implement consent logging endpoint
5. ✅ Implement chat message endpoints
6. ✅ Seed landmark cases data
7. ✅ Update frontend to use real API calls
8. ✅ Test all integrations
9. ✅ Add error handling and validation
