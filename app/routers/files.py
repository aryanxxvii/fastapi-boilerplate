from fastapi import APIRouter
from .auth import get_current_user
from fastapi import UploadFile, File,HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from ..database import get_db
import uuid
from ..models import File

files_router = APIRouter()

@files_router.post("/upload")
async def upload_file(file: UploadFile, username: str = Depends(get_current_user), db = Depends(get_db)):
    try:
        contents = await file.read()
        
        filename = str(uuid.uuid4())
        with open(f"./uploads/{filename}", "+wb") as f:
            f.write(contents)

        db_file = File(filename=filename, uploaded_by=username)
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return JSONResponse(content={"message": "File uploaded successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@files_router.get("/")
def get_files(username: str = Depends(get_current_user), db = Depends(get_db)):
    files = db.query(File).filter(File.uploaded_by == username).all()
    return files

@files_router.get("/{filename}")
def get_file(filename: str, username: str = Depends(get_current_user), db = Depends(get_db)):
    file = db.query(File).filter(File.filename == filename).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = "./uploads/" + file.filename
    
    try:
        return FileResponse(
            path=file_path,
            filename=file.filename, # If you stored the original filename
            media_type='application/octet-stream'  # Uncomment to force download
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="File not found")
    
@files_router.delete("/{filename}")
def delete_file(filename: str, username: str = Depends(get_current_user), db = Depends(get_db)):
    file = db.query(File).filter(File.filename == filename).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.uploaded_by != username:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this file")
    
    db.delete(file)
    db.commit()

    return {"message": "File deleted successfully"}