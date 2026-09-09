from sqlalchemy import Column,Integer,String,DateTime,Boolean,ForeignKey,JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base

#overarching story which contain the metadata as a whole
class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer,primary_key=True,index=True)
    session_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    nodes = relationship("StoryNode", back_populates="story")
    
#Then we have the storynode which contain all of the options
class StoryNode(Base):
    __tablename__ = "story_nodes"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), index=True)
    content = Column(String)
    is_root = Column(Boolean, default=False)
    is_ending = Column(Boolean, default=False)
    is_winning_ending = Column(Boolean, default=False)
    options = Column(JSON, default=list)

    story = relationship("Story", back_populates="nodes")