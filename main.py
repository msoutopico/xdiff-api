#!/usr/bin/env python 
 
# main.py

from datetime import date, datetime
from fastapi import FastAPI, HTTPException
from mongita import MongitaClientDisk
from typing import Dict, List
from pydantic import BaseModel, conint
from pyexpat import model


class OmegatProps(BaseModel):
    project_name: str
    source_lang: str
    target_lang: str
    segmentation: bool

class Segment(BaseModel):
    segment_number: int
    file_name: str
    source_text: str 
    target_text: str
    original_mt: str
    repetition: bool
    alternative: bool
    created_by: str
    created_on: datetime
    changed_by: str
    changed_on: datetime
    note: str

class Segments(BaseModel):
    segments: list = [Segment]

class Report(BaseModel):
    report_id: str
    props: OmegatProps
    # props: Dict[str, str] = {}
    segments: List[Segment]


app = FastAPI()

client = MongitaClientDisk()
db = client.xdiff_db
reports = db.reports
# client.drop_database('db')
# client.drop_database('xdiff_db')


  
@app.get("/")
async def root():
    return {"message": "Hello world!"}

@app.get("/reports")
async def get_reports():
    existing_reports = reports.find({})
    return [
        {key: report[key] for key in report if key != "_id"}
        for report in existing_reports
    ]

@app.get("/reports/{report_id}")
async def get_report_by_id(report_id: str):
    if reports.count_documents({"report_id": report_id}) > 0:
        report = reports.find_one({"report_id": report_id})
        return {key: report[key] for key in report if key != "_id"}
    raise HTTPException(status_code=404, detail=f"No report with id {report_id} found.")

@app.post("/reports")
async def post_report(report: Report):
    reports.insert_one(report.dict())
    return report

@app.put("/reports/{report_id}")
async def update_report(report_id: str, report: Report):
    reports.replace_one({"report_id": report_id}, report.dict(), upsert=True)
    return report
    # return URL of the report !!! 

@app.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    delete_result = reports.delete_many({"id": report_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"No report with id {report_id} exists.")
    return {"OK": True}

@app.get("/sub")
async def call_another_func():
    x = root()
    return x
# authentication (basic auth?)
# query parameters
# web sockets???
# capps.capstan.be/api/xdiff
# add user id to props ??+
# drop mongita and upgrade to mongo?

# project_name is fine as id? or hash would be better? 