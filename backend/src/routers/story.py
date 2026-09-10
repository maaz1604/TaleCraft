import uuid
from typing import Optional,Annotated,cast
from datetime import datetime
from fastapi import APIRouter,FastAPI,Depends,HTTPException,Cookie,Response,BackgroundTasks
from sqlalchemy.orm import Session

from db.database import get_db,SessionLocal
from models.story import Story,StoryNode
from models.job import StoryJob
from schemas.story import (
    CompleteStoryNodeResponse,CompleteStoryResponse,CreateStoryRequest
)
from schemas.job import StoryJobResponse
from core.story_generator import StoryGenerator


router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)

def get_session_id(session_id:Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

@router.post("/create",response_model=StoryJobResponse)
def create_story(
    request:CreateStoryRequest,
    background_tasks:BackgroundTasks,
    response:Response,
    session_id:Annotated[str,Depends(get_session_id)],
    db:Annotated[Session,Depends(get_db)]
):
    response.set_cookie(key="session_id",value=session_id,httponly=True)
    job_id = str(uuid.uuid4())

    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,
        status="pending"
    )
    db.add(job)
    db.commit()
    
    background_tasks.add_task(
        generate_story_task,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id
    )
    
    return job

def generate_story_task(job_id: str, theme: str, session_id: str):
    db = SessionLocal()

    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

        if not job:
            return

        try:
            setattr(job, "status", "processing")
            db.commit()
            
            story = StoryGenerator.generate_story(db, session_id, theme)
            job.story_id= story.id
            setattr(job,"status","completed")
            job.completed_at = datetime.now()  # type: ignore
            db.commit()
        except Exception as e:
            job.status = "failed" # type: ignore
            job.completed_at = datetime.now() # type: ignore
            job.error = str(e) # type: ignore
            db.commit()
    finally:
        db.close()
        
@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Annotated[Session,Depends(get_db)]):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    complete_story = build_complete_story_tree(db,story)
    return complete_story

def build_complete_story_tree(db: Session, story: Story) -> CompleteStoryResponse: 
    nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()

    node_dict = {}
    for node in nodes:
        node_response = CompleteStoryNodeResponse(
            id=cast(int, node.id),
            content=node.content, # type: ignore
            is_ending=node.is_ending,# type: ignore
            is_winning_ending=node.is_winning_ending,# type: ignore
            options=node.options# type: ignore
        )
        node_dict[node.id] = node_response

    root_node = next((node for node in nodes if cast(bool, node.is_root)), None) 
    if not root_node:
        raise HTTPException(status_code=500, detail="Story root node not found")

    return CompleteStoryResponse(
        id=story.id,# type: ignore
        title= story.title,# type: ignore
        session_id=story.session_id,# type: ignore
        created_at=story.created_at,# type: ignore
        root_node=node_dict[root_node.id],
        all_nodes=node_dict
    )