from fastapi.testclient import TestClient
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from database import Base, engine
from main import app, get_db

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_experiment_v2():
    test_data = {
        "experiment_id": "EXP-V2-001",
        "title": "First V2 Test",
        "date": "2026-03-08",
        "start_time": "10:00:00",
        "researcher": "Test Script",
        "lab_system": "Simulation",
        "technique": "Raman",
        "status": "completed",
        "objective_short": "Test the new API",
        "motivation": "Need to ensure complex nesting works",
        "research_question": "Does it blend?",
        "expected_outcome": "Yes",
        "general_setup_notes": "None",
        "preliminary_impression": "Looks good",
        "challenges_faced": "None",
        "things_to_improve": "Nothing",
        "things_that_worked_nicely": "Everything",
        "tags": "test, api, v2",
        "sample": {
            "sample_id": "SAMP-001",
            "sample_name": "Test Si",
            "sample_type": "single crystal"
        },
        "module_selection": {
            "temperature_enabled": True
        },
        "temperature_module": {
            "enabled": True,
            "start_temperature_K": 298.0,
            "end_temperature_K": 4.0,
            "temperature_step_K": 10.0,
            "scan_direction": "cooling"
        },
        "timeline_entries": [
            {
                "entry_id": "TL-001",
                "timestamp": "2026-03-08T10:05:00",
                "author": "Test Script",
                "entry_type": "preparation",
                "text": "Starting the run"
            }
        ],
        "datasets": [
           {
               "dataset_id": "DS-001",
               "run_name": "Ambient Check",
               "file_name": "ambient_01.txt",
               "file_type": "txt",
               "quality_flag": "good"
           }
        ]
    }
    
    response = client.post("/experiments/", json=test_data)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["experiment_id"] == "EXP-V2-001"
    assert data["sample"]["sample_name"] == "Test Si"
