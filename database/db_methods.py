from sqlalchemy.orm import Session
from models.models import Project, Book, Document, DocumentDetail

from .db_config import SessionLocal

def get_all_project_names():
    """Fetch all project names from the database."""
    session = SessionLocal()
    projects = session.query(Project.id, Project.name).all()
    session.close()
    return {project.name: project.id for project in projects}  # Extract names from tuples

def get_project_by_name(name):
    """Fetch a specific project by name."""
    session = SessionLocal()
    project = session.query(Project).filter(Project.name == name).first()
    session.close()
    return project

def get_project_by_id(project_id):
    """Fetch a specific project by its ID."""
    session = SessionLocal()
    project = session.query(Project).filter(Project.id == project_id).first()
    session.close()
    return project


def get_books_by_project(project_id):
    """Fetches books by project ID"""
    session = SessionLocal()
    book_list = session.query(Book).filter(Book.project_id == project_id).all()
    session.close()
    return book_list