Just a simple storage app using FastAPI to practice things like JWT auth, file uploads, and working with a SQL database.

### Features

- User Auth: Register and login with JWT tokens.
- File Management: Upload, list, fetch, and delete files.


### API Endpoints

- `POST /register`: Register a new user.
- `POST /login`: Login to get a JWT token.
- `POST /upload`: Upload a file.
- `GET /files`: List all your files.
- `GET /files/{file_id}`: Download a specific file.
- `DELETE /files/{file_id}`: Delete a file.

