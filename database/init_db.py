from .db_config import engine, Base, SessionLocal
from models.models import Project, Book, Document, DocumentDetail



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
