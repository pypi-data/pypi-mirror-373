from enum import StrEnum


class ServiceType(StrEnum):
    BACKEND = "backend"
    FRONTEND = "frontend"


class Category(StrEnum):
    CORE = "core"
    AI = "ai"


class ShortKey(StrEnum):
    STUDIO = "studio"
    NEXUS = "nexus"
    TELEMETRY = "telemetry"
    METADATA = "metadata"
    IDENTITY = "identity"
    ACCESS = "access"
    WORKSHOP = "workshop"
    RESEARCH = "research"
    SOAPIE = "soapie"
    MEDIX = "medix"
    DICOM = "dicom"
    SCRIBE = "scribe"
    CDS = "cds"
    IMAGING = "imaging"
    MCU = "mcu"


class Key(StrEnum):
    STUDIO = "maleo-studio"
    NEXUS = "maleo-nexus"
    TELEMETRY = "maleo-telemetry"
    METADATA = "maleo-metadata"
    IDENTITY = "maleo-identity"
    ACCESS = "maleo-access"
    WORKSHOP = "maleo-workshop"
    RESEARCH = "maleo-research"
    SOAPIE = "maleo-soapie"
    MEDIX = "maleo-medix"
    DICOM = "maleo-dicom"
    SCRIBE = "maleo-scribe"
    CDS = "maleo-cds"
    IMAGING = "maleo-imaging"
    MCU = "maleo-mcu"


class ShortName(StrEnum):
    STUDIO = "Studio"
    NEXUS = "Nexus"
    TELEMETRY = "Telemetry"
    METADATA = "Metadata"
    IDENTITY = "Identity"
    ACCESS = "Access"
    WORKSHOP = "Workshop"
    RESEARCH = "Research"
    SOAPIE = "SOAPIE"
    MEDIX = "Medix"
    DICOM = "DICON"
    SCRIBE = "Scribe"
    CDS = "CDS"
    IMAGING = "Imaging"
    MCU = "MCU"


class Name(StrEnum):
    STUDIO = "MaleoStudio"
    NEXUS = "MaleoNexus"
    TELEMETRY = "MaleoTelemetry"
    METADATA = "MaleoMetadata"
    IDENTITY = "MaleoIdentity"
    ACCESS = "MaleoAccess"
    WORKSHOP = "MaleoWorkshop"
    RESEARCH = "MaleoResearch"
    SOAPIE = "MaleoSOAPIE"
    MEDIX = "MaleoMedix"
    DICOM = "MaleoDICON"
    SCRIBE = "MaleoScribe"
    CDS = "MaleoCDS"
    IMAGING = "MaleoImaging"
    MCU = "MaleoMCU"
