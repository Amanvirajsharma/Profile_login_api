from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import profile, auth  # Added auth

app = FastAPI(
    title="Profile API with Authentication",
    description="""
    ## Profile & Authentication API
    
    ### Features:
    - 🔐 User Registration & Login
    - 🎫 JWT Token Authentication
    - 👤 User Profiles (User & Institution)
    - 🔍 Search & Filter
    
    ### Authentication:
    1. Register using `/api/v1/auth/register`
    2. Login using `/api/v1/auth/login`
    3. Use the token in Authorization header: `Bearer <token>`
    
    ### Made with ❤️ using FastAPI + Supabase
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/v1")      # Auth routes
app.include_router(profile.router, prefix="/api/v1")   # Profile routes


@app.get("/")
def root():
    return {
        "message": "Welcome to Profile API with Authentication!",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "profiles": "/api/v1/profiles"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running!"}