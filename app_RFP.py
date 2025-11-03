"""
🎯 RFP Vendor Evaluation & Selection Platform
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enterprise platform for evaluating and selecting logistics service providers
Supporting Warehouse, Customer Service Operations, and Fulfillment Services
Full document upload support for single consolidated or multiple service-specific RFPs
"""

import streamlit as st
import anthropic
import PyPDF2
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pptx import Presentation
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import re
from datetime import datetime, timedelta
import io
import hashlib
import uuid
from typing import Dict, List, Optional, Tuple, Any
import base64
import time
import random
from faker import Faker
import zipfile
import openpyxl
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment

# Initialize Faker for sample data
fake = Faker()

# ========================================
# CONFIGURATION & INITIALIZATION
# ========================================

st.set_page_config(
    page_title="RFP Vendor Evaluation Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'workflow_stages' not in st.session_state:
    st.session_state.workflow_stages = None
if 'vendors' not in st.session_state:
    st.session_state.vendors = {}
if 'rfp_documents' not in st.session_state:
    st.session_state.rfp_documents = {}
if 'vendor_documents' not in st.session_state:
    st.session_state.vendor_documents = {}

# Professional CSS styling
st.markdown("""
<style>
    :root {
        --primary: #1e3a8a;
        --secondary: #3b82f6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #06b6d4;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .workflow-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid var(--primary);
        transition: all 0.3s;
    }
    
    .workflow-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    .stage-pending {
        border-left-color: #94a3b8;
        background: #f8fafc;
        opacity: 0.8;
    }
    
    .stage-active {
        border-left-color: var(--warning);
        background: #fef3c7;
        animation: pulse 2s infinite;
    }
    
    .stage-complete {
        border-left-color: var(--success);
        background: #d1fae5;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.9; }
    }
    
    .vendor-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        position: relative;
        border: 2px solid #e5e7eb;
        transition: all 0.3s;
    }
    
    .vendor-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }
    
    .vendor-selected {
        border-color: var(--success);
        background: #f0fdf4;
    }
    
    .vendor-shortlisted {
        border-color: var(--warning);
        background: #fffbeb;
    }
    
    .vendor-rejected {
        opacity: 0.6;
        border-color: var(--danger);
        background: #fef2f2;
    }
    
    .service-model-card {
        background: linear-gradient(135deg, #f3f4f6 0%, #ffffff 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid #e5e7eb;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .service-model-selected {
        border-color: var(--success);
        background: linear-gradient(135deg, #d1fae5 0%, #ffffff 100%);
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.25rem;
    }
    
    .score-excellent { background: #d1fae5; color: #065f46; }
    .score-good { background: #dbeafe; color: #1e3a8a; }
    .score-fair { background: #fed7aa; color: #9a3412; }
    .score-poor { background: #fecaca; color: #991b1b; }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 3px solid var(--secondary);
    }
    
    .service-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 15px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .service-warehouse { background: #e0e7ff; color: #3730a3; }
    .service-cso { background: #fce7f3; color: #a21caf; }
    .service-csg { background: #f0fdfa; color: #0f766e; }
    
    .document-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .document-upload-zone {
        border: 2px dashed var(--secondary);
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f0f9ff;
        margin: 1rem 0;
        transition: all 0.3s;
    }
    
    .document-upload-zone:hover {
        border-color: var(--primary);
        background: #e0f2fe;
    }
    
    .progress-bar {
        background: #e5e7eb;
        height: 30px;
        border-radius: 15px;
        overflow: hidden;
        margin: 20px 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, var(--success), var(--secondary));
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        transition: width 0.5s ease;
    }
    
    .test-mode-banner {
        background: linear-gradient(90deg, #8b5cf6, #ec4899);
        color: white;
        padding: 1rem;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
        border-radius: 5px;
        animation: gradient 3s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .action-button {
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# DATA MODELS & CLASSES
# ========================================

class ServiceModel:
    """Represents different service models for RFP"""
    STANDALONE = "Standalone"
    CONSOLIDATED = "Consolidated"
    
    @staticmethod
    def get_description(model):
        if model == ServiceModel.STANDALONE:
            return "Single vendor for one specific service (Warehouse OR CSO OR CSG)"
        else:
            return "Single vendor for multiple integrated services (Warehouse + CSO + CSG)"

class ServiceType:
    """Types of services being procured"""
    WAREHOUSE = "Warehouse Services"
    CSO = "Customer Service Operations"
    CSG = "Consumer Solutions Group"
    
    @staticmethod
    def get_all():
        return [ServiceType.WAREHOUSE, ServiceType.CSO, ServiceType.CSG]
    
    @staticmethod
    def get_requirements(service):
        requirements = {
            ServiceType.WAREHOUSE: [
                "Storage capacity (minimum sq ft)",
                "Temperature-controlled zones",
                "24/7 operations capability",
                "Inventory management systems (WMS)",
                "Cross-docking capabilities",
                "Security measures and certifications"
            ],
            ServiceType.CSO: [
                "RMA processing capability",
                "Returns management system",
                "Customer support (24/7)",
                "Replacement fulfillment",
                "Quality inspection processes",
                "Response time SLAs"
            ],
            ServiceType.CSG: [
                "Kitting services capacity",
                "Packaging capabilities",
                "Assembly operations",
                "Labeling services",
                "Custom fulfillment solutions",
                "Quality control processes"
            ]
        }
        return requirements.get(service, [])

class WorkflowStage:
    """RFP workflow stages with proper state management"""
    def __init__(self, stage_id: str, stage_num: int, name: str, description: str,
                 required_docs: List[str], deliverables: List[str], duration: str):
        self.stage_id = stage_id
        self.stage_num = stage_num
        self.name = name
        self.description = description
        self.required_docs = required_docs
        self.deliverables = deliverables
        self.duration = duration
        self.status = "pending"
        self.progress = 0
        self.start_date = None
        self.end_date = None
        self.documents = {}
        
    def can_start(self, previous_stage) -> bool:
        """Check if stage can be started"""
        if previous_stage is None:
            return True
        return previous_stage.status == "complete"
    
    def start(self):
        """Start the workflow stage"""
        self.status = "active"
        self.start_date = datetime.now()
        self.progress = 10
        return True
        
    def complete(self):
        """Complete the workflow stage"""
        self.status = "complete"
        self.end_date = datetime.now()
        self.progress = 100
        return True
        
    def update_progress(self, progress: int):
        """Update stage progress"""
        self.progress = min(100, max(0, progress))
        if self.progress == 100 and self.status != "complete":
            self.complete()
        return True

class DocumentManager:
    """Manages document uploads and extraction"""
    
    @staticmethod
    def extract_text_from_pdf(file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file) -> str:
        """Extract text from Word document"""
        try:
            doc = docx.Document(file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + "\t"
                    text += "\n"
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text_from_file(uploaded_file) -> Dict:
        """Extract text and metadata from uploaded file"""
        file_info = {
            "name": uploaded_file.name,
            "type": uploaded_file.type,
            "size": uploaded_file.size,
            "content": "",
            "upload_date": datetime.now()
        }
        
        if "pdf" in uploaded_file.type:
            file_info["content"] = DocumentManager.extract_text_from_pdf(uploaded_file)
        elif "wordprocessingml" in uploaded_file.type or uploaded_file.name.endswith('.docx'):
            file_info["content"] = DocumentManager.extract_text_from_docx(uploaded_file)
        elif "text" in uploaded_file.type:
            file_info["content"] = str(uploaded_file.read(), "utf-8")
        else:
            file_info["content"] = "Binary file - content extraction not supported"
        
        return file_info
    
    @staticmethod
    def identify_document_type(content: str, filename: str) -> Dict:
        """Identify document type and extract key information"""
        doc_type = {
            "is_rfp": False,
            "is_sow": False,
            "is_pricing": False,
            "is_technical": False,
            "services_mentioned": [],
            "model_type": None
        }
        
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # Check document type
        if "request for proposal" in content_lower or "rfp" in filename_lower:
            doc_type["is_rfp"] = True
        if "statement of work" in content_lower or "sow" in filename_lower:
            doc_type["is_sow"] = True
        if "pricing" in content_lower or "cost" in content_lower:
            doc_type["is_pricing"] = True
        if "technical" in content_lower:
            doc_type["is_technical"] = True
        
        # Check services mentioned
        if "warehouse" in content_lower:
            doc_type["services_mentioned"].append(ServiceType.WAREHOUSE)
        if "customer service" in content_lower or "cso" in content_lower or "rma" in content_lower:
            doc_type["services_mentioned"].append(ServiceType.CSO)
        if "csg" in content_lower or "kitting" in content_lower or "packaging" in content_lower:
            doc_type["services_mentioned"].append(ServiceType.CSG)
        
        # Check service model
        if "consolidated" in content_lower:
            doc_type["model_type"] = ServiceModel.CONSOLIDATED
        elif "standalone" in content_lower:
            doc_type["model_type"] = ServiceModel.STANDALONE
        
        return doc_type

class VendorProfile:
    """Vendor profile for RFP response"""
    def __init__(self, vendor_id: str, name: str, service_model: str):
        self.vendor_id = vendor_id
        self.name = name
        self.service_model = service_model
        self.services_offered = []
        self.registration_date = datetime.now()
        self.documents = {}
        self.pricing = {}
        self.scores = {}
        self.overall_score = 0
        self.status = "Registered"
        self.submission_date = None
        self.evaluation_date = None
        self.capabilities = {}
        self.certifications = []
        self.strengths = []
        self.weaknesses = []
        self.decision = None
        
    def add_service(self, service_type: str):
        if service_type not in self.services_offered:
            self.services_offered.append(service_type)
    
    def submit_proposal(self, documents: Dict = None):
        if documents:
            self.documents.update(documents)
        self.submission_date = datetime.now()
        self.status = "Submitted"
    
    def evaluate(self, scores: Dict):
        self.scores = scores
        self.overall_score = sum(scores.values()) / len(scores) if scores else 0
        self.evaluation_date = datetime.now()
        self.status = "Evaluated"
        
        self.strengths = [k.replace('_', ' ').title() for k, v in scores.items() if v >= 85]
        self.weaknesses = [k.replace('_', ' ').title() for k, v in scores.items() if v < 70]

class RFPManager:
    """Main RFP management system with persistent state"""
    def __init__(self):
        self.rfp_details = self._initialize_rfp()
        
        # Use session state for persistence
        if st.session_state.workflow_stages is None:
            st.session_state.workflow_stages = self._initialize_workflow()
        
        self.evaluation_criteria = self._get_evaluation_criteria()
        self.selected_vendors = {}
        self.test_mode = False
        
    def _initialize_rfp(self):
        """Initialize RFP details"""
        return {
            "rfp_id": f"RFP-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}",
            "title": "Request for Proposal - Logistics & Warehouse Services",
            "issue_date": datetime.now(),
            "due_date": datetime.now() + timedelta(days=30),
            "services_required": ServiceType.get_all(),
            "service_models": [ServiceModel.STANDALONE, ServiceModel.CONSOLIDATED],
            "budget_range": "$5M - $25M annually",
            "contract_duration": "3 years with 2 optional 1-year extensions"
        }
    
    def _initialize_workflow(self) -> Dict[str, WorkflowStage]:
        """Initialize RFP workflow stages"""
        stages = {}
        
        workflow_definition = [
            {
                "id": "requirements",
                "name": "Requirements Definition",
                "desc": "Define service requirements and prepare RFP documentation",
                "docs": ["Service Requirements", "Budget Approval", "Stakeholder Input"],
                "deliverables": ["RFP Package", "Evaluation Criteria", "SOWs for each service"],
                "duration": "5 days"
            },
            {
                "id": "rfp_publication",
                "name": "RFP Publication",
                "desc": "Publish RFP and invite vendors to participate",
                "docs": ["Complete RFP Package", "Vendor List", "Legal Terms"],
                "deliverables": ["Published RFP", "Vendor Invitations", "Q&A Schedule"],
                "duration": "2 days"
            },
            {
                "id": "vendor_registration",
                "name": "Vendor Registration",
                "desc": "Vendors register and indicate service model preference",
                "docs": ["Vendor Registration Forms", "NDA Agreements"],
                "deliverables": ["Registered Vendor List", "Service Model Selections"],
                "duration": "7 days"
            },
            {
                "id": "qa_clarifications",
                "name": "Q&A and Clarifications",
                "desc": "Address vendor questions and provide clarifications",
                "docs": ["Vendor Questions", "Technical Specifications"],
                "deliverables": ["Q&A Responses", "RFP Addendums"],
                "duration": "5 days"
            },
            {
                "id": "proposal_submission",
                "name": "Proposal Submission",
                "desc": "Receive and validate vendor proposals",
                "docs": ["Technical Proposals", "Pricing Proposals", "Compliance Documents"],
                "deliverables": ["Submission Log", "Completeness Check"],
                "duration": "1 day"
            },
            {
                "id": "initial_evaluation",
                "name": "Initial Evaluation",
                "desc": "Evaluate proposals against requirements",
                "docs": ["Evaluation Matrix", "Scoring Sheets"],
                "deliverables": ["Initial Scores", "Compliance Status"],
                "duration": "7 days"
            },
            {
                "id": "detailed_assessment",
                "name": "Detailed Assessment",
                "desc": "Deep dive into shortlisted vendors",
                "docs": ["Technical Reviews", "Reference Checks", "Site Visit Reports"],
                "deliverables": ["Detailed Evaluation Report", "Risk Assessment"],
                "duration": "10 days"
            },
            {
                "id": "vendor_selection",
                "name": "Vendor Selection",
                "desc": "Select vendors for each service model",
                "docs": ["Final Evaluation", "Selection Criteria"],
                "deliverables": ["Selected Vendors", "Service Assignments"],
                "duration": "3 days"
            },
            {
                "id": "negotiation",
                "name": "Contract Negotiation",
                "desc": "Negotiate terms with selected vendors",
                "docs": ["Draft Contracts", "SLAs", "Pricing Agreements"],
                "deliverables": ["Negotiated Terms", "Final Pricing"],
                "duration": "7 days"
            },
            {
                "id": "award",
                "name": "Contract Award",
                "desc": "Award contracts to selected vendors",
                "docs": ["Final Contracts", "Legal Approval"],
                "deliverables": ["Executed Contracts", "Implementation Schedule"],
                "duration": "2 days"
            },
            {
                "id": "implementation",
                "name": "Implementation Planning",
                "desc": "Plan service transition and implementation",
                "docs": ["Transition Plan", "Resource Allocation"],
                "deliverables": ["Kickoff Meeting", "Go-Live Schedule"],
                "duration": "5 days"
            }
        ]
        
        for idx, stage_def in enumerate(workflow_definition, 1):
            stages[stage_def["id"]] = WorkflowStage(
                stage_def["id"],
                idx,
                stage_def["name"],
                stage_def["desc"],
                stage_def["docs"],
                stage_def["deliverables"],
                stage_def["duration"]
            )
        
        return stages
    
    def _get_evaluation_criteria(self) -> Dict:
        """Define evaluation criteria for vendors"""
        return {
            "technical_capability": {
                "weight": 0.25,
                "description": "Technology, systems, and infrastructure"
            },
            "operational_excellence": {
                "weight": 0.20,
                "description": "Service quality, efficiency, and reliability"
            },
            "pricing_competitiveness": {
                "weight": 0.20,
                "description": "Cost structure and value for money"
            },
            "compliance_security": {
                "weight": 0.15,
                "description": "Certifications, security measures, and compliance"
            },
            "experience_references": {
                "weight": 0.10,
                "description": "Past performance and client references"
            },
            "innovation_flexibility": {
                "weight": 0.10,
                "description": "Innovation capabilities and service flexibility"
            }
        }
    
    def get_workflow_progress(self) -> int:
        """Calculate overall workflow progress"""
        stages = st.session_state.workflow_stages
        if not stages:
            return 0
        
        total_stages = len(stages)
        completed = sum(1 for s in stages.values() if s.status == "complete")
        active_progress = sum(s.progress/100 for s in stages.values() if s.status == "active")
        
        return int(((completed + active_progress) / total_stages) * 100)
    
    def register_vendor(self, name: str, service_model: str, services: List[str]) -> VendorProfile:
        """Register a new vendor"""
        vendor_id = f"VND-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        vendor = VendorProfile(vendor_id, name, service_model)
        
        for service in services:
            vendor.add_service(service)
        
        st.session_state.vendors[vendor_id] = vendor
        return vendor
    
    def evaluate_vendor(self, vendor_id: str) -> Dict:
        """Evaluate a vendor's proposal"""
        if vendor_id not in st.session_state.vendors:
            return {}
        
        vendor = st.session_state.vendors[vendor_id]
        
        # Generate scores based on service model and documents
        base_score = 70
        
        # Bonus for consolidated model
        if vendor.service_model == ServiceModel.CONSOLIDATED:
            base_score += 5
        
        # Bonus for complete documentation
        if len(vendor.documents) > 3:
            base_score += 5
        
        # Score each criterion
        scores = {}
        for criterion, details in self.evaluation_criteria.items():
            variation = random.uniform(-10, 15)
            scores[criterion] = min(100, max(50, base_score + variation))
        
        vendor.evaluate(scores)
        return scores

# ========================================
# UI COMPONENTS
# ========================================

def render_header():
    """Render application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 RFP Vendor Evaluation Platform</h1>
        <h3>Comprehensive Logistics & Warehouse Services Procurement</h3>
        <p>Supporting Standalone and Consolidated Service Models</p>
    </div>
    """, unsafe_allow_html=True)

def render_document_upload():
    """Render comprehensive document upload section"""
    st.header("📄 Document Management")
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload RFP Documents", "📥 Vendor Proposals", "📁 View Documents"])
    
    with tab1:
        st.subheader("Upload RFP Documents")
        st.info("Upload your RFP documents - either a single consolidated RFP or multiple service-specific documents")
        
        # Upload options
        upload_type = st.radio(
            "Document Type",
            ["Single Consolidated RFP", "Multiple Service-Specific Documents"],
            horizontal=True
        )
        
        if upload_type == "Single Consolidated RFP":
            st.markdown("### Upload Consolidated RFP Document")
            
            uploaded_file = st.file_uploader(
                "Choose RFP document",
                type=['pdf', 'docx', 'doc', 'txt'],
                key="consolidated_rfp",
                help="Upload a single document containing all service requirements"
            )
            
            if uploaded_file:
                # Process the document
                doc_info = DocumentManager.extract_text_from_file(uploaded_file)
                doc_analysis = DocumentManager.identify_document_type(doc_info["content"], doc_info["name"])
                
                # Store in session state
                st.session_state.rfp_documents["consolidated"] = doc_info
                
                # Display analysis
                st.success(f"✅ Uploaded: {uploaded_file.name}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Size", f"{doc_info['size'] / 1024:.1f} KB")
                with col2:
                    st.metric("Document Type", "RFP" if doc_analysis["is_rfp"] else "Other")
                with col3:
                    services_found = len(doc_analysis["services_mentioned"])
                    st.metric("Services Identified", services_found)
                
                if doc_analysis["services_mentioned"]:
                    st.write("**Services Found:**")
                    for service in doc_analysis["services_mentioned"]:
                        if service == ServiceType.WAREHOUSE:
                            st.markdown('<span class="service-tag service-warehouse">Warehouse</span>', 
                                      unsafe_allow_html=True)
                        elif service == ServiceType.CSO:
                            st.markdown('<span class="service-tag service-cso">CSO</span>', 
                                      unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="service-tag service-csg">CSG</span>', 
                                      unsafe_allow_html=True)
                
                # Update workflow
                if "requirements" in st.session_state.workflow_stages:
                    stage = st.session_state.workflow_stages["requirements"]
                    if stage.status == "pending":
                        stage.start()
                    stage.update_progress(50)
        
        else:  # Multiple Service-Specific Documents
            st.markdown("### Upload Service-Specific Documents")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### Warehouse Services")
                warehouse_doc = st.file_uploader(
                    "Warehouse SOW",
                    type=['pdf', 'docx', 'doc', 'txt'],
                    key="warehouse_sow"
                )
                if warehouse_doc:
                    doc_info = DocumentManager.extract_text_from_file(warehouse_doc)
                    st.session_state.rfp_documents["warehouse"] = doc_info
                    st.success(f"✅ {warehouse_doc.name}")
            
            with col2:
                st.markdown("#### CSO Services")
                cso_doc = st.file_uploader(
                    "CSO SOW",
                    type=['pdf', 'docx', 'doc', 'txt'],
                    key="cso_sow"
                )
                if cso_doc:
                    doc_info = DocumentManager.extract_text_from_file(cso_doc)
                    st.session_state.rfp_documents["cso"] = doc_info
                    st.success(f"✅ {cso_doc.name}")
            
            with col3:
                st.markdown("#### CSG Services")
                csg_doc = st.file_uploader(
                    "CSG SOW",
                    type=['pdf', 'docx', 'doc', 'txt'],
                    key="csg_sow"
                )
                if csg_doc:
                    doc_info = DocumentManager.extract_text_from_file(csg_doc)
                    st.session_state.rfp_documents["csg"] = doc_info
                    st.success(f"✅ {csg_doc.name}")
            
            # Additional documents
            st.markdown("#### Additional Documents")
            additional_docs = st.file_uploader(
                "Upload additional documents (Terms, Conditions, etc.)",
                type=['pdf', 'docx', 'doc', 'txt', 'xlsx', 'xls'],
                accept_multiple_files=True,
                key="additional_docs"
            )
            
            if additional_docs:
                for doc in additional_docs:
                    doc_info = DocumentManager.extract_text_from_file(doc)
                    st.session_state.rfp_documents[f"additional_{doc.name}"] = doc_info
                    st.success(f"✅ {doc.name}")
            
            # Update workflow if documents uploaded
            if len(st.session_state.rfp_documents) > 0:
                if "requirements" in st.session_state.workflow_stages:
                    stage = st.session_state.workflow_stages["requirements"]
                    if stage.status == "pending":
                        stage.start()
                    progress = min(100, 30 * len(st.session_state.rfp_documents))
                    stage.update_progress(progress)
    
    with tab2:
        st.subheader("Vendor Proposal Submission")
        
        # Select vendor
        if st.session_state.vendors:
            vendor_id = st.selectbox(
                "Select Vendor",
                options=list(st.session_state.vendors.keys()),
                format_func=lambda x: st.session_state.vendors[x].name
            )
            
            if vendor_id:
                vendor = st.session_state.vendors[vendor_id]
                
                st.info(f"Uploading documents for: **{vendor.name}** ({vendor.service_model} Model)")
                
                # Document upload based on service model
                if vendor.service_model == ServiceModel.CONSOLIDATED:
                    st.markdown("### Consolidated Proposal Documents")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        technical_doc = st.file_uploader(
                            "Technical Proposal",
                            type=['pdf', 'docx', 'doc'],
                            key=f"tech_{vendor_id}"
                        )
                        if technical_doc:
                            vendor.documents["technical"] = technical_doc.name
                            st.success("✅ Technical Proposal uploaded")
                        
                        pricing_doc = st.file_uploader(
                            "Consolidated Pricing Proposal",
                            type=['pdf', 'docx', 'doc', 'xlsx'],
                            key=f"price_{vendor_id}"
                        )
                        if pricing_doc:
                            vendor.documents["pricing"] = pricing_doc.name
                            st.success("✅ Pricing Proposal uploaded")
                    
                    with col2:
                        compliance_doc = st.file_uploader(
                            "Compliance & Certifications",
                            type=['pdf', 'docx', 'doc'],
                            key=f"comp_{vendor_id}"
                        )
                        if compliance_doc:
                            vendor.documents["compliance"] = compliance_doc.name
                            st.success("✅ Compliance documents uploaded")
                        
                        references = st.file_uploader(
                            "References",
                            type=['pdf', 'docx', 'doc'],
                            key=f"ref_{vendor_id}"
                        )
                        if references:
                            vendor.documents["references"] = references.name
                            st.success("✅ References uploaded")
                
                else:  # Standalone
                    st.markdown(f"### Standalone Proposal for {', '.join(vendor.services_offered)}")
                    
                    for service in vendor.services_offered:
                        st.markdown(f"#### {service} Documents")
                        
                        service_doc = st.file_uploader(
                            f"{service} Proposal",
                            type=['pdf', 'docx', 'doc'],
                            key=f"{service}_{vendor_id}"
                        )
                        if service_doc:
                            vendor.documents[service] = service_doc.name
                            st.success(f"✅ {service} proposal uploaded")
                
                # Submit button
                if st.button(f"Submit Proposal for {vendor.name}", type="primary"):
                    vendor.submit_proposal()
                    st.success(f"✅ Proposal submitted for {vendor.name}!")
                    
                    # Update workflow
                    if "proposal_submission" in st.session_state.workflow_stages:
                        stage = st.session_state.workflow_stages["proposal_submission"]
                        if stage.status == "pending":
                            stage.start()
                        submitted_count = sum(1 for v in st.session_state.vendors.values() 
                                            if v.status == "Submitted")
                        progress = min(100, submitted_count * 20)
                        stage.update_progress(progress)
                    
                    st.rerun()
        else:
            st.warning("No vendors registered yet. Please register vendors first.")
    
    with tab3:
        st.subheader("Document Repository")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### RFP Documents")
            if st.session_state.rfp_documents:
                for doc_key, doc_info in st.session_state.rfp_documents.items():
                    st.markdown(f"""
                    <div class="document-card">
                        <div>
                            📄 <strong>{doc_info['name']}</strong><br>
                            <small>{doc_info['size'] / 1024:.1f} KB | Uploaded: {doc_info['upload_date'].strftime('%Y-%m-%d %H:%M')}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No RFP documents uploaded yet")
        
        with col2:
            st.markdown("### Vendor Documents")
            if st.session_state.vendors:
                for vendor in st.session_state.vendors.values():
                    if vendor.documents:
                        st.markdown(f"**{vendor.name}** ({vendor.status})")
                        for doc_type, doc_name in vendor.documents.items():
                            st.write(f"• {doc_type}: {doc_name}")
            else:
                st.info("No vendor documents uploaded yet")

def render_workflow_management(manager: RFPManager):
    """Render workflow management section with working stages"""
    st.header("⚙️ RFP Workflow Management")
    
    # Overall progress
    progress = manager.get_workflow_progress()
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress}%;">
            Overall Progress: {progress}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Workflow stages
    stages = st.session_state.workflow_stages
    stage_list = list(stages.values())
    
    for idx, stage in enumerate(stage_list):
        prev_stage = stage_list[idx - 1] if idx > 0 else None
        
        # Determine styling
        if stage.status == "complete":
            icon = "✅"
            card_class = "stage-complete"
        elif stage.status == "active":
            icon = "🔄"
            card_class = "stage-active"
        else:
            icon = "⏳"
            card_class = "stage-pending"
        
        with st.expander(f"{icon} **Stage {stage.stage_num}: {stage.name}** ({stage.status.upper()})", 
                        expanded=(stage.status == "active")):
            
            col1, col2, col3 = st.columns([4, 3, 3])
            
            with col1:
                st.write(f"**Description:** {stage.description}")
                st.write(f"**Duration:** {stage.duration}")
                
                if stage.status == "active":
                    new_progress = st.slider(
                        "Progress", 0, 100, stage.progress,
                        key=f"progress_{stage.stage_id}_{idx}"
                    )
                    if new_progress != stage.progress:
                        stage.update_progress(new_progress)
                        st.rerun()
                elif stage.status == "complete":
                    st.progress(1.0)
                    if stage.end_date:
                        st.caption(f"Completed: {stage.end_date.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                st.write("**Required Documents:**")
                for doc in stage.required_docs[:3]:
                    st.caption(f"• {doc}")
                if len(stage.required_docs) > 3:
                    st.caption(f"...and {len(stage.required_docs) - 3} more")
            
            with col3:
                if stage.status == "pending":
                    if st.button(f"▶️ Start Stage", key=f"start_{stage.stage_id}_{idx}", type="primary"):
                        if stage.can_start(prev_stage):
                            if stage.start():
                                st.success(f"Started: {stage.name}")
                                st.rerun()
                        else:
                            st.error(f"Please complete '{prev_stage.name}' first!")
                
                elif stage.status == "active":
                    if stage.progress >= 100:
                        if st.button(f"✔️ Complete Stage", key=f"complete_{stage.stage_id}_{idx}", 
                                    type="primary"):
                            if stage.complete():
                                st.success(f"Completed: {stage.name}")
                                st.rerun()
                    else:
                        st.info(f"Progress: {stage.progress}%")

def render_vendor_management(manager: RFPManager):
    """Render vendor management section"""
    st.header("👥 Vendor Management")
    
    # Add vendor section
    with st.expander("➕ Register New Vendor", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            vendor_name = st.text_input("Vendor Name", key="new_vendor_name")
        
        with col2:
            service_model = st.selectbox(
                "Service Model",
                [ServiceModel.STANDALONE, ServiceModel.CONSOLIDATED],
                format_func=lambda x: f"{x} - {ServiceModel.get_description(x)}",
                key="new_vendor_model"
            )
        
        with col3:
            if service_model == ServiceModel.CONSOLIDATED:
                services = st.multiselect(
                    "Services Offered",
                    ServiceType.get_all(),
                    default=ServiceType.get_all(),
                    key="new_vendor_services"
                )
            else:
                service = st.selectbox(
                    "Service Offered",
                    ServiceType.get_all(),
                    key="new_vendor_service"
                )
                services = [service]
        
        if st.button("Register Vendor", type="primary", disabled=not vendor_name):
            if vendor_name and services:
                vendor = manager.register_vendor(vendor_name, service_model, services)
                st.success(f"✅ Registered: {vendor.name} (ID: {vendor.vendor_id})")
                
                # Update workflow
                if "vendor_registration" in st.session_state.workflow_stages:
                    stage = st.session_state.workflow_stages["vendor_registration"]
                    if stage.status == "pending":
                        stage.start()
                    vendor_count = len(st.session_state.vendors)
                    progress = min(100, vendor_count * 20)
                    stage.update_progress(progress)
                
                st.rerun()
    
    # Display vendors
    if st.session_state.vendors:
        st.subheader("Registered Vendors")
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Vendors", len(st.session_state.vendors))
        with col2:
            submitted = sum(1 for v in st.session_state.vendors.values() if v.status != "Registered")
            st.metric("Proposals Submitted", submitted)
        with col3:
            evaluated = sum(1 for v in st.session_state.vendors.values() if v.status == "Evaluated")
            st.metric("Evaluated", evaluated)
        with col4:
            consolidated = sum(1 for v in st.session_state.vendors.values() 
                             if v.service_model == ServiceModel.CONSOLIDATED)
            st.metric("Consolidated Model", consolidated)
        
        # Vendor cards
        for vendor in st.session_state.vendors.values():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    st.markdown(f"### {vendor.name}")
                    st.caption(f"ID: {vendor.vendor_id}")
                    
                    for service in vendor.services_offered:
                        if service == ServiceType.WAREHOUSE:
                            tag = '<span class="service-tag service-warehouse">Warehouse</span>'
                        elif service == ServiceType.CSO:
                            tag = '<span class="service-tag service-cso">CSO</span>'
                        else:
                            tag = '<span class="service-tag service-csg">CSG</span>'
                        st.markdown(tag, unsafe_allow_html=True)
                
                with col2:
                    st.write(f"**Model:** {vendor.service_model}")
                    st.write(f"**Status:** {vendor.status}")
                    if vendor.submission_date:
                        st.caption(f"Submitted: {vendor.submission_date.strftime('%Y-%m-%d')}")
                
                with col3:
                    if vendor.overall_score > 0:
                        if vendor.overall_score >= 85:
                            badge_class = "score-excellent"
                        elif vendor.overall_score >= 75:
                            badge_class = "score-good"
                        elif vendor.overall_score >= 65:
                            badge_class = "score-fair"
                        else:
                            badge_class = "score-poor"
                        
                        st.markdown(f'<div class="score-badge {badge_class}">Score: {vendor.overall_score:.1f}</div>',
                                  unsafe_allow_html=True)
                
                with col4:
                    if vendor.status == "Submitted" and vendor.overall_score == 0:
                        if st.button("📊 Evaluate", key=f"eval_{vendor.vendor_id}"):
                            scores = manager.evaluate_vendor(vendor.vendor_id)
                            st.success(f"Evaluated: {vendor.overall_score:.1f}/100")
                            
                            # Update workflow
                            if "initial_evaluation" in st.session_state.workflow_stages:
                                stage = st.session_state.workflow_stages["initial_evaluation"]
                                if stage.status == "pending":
                                    stage.start()
                                evaluated = sum(1 for v in st.session_state.vendors.values() 
                                              if v.status == "Evaluated")
                                progress = min(100, evaluated * 25)
                                stage.update_progress(progress)
                            
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("No vendors registered yet. Use the form above to register vendors.")

def render_sidebar(manager: RFPManager):
    """Render sidebar"""
    with st.sidebar:
        st.markdown("### 🎯 RFP Management")
        
        # Test Mode
        test_mode = st.checkbox(
            "Enable Test Mode",
            value=st.session_state.get('test_mode', False),
            help="Load sample vendors and documents for testing"
        )
        
        if test_mode != st.session_state.get('test_mode', False):
            st.session_state.test_mode = test_mode
            if test_mode:
                # Generate test data
                from .sample_data_generator import SampleDataGenerator
                generator = SampleDataGenerator()
                
                # Create test vendors
                test_vendors_data = [
                    ("Global Logistics Solutions", ServiceModel.CONSOLIDATED, ServiceType.get_all()),
                    ("Premier Warehousing Inc.", ServiceModel.STANDALONE, [ServiceType.WAREHOUSE]),
                    ("Customer Service Experts", ServiceModel.STANDALONE, [ServiceType.CSO]),
                    ("Packaging Solutions Corp.", ServiceModel.STANDALONE, [ServiceType.CSG]),
                    ("Integrated Services LLC", ServiceModel.CONSOLIDATED, ServiceType.get_all())
                ]
                
                for name, model, services in test_vendors_data:
                    vendor = manager.register_vendor(name, model, services)
                    vendor.submit_proposal({"test": "Test Document"})
                    manager.evaluate_vendor(vendor.vendor_id)
                
                st.success("✅ Test data loaded!")
                st.rerun()
        
        st.markdown("---")
        
        # RFP Info
        st.markdown("### 📋 RFP Details")
        st.caption(f"**ID:** {manager.rfp_details['rfp_id']}")
        st.caption(f"**Budget:** {manager.rfp_details['budget_range']}")
        
        days_remaining = (manager.rfp_details['due_date'] - datetime.now()).days
        if days_remaining > 0:
            st.success(f"📅 {days_remaining} days until due date")
        else:
            st.error("⚠️ RFP overdue")
        
        # Progress
        st.markdown("### 📊 Progress")
        progress = manager.get_workflow_progress()
        st.progress(progress / 100)
        st.caption(f"{progress}% Complete")
        
        # Document Stats
        st.markdown("### 📄 Documents")
        st.metric("RFP Documents", len(st.session_state.rfp_documents))
        
        vendor_docs = sum(len(v.documents) for v in st.session_state.vendors.values())
        st.metric("Vendor Documents", vendor_docs)

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    """Main application"""
    
    # Initialize
    manager = RFPManager()
    
    # Render UI
    render_header()
    
    if st.session_state.get('test_mode', False):
        st.markdown("""
        <div class="test-mode-banner">
            🧪 TEST MODE - Sample data loaded for demonstration
        </div>
        """, unsafe_allow_html=True)
    
    render_sidebar(manager)
    
    # Main content tabs
    tabs = st.tabs([
        "📄 Documents",
        "⚙️ Workflow",
        "👥 Vendors",
        "📊 Evaluation",
        "🎯 Selection"
    ])
    
    with tabs[0]:
        render_document_upload()
    
    with tabs[1]:
        render_workflow_management(manager)
    
    with tabs[2]:
        render_vendor_management(manager)
    
    with tabs[3]:
        st.header("📊 Vendor Evaluation")
        evaluated = [v for v in st.session_state.vendors.values() if v.status == "Evaluated"]
        
        if evaluated:
            # Comparison chart
            vendor_names = [v.name for v in evaluated]
            scores = [v.overall_score for v in evaluated]
            models = [v.service_model for v in evaluated]
            
            fig = go.Figure()
            colors = ['#3b82f6' if m == ServiceModel.CONSOLIDATED else '#10b981' for m in models]
            
            fig.add_trace(go.Bar(
                x=vendor_names,
                y=scores,
                marker_color=colors,
                text=[f'{s:.1f}' for s in scores],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Vendor Score Comparison",
                xaxis_title="Vendors",
                yaxis_title="Overall Score",
                yaxis_range=[0, 100]
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No vendors evaluated yet. Submit proposals and evaluate vendors first.")
    
    with tabs[4]:
        st.header("🎯 Vendor Selection")
        st.info("Select vendors for each service based on evaluation scores")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>RFP Vendor Evaluation Platform v3.0</p>
        <p>Complete Document Management • Full Workflow Support • Multi-Service Models</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
