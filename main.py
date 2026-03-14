import os
import asyncio
import traceback
import uuid
import multiprocessing as mp
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from reportes import build_daily_report, build_monthly_report 

from db import get_conn



try:
    mp.set_start_method("spawn",force=True)
except RuntimeError:
    pass

app = FastAPI(title="Reporte de ventas")
manager = mp.Manager()
JOBS :Dict[str,Any]= manager.dict()

DEBUG_AWAIT = float(os.getenv("debug espera","2.0"))



class Daily_Request(BaseModel):
    start_date: str = Field(..., description="YYYY-MM-DD o YYYY-MM-DD HH:MM:SS")
    end_date: str = Field(..., description="YYYY-MM-DD o YYYY-MM-DD HH:MM:SS (exclusive recomendado)")
    debug_wait: bool = Field(True, description="await para poder ver/adjuntar al PID antes de que procese")



class Monthly_Request(BaseModel):
    year:int
    month: int=Field(...,ge=1,le=12)# parmetros entre 1 al 12
    debug_wait:bool = Field(True)



def _run_job(job_id:str,kind:str,payload:dict):
    """
    Se ejecuta el proceso y se liga a un PID
    """
    try:
        pid= os.getpid()
        JOBS[job_id]={"estatus":"Running",
                      "pid":pid,"kind":kind}
        
        if kind== "daily":
            res= build_daily_report(payload["start_date"],payload["end_date"])
        elif kind =="monthly":
             res= build_monthly_report(payload["year"],payload["month"])
        else:
            raise ValueError("kind invalido")
        
        # Guardar resultado
        JOBS[job_id]={
            "status":"completed",
            "pid":pid,
            "kind":kind,
            "result": res
        }
    except Exception as e:
        JOBS[job_id]={
            "status":"error",
            "pid":os.getpid(),
            "kind":kind ,
            "error":str(e),
            "trace":traceback.format_exc()
        }

@app.post("/reports/daily")
async def create_daily(req:Daily_Request):
    #uuid universal unique identifiers (inmutable)
    job_id = uuid.uuid4().hex
    JOBS[job_id]={
        "status":"quit",
        "pid":None,
        "kind":"daily"
    }

    p = mp.Process(
        target=_run_job,
        args=(job_id, "daily",{"start_date":req.start_date, "end_date":req.end_date}),
        daemon=False,
        name = f"daily_report_{job_id[:8]}",
        )
    

    p.start()
    pid = p.pid
    JOBS[job_id]= {"status":"running","pid":pid,"kind":"daily"}

    #debug para ver el pid

    if req.debug_wait:
        await asyncio.sleep(DEBUG_AWAIT)
    return {"job_id":job_id, "pid":pid, "status":"running"}




@app.post("/reports/monthly")
async def create_monthly(req:Monthly_Request):
    #uuid universal unique identifiers (inmutable)
    job_id = uuid.uuid4().hex
    JOBS[job_id]={
        "status":"quit",
        "pid":None,
        "kind":"month"
    }

    p = mp.Process(
        target=_run_job,
        args=(job_id, "monthly",{"year":req.year, "month":req.month}),
        daemon=False,
        name = f"monthly_report_{job_id[:8]}",
        )
    

    p.start()
    pid = p.pid
    JOBS[job_id]= {"status":"running","pid":pid,"kind":"monthly"}

    #debug para ver el pid

    if req.debug_wait:
        await asyncio.sleep(DEBUG_AWAIT)
    return {"job_id":job_id, "pid":pid, "status":"running"}





@app.get("/reports/{job_id}/status")
async def report_status(job_id:str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404,detail="no existe el trabajo job_id")
    return dict(job)


@app.get("/reports/{job_id}/result")
async def get_report_result(job_id:str):
    """
    Obtener resultado del reporte cuando esté listo
    """
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    
    if job.get("status") == "running":
        raise HTTPException(status_code=202, detail="El reporte aún se está procesando")
    
    if job.get("status") == "error":
        raise HTTPException(status_code=500, detail=f"Error: {job.get('error')}")
    
    # Retornar resultado si está disponible
    result = job.get("result")
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Resultado no disponible aún")