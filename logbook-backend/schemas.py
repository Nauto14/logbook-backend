from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
import datetime

# =======================
# AUTH SCHEMAS
# =======================
class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# =======================
# AI SCHEMAS
# =======================
class AIQueryRequest(BaseModel):
    question: str
    experiments: List[Any] = []

class AIQueryResponse(BaseModel):
    answer: str
    referenced_experiments: List[str] = []

# =======================
# SAMPLE SCHEMAS
# =======================
class SampleBase(BaseModel):
    sample_name: str
    chemical_formula: Optional[str] = None
    sample_type: str
    growth_method: Optional[str] = None
    batch_or_growth_id: Optional[str] = None
    orientation: Optional[str] = None
    dimensions: Optional[str] = None
    thickness: Optional[str] = None
    substrate: Optional[str] = None
    preparation_notes: Optional[str] = None
    mounting_notes: Optional[str] = None
    storage_notes: Optional[str] = None
    sample_images: Optional[str] = None

class SampleCreate(SampleBase):
    sample_id: str

class SampleResponse(SampleBase):
    id: int
    sample_id: str
    
    class ConfigDict:
        from_attributes = True

# =======================
# MODULE SCHEMAS
# =======================
class ModuleSelectionBase(BaseModel):
    temperature_enabled: bool = False
    pressure_enabled: bool = False
    polarization_enabled: bool = False
    magnetic_field_enabled: bool = False
    angle_enabled: bool = False
    time_enabled: bool = False
    laser_power_enabled: bool = False
    wavelength_enabled: bool = False
    mapping_enabled: bool = False

class TemperatureModuleBase(BaseModel):
    enabled: bool = False
    start_temperature_K: float
    end_temperature_K: float
    temperature_step_K: float
    custom_temperature_points_K: Optional[str] = None
    stabilization_time_min: Optional[float] = None
    scan_direction: str
    controller: Optional[str] = None
    sensor: Optional[str] = None
    reason_for_temperature_points: Optional[str] = None
    temperature_notes: Optional[str] = None

class PressureModuleBase(BaseModel):
    enabled: bool = False
    start_pressure_GPa: float
    end_pressure_GPa: float
    pressure_step_GPa: Optional[float] = None
    custom_pressure_points_GPa: Optional[str] = None
    cell_type: str
    cell_id: Optional[str] = None
    culet_size_um: Optional[float] = None
    gasket_material: Optional[str] = None
    gasket_thickness_um: Optional[float] = None
    gasket_hole_diameter_um: Optional[float] = None
    sample_length_um: Optional[float] = None
    sample_width_um: Optional[float] = None
    sample_thickness_um: Optional[float] = None
    sample_shape: Optional[str] = None
    sample_dimensions_notes: Optional[str] = None
    pressure_medium: str
    pressure_calibration_method: str
    temperature_sensor: Optional[str] = None
    loading_notes: Optional[str] = None
    reason_for_pressure_points: Optional[str] = None

class PolarizationModuleBase(BaseModel):
    enabled: bool = False
    selected_polarizations: str
    custom_polarization_optional: Optional[str] = None
    porto_notation: Optional[str] = None
    incident_polarization: Optional[str] = None
    analyzed_polarization: Optional[str] = None
    crystal_orientation_reference: str
    rotation_notes: Optional[str] = None
    alignment_quality_comments: Optional[str] = None

class LaserOpticsModuleBase(BaseModel):
    laser_wavelength_nm: float
    laser_power_mW: Optional[float] = None
    objective: str
    grating: str
    slit_size: Optional[str] = None
    neutral_density_filter: Optional[str] = None
    confocal_setting: Optional[str] = None
    spot_size_estimate_um: Optional[float] = None
    spectral_range_cm_1: Optional[str] = None
    spectrometer: str

class MappingModuleBase(BaseModel):
    enabled: bool = False
    scan_type: str
    map_dimensions: Optional[str] = None
    step_size_um: Optional[float] = None
    number_of_points: Optional[int] = None
    scan_axis_definition: Optional[str] = None
    mapping_notes: Optional[str] = None

