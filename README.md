# Geo-Spatial RAG Real Estate Agent

An AI-powered location-aware real estate search system that understands natural language queries and returns relevant properties using Geo-Spatial filtering + Vector Search + RAG

#  What it does --

Supports queries like:
“2 BHK flats under 80 lakh within 3 km of Andheri West, with gym.”

The system:
Understands user intent
Filters by location and distance
Ranks results semantically
Explains results in natural language


# Project Flow (What Actually Happens)

This project allows users to search for real estate properties using natural language queries. A user can type queries like “2 BHK flat under 80 lakh in Andheri West with gym” through the UI or directly via the API. The backend receives this query and first checks whether it is related to real estate and whether the selected location matches the city mentioned in the query. Currently, the system supports Mumbai only, because the dataset used is a Mumbai real estate dataset sourced from Kaggle.

Before users can search, the dataset is ingested offline using a script. During ingestion, property data from the CSV file is read, locations are converted into latitude and longitude using geocoding, text descriptions are converted into vector embeddings, and everything is stored in Qdrant, a vector database. At the same time, the geographic bounds of the dataset are saved so the system knows which locations are supported.

When a user sends a query, the system geocodes the user’s location (for example, “Andheri West”) into coordinates, converts the query into a vector, and performs a geo-spatial + vector similarity search in Qdrant. The results are then softly ranked based on preferences like BHK, budget, and amenities. Finally, an LLM generates a natural-language explanation describing why these properties were selected, and the response is returned to the user.

Remmember the files like auth_service.py contains the code for future implementation which is currently not used in the project you can choose to ignore it . Also same is the case with relevance.py .

# ⭐Project Structure & Responsibilities⭐

real_estate_geo_rag/
│
├── main.py
│   └── Creates FastAPI app and registers routes
│
├── api/
│   ├── query.py            # ⭐ MAIN CONTROLLER
│   │   ├── /api/ask endpoint
│   │   ├── Guard checks (intent, city, dataset)
│   │   └── Orchestrates all services
│   │
│   └── ingest.py
│       └── Guard endpoint for ingestion
│
├── services/
│   ├── query_parser.py     # ⭐ CRITICAL LOGIC
│   │   ├── parse_query()        → extract bhk, price, amenities
│   │   └── parse_max_price()
│   │
│   ├── geocoding.py
│   │   └── geocode()            → location → coordinates
│   │
│   ├── embedding.py
│   │   └── embed()              → text → vector embedding
│   │
│   ├── llm_explainer.py
│   │   └── explain_results()    → RAG-based explanation
│   │
│   ├── dataset_scope.py
│   │   └── is_inside_dataset()  → geo-bound check
│   │
│   └── logger.py
│       └── get_logger()          → centralized logging
│
├── db/
│   └── vector_db.py         # ⭐ SEARCH ENGINE
│       ├── insert()             → store vectors
│       └── geo_vector_search()  → geo + semantic search
│
├── models/
│   ├── query_schema.py
│   │   └── UserQuery            → API input schema
│   │
│   └── property.py
│       └── Property             → property data model
│
├── scripts/
│   └── ingest_dataset.py
│       ├── Reads CSV dataset
│       ├── Geocodes locations
│       ├── Generates embeddings
│       ├── Inserts into Qdrant
│       └── Saves dataset bounds
│
├── tests/
│   ├── test_query_api.py
│   ├── test_query_parser.py
│   └── test_ingest_api.py
│
├── frontend.py
│   └── Streamlit UI (optional)
│
├── .env
│   └── Environment configuration
│
├── requirements.txt
└── pytest.ini

            
# ⭐Key Files You Should Read First ⭐

1️⃣ api/query.py
→ Full request lifecycle & business flow

2️⃣ services/query_parser.py
→ Core intent extraction logic

3️⃣ db/vector_db.py
→ Geo-spatial + vector search

4️⃣ scripts/ingest_dataset.py


# ⭐ PROJECT ARCHITECTURE ⭐
            ┌──────────────┐
            │   User / UI  │
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │ FastAPI API  │
            │   /api/ask  │
            └──────┬───────┘
                   │
    ┌──────────────┼──────────────────────────┐
    ▼              ▼                          ▼
Query Parsing   Geocoding                  Embedding
 (regex)       (lat / lon)               (vector)
    │              │                          │
    └──────────────┼──────────────────────────┘
                   ▼
         Geo + Vector Search (Qdrant)
                   │
                   ▼
         Soft Filtering & Scoring
                   │
                   ▼
          LLM Explanation (RAG)
                   │
                   ▼
           Final JSON Response

            
 # ⭐ INSTRUCTION TO RUN MY PROJECT ⭐ 

Follow these steps to run the Geo-Spatial RAG Real Estate Agent locally.

# Prerequisites
Make sure you have the following installed:
Python 3.10+
Git
Ollama (for LLM explanations)
Internet connection (for geocoding during ingestion)

# 1️⃣ Clone the Repository
-git clone <your-repo-url>
-cd real_estate_geo_rag

# 2️⃣ Create and Activate Virtual Environment
for Windows
-python -m venv venv
-venv\Scripts\activate

for macOS / Linux
-python3 -m venv venv
-source venv/bin/activate

You should now see (venv) in your terminal.

# 3️⃣ Install Dependencies
-pip install -r requirements.txt
This installs FastAPI, Qdrant client, sentence-transformers, Streamlit, pytest, and other required libraries.

# 4️⃣ Setup Environment Variables
Create a .env file in the project root and add:
# App
APP_ENV=development
LOG_LEVEL=DEBUG
# Dataset
SUPPORTED_CITY=mumbai
# Qdrant
QDRANT_PATH=qdrant_data
QDRANT_COLLECTION=properties
# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

These values control:
Which city is supported
Where Qdrant data is stored
Which embedding model is used

# 5️⃣ Prepare Dataset (One-Time Step)
The project uses a Mumbai real estate dataset from Kaggle.
Place dataset
Make sure the CSV file exists at:
-data/raw/Mumbai1.csv

# 6️⃣ Ingest Dataset into Vector Database
This is a one-time operation.

-python scripts/ingest_dataset.py

What this command does:
Reads the CSV dataset
Geocodes each property location
Generates vector embeddings
Stores data in Qdrant
Saves dataset geographic bounds

You should see logs like:
-Ingested 500 properties successfully
-Dataset geographic bounds saved

# 7️⃣ Start the Backend API Server
-uvicorn main:app --reload

If successful, you’ll see:
Uvicorn running on http://127.0.0.1:8000

Test backend health
Open browser:
http://127.0.0.1:8000

Expected response:
{"status":"running"}

# 8️⃣ (Optional) Run Frontend UI
The project includes a Streamlit UI.
-streamlit run frontend.py

This opens a browser UI where you can:
Enter natural language queries
Apply filters
View results and explanations

# 9️⃣ Run Tests (Optional but Recommended)
-pytest

Generate Coverage Report
-pytest --cov=. --cov-report=html

Open:
htmlcov/index.html

Example Query to Try:
"2 bhk flat under 80 lakh in Andheri West with gym"

        
      