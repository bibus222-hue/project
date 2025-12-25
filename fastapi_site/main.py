from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app import models, schemas, crud
from app.routers import users, items
from app.auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
import os

# Создание таблиц
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Site with Database",
    description="Пример сайта на FastAPI с базой данных SQLite",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(users.router)
app.include_router(items.router)

# Создание папки для статических файлов если её нет
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Авторизация
@app.post("/auth/login")
async def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI Site</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            .endpoints {
                margin-top: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
            .endpoint {
                margin: 10px 0;
                padding: 10px;
                background-color: white;
                border-left: 4px solid #007bff;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 FastAPI Site with Database</h1>
            <p>Добро пожаловать в пример сайта на FastAPI с базой данных!</p>
            
            <div class="endpoints">
                <h2>📡 Доступные эндпоинты:</h2>
                
                <div class="endpoint">
                    <strong>POST /auth/login</strong> - Авторизация
                </div>
                
                <div class="endpoint">
                    <strong>GET /users/</strong> - Получить всех пользователей
                </div>
                
                <div class="endpoint">
                    <strong>POST /users/</strong> - Создать пользователя
                </div>
                
                <div class="endpoint">
                    <strong>GET /items/</strong> - Получить все товары
                </div>
                
                <div class="endpoint">
                    <strong>POST /items/</strong> - Создать товар (требуется авторизация)
                </div>
                
                <div class="endpoint">
                    <strong>GET /docs</strong> - Документация Swagger
                </div>
                
                <div class="endpoint">
                    <strong>GET /redoc</strong> - Альтернативная документация
                </div>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background-color: #e8f4fd; border-radius: 5px;">
                <h3>🔧 Настройка окружения:</h3>
                <p>1. Установите зависимости: <code>pip install -r requirements.txt</code></p>
                <p>2. Создайте файл <code>.env</code> с переменными окружения</p>
                <p>3. Запустите сервер: <code>uvicorn app.main:app --reload</code></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# Информация о API
@app.get("/api/info")
async def get_api_info():
    return {
        "name": "FastAPI Site with Database",
        "version": "1.0.0",
        "description": "Пример сайта с CRUD операциями и аутентификацией",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Главная страница"},
            {"path": "/auth/login", "method": "POST", "description": "Авторизация"},
            {"path": "/users/", "method": "GET", "description": "Получить всех пользователей"},
            {"path": "/users/", "method": "POST", "description": "Создать пользователя"},
            {"path": "/users/{id}", "method": "GET", "description": "Получить пользователя по ID"},
            {"path": "/items/", "method": "GET", "description": "Получить все товары"},
            {"path": "/items/", "method": "POST", "description": "Создать товар"},
            {"path": "/docs", "method": "GET", "description": "Документация Swagger UI"},
        ]
    }

# Проверка здоровья
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Проверяем соединение с БД
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)