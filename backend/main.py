from fastapi import FastAPI 
 
app = FastAPI(title="体育用品批发销售信息系统") 
 
@app.get("/") 
def root(): 
    return {"message": "体育用品销售信息系统 API"} 
