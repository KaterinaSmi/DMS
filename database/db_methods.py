
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from models.models import Project, Book, Document, DocumentDetail, ProjectSection, ProjectSubSection, SectionRelation

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

def get_documents_by_book(book_id):
    """Fetches documents by books"""
    session = SessionLocal()
    document_list = session.query(Document).filter(Document.book_id == book_id).all()
    session.close()
    return document_list

def get_sections_by_project(project_id):
    """Fetches section names by project ID."""
    session = SessionLocal()
    try:
        # Query to join SectionRelation and ProjectSection to get section names
        sections = session.query(SectionRelation).join(ProjectSection, SectionRelation.section_id == ProjectSection.section_id)\
            .filter(SectionRelation.project_id == project_id)\
            .all()

        if sections:
            section_list = []
            for section_relation in sections:
                section_name = section_relation.section.section_name  # Accessing the section name from the related table
                section_list.append({
                    "section_id": section_relation.section_id,
                    "section_name": section_name
                })
            return section_list
        else:
            print("No sections found for the given project ID.")
            return []
    except Exception as e:
        print(f"Error fetching sections: {e}")
        return []
    finally:
        session.close()

def get_subsections_by_project(project_id):
    """Fetches section names by project ID."""
    session = SessionLocal()
    try:
        # Query to join SectionRelation and ProjectSection to get section names
        subsections = session.query(SectionRelation).join(ProjectSection, SectionRelation.subsection_id == ProjectSection.subsection_id)\
            .filter(SectionRelation.project_id == project_id)\
            .all()

        if subsections:
            subsection_list = []
            for subsection_relation in subsections:
                subsection_name = subsection_relation.section.section_name  # Accessing the section name from the related table
                subsection_list.append({
                    "section_id": subsection_relation.section_id,
                    "section_name": subsection_name
                })
            return subsection_list
        else:
            print("No subsections found for the given project ID.")
            return []
    except Exception as e:
        print(f"Error fetching sections: {e}")
        return []
    finally:
        session.close()



def get_document_detail_columns():
    """Fetch all column names from tbldocument_detail dynamically."""
    inspector = inspect(DocumentDetail)
    return [column.name for column in inspector.columns]


def get_project_details(project_id: int, selected_documents: dict):
    """Fetch details for a project only for selected documents."""
    session = SessionLocal()

    try:
        # Prepare a list of document IDs to filter
        selected_doc_ids = []
        for book_data in selected_documents.values():
            for document in book_data["documents"]:
                selected_doc_ids.append(document.id)  # Use .id because it's a Document object

        # Fetching Project, Books, Documents, Sections, and Subsections
        query = (
            session.query(
                Project.name.label("project_name"),
                Book.id.label("book_id"),
                Book.name.label("book_name"),
                Document.id.label("document_id"),
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
                SectionRelation.relation_order
            )
            .join(Book, Book.project_id == Project.id)
            .join(Document, Document.book_id == Book.id)
            .join(SectionRelation, SectionRelation.relation_id == Document.id)
            .join(ProjectSection, ProjectSection.section_id == SectionRelation.section_id)
            .join(ProjectSubSection, ProjectSubSection.subsection_id == SectionRelation.subsection_id)
            .filter(Project.id == project_id)
            .filter(Document.id.in_(selected_doc_ids))  # Filter only selected documents
            .order_by(SectionRelation.relation_order)
        )

        results = query.all()

        # Prepare the placeholders
        project_data = {}
        books_data = {}

        for row in results:
            row_dict = dict(row._mapping)  # Allows access rows data as dictionary.

            # Save Project Data (only once)
            if not project_data:
                project_data["project_name"] = row_dict["project_name"]

            # Save Books Data
            book_id = row_dict["book_id"]
            if book_id not in books_data:
                books_data[book_id] = {
                    "book_name": row_dict["book_name"],
                    "documents": []
                }

            # Save Document Data
            document_data = {
                "document_id": row_dict["document_id"],
                "title": row_dict["title"],
                "doc": row_dict["doc"],
                "cur_rev": row_dict["cur_rev"],
                "description": row_dict["description"],
                "state": row_dict["state"],
                "owner": row_dict["owner"],
                "release_date": row_dict["release_date"],
                "author": row_dict["author"],
                "approved_date": row_dict["approved_date"],
                "release_type": row_dict["release_type"],
                "section": row_dict["section"],
                "subsection": row_dict["subsection"],
                "relation_order": row_dict["relation_order"]
            }
            books_data[book_id]["documents"].append(document_data)

        # Combine all data in a structured format
        structured_data = {
            "project": project_data,
            "books": books_data,
        }

        return structured_data

    finally:
        session.close()



def get_document_details(project_id: int, book_id: int, document_id: int):
    """Fetch all document details related to a specific project, book, and document."""
    session = SessionLocal()

    try:
        document_detail_columns = get_document_detail_columns()
        document_detail_columns_objs = [getattr(DocumentDetail, col) for col in document_detail_columns]

        query = (
            session.query(*document_detail_columns_objs)
            .join(Document, DocumentDetail.document_id == Document.id)
            .join(Book, Document.book_id == Book.id)
            .filter(Book.project_id == project_id)
            .filter(Book.id == book_id)
            .filter(Document.id == document_id)
        )

        results = query.all()

        document_details = []
        for row in results:
            row_dict = dict(row._mapping)
            document_details.append(row_dict)

        return document_details  # Returns a list of document details

    finally:
        session.close()

