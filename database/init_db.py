from .db_config import engine, Base, SessionLocal
import mysql.connector

from sqlalchemy.orm import Session
from sqlalchemy import select, join
from models.models import (Project, Book, Document, DocumentDetail,
                           SectionRelation, ProjectSection, ProjectSubSection)


def get_project_details(project_id: int):
    """Fetch all necessary details for a project."""
    session = SessionLocal()

    try:
        query = (
            session.query(
                Project.name.label("project_name"),
                Book.name.label("book"),
                Document.title.label("title"),
                Document.name.label("doc"),
                Document.revision.label("cur_rev"),
                Document.description.label("description"),
                Document.state.label("state"),
                Document.owner.label("owner"),
                Document.releasedate.label("release_date"),
                Document.author.label("author"),
                Document.approveddate.label("approved_date"),
                Document.releasetype.label("release_type"),
                ProjectSection.section_name.label("section"),
                ProjectSubSection.subsection_name.label("subsection"),
                DocumentDetail.document_detail_id,
                DocumentDetail.document_id,
                Document.book_id,
                SectionRelation.relation_order
            )
            .join(Book, Book.project_id == Project.id)
            .join(Document, Document.book_id == Book.id)
            .join(DocumentDetail, DocumentDetail.document_id == Document.id)
            .join(SectionRelation, SectionRelation.relation_id == DocumentDetail.relation_id)
            .join(ProjectSection, ProjectSection.section_id == SectionRelation.section_id)
            .join(ProjectSubSection, ProjectSubSection.subsection_id == SectionRelation.subsection_id)
            .filter(Project.id == project_id)
            .order_by(SectionRelation.relation_order)
        )

        results = query.all()

        # Process results
        project_data = []
        for row in results:
            project_data.append({
                "project_name": row.project_name,
                "book": row.book,
                "title": row.title,
                "doc": row.doc,
                "cur_rev": row.cur_rev,
                "description": row.description,
                "state": row.state,
                "owner": row.owner,
                "release_date": row.release_date,
                "author": row.author,
                "approved_date": row.approved_date,
                "release_type": row.release_type,
                "section": row.section,
                "subsection": row.subsection,
                "document_detail_id": row.document_detail_id,
                "document_id": row.document_id,
                "book_id": row.book_id,
                "relation_order": row.relation_order
            })
        print(project_data)
        return project_data
    finally:
        session.close()

#Subsections
#JSON??

   # section_n

# Example Usage
# books = get_books_by_project(1)
# def init_db():
#     """Creates database tables if they don't exist."""
#     print(" Checking if tables exist...")
#     Base.metadata.create_all(bind=engine)
#     print(" Tables created (if missing).")
#
# #  Run this manually when needed
# if __name__ == "__main__":
#     init_db()
