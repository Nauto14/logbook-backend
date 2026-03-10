from sqlalchemy import Column, Integer, String, Float, Text, Date, Time, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String, unique=True, index=True)
    title = Column(String)
    date = Column(Date, index=True)
    start_time = Column(Time)
    end_time = Column(Time, nullable=True)
    researcher = Column(String, index=True)
    collaborators = Column(String, nullable=True) # Stored as comma-separated
    lab_system = Column(String)
    technique = Column(String)
    status = Column(String)
    objective_short = Column(String)
    motivation = Column(Text)
    research_question = Column(Text)
    expected_outcome = Column(Text)
    related_previous_experiment_id = Column(String, nullable=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=True)
    general_setup_notes = Column(Text)
    preliminary_impression = Column(Text)
    challenges_faced = Column(Text)
    things_to_improve = Column(Text)
    things_that_worked_nicely = Column(Text)
    reflection_image_attachments = Column(Text, nullable=True)
    final_summary = Column(Text, nullable=True)
    tags = Column(String) # Stored as comma-separated
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    sample = relationship("Sample", back_populates="experiments")
    module_selection = relationship("ModuleSelection", back_populates="experiment", uselist=False, cascade="all, delete-orphan")
    temperature_module = relationship("TemperatureModule", back_populates="experiment", uselist=False, cascade="all, delete-orphan")
    pressure_module = relationship("PressureModule", back_populates="experiment", uselist=False, cascade="all, delete-orphan")
    polarization_module = relationship("PolarizationModule", back_populates="experiment", uselist=False, cascade="all, delete-orphan")
    laser_optics_module = relationship("LaserOpticsModule", back_populates="experiment", uselist=False, cascade="all, delete-orphan")
    mapping_module = relationship("MappingModule", back_populates="experiment", uselist=False, cascade="all, delete-orphan")
    timeline_entries = relationship("TimelineEntry", back_populates="experiment", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="experiment", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="experiment", cascade="all, delete-orphan")


class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String, unique=True, index=True)
    sample_name = Column(String, index=True)
    chemical_formula = Column(String)
    sample_type = Column(String)
    growth_method = Column(String)
    batch_or_growth_id = Column(String, nullable=True)
    orientation = Column(String)
    dimensions = Column(Text)
    thickness = Column(String, nullable=True)
    substrate = Column(String, nullable=True)
    preparation_notes = Column(Text)
    mounting_notes = Column(Text, nullable=True)
    storage_notes = Column(Text, nullable=True)
    sample_images = Column(Text, nullable=True)

    experiments = relationship("Experiment", back_populates="sample")


class ModuleSelection(Base):
    __tablename__ = "module_selections"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    temperature_enabled = Column(Boolean, default=False)
    pressure_enabled = Column(Boolean, default=False)
    polarization_enabled = Column(Boolean, default=False)
    magnetic_field_enabled = Column(Boolean, default=False)
    angle_enabled = Column(Boolean, default=False)
    time_enabled = Column(Boolean, default=False)
    laser_power_enabled = Column(Boolean, default=False)
    wavelength_enabled = Column(Boolean, default=False)
    mapping_enabled = Column(Boolean, default=False)

    experiment = relationship("Experiment", back_populates="module_selection")


class TemperatureModule(Base):
    __tablename__ = "temperature_modules"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    enabled = Column(Boolean, default=False)
    start_temperature_K = Column(Float)
    end_temperature_K = Column(Float)
    temperature_step_K = Column(Float)
    custom_temperature_points_K = Column(String, nullable=True) # comma separated
    stabilization_time_min = Column(Float, nullable=True)
    scan_direction = Column(String)
    controller = Column(String, nullable=True)
    sensor = Column(String, nullable=True)
    reason_for_temperature_points = Column(Text)
    temperature_notes = Column(Text)

    experiment = relationship("Experiment", back_populates="temperature_module")


