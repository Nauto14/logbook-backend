import os
import models, schemas
from database import engine, SessionLocal
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session, joinedload
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import traceback
import json
from storage import save_uploaded_file, BASE_STORAGE_PATH
from auth import hash_password, verify_password, create_access_token, get_current_user
import ai as ai_module

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Physics Logbook V2")

# CORS — configurable via CORS_ORIGINS env var (comma-separated), defaults to allow all
_cors_origins_env = os.environ.get("CORS_ORIGINS", "*")
if _cors_origins_env == "*":
    _cors_origins = ["*"]
else:
    _cors_origins = [origin.strip() for origin in _cors_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _experiment_query(db: Session):
    """Return a base query for Experiment with all relationships eagerly loaded."""
    return db.query(models.Experiment).options(
        joinedload(models.Experiment.sample),
        joinedload(models.Experiment.module_selection),
        joinedload(models.Experiment.temperature_module),
        joinedload(models.Experiment.pressure_module),
        joinedload(models.Experiment.polarization_module),
        joinedload(models.Experiment.laser_optics_module),
        joinedload(models.Experiment.mapping_module),
        joinedload(models.Experiment.timeline_entries),
        joinedload(models.Experiment.datasets),
        joinedload(models.Experiment.attachments),
    )

# ─── AUTH ENDPOINTS ───────────────────────────────────────────────

@app.post("/api/auth/register", response_model=schemas.TokenResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check for existing email
        if db.query(models.User).filter(models.User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        # Check for existing username
        if db.query(models.User).filter(models.User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")
        # Create user
        db_user = models.User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # Generate token
        token = create_access_token({"sub": str(db_user.id)})
        return schemas.TokenResponse(
            access_token=token,
            user=schemas.UserResponse.model_validate(db_user),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("REGISTER ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(user.id)})
    return schemas.TokenResponse(
        access_token=token,
        user=schemas.UserResponse.model_validate(user),
    )

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return schemas.UserResponse.model_validate(current_user)

# ─── AI ENDPOINT ──────────────────────────────────────────────────

@app.post("/api/ai/query", response_model=schemas.AIQueryResponse)
def ai_query(
    request: schemas.AIQueryRequest,
    current_user: models.User = Depends(get_current_user),
):
    result = ai_module.query_experiments(request.question, request.experiments)
    return schemas.AIQueryResponse(**result)



@app.post("/api/experiments/", response_model=schemas.ExperimentResponse)
def create_experiment(
    metadata: str = Form(...),
    dataset_files: List[UploadFile] = File(default=[]),
    sample_images: List[UploadFile] = File(default=[]),
    reflection_images: List[UploadFile] = File(default=[]),
    timeline_images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    try:
        experiment_dict = json.loads(metadata)
        experiment = schemas.ExperimentCreate(**experiment_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid metadata payload: {str(e)}")

    db_experiment = db.query(models.Experiment).filter(models.Experiment.experiment_id == experiment.experiment_id).first()
    if db_experiment:
        raise HTTPException(status_code=400, detail="Experiment ID already exists")

    try:
        # Create core experiment
        exp_data = experiment.model_dump(exclude={
            'sample', 'module_selection', 'temperature_module', 'pressure_module', 
            'polarization_module', 'laser_optics_module', 'mapping_module', 
            'timeline_entries', 'datasets', 'attachments'
        })
        db_exp = models.Experiment(**exp_data)
        db.add(db_exp)
        db.flush() # get ID

        # 1. SAMPLE
        if experiment.sample:
            db_sample = models.Sample(**experiment.sample.model_dump())
            db.add(db_sample)
            db.flush()
            db_exp.sample_id = db_sample.id

        # 2. MODULE SELECTION
        if experiment.module_selection:
            db_mod_sel = models.ModuleSelection(**experiment.module_selection.model_dump(), experiment_id=db_exp.id)
            db.add(db_mod_sel)

        # 3. OPTIONAL MODULES
        if experiment.temperature_module:
            db.add(models.TemperatureModule(**experiment.temperature_module.model_dump(), experiment_id=db_exp.id))
        
        if experiment.pressure_module:
            db.add(models.PressureModule(**experiment.pressure_module.model_dump(), experiment_id=db_exp.id))
            
        if experiment.polarization_module:
            db.add(models.PolarizationModule(**experiment.polarization_module.model_dump(), experiment_id=db_exp.id))
            
        if experiment.laser_optics_module:
            db.add(models.LaserOpticsModule(**experiment.laser_optics_module.model_dump(), experiment_id=db_exp.id))
            
        if experiment.mapping_module:
            db.add(models.MappingModule(**experiment.mapping_module.model_dump(), experiment_id=db_exp.id))

        # 4. TIMELINE & DATASETS (Lists)
        for t_entry in experiment.timeline_entries:
            db.add(models.TimelineEntry(**t_entry.model_dump(), experiment_id=db_exp.id))
            
        for d_entry in experiment.datasets:
            db.add(models.Dataset(**d_entry.model_dump(), experiment_id=db_exp.id))

        db.flush()

        # 5. PHYSICAL UPLOADS & ATTACHMENTS
        # Datasets
        for d_file in dataset_files:
            file_path = save_uploaded_file(d_file, experiment.experiment_id, "datasets")
            db_ds = db.query(models.Dataset).filter_by(experiment_id=db_exp.id, file_name=d_file.filename).first()
            if db_ds:
                db_ds.file_path = file_path

        # Sample Images
        for s_img in sample_images:
            file_path = save_uploaded_file(s_img, experiment.experiment_id, "sample_images")
            db.add(models.Attachment(
                experiment_id=db_exp.id,
                parent_type='sample',
                parent_id=str(db_exp.sample_id),
                attachment_category='sample_image',
                file_name=s_img.filename,
                file_path=file_path
            ))

        # Reflection Images
        for r_img in reflection_images:
            file_path = save_uploaded_file(r_img, experiment.experiment_id, "reflections")
            db.add(models.Attachment(
                experiment_id=db_exp.id,
                parent_type='experiment',
                parent_id=str(db_exp.id),
                attachment_category='reflection_image',
                file_name=r_img.filename,
                file_path=file_path
            ))

        # Timeline Images
        for t_img in timeline_images:
            file_path = save_uploaded_file(t_img, experiment.experiment_id, "notes")
            db.add(models.Attachment(
                experiment_id=db_exp.id,
                parent_type='timeline_entry',
                attachment_category='note_image',
                file_name=t_img.filename,
                file_path=file_path
            ))

        db.commit()
        db.refresh(db_exp)
        return db_exp

    except Exception as e:
        db.rollback()
        print("Error saving experiment:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/experiments/", response_model=List[schemas.ExperimentResponse])
def get_experiments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    experiments = _experiment_query(db).order_by(models.Experiment.created_at.desc()).offset(skip).limit(limit).all()
    return experiments

@app.get("/api/experiments/{experiment_id}", response_model=schemas.ExperimentResponse)
def get_experiment_detail(experiment_id: str, db: Session = Depends(get_db)):
    db_experiment = _experiment_query(db).filter(models.Experiment.experiment_id == experiment_id).first()
    if not db_experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return db_experiment

@app.get("/api/samples/", response_model=List[schemas.SampleResponse])
def get_samples(db: Session = Depends(get_db)):
    samples_db = db.query(models.Sample).order_by(models.Sample.id.desc()).all()
    seen = set()
    unique_samples = []
    for s in samples_db:
        if s.sample_name and s.sample_name not in seen:
            seen.add(s.sample_name)
            unique_samples.append(s)
    return unique_samples

@app.put("/api/experiments/{experiment_id}", response_model=schemas.ExperimentResponse)
def update_experiment(
    experiment_id: str,
    metadata: str = Form(...),
    dataset_files: List[UploadFile] = File(default=[]),
    sample_images: List[UploadFile] = File(default=[]),
    reflection_images: List[UploadFile] = File(default=[]),
    timeline_images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    db_exp = db.query(models.Experiment).filter(models.Experiment.experiment_id == experiment_id).first()
    if not db_exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    try:
        experiment_dict = json.loads(metadata)
        if 'experiment_id' not in experiment_dict:
            experiment_dict['experiment_id'] = experiment_id
        experiment = schemas.ExperimentCreate(**experiment_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid metadata payload: {str(e)}")

    try:
        # Update core experiment fields
        exp_data = experiment.model_dump(exclude={
            'sample', 'module_selection', 'temperature_module', 'pressure_module', 
            'polarization_module', 'laser_optics_module', 'mapping_module', 
            'timeline_entries', 'datasets', 'attachments', 'experiment_id'
        })
        for key, value in exp_data.items():
            setattr(db_exp, key, value)

        # 1. Update Sample (create if new name or different, or update existing)
        if experiment.sample:
            if db_exp.sample and db_exp.sample.sample_name == experiment.sample.sample_name:
                for k, v in experiment.sample.model_dump(exclude={'sample_id'}).items():
                    setattr(db_exp.sample, k, v)
            else:
                db_sample = models.Sample(**experiment.sample.model_dump())
                db.add(db_sample)
                db.flush()
                db_exp.sample_id = db_sample.id

        # Delete old 1-to-1 modules for clean recreation
        db.query(models.ModuleSelection).filter_by(experiment_id=db_exp.id).delete()
        db.query(models.TemperatureModule).filter_by(experiment_id=db_exp.id).delete()
        db.query(models.PressureModule).filter_by(experiment_id=db_exp.id).delete()
        db.query(models.PolarizationModule).filter_by(experiment_id=db_exp.id).delete()
        db.query(models.LaserOpticsModule).filter_by(experiment_id=db_exp.id).delete()
        db.query(models.MappingModule).filter_by(experiment_id=db_exp.id).delete()

        # 2. Recreate MODULE SELECTION
        if experiment.module_selection:
            db.add(models.ModuleSelection(**experiment.module_selection.model_dump(), experiment_id=db_exp.id))

        # 3. Recreate OPTIONAL MODULES
        if experiment.temperature_module:
            db.add(models.TemperatureModule(**experiment.temperature_module.model_dump(), experiment_id=db_exp.id))
        if experiment.pressure_module:
            db.add(models.PressureModule(**experiment.pressure_module.model_dump(), experiment_id=db_exp.id))
        if experiment.polarization_module:
            db.add(models.PolarizationModule(**experiment.polarization_module.model_dump(), experiment_id=db_exp.id))
        if experiment.laser_optics_module:
            db.add(models.LaserOpticsModule(**experiment.laser_optics_module.model_dump(), experiment_id=db_exp.id))
        if experiment.mapping_module:
            db.add(models.MappingModule(**experiment.mapping_module.model_dump(), experiment_id=db_exp.id))

        # 4. TIMELINE & DATASETS
        old_datasets = {d.file_name: d.file_path for d in db_exp.datasets if d.file_path}
        
        db.query(models.TimelineEntry).filter_by(experiment_id=db_exp.id).delete()
        db.query(models.Dataset).filter_by(experiment_id=db_exp.id).delete()

        for t_entry in experiment.timeline_entries:
            t_dict = t_entry.model_dump()
            t_dict['entry_id'] = f"TL-{db_exp.id}-{t_dict.get('entry_id', '')}-{id(t_dict)}"
            db.add(models.TimelineEntry(**t_dict, experiment_id=db_exp.id))
            
        for d_entry in experiment.datasets:
            d_dict = d_entry.model_dump()
            if d_dict['file_name'] in old_datasets and not d_dict.get('file_path'):
                d_dict['file_path'] = old_datasets[d_dict['file_name']]
            db.add(models.Dataset(**d_dict, experiment_id=db_exp.id))

        db.flush()

        # 5. PHYSICAL UPLOADS & ATTACHMENTS (Append only)
        for d_file in dataset_files:
            file_path = save_uploaded_file(d_file, experiment.experiment_id, "datasets")
            db_ds = db.query(models.Dataset).filter_by(experiment_id=db_exp.id, file_name=d_file.filename).first()
            if db_ds:
                db_ds.file_path = file_path

        for s_img in sample_images:
            file_path = save_uploaded_file(s_img, experiment.experiment_id, "sample_images")
            db.add(models.Attachment(
                experiment_id=db_exp.id, parent_type='sample', parent_id=str(db_exp.sample_id),
                attachment_category='sample_image', file_name=s_img.filename, file_path=file_path
            ))

        for r_img in reflection_images:
            file_path = save_uploaded_file(r_img, experiment.experiment_id, "reflections")
            db.add(models.Attachment(
                experiment_id=db_exp.id, parent_type='experiment', parent_id=str(db_exp.id),
                attachment_category='reflection_image', file_name=r_img.filename, file_path=file_path
            ))

        for t_img in timeline_images:
            file_path = save_uploaded_file(t_img, experiment.experiment_id, "notes")
            db.add(models.Attachment(
                experiment_id=db_exp.id, parent_type='timeline_entry',
                attachment_category='note_image', file_name=t_img.filename, file_path=file_path
            ))

        db.commit()
        db.refresh(db_exp)
        return db_exp

    except Exception as e:
        db.rollback()
        print("Error updating experiment:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Serve uploaded files — uses deployment-safe path from env var
_files_dir = str(BASE_STORAGE_PATH / "experiments")
if os.path.isdir(_files_dir):
    app.mount("/api/files", StaticFiles(directory=_files_dir), name="files")
else:
    # Create the directory so the mount works on first run
    os.makedirs(_files_dir, exist_ok=True)
    app.mount("/api/files", StaticFiles(directory=_files_dir), name="files")
