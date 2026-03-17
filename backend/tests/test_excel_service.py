# test_excel_service.py
"""
Comprehensive test script for excel_service.py
Run with: python test_excel_service.py
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import service and models
from app.services.excel_service import (
    load_excel_file,
    identify_skill_columns,
    create_or_get_skill,
    create_or_get_developer,
    process_excel_data,
    ai_normalize_skill_name,
    ai_extract_skills_from_text,
    ai_infer_developer_role,
    ai_analyze_row_quality,
    ai_detect_duplicate_developer,
    debug_log,
    llm
)
from app.models.developer_model import Developer
from app.models.skill_model import Skill
from app.models.developer_skill_model import DeveloperSkill
from app.database.connection import Base

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()  # Looks for .env file in current directory

# Verify token is loaded
print(f"Token loaded: {'Yes' if os.getenv('HUGGINGFACEHUB_API_TOKEN') else 'No'}")

class TestExcelService(unittest.TestCase):
    """Test suite for Excel service functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database"""
        # Use in-memory SQLite for testing
        cls.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine)
        
    def setUp(self):
        """Create a new session for each test"""
        self.db = self.SessionLocal()
        self.test_file = None
        
    def tearDown(self):
        """Clean up after each test"""
        self.db.rollback()
        self.db.close()
        
        # Remove test file if created
        if self.test_file and os.path.exists(self.test_file):
            os.unlink(self.test_file)

    def setUp(self):
        """Create a new session and clean database for each test"""
        # Clear all tables before each test
        self.db = self.SessionLocal()
        self.db.query(DeveloperSkill).delete()
        self.db.query(Developer).delete() 
        self.db.query(Skill).delete()
        self.db.commit()
    
        self.test_file = None
    
    def create_test_excel(self, data: list, filename: str = "test_skills.xlsx") -> str:
        """Helper to create test Excel files"""
        df = pd.DataFrame(data)
        self.test_file = filename
        df.to_excel(filename, index=False)
        return filename
    
    # ========== TEST 1: Basic Excel Loading ==========
    def test_load_excel_file(self):
        """Test loading Excel file into DataFrame"""
        test_data = [
            {"Name": "John Doe", "Email": "john@example.com", "Python": 5}
        ]
        file_path = self.create_test_excel(test_data)
        
        df = load_excel_file(file_path)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["Name"], "John Doe")
    
    # ========== TEST 2: Skill Column Identification ==========
    def test_identify_skill_columns(self):
        """Test identifying which columns are skills"""
        test_data = [
            {
                "timestamp": "2024-01-01",
                "name": "John Doe", 
                "email": "john@example.com",
                "department": "Engineering",
                "role": "Developer",
                "Python": 5,
                "JavaScript": 4,
                "AWS": 3
            }
        ]
        df = pd.DataFrame(test_data)
        
        skill_columns = identify_skill_columns(df)
        
        # Should identify Python, JavaScript, AWS as skills
        self.assertIn("Python", skill_columns)
        self.assertIn("JavaScript", skill_columns)
        self.assertIn("AWS", skill_columns)
        self.assertNotIn("name", [c.lower() for c in skill_columns])
    
    # ========== TEST 3: Create or Get Skill ==========
    def test_create_or_get_skill(self):
        """Test skill creation and retrieval"""
        # Test creating new skill
        skill1 = create_or_get_skill(self.db, "Python")
        self.assertIsNotNone(skill1)
        self.assertEqual(skill1.skill_name, "python")  # Normalized to lowercase
        
        # Test retrieving existing skill
        skill2 = create_or_get_skill(self.db, "Python")
        self.assertEqual(skill1.id, skill2.id)
        
        # Verify only one skill in database
        count = self.db.query(Skill).count()
        self.assertEqual(count, 1)
    
    # ========== TEST 4: Create or Get Developer ==========
    def test_create_or_get_developer(self):
        """Test developer creation and retrieval"""
        # Test creating new developer
        dev1 = create_or_get_developer(
            self.db, 
            name="John Doe",
            email="john@example.com",
            department="Engineering",
            role="Developer"
        )
        self.assertIsNotNone(dev1)
        self.assertEqual(dev1.email, "john@example.com")
        
        # Test retrieving existing developer
        dev2 = create_or_get_developer(
            self.db,
            name="John Doe Updated",
            email="john@example.com", 
            department="Engineering",
            role="Senior Developer"
        )
        self.assertEqual(dev1.id, dev2.id)
        
        # Verify only one developer in database
        count = self.db.query(Developer).count()
        self.assertEqual(count, 1)
    
    # ========== TEST 5: Complete Excel Processing ==========
    def test_process_excel_data_complete(self):
        """Test complete Excel processing with multiple rows"""
        test_data = [
            {
                "Full name": "Alice Smith",
                "Email address": "alice@example.com",
                "Department": "Engineering",
                "Role": "Frontend Dev",
                "Python": 4,
                "JavaScript": 5,
                "React": 3
            },
            {
                "Full name": "Bob Johnson", 
                "Email address": "bob@example.com",
                "Department": "Engineering",
                "Role": "Backend Dev",
                "Python": 5,
                "AWS": 4,
                "Docker": 3
            }
        ]
        
        file_path = self.create_test_excel(test_data)
        stats = process_excel_data(file_path, self.db)
        
        # Verify stats
        self.assertEqual(stats["rows_processed"], 2)
        self.assertEqual(stats["developers_created"], 2)
        self.assertEqual(stats["skills_mapped"], 6)  # 3 skills per developer
        
        # Verify database contents
        developers = self.db.query(Developer).all()
        self.assertEqual(len(developers), 2)
        
        skills = self.db.query(Skill).all()
        self.assertEqual(len(skills), 5)  # Python, JavaScript, React, AWS, Docker
        
        mappings = self.db.query(DeveloperSkill).all()
        self.assertEqual(len(mappings), 6)
    
    # ========== TEST 6: Handle Missing Data ==========
    def test_process_excel_missing_data(self):
        """Test handling of missing required fields"""
        test_data = [
            {
                "Full name": "Valid User",
                "Email address": "valid@example.com",
                "Python": 3
            },
            {
                "Full name": "Missing Email",
                "Email address": None,
                "Python": 4
            },
            {
                "Full name": None,
                "Email address": "missingname@example.com", 
                "Python": 5
            }
        ]
        
        file_path = self.create_test_excel(test_data)
        stats = process_excel_data(file_path, self.db)
        
        # Should only process the first row (others have missing data)
        self.assertEqual(stats["rows_processed"], 1)
        self.assertEqual(stats["developers_created"], 1)
        self.assertEqual(stats["skills_mapped"], 1)
    
    # ========== TEST 7: Handle Different Proficiency Formats ==========
    def test_proficiency_formats(self):
        """Test handling of different proficiency value formats"""
        test_data = [
            {
                "Full name": "User One",
                "Email address": "user1@example.com",
                "Python": "5",
                "JavaScript": "4.5",
                "AWS": "3.0"
            }
        ]
        
        file_path = self.create_test_excel(test_data)
        stats = process_excel_data(file_path, self.db)
        
        self.assertEqual(stats["skills_mapped"], 3)
        
        # Check years of experience calculation
        mapping = self.db.query(DeveloperSkill).first()
        self.assertIsNotNone(mapping)
        # Proficiency 5 should give 4 years of experience
        self.assertEqual(mapping.years_of_experience, 4)
    
    # ========== TEST 8: Update Existing Developer ==========
    def test_update_existing_developer(self):
        """Test updating an existing developer's skills"""
        # First import
        test_data1 = [
            {
                "Full name": "Update User",
                "Email address": "update@example.com",
                "Python": 3
            }
        ]
        file_path1 = self.create_test_excel(test_data1, "test1.xlsx")
        stats1 = process_excel_data(file_path1, self.db)
        
        # Second import with more skills
        test_data2 = [
            {
                "Full name": "Update User Updated",
                "Email address": "update@example.com",
                "Python": 4,
                "JavaScript": 5
            }
        ]
        file_path2 = self.create_test_excel(test_data2, "test2.xlsx")
        stats2 = process_excel_data(file_path2, self.db)
        
        # Should create no new developers, but add new skills
        self.assertEqual(stats1["developers_created"], 1)
        self.assertEqual(stats2["developers_created"], 0)
        self.assertEqual(stats2["skills_mapped"], 1)  # Only JavaScript is new
        
        # Verify total skills for developer
        dev = self.db.query(Developer).filter(Developer.email == "update@example.com").first()
        skills_count = self.db.query(DeveloperSkill).filter(DeveloperSkill.developer_id == dev.id).count()
        self.assertEqual(skills_count, 2)
    
    # ========== TEST 9: Column Name Flexibility ==========
    def test_column_name_flexibility(self):
        """Test that service handles various column name formats"""
        test_data = [
            {
                "Name (responses)": "Flex User",
                "Email Address (responses)": "flex@example.com",
                "Department": "Engineering",
                "Role": "Dev",
                "Python": 5
            }
        ]
        
        file_path = self.create_test_excel(test_data)
        stats = process_excel_data(file_path, self.db)
        
        self.assertEqual(stats["rows_processed"], 1)
        self.assertEqual(stats["developers_created"], 1)
    
    # ========== TEST 10: Zero Proficiency Skills ==========
    def test_zero_proficiency_handling(self):
        """Test that zero proficiency skills are not mapped"""
        test_data = [
            {
                "Full name": "Zero User",
                "Email address": "zero@example.com",
                "Python": 0,
                "JavaScript": 5,
                "AWS": 0
            }
        ]
        
        file_path = self.create_test_excel(test_data)
        stats = process_excel_data(file_path, self.db)
        
        # Should only map JavaScript (proficiency 5)
        self.assertEqual(stats["skills_mapped"], 1)
    
    # ========== TEST 11: LLM Functions (if available) ==========
    def test_llm_functions(self):
        """Test LLM helper functions (may be skipped if no API key)"""
        if not llm:
            self.skipTest("LLM not available - skipping AI tests")
        
        # Test skill normalization
        normalized = ai_normalize_skill_name("python3")
        self.assertIsInstance(normalized, str)
        
        # Test role inference
        role = ai_infer_developer_role(["Python", "Django", "PostgreSQL"])
        self.assertIsInstance(role, str)
        
        # Test duplicate detection
        is_duplicate = ai_detect_duplicate_developer(
            "John Smith", 
            "john@example.com",
            ["John S.", "Jon Smith", "Jane Doe"]
        )
        self.assertIsInstance(is_duplicate, bool)
    
    # ========== TEST 12: Error Handling ==========
    def test_error_handling(self):
        """Test error handling with invalid files"""
        # Test with non-existent file
        with self.assertRaises(Exception):
            load_excel_file("nonexistent_file.xlsx")
        
        # Test with empty file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        
        stats = process_excel_data(tmp_path, self.db)
        self.assertEqual(stats["rows_processed"], 0)
        
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

