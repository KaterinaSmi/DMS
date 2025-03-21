# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#
# from database.db_config import engine, Base, SessionLocal
# import mysql.connector
#
# from sqlalchemy.orm import Session
# from sqlalchemy import select, join, inspect
#
# from models.models import (Project, Book, Document, DocumentDetail,
#                            SectionRelation, ProjectSection, ProjectSubSection)
#
#
# def get_project_details(project_id: int):
#     """Fetch all necessary details for a project, including dynamic DocumentDetail fields."""
#     session = SessionLocal()
#
#     try:
#         # Get all columns dynamically from DocumentDetail
#         document_detail_columns = [column.name for column in inspect(DocumentDetail).columns]
#         document_detail_columns_objs = [getattr(DocumentDetail, col) for col in document_detail_columns]
#
#         query = (
#             session.query(
#                 Project.name.label("project_name"),
#                 Book.id.label("book_id"),
#                 Book.name.label("book_name"),
#                 Document.title.label("title"),
#                 Document.name.label("doc"),
#                 Document.revision.label("cur_rev"),
#                 Document.description.label("description"),
#                 Document.state.label("state"),
#                 Document.owner.label("owner"),
#                 Document.releasedate.label("release_date"),
#                 Document.author.label("author"),
#                 Document.approveddate.label("approved_date"),
#                 Document.releasetype.label("release_type"),
#                 ProjectSection.section_name.label("section"),
#                 ProjectSubSection.subsection_name.label("subsection"),
#                 SectionRelation.relation_order,
#                 *document_detail_columns_objs  # Add all DocumentDetail columns dynamically
#             )
#             .join(Book, Book.project_id == Project.id)
#             .join(Document, Document.book_id == Book.id)
#             .join(DocumentDetail, DocumentDetail.document_id == Document.id)
#             .join(SectionRelation, SectionRelation.relation_id == DocumentDetail.relation_id)
#             .join(ProjectSection, ProjectSection.section_id == SectionRelation.section_id)
#             .join(ProjectSubSection, ProjectSubSection.subsection_id == SectionRelation.subsection_id)
#             .filter(Project.id == project_id)
#             .order_by(SectionRelation.relation_order)
#         )
#
#         results = query.all()
#
#         # Prepare the placeholders
#         project_data = {}
#         books_data = {}
#         document_details = []
#
#         for row in results:
#             row_dict = dict(row._mapping) #Allows access rows data as dictionary.
#
#             # Save Project Data (only once)
#             if not project_data:
#                 project_data["project_name"] = row_dict["project_name"]
#
#             # Save Books Data
#             book_id = row_dict["book_id"]
#             if book_id not in books_data:
#                 books_data[book_id] = {
#                     "book_name": row_dict["book_name"],
#                     "documents": []
#                 }
#
#             # Save Document Data
#             document_data = {
#                 "title": row_dict["title"],
#                 "doc": row_dict["doc"],
#                 "cur_rev": row_dict["cur_rev"],
#                 "description": row_dict["description"],
#                 "state": row_dict["state"],
#                 "owner": row_dict["owner"],
#                 "release_date": row_dict["release_date"],
#                 "author": row_dict["author"],
#                 "approved_date": row_dict["approved_date"],
#                 "release_type": row_dict["release_type"],
#                 "section": row_dict["section"],
#                 "subsection": row_dict["subsection"],
#                 "relation_order": row_dict["relation_order"]
#             }
#             books_data[book_id]["documents"].append(document_data)
#
#             # Save Document Details
#             document_detail_data = {key: value for key, value in row_dict.items() if key in document_detail_columns}
#             document_details.append(document_detail_data)
#
#             # Combine all data in a structured format
#         structured_data = {
#             "project": project_data,
#             "books": books_data,
#             "document_details": document_details
#         }
#
#         return structured_data
#
#     finally:
#         session.close()
#
# if __name__ == "__main__":
#     project_id = 1  # Replace with your actual project_id
#     data = get_project_details(project_id)
#     import json
#     print(json.dumps(data, indent=4, default=str))