# =======================
# TIMELINE & DATASETS
# =======================
class TimelineEntryBase(BaseModel):
    timestamp: datetime.datetime
    author: str
    entry_type: str
    text: str
    image_attachments: Optional[str] = None

class TimelineEntryCreate(TimelineEntryBase):
    entry_id: str

class TimelineEntryResponse(TimelineEntryBase):
    id: int
    entry_id: str
    
    class ConfigDict:
        from_attributes = True

class DatasetBase(BaseModel):
    dataset_group_name: Optional[str] = None
    run_name: str
    file_name: str
    file_path: Optional[str] = None
    file_type: str
    acquisition_timestamp: Optional[datetime.datetime] = None
    temperature_K: Optional[float] = None
    pressure_GPa: Optional[float] = None
    polarization: Optional[str] = None
    magnetic_field_T: Optional[float] = None
    angle_deg: Optional[float] = None
    laser_wavelength_nm: Optional[float] = None
    laser_power_mW: Optional[float] = None
    integration_time_s: Optional[float] = None
    accumulations: Optional[int] = None
    scan_order: Optional[int] = None
    quality_flag: str
    comments: Optional[str] = None
    tags: Optional[str] = None

class DatasetCreate(DatasetBase):
    dataset_id: str

class DatasetResponse(DatasetBase):
    id: int
    dataset_id: str
    
    class ConfigDict:
        from_attributes = True

class AttachmentBase(BaseModel):
    parent_type: str
    parent_id: Optional[str] = None
    attachment_category: str
    file_name: str
    file_path: str

class AttachmentCreate(AttachmentBase):
    pass

class AttachmentResponse(AttachmentBase):
    id: int
    uploaded_at: datetime.datetime

    class ConfigDict:
        from_attributes = True

# =======================
# EXPERIMENT SCHEMAS
# =======================
class ExperimentBase(BaseModel):
    title: str
    date: datetime.date
    start_time: datetime.time
    end_time: Optional[datetime.time] = None
    researcher: str
    collaborators: Optional[str] = None
    lab_system: str
    technique: str
    status: str
    objective_short: str
    motivation: Optional[str] = ''
    research_question: Optional[str] = ''
    expected_outcome: Optional[str] = ''
    related_previous_experiment_id: Optional[str] = None
    general_setup_notes: Optional[str] = ''
    preliminary_impression: Optional[str] = ''
    challenges_faced: Optional[str] = ''
    things_to_improve: Optional[str] = ''
    things_that_worked_nicely: Optional[str] = ''
    reflection_image_attachments: Optional[str] = None
    final_summary: Optional[str] = None
    tags: Optional[str] = ''

class ExperimentCreate(ExperimentBase):
    experiment_id: str
    sample: SampleCreate
    module_selection: ModuleSelectionBase
    temperature_module: Optional[TemperatureModuleBase] = None
    pressure_module: Optional[PressureModuleBase] = None
    polarization_module: Optional[PolarizationModuleBase] = None
    laser_optics_module: Optional[LaserOpticsModuleBase] = None
    mapping_module: Optional[MappingModuleBase] = None
    timeline_entries: List[TimelineEntryCreate] = []
    datasets: List[DatasetCreate] = []
    attachments: List[AttachmentCreate] = []

class ExperimentResponse(ExperimentBase):
    id: int
    experiment_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    sample: Optional[SampleResponse] = None
    module_selection: Optional[ModuleSelectionBase] = None
    temperature_module: Optional[TemperatureModuleBase] = None
    pressure_module: Optional[PressureModuleBase] = None
    polarization_module: Optional[PolarizationModuleBase] = None
    laser_optics_module: Optional[LaserOpticsModuleBase] = None
    mapping_module: Optional[MappingModuleBase] = None
    timeline_entries: List[TimelineEntryResponse] = []
    datasets: List[DatasetResponse] = []
    attachments: List[AttachmentResponse] = []
    
    class ConfigDict:
        from_attributes = True
