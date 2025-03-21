from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from database.db_config import Base  # Import `Base`

class Project(Base):
    """Project model representing stored projects."""
    __tablename__ = 'tblproject'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    description = Column(String(1000), nullable=True)

    # A project has many books
    books = relationship("Book", back_populates="project", cascade="all, delete-orphan")
    section_relations = relationship("SectionRelation", back_populates="project", cascade="all, delete-orphan")
    document_details = relationship("DocumentDetail", back_populates="project", cascade="all, delete-orphan")  # <-- New relationship

class Book(Base):
    """Book model linked to Project."""
    __tablename__ = 'tblbooks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    description = Column(String(1000), nullable=True)
    project_id = Column(Integer, ForeignKey('tblproject.id', ondelete='CASCADE', onupdate='CASCADE'))

    # Relationships
    project = relationship("Project", back_populates="books")
    documents = relationship("Document", back_populates="book", cascade="all, delete-orphan")


class Document(Base):
    """Document model linked to Book."""
    __tablename__ = 'tbldocuments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    title = Column(String(1000))
    description = Column(String(1000))
    owner = Column(String(255))
    revision = Column(String(1000))
    state = Column(String(100))
    releasedate = Column(Date)
    author = Column(String(255))
    approveddate = Column(Date)
    createdon = Column(Date)
    releasetype = Column(String(255))
    book_id = Column(Integer, ForeignKey('tblbooks.id', ondelete='CASCADE', onupdate='CASCADE'))

    # Relationships
    book = relationship("Book", back_populates="documents")
    document_details = relationship("DocumentDetail", back_populates="document", cascade="all, delete-orphan")


class DocumentDetail(Base):
    """Model for tbldocument_detail"""
    __tablename__ = 'tbldocument_detail'

    document_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('tbldocuments.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    relation_id = Column(Integer, ForeignKey('tblsection_relation.relation_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    project_id = Column(Integer,ForeignKey('tblproject.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    active = Column(Integer, nullable=True)

    # Text fields (Optional fields)
    M0 = Column(Text, nullable=True)
    M1 = Column(Text, nullable=True)
    FDR1 = Column(Text, nullable=True)
    eFDR = Column(Text, nullable=True)
    sFDR1 = Column(Text, nullable=True)
    FDR2 = Column(Text, nullable=True)
    FDR8 = Column(Text, nullable=True)
    LP1 = Column(Text, nullable=True)
    LR = Column(Text, nullable=True)
    FDR3 = Column(Text, nullable=True)
    LR2 = Column(Text, nullable=True)
    LP2 = Column(Text, nullable=True)
    FDRE = Column(Text, nullable=True)
    SW31243 = Column(Text, nullable=True)
    FDR28450 = Column(Text, nullable=True)
    SW31286 = Column(Text, nullable=True)
    SW3XXX = Column(Text, nullable=True)
    SW3369 = Column(Text, nullable=True)
    SW3337 = Column(Text, nullable=True)
    SW33377 = Column(Text, nullable=True)
    SW33396 = Column(String(255), nullable=True)
    # Relationships
    document = relationship("Document", back_populates="document_details")
    section_relation = relationship("SectionRelation", back_populates="document_details")
    project = relationship("Project", back_populates="document_details")  # <-- Proper relationship


class ProjectSection(Base):
    """Sections within the project."""
    __tablename__ = 'tblproject_section'

    section_id = Column(Integer, primary_key=True, autoincrement=True)
    section_name = Column(String(255), nullable=False)
    section_desc = Column(Text, nullable=True)

    # Relationships
    subsections = relationship("ProjectSubSection", back_populates="section", cascade="all, delete-orphan")


class ProjectSubSection(Base):
    """Subsections under a section."""
    __tablename__ = 'tblproject_subsection'

    subsection_id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('tblproject_section.section_id', ondelete='CASCADE', onupdate='CASCADE'))
    subsection_name = Column(String(255), nullable=False)
    subsection_desc = Column(Text, nullable=True)

    # Relationships
    section = relationship("ProjectSection", back_populates="subsections")


class SectionRelation(Base):
    """Defines the relation between a document and its section & subsection."""
    __tablename__ = 'tblsection_relation'

    relation_id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('tblproject_section.section_id', ondelete='CASCADE', onupdate='CASCADE'))
    subsection_id = Column(Integer, ForeignKey('tblproject_subsection.subsection_id', ondelete='CASCADE', onupdate='CASCADE'))
    project_id = Column(Integer, ForeignKey('tblproject.id', ondelete='CASCADE', onupdate='CASCADE'))
    relation_order = Column(Integer, nullable=False)

    # Relationships
    project = relationship("Project")
    section = relationship("ProjectSection")
    subsection = relationship("ProjectSubSection")
    document_details = relationship("DocumentDetail", back_populates="section_relation")
