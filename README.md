# ToDo и Short URL
Два независимых сервиса на FastAPI. Для хранения используется SQLite, таблицы создаются при запуске.

## Локальный запуск (PowerShell)
Из корня проекта:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r todo_app/requirements.txt
.\.venv\Scripts\python.exe -m uvicorn todo_app.main:app --port 8000
```
Во втором терминале из корня проекта:
```powershell
.\.venv\Scripts\python.exe -m uvicorn shorturl_app.main:app --port 8001
```
Документация: http://localhost:8000/docs и http://localhost:8001/docs.

## Docker
```powershell
docker build -t todo-service todo_app/
docker build -t shorturl-service shorturl_app/
docker volume create todo_data
docker volume create shorturl_data
docker run -d --name todo -p 8000:80 -v todo_data:/app/data todo-service
docker run -d --name shorturl -p 8001:80 -v shorturl_data:/app/data shorturl-service
```
В Swagger UI создайте задачу через POST /items (например, {"title":"Проверить проект"}), затем проверьте GET, PUT и DELETE. Для Short URL отправьте POST /shorten с {"url":"https://example.com/"}, проверьте /stats/{short_id} и переход по короткой ссылке.
Для проверки сохранности создайте записи, выполните `docker restart todo shorturl` и повторите GET. Для более строгой проверки удалите контейнеры командой `docker rm -f todo shorturl` и повторите команды docker run с теми же томами. Не удаляйте тома.

## Публикация
Создайте пустой публичный репозиторий GitHub, затем выполните git init, git add ., git commit -m "Initial project", git branch -M main, git remote add origin URL_РЕПОЗИТОРИЯ, git push -u origin main.
В Docker Hub создайте два публичных репозитория todo-service и shorturl-service. Замените LOGIN своим логином:
```powershell
docker login
docker tag todo-service LOGIN/todo-service:latest
docker tag shorturl-service LOGIN/shorturl-service:latest
docker push LOGIN/todo-service:latest
docker push LOGIN/shorturl-service:latest
```
