# Installation Instructions

## Python Dependencies

### Current Python Dependencies (Python 3.11.13)

#### Core AI and LangChain:
- langchain>=0.3.26
- langchain-core>=0.3.69
- langchain-openai>=0.3.28
- langgraph>=0.6.3

#### Data Processing:
- pandas>=2.3.1
- openpyxl>=3.1.5
- xlrd>=2.0.2

#### Document Processing:
- pypdf2>=3.0.1
- python-docx>=1.2.0

#### Additional Dependencies (used in Flask backend):
- Flask (for the web framework)
- Flask-CORS (for cross-origin requests)
- psycopg2-binary (for PostgreSQL database connection)

### Installation Methods

The project uses Python 3.11.13 and the dependencies are managed through the pyproject.toml file. If you need to install these dependencies locally, you can use:

#### Option 1: Manual Installation
```bash
pip install langchain>=0.3.26 langchain-core>=0.3.69 langchain-openai>=0.3.28 langgraph>=0.6.3 pandas>=2.3.1 openpyxl>=3.1.5 xlrd>=2.0.2 pypdf2>=3.0.1 python-docx>=1.2.0 flask flask-cors psycopg2-binary
```

#### Option 2: Using Project Configuration
```bash
pip install -e .
```

This will install all the dependencies specified in the pyproject.toml file.