class PressureModule(Base):
    __tablename__ = "pressure_modules"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    enabled = Column(Boolean, default=False)
    start_pressure_GPa = Column(Float)
    end_pressure_GPa = Column(Float)
    pressure_step_GPa = Column(Float, nullable=True)
    custom_pressure_points_GPa = Column(String, nullable=True) # comma separated
    cell_type = Column(String)
    cell_id = Column(String, nullable=True)
    culet_size_um = Column(Float, nullable=True)
    gasket_material = Column(String, nullable=True)
    gasket_thickness_um = Column(Float, nullable=True)
    gasket_hole_diameter_um = Column(Float, nullable=True)
    sample_length_um = Column(Float, nullable=True)
    sample_width_um = Column(Float, nullable=True)
    sample_thickness_um = Column(Float, nullable=True)
    sample_shape = Column(String, nullable=True)
    sample_dimensions_notes = Column(Text, nullable=True)
    pressure_medium = Column(String)
    pressure_calibration_method = Column(String)
    temperature_sensor = Column(String, nullable=True)
    loading_notes = Column(Text)
    reason_for_pressure_points = Column(Text)

    experiment = relationship("Experiment", back_populates="pressure_module")


class PolarizationModule(Base):
    __tablename__ = "polarization_modules"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    enabled = Column(Boolean, default=False)
    selected_polarizations = Column(String) # comma separated
    custom_polarization_optional = Column(String, nullable=True)
    porto_notation = Column(Text, nullable=True)
    incident_polarization = Column(String, nullable=True)
    analyzed_polarization = Column(String, nullable=True)
    crystal_orientation_reference = Column(Text)
    rotation_notes = Column(Text)
    alignment_quality_comments = Column(Text)

    experiment = relationship("Experiment", back_populates="polarization_module")


class LaserOpticsModule(Base):
    __tablename__ = "laser_optics_modules"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    laser_wavelength_nm = Column(Float)
    laser_power_mW = Column(Float, nullable=True)
    objective = Column(String)
    grating = Column(String)
    slit_size = Column(String, nullable=True)
    # integration_time_s and accumulations moved to datasets
    neutral_density_filter = Column(String, nullable=True)
    confocal_setting = Column(String, nullable=True)
    spot_size_estimate_um = Column(Float, nullable=True)
    spectral_range_cm_1 = Column(String, nullable=True)
    spectrometer = Column(String)

    experiment = relationship("Experiment", back_populates="laser_optics_module")


class MappingModule(Base):
    __tablename__ = "mapping_modules"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    enabled = Column(Boolean, default=False)
    scan_type = Column(String)
    map_dimensions = Column(String, nullable=True)
    step_size_um = Column(Float, nullable=True)
    number_of_points = Column(Integer, nullable=True)
    scan_axis_definition = Column(Text, nullable=True)
    mapping_notes = Column(Text)

    experiment = relationship("Experiment", back_populates="mapping_module")


class TimelineEntry(Base):
    __tablename__ = "timeline_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(String, unique=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    timestamp = Column(DateTime)
    author = Column(String)
    entry_type = Column(String)
    text = Column(Text)
    image_attachments = Column(Text, nullable=True)

    experiment = relationship("Experiment", back_populates="timeline_entries")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, unique=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    dataset_group_name = Column(String, nullable=True)
    run_name = Column(String)
    file_name = Column(String)
    file_path = Column(String) # Physical path on disk
    file_type = Column(String)
    acquisition_timestamp = Column(DateTime, nullable=True)
    temperature_K = Column(Float, nullable=True)
    pressure_GPa = Column(Float, nullable=True)
    polarization = Column(String, nullable=True)
    magnetic_field_T = Column(Float, nullable=True)
    angle_deg = Column(Float, nullable=True)
    laser_wavelength_nm = Column(Float, nullable=True)
    laser_power_mW = Column(Float, nullable=True)
    integration_time_s = Column(Float, nullable=True)
    accumulations = Column(Integer, nullable=True)
    scan_order = Column(Integer, nullable=True)
    quality_flag = Column(String)
    comments = Column(Text)
    tags = Column(String) # comma separated

    experiment = relationship("Experiment", back_populates="datasets")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    parent_type = Column(String) # 'experiment', 'sample', 'timeline_entry', etc.
    parent_id = Column(String, nullable=True) # string ID if applicable
    attachment_category = Column(String) # 'sample_image', 'reflection_image', 'note_image'
    file_name = Column(String)
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    experiment = relationship("Experiment", back_populates="attachments")