# ========== Manual Test Script ==========
def run_manual_test():
    """Run a manual test with real Excel file"""
    print("\n=== Running Manual Excel Service Test ===\n")
    
    # Create a test database
    engine = create_engine('sqlite:///test_database.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Create test Excel file
    test_data = {
        "Timestamp": [datetime.now(), datetime.now()],
        "Full Name": ["Alice Wonder", "Bob Builder"],
        "Email Address": ["alice@test.com", "bob@test.com"],
        "Department": ["Engineering", "Engineering"],
        "Role": ["", "DevOps Engineer"],  # Empty role for AI inference
        "Python": [5, 3],
        "JavaScript": [4, 2],
        "AWS": [0, 5],
        "Docker": [3, 4],
        "Kubernetes": [2, 0]
    }
    
    df = pd.DataFrame(test_data)
    excel_path = "manual_test_skills.xlsx"
    df.to_excel(excel_path, index=False)
    
    print(f"Created test Excel file: {excel_path}")
    print("\n" + "="*50)
    print("Test Data:")
    print(df.to_string())
    print("="*50)
    
    # Process the Excel file
    print("\nProcessing Excel file...")
    stats = process_excel_data(excel_path, db)
    
    print("\n" + "="*50)
    print("Processing Results:")
    print(f"Rows processed: {stats['rows_processed']}")
    print(f"Developers created: {stats['developers_created']}")
    print(f"Skills mapped: {stats['skills_mapped']}")
    print("="*50)
    
    # Query and display results
    print("\n" + "="*50)
    print("Database Contents:")
    print("-"*30)
    
    developers = db.query(Developer).all()
    for dev in developers:
        print(f"\nDeveloper: {dev.name} ({dev.email})")
        print(f"Role: {dev.current_role}")
        print(f"Department: {dev.department}")
        print("Skills:")
        
        dev_skills = db.query(DeveloperSkill).filter(
            DeveloperSkill.developer_id == dev.id
        ).all()
        
        for ds in dev_skills:
            skill = db.query(Skill).filter(Skill.id == ds.skill_id).first()
            print(f"  - {skill.skill_name}: Proficiency {ds.proficiency_level}, "
                  f"Experience {ds.years_of_experience} years")
    
    print("="*50)
    
    # Cleanup
    print("\n--- Cleaning up ---")
    db.close()
    engine.dispose()

    import time
    time.sleep(0.5)  # Give OS time to release file

    for file in [excel_path, "test_database.db"]:
        try:
            if os.path.exists(file):
                os.unlink(file)
                print(f"✅ Deleted: {file}")
        except PermissionError:
            print(f"⚠️  Could not delete: {file} (still in use)")
        except Exception as e:
            print(f"⚠️  Error deleting {file}: {e}")
    
    return stats

if __name__ == "__main__":
    print("="*60)
    print("EXCEL SERVICE TEST SUITE")
    print("="*60)
    print("\nChoose test mode:")
    print("1. Run unit tests")
    print("2. Run manual test with sample data")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        run_manual_test()
        from dotenv import load_dotenv
        load_dotenv()  # Add this line
    else:
        unittest.main(argv=[''], verbosity=2)