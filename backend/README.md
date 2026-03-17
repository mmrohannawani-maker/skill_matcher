# Documentation for backend setup and usage

<img src="skill_matcher_architecture.png" alt="System Architecture" style="max-width: 100%; height: auto;">

# Developer Skill Intelligence AI Backend

An enterprise-grade FastAPI backend system designed for managing developer talent, automating skill matrices, and matching candidates to job descriptions. This project features a hybrid architecture combining deterministic Python logic with the **DeepSeek-V3 LLM** for intelligent data processing.

---

## 🏗 System Architecture

The Skill Matrix & Resource Finder system uses a modern, cloud-native modular design. Below is a structural representation of the data and request flow:

### Logical Zone Flow

| **Zone 1: Client Access** | **Zone 2: API Gateway** | **Zone 3: Core Processing** | **Zone 4: AI & Matching** |
| :--- | :--- | :--- | :--- |
| • Admin Portal<br>• Developer Dashboard<br>• Sales UI | **FastAPI Backend**<br>• Auth API<br>• Developer API<br>• Skill API<br>• JD Match API<br>• Reports API<br>• Excel API | • Auth Service<br>• Developer Service<br>• Skill Service<br>• JD Match Service<br>• Report Service<br>• Excel Service | **DeepSeek-V3 Engine**<br>• Extract Keywords<br>• Match JD Skills<br>• Calc Experience<br>• Calc Proficiency<br>• Rank Developers |

<br>

| **Zone 5: Data Storage** | **Zone 6: Batch Processing** | **Zone 7: Analytics** |
| :--- | :--- | :--- |
| **SQL Database**<br>• Users, Roles<br>• Developers, Skills<br>• DeveloperSkills<br>• JDSearches<br><br>**Blob Storage**<br>• Uploaded Excel<br>• PDF/Excel Reports | **Excel Pipeline**<br>1. Admin Uploads<br>2. Excel Processing Svc<br>3. Pandas Parsing<br>4. Data Validation<br>5. DB Insertion | **Reports Generated**<br>• Skill Availability<br>• Top Experts<br>• Resource Availability<br>• Skill Gap<br>• Org Summary |

---



---



## 🌟 Key AI Enhancements
This system integrates the **DeepSeek-V3 model** via HuggingFace to add intelligence to traditional CRUD operations:

* **Skill Normalization:** Automatically standardizes tech names (e.g., "python3" → "Python").
* **Semantic Matching:** Identifies that "ReactJS" and "React" are identical during scoring.
* **Security Intelligence:** Analyzes login/registration patterns to identify suspicious or brute-force behavior.
* **Automated Insights:** Generates executive-level trend reports and developer profile summaries.
* **JD Inference:** Automatically detects years of experience and hidden requirements within raw job descriptions.

---

## 🏗 Project Architecture
The backend follows a strict **Layered Modular Design** to ensure scalability and ease of debugging:

* **Routers:** API endpoints handling HTTP requests and responses.
* **Services:** Business logic layer where LLM and database operations are coordinated.
* **Core:** Security utilities (JWT, Hashing) and FastAPI dependencies.
* **Utils:** Pure algorithmic engines for JD matching and scoring.
* **Database:** SQLAlchemy models and connection management.



---

## 📁 File Structure
```text
backend/
├── app/
│   ├── core/               # Security (JWT, bcrypt) & Dependencies
│   ├── database/           # SQLite/SQLAlchemy connection & Base models
│   ├── models/             # Database ORM Tables (User, Dev, Skill, JD)
│   ├── schemas/            # Pydantic data validation models
│   ├── services/           # AI-Integrated Business Logic
│   ├── routers/            # API Route definitions
│   ├── utils/              # Scoring and Matching algorithms
│   ├── config.py           # Environment & App configuration
│   └── main.py             # Entry point & App bootstrap
├── .env                    # Environment variables (Secrets)
└── requirements.txt        # Python dependencies

```

## 🚀 Getting Started
1. InstallationEnsure you have Python 3.9+ installed. Install the required packages:
```
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] 
passlib[bcrypt] python-dotenv langchain-huggingface 
huggingface_hub spacy pandas openpyxl
```
Download the spaCy NLP model:
```
python -m spacy download en_core_web_sm
```
## 2. Configuration

Create a .env file in the project root:
```
Code snippetDATABASE_URL=sqlite:///./app.db
SECRET_KEY=generate_a_secure_hex_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
HUGGINGFACEHUB_API_TOKEN=your_huggingface_api_token
```
## 3. Running the Server
```
uvicorn app.main:app --reload
```
The API documentation will be available at :
```
Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc🚦 
```
## Core API Endpoints

| Tag | Method | Path | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | POST | `/auth/register` | User signup with AI security risk check |
| **Auth** | POST | `/auth/login` | Secure login and JWT generation |
| **Developers** | GET/POST | `/developers` | Manage developer profiles |
| **Skills** | POST | `/skills` | Add skills with AI-powered normalization |
| **JD Match** | POST | `/jd/analyze` | AI analysis of JDs against the developer pool |
| **Excel** | POST | `/excel/upload` | Bulk ingestion with AI data cleaning |
| **Reports** | GET | `/reports/summary` | Organization analytics & AI trend insights |


## 🧪 Scoring Logic

The system evaluates matches using a multidimensional scoring engine:

1. **Skill Match:** 17 points max per skill (10 for proficiency + 7 for experience).

2. **Semantic Mapping:** Uses AI to ensure variations in tech names don't penalize scores.

3. **Penalty:** -5 points for every missing critical skill identified by the AI.

4. **Percentage:** Normalized score from 0-100% with a human-readable AI explanation.

## 🛡 Security & Best Practices

1. **JWT Authentication:** All private routes are protected via Bearer tokens.

2. **Password Hashing:** Passwords never stored in plain text; hashed with bcrypt.

3. **Error Handling:** Global try-except blocks in routers ensure clean API responses.

4. **Debug Logging:** Traceable logs in every layer ([CONFIG DEBUG], [AUTH ROUTER], etc.).

