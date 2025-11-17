# Authentication Setup Guide

This guide will help you set up the authentication system for MyAIStorybook.

## Prerequisites

1. **PostgreSQL Database**: Make sure PostgreSQL is installed and running on your system.
2. **Database Created**: Create a database named `myaistorybook` (or update the connection string).

## Setup Steps

### 1. Install Dependencies

Make sure all required packages are installed:

```bash
cd backend
pip install -r requirements.txt
```

The authentication system requires:
- `sqlalchemy` - ORM for database operations
- `psycopg2-binary` - PostgreSQL adapter
- `python-jose[cryptography]` - JWT token handling
- `passlib[bcrypt]` - Password hashing
- `python-multipart` - Form data handling
- `email-validator` - Email validation

### 2. Configure Database Connection

**IMPORTANT**: The default connection string uses `postgres:postgres` which may not match your PostgreSQL setup.

The default database connection string is:
```
postgresql://postgres:postgres@localhost:5432/myaistorybook
```

**To fix the connection error**, you need to set the `DATABASE_URL` environment variable with your actual PostgreSQL credentials:

```bash
# Windows PowerShell (run before starting the backend)
$env:DATABASE_URL="postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/myaistorybook"

# Windows Command Prompt
set DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/myaistorybook

# Linux/Mac
export DATABASE_URL="postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/myaistorybook"
```

**To find your PostgreSQL username and password:**
- If you installed PostgreSQL, you may have set a password during installation
- Default username is often `postgres`
- If you forgot your password, you can reset it or check your PostgreSQL configuration

**Alternative: Create a `.env` file** (recommended for development):
Create a file named `.env` in the `backend/` directory:
```
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/myaistorybook
```

Then install `python-dotenv` and load it in your code (optional enhancement).

### 3. Create the Database

**IMPORTANT**: Before starting the backend, you need to create the database itself.

**Option 1: Using the provided script (Windows)**
```bash
cd backend
.\create_database.bat
```

**Option 2: Using psql command line**
```bash
psql -U postgres
# Then in psql prompt:
CREATE DATABASE myaistorybook;
\q
```

**Option 3: Using pgAdmin**
1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Right-click on "Databases" → "Create" → "Database"
4. Name it `myaistorybook`
5. Click "Save"

### 4. Initialize Database Tables

The tables will be created automatically when you start the backend server (via `Base.metadata.create_all()` in `main.py`).

Alternatively, you can run the initialization script manually:
```bash
cd backend
python auth/init_db.py
```

### 5. Configure JWT Secret Key (Optional)

For production, set a secure secret key:

```bash
# Windows PowerShell
$env:SECRET_KEY="your-super-secret-key-minimum-32-characters-long"

# Linux/Mac
export SECRET_KEY="your-super-secret-key-minimum-32-characters-long"
```

If not set, a default key will be used (not recommended for production).

### 6. Start the Backend

```bash
cd backend
.\start_backend.bat
```

Or manually:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication Endpoints

- `POST /api/auth/register` - Register a new user
  - Body: `{ "email": "user@example.com", "username": "username", "password": "password" }`
  - Returns: `{ "access_token": "...", "token_type": "bearer", "user": {...} }`

- `POST /api/auth/login` - Login
  - Body: `{ "email": "user@example.com", "password": "password" }`
  - Returns: `{ "access_token": "...", "token_type": "bearer", "user": {...} }`

- `GET /api/auth/me` - Get current user info (requires authentication)
  - Headers: `Authorization: Bearer <token>`
  - Returns: `{ "id": 1, "email": "...", "username": "...", ... }`

### Protected Endpoints

- `POST /api/generate` - Generate story
  - **Guest users**: Can generate text-only stories (generate_images must be false)
  - **Authenticated users**: Can generate stories with images
  - Headers: `Authorization: Bearer <token>` (optional for guests)

## Frontend Integration

The frontend automatically:
- Shows login/register buttons in navigation for guests
- Disables the "Illustrate My Story" toggle for guests
- Shows a login prompt when guests try to enable image generation
- Stores JWT tokens in localStorage
- Sends Authorization headers with authenticated requests

## Guest Mode

By default, users are in guest mode and can:
- ✅ Create text-only stories
- ❌ Generate images (requires login)

After logging in, users can:
- ✅ Create text-only stories
- ✅ Generate images

## Troubleshooting

### Database Connection Issues

1. **Check PostgreSQL is running**:
   ```bash
   # Windows
   Get-Service postgresql*
   
   # Linux/Mac
   sudo systemctl status postgresql
   ```

2. **Verify database exists**:
   ```sql
   -- Connect to PostgreSQL
   psql -U postgres
   
   -- List databases
   \l
   
   -- Create database if needed
   CREATE DATABASE myaistorybook;
   ```

3. **Check connection string**: Ensure the username, password, host, and database name are correct.

### Import Errors

If you get import errors, make sure you're running from the correct directory:
```bash
cd backend
python auth/init_db.py
```

### Token Issues

- Tokens expire after 7 days by default
- Clear localStorage in browser to reset authentication state
- Check browser console for authentication errors

## Security Notes

- Passwords are hashed using bcrypt
- JWT tokens are signed with HS256 algorithm
- Tokens include expiration time
- Database credentials should be kept secure
- Use environment variables for sensitive configuration in production

