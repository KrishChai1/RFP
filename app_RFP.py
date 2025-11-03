"""
🎯 RFP Vendor Evaluation & Selection Platform
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enterprise platform for evaluating and selecting logistics service providers
Supporting Warehouse, Customer Service Operations, and Fulfillment Services
Full document upload support and comprehensive workflow testing
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import re
from datetime import datetime, timedelta
import io
import uuid
from typing import Dict, List, Optional, Tuple, Any
import base64
import time
import random
import zipfile

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
if 'selected_vendors' not in st.session_state:
    st.session_state.selected_vendors = {}
if 'test_data_generated' not in st.session_state:
    st.session_state.test_data_generated = False

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
    
    .document-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .document-upload-zone {
        border: 2px dashed var(--secondary);
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f0f9ff;
        margin: 1rem 0;
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
    }
    
    .test-control-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
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
                "Storage capacity (minimum 500,000 sq ft)",
                "Temperature-controlled zones (ambient, cooled, frozen)",
                "24/7 operations capability with 99.9% uptime",
                "WMS integration (SAP EWM, Manhattan, or equivalent)",
                "Cross-docking and transloading capabilities",
                "Security: C-TPAT and TAPA certifications required"
            ],
            ServiceType.CSO: [
                "RMA processing (same-day turnaround)",
                "Returns management system integration",
                "Customer support (24/7, multi-channel)",
                "Replacement fulfillment within 24 hours",
                "Quality inspection processes (99.5% accuracy)",
                "Response time SLAs (< 2 hours)"
            ],
            ServiceType.CSG: [
                "Kitting services (10,000+ units/day capacity)",
                "Custom packaging capabilities",
                "Assembly operations (electronics, mechanical)",
                "Labeling services (barcode, RFID)",
                "Custom fulfillment solutions",
                "Quality control (Six Sigma processes)"
            ]
        }
        return requirements.get(service, [])

class WorkflowStage:
    """RFP workflow stages"""
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
        if previous_stage is None:
            return True
        return previous_stage.status == "complete"
    
    def start(self):
        self.status = "active"
        self.start_date = datetime.now()
        self.progress = 10
        return True
        
    def complete(self):
        self.status = "complete"
        self.end_date = datetime.now()
        self.progress = 100
        return True
        
    def update_progress(self, progress: int):
        self.progress = min(100, max(0, progress))
        if self.progress == 100 and self.status != "complete":
            self.complete()
        return True

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

class TestDataGenerator:
    """Generate comprehensive test data for workflow testing"""
    
    def __init__(self):
        self.vendor_names = [
            "Global Logistics Partners LLC",
            "Integrated Warehouse Solutions Inc.",
            "Premier Distribution Services",
            "NextGen Fulfillment Corp.",
            "Strategic Supply Chain Co.",
            "National Logistics Network",
            "Express Warehouse Group",
            "Unified Transport Solutions"
        ]
        
        self.company_names = [
            "Tech Corp", "Global Industries", "Future Systems", "Prime Solutions",
            "Advanced Logistics", "Smart Supply", "Digital Warehouse", "Rapid Fulfillment"
        ]
    
    def generate_sample_rfp_documents(self) -> Dict:
        """Generate sample RFP documents"""
        docs = {
            "main_rfp": {
                "name": "RFP_Logistics_Services_2025.pdf",
                "type": "application/pdf",
                "size": 2048576,
                "content": self._generate_rfp_content(),
                "upload_date": datetime.now()
            },
            "warehouse_sow": {
                "name": "Warehouse_Services_SOW.docx",
                "type": "application/docx",
                "size": 1024768,
                "content": self._generate_sow_content(ServiceType.WAREHOUSE),
                "upload_date": datetime.now()
            },
            "cso_sow": {
                "name": "CSO_Services_SOW.docx",
                "type": "application/docx",
                "size": 896432,
                "content": self._generate_sow_content(ServiceType.CSO),
                "upload_date": datetime.now()
            },
            "csg_sow": {
                "name": "CSG_Services_SOW.docx",
                "type": "application/docx",
                "size": 754892,
                "content": self._generate_sow_content(ServiceType.CSG),
                "upload_date": datetime.now()
            }
        }
        return docs
    
    def _generate_rfp_content(self) -> str:
        """Generate sample RFP content"""
        return f"""
        REQUEST FOR PROPOSAL (RFP)
        RFP Number: RFP-{datetime.now().year}-{random.randint(1000,9999)}
        Issue Date: {datetime.now().strftime('%B %d, %Y')}
        Due Date: {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')}
        
        EXECUTIVE SUMMARY:
        We are seeking qualified vendors to provide comprehensive logistics and warehouse services
        for our distribution network. This RFP encompasses warehousing, customer service operations (CSO),
        and consumer solutions group (CSG) services.
        
        SERVICE MODELS:
        1. Standalone Model: Single vendor for one specific service
        2. Consolidated Model: Single vendor for multiple integrated services
        
        EVALUATION CRITERIA:
        - Technical Capability: 25%
        - Operational Excellence: 20%
        - Pricing Competitiveness: 20%
        - Compliance & Security: 15%
        - Experience & References: 10%
        - Innovation & Flexibility: 10%
        
        Budget Range: $5M - $25M annually
        Contract Duration: 3 years with 2 optional 1-year extensions
        """
    
    def _generate_sow_content(self, service_type: str) -> str:
        """Generate sample SOW content for a specific service"""
        requirements = ServiceType.get_requirements(service_type)
        req_text = "\n".join([f"- {req}" for req in requirements])
        
        return f"""
        STATEMENT OF WORK (SOW)
        Service: {service_type}
        
        SCOPE OF SERVICES:
        The vendor shall provide comprehensive {service_type} including but not limited to:
        
        KEY REQUIREMENTS:
        {req_text}
        
        PERFORMANCE METRICS:
        - Service Level Agreement: 99.5% uptime
        - Quality Standards: Six Sigma processes
        - Response Time: Based on service type
        - Compliance: All industry standards
        
        PRICING MODEL:
        - Unit-based pricing for standalone model
        - Consolidated pricing for integrated services
        - Volume discounts available
        """
    
    def generate_sample_vendors(self, count: int = 8) -> List[VendorProfile]:
        """Generate sample vendors with different configurations"""
        vendors = []
        
        # Generate mix of consolidated and standalone vendors
        for i in range(count):
            vendor_id = f"VND-TEST-{str(uuid.uuid4())[:8].upper()}"
            name = self.vendor_names[i % len(self.vendor_names)]
            
            # First 3 vendors are consolidated, rest are standalone
            if i < 3:
                model = ServiceModel.CONSOLIDATED
                services = ServiceType.get_all()
            else:
                model = ServiceModel.STANDALONE
                # Distribute standalone vendors across services
                service_index = (i - 3) % 3
                services = [ServiceType.get_all()[service_index]]
            
            vendor = VendorProfile(vendor_id, name, model)
            for service in services:
                vendor.add_service(service)
            
            # Add sample documents
            vendor.documents = {
                "technical": f"{name}_Technical_Proposal.pdf",
                "pricing": f"{name}_Pricing_Proposal.xlsx",
                "compliance": f"{name}_Certifications.pdf",
                "references": f"{name}_References.pdf"
            }
            
            # Set vendor at different stages for testing
            if i < 2:  # First 2 vendors are fully evaluated
                vendor.submit_proposal(vendor.documents)
                scores = self._generate_evaluation_scores(i)
                vendor.evaluate(scores)
            elif i < 5:  # Next 3 have submitted proposals
                vendor.submit_proposal(vendor.documents)
            # Rest are just registered
            
            vendors.append(vendor)
        
        return vendors
    
    def _generate_evaluation_scores(self, quality_tier: int) -> Dict:
        """Generate evaluation scores based on tier"""
        base_scores = {
            0: 90,  # Excellent
            1: 82,  # Good
            2: 75,  # Fair
            3: 68,  # Marginal
            4: 60   # Poor
        }
        
        base = base_scores.get(quality_tier, 70)
        
        return {
            "technical_capability": base + random.uniform(-5, 5),
            "operational_excellence": base + random.uniform(-5, 5),
            "pricing_competitiveness": base + random.uniform(-10, 5),
            "compliance_security": base + random.uniform(-3, 7),
            "experience_references": base + random.uniform(-5, 5),
            "innovation_flexibility": base + random.uniform(-7, 3)
        }
    
    def progress_workflow_to_stage(self, stages: Dict, target_stage_num: int):
        """Progress workflow to a specific stage"""
        stage_list = list(stages.values())
        
        for i in range(min(target_stage_num, len(stage_list))):
            stage = stage_list[i]
            if i < target_stage_num - 1:
                # Complete stages before target
                stage.status = "complete"
                stage.progress = 100
                stage.end_date = datetime.now() - timedelta(days=(target_stage_num - i))
            elif i == target_stage_num - 1:
                # Make target stage active
                stage.status = "active"
                stage.progress = random.randint(30, 70)
                stage.start_date = datetime.now()

class RFPManager:
    """Main RFP management system"""
    def __init__(self):
        self.rfp_details = self._initialize_rfp()
        
        # Initialize workflow stages in session state
        if st.session_state.workflow_stages is None:
            st.session_state.workflow_stages = self._initialize_workflow()
        
        self.evaluation_criteria = self._get_evaluation_criteria()
        self.test_generator = TestDataGenerator()
        
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
                "deliverables": ["RFP Package", "Evaluation Criteria", "SOWs"],
                "duration": "5 days"
            },
            {
                "id": "rfp_publication",
                "name": "RFP Publication",
                "desc": "Publish RFP and invite vendors to participate",
                "docs": ["RFP Package", "Vendor List", "Legal Terms"],
                "deliverables": ["Published RFP", "Vendor Invitations"],
                "duration": "2 days"
            },
            {
                "id": "vendor_registration",
                "name": "Vendor Registration",
                "desc": "Vendors register and indicate service model preference",
                "docs": ["Registration Forms", "NDA Agreements"],
                "deliverables": ["Vendor List", "Service Model Selections"],
                "duration": "7 days"
            },
            {
                "id": "qa_clarifications",
                "name": "Q&A and Clarifications",
                "desc": "Address vendor questions and provide clarifications",
                "docs": ["Vendor Questions", "Technical Specs"],
                "deliverables": ["Q&A Responses", "RFP Addendums"],
                "duration": "5 days"
            },
            {
                "id": "proposal_submission",
                "name": "Proposal Submission",
                "desc": "Receive and validate vendor proposals",
                "docs": ["Technical Proposals", "Pricing", "Compliance"],
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
                "docs": ["Technical Reviews", "Reference Checks"],
                "deliverables": ["Evaluation Report", "Risk Assessment"],
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
                "docs": ["Draft Contracts", "SLAs", "Pricing"],
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
        """Define evaluation criteria"""
        return {
            "technical_capability": {"weight": 0.25, "description": "Technology and infrastructure"},
            "operational_excellence": {"weight": 0.20, "description": "Service quality and reliability"},
            "pricing_competitiveness": {"weight": 0.20, "description": "Cost structure and value"},
            "compliance_security": {"weight": 0.15, "description": "Certifications and security"},
            "experience_references": {"weight": 0.10, "description": "Past performance"},
            "innovation_flexibility": {"weight": 0.10, "description": "Innovation capabilities"}
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
    
    def evaluate_vendor(self, vendor_id: str) -> Dict:
        """Evaluate a vendor"""
        if vendor_id not in st.session_state.vendors:
            return {}
        
        vendor = st.session_state.vendors[vendor_id]
        
        # Generate scores
        base_score = 70
        if vendor.service_model == ServiceModel.CONSOLIDATED:
            base_score += 5
        
        scores = {}
        for criterion in self.evaluation_criteria.keys():
            scores[criterion] = min(100, max(50, base_score + random.uniform(-10, 15)))
        
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
        <p>Complete Workflow Testing • Document Management • Vendor Selection</p>
    </div>
    """, unsafe_allow_html=True)

def render_test_controls(manager: RFPManager):
    """Render test data generation controls"""
    st.header("🧪 Test Data Generator")
    
    st.markdown("""
    <div class="test-control-card">
        <h3>Generate Test Data for Complete Workflow Testing</h3>
        <p>Create sample RFP documents, vendors, and progress through workflow stages</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📄 RFP Documents")
        if st.button("Generate RFP Documents", type="primary", use_container_width=True):
            docs = manager.test_generator.generate_sample_rfp_documents()
            st.session_state.rfp_documents.update(docs)
            st.success(f"✅ Generated {len(docs)} RFP documents")
            st.rerun()
        
        if st.session_state.rfp_documents:
            st.success(f"✓ {len(st.session_state.rfp_documents)} documents loaded")
            for doc_key, doc in list(st.session_state.rfp_documents.items())[:3]:
                st.caption(f"• {doc['name']}")
    
    with col2:
        st.subheader("👥 Vendors")
        vendor_count = st.number_input("Number of vendors", min_value=3, max_value=10, value=8)
        if st.button("Generate Vendors", type="primary", use_container_width=True):
            vendors = manager.test_generator.generate_sample_vendors(vendor_count)
            for vendor in vendors:
                st.session_state.vendors[vendor.vendor_id] = vendor
            st.success(f"✅ Generated {len(vendors)} vendors")
            st.rerun()
        
        if st.session_state.vendors:
            st.success(f"✓ {len(st.session_state.vendors)} vendors registered")
            consolidated = sum(1 for v in st.session_state.vendors.values() 
                             if v.service_model == ServiceModel.CONSOLIDATED)
            st.caption(f"• {consolidated} Consolidated")
            st.caption(f"• {len(st.session_state.vendors) - consolidated} Standalone")
    
    with col3:
        st.subheader("⚙️ Workflow Progress")
        target_stage = st.selectbox(
            "Progress to stage",
            options=range(1, 12),
            format_func=lambda x: f"Stage {x}: {list(st.session_state.workflow_stages.values())[x-1].name}"
        )
        
        if st.button("Set Workflow Progress", type="primary", use_container_width=True):
            manager.test_generator.progress_workflow_to_stage(
                st.session_state.workflow_stages, 
                target_stage
            )
            st.success(f"✅ Progressed to stage {target_stage}")
            st.rerun()
        
        current_progress = manager.get_workflow_progress()
        st.progress(current_progress / 100)
        st.caption(f"Overall: {current_progress}% complete")
    
    # Quick setup options
    st.subheader("🚀 Quick Setup Scenarios")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Initial Setup", use_container_width=True):
            # Generate everything at stage 1
            docs = manager.test_generator.generate_sample_rfp_documents()
            st.session_state.rfp_documents.update(docs)
            vendors = manager.test_generator.generate_sample_vendors(8)
            for vendor in vendors:
                st.session_state.vendors[vendor.vendor_id] = vendor
            manager.test_generator.progress_workflow_to_stage(st.session_state.workflow_stages, 1)
            st.success("✅ Initial setup complete")
            st.rerun()
    
    with col2:
        if st.button("📊 Mid-Evaluation", use_container_width=True):
            # Setup at evaluation stage
            if not st.session_state.rfp_documents:
                docs = manager.test_generator.generate_sample_rfp_documents()
                st.session_state.rfp_documents.update(docs)
            if not st.session_state.vendors:
                vendors = manager.test_generator.generate_sample_vendors(8)
                for vendor in vendors:
                    st.session_state.vendors[vendor.vendor_id] = vendor
            manager.test_generator.progress_workflow_to_stage(st.session_state.workflow_stages, 6)
            st.success("✅ Setup at evaluation stage")
            st.rerun()
    
    with col3:
        if st.button("🎯 Selection Ready", use_container_width=True):
            # Setup ready for selection
            if not st.session_state.rfp_documents:
                docs = manager.test_generator.generate_sample_rfp_documents()
                st.session_state.rfp_documents.update(docs)
            if not st.session_state.vendors:
                vendors = manager.test_generator.generate_sample_vendors(8)
                for vendor in vendors:
                    st.session_state.vendors[vendor.vendor_id] = vendor
            # Evaluate all vendors
            for vendor in st.session_state.vendors.values():
                if vendor.status == "Submitted":
                    manager.evaluate_vendor(vendor.vendor_id)
            manager.test_generator.progress_workflow_to_stage(st.session_state.workflow_stages, 8)
            st.success("✅ Ready for vendor selection")
            st.rerun()
    
    with col4:
        if st.button("🏁 Near Complete", use_container_width=True):
            # Setup near completion
            if not st.session_state.rfp_documents:
                docs = manager.test_generator.generate_sample_rfp_documents()
                st.session_state.rfp_documents.update(docs)
            if not st.session_state.vendors:
                vendors = manager.test_generator.generate_sample_vendors(8)
                for vendor in vendors:
                    st.session_state.vendors[vendor.vendor_id] = vendor
            manager.test_generator.progress_workflow_to_stage(st.session_state.workflow_stages, 10)
            st.success("✅ Near completion setup")
            st.rerun()
    
    # Clear data option
    st.markdown("---")
    if st.button("🗑️ Clear All Test Data", use_container_width=True):
        st.session_state.vendors = {}
        st.session_state.rfp_documents = {}
        st.session_state.workflow_stages = manager._initialize_workflow()
        st.session_state.test_data_generated = False
        st.success("✅ All test data cleared")
        st.rerun()

def render_workflow_management(manager: RFPManager):
    """Render workflow management"""
    st.header("⚙️ Workflow Management")
    
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
            stage_color = "#10b981"
        elif stage.status == "active":
            icon = "🔄"
            stage_color = "#f59e0b"
        else:
            icon = "⏳"
            stage_color = "#94a3b8"
        
        with st.expander(f"{icon} **Stage {stage.stage_num}: {stage.name}**", expanded=(stage.status == "active")):
            col1, col2, col3 = st.columns([4, 3, 3])
            
            with col1:
                st.write(f"**Status:** {stage.status.upper()}")
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
            
            with col2:
                st.write("**Required Documents:**")
                for doc in stage.required_docs:
                    st.caption(f"• {doc}")
            
            with col3:
                if stage.status == "pending":
                    if st.button(f"▶️ Start", key=f"start_{stage.stage_id}_{idx}"):
                        if stage.can_start(prev_stage):
                            stage.start()
                            st.rerun()
                        else:
                            st.error(f"Complete '{prev_stage.name}' first")
                
                elif stage.status == "active" and stage.progress >= 100:
                    if st.button(f"✔️ Complete", key=f"complete_{stage.stage_id}_{idx}"):
                        stage.complete()
                        st.rerun()

def render_vendor_dashboard(manager: RFPManager):
    """Render vendor dashboard"""
    st.header("👥 Vendor Management")
    
    if not st.session_state.vendors:
        st.info("No vendors registered. Use Test Data Generator to create sample vendors.")
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Vendors", len(st.session_state.vendors))
    with col2:
        evaluated = sum(1 for v in st.session_state.vendors.values() if v.status == "Evaluated")
        st.metric("Evaluated", evaluated)
    with col3:
        consolidated = sum(1 for v in st.session_state.vendors.values() 
                         if v.service_model == ServiceModel.CONSOLIDATED)
        st.metric("Consolidated", consolidated)
    with col4:
        if evaluated > 0:
            avg_score = sum(v.overall_score for v in st.session_state.vendors.values() 
                          if v.status == "Evaluated") / evaluated
            st.metric("Avg Score", f"{avg_score:.1f}")
    
    # Vendor list
    for vendor in st.session_state.vendors.values():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            st.write(f"**{vendor.name}**")
            st.caption(f"ID: {vendor.vendor_id}")
            
            for service in vendor.services_offered:
                if service == ServiceType.WAREHOUSE:
                    st.markdown('<span class="service-tag service-warehouse">Warehouse</span>', unsafe_allow_html=True)
                elif service == ServiceType.CSO:
                    st.markdown('<span class="service-tag service-cso">CSO</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="service-tag service-csg">CSG</span>', unsafe_allow_html=True)
        
        with col2:
            st.write(f"Model: {vendor.service_model}")
            st.write(f"Status: {vendor.status}")
        
        with col3:
            if vendor.overall_score > 0:
                if vendor.overall_score >= 85:
                    badge = "score-excellent"
                elif vendor.overall_score >= 75:
                    badge = "score-good"
                elif vendor.overall_score >= 65:
                    badge = "score-fair"
                else:
                    badge = "score-poor"
                
                st.markdown(f'<div class="score-badge {badge}">Score: {vendor.overall_score:.1f}</div>',
                          unsafe_allow_html=True)
        
        with col4:
            if vendor.status == "Submitted":
                if st.button("Evaluate", key=f"eval_{vendor.vendor_id}"):
                    manager.evaluate_vendor(vendor.vendor_id)
                    st.rerun()
        
        st.markdown("---")

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    """Main application"""
    
    # Initialize manager
    manager = RFPManager()
    
    # Render header
    render_header()
    
    # Test mode banner
    if st.session_state.get('test_mode', False):
        st.markdown("""
        <div class="test-mode-banner">
            🧪 TEST MODE ACTIVE - Use controls below to generate test data
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 RFP Platform")
        
        # Enable test mode
        test_mode = st.checkbox(
            "Enable Test Mode",
            value=st.session_state.get('test_mode', False)
        )
        st.session_state.test_mode = test_mode
        
        st.markdown("---")
        
        # RFP Info
        st.markdown("### 📋 RFP Details")
        st.caption(f"**ID:** {manager.rfp_details['rfp_id']}")
        st.caption(f"**Budget:** {manager.rfp_details['budget_range']}")
        
        # Progress
        st.markdown("### 📊 Progress")
        progress = manager.get_workflow_progress()
        st.progress(progress / 100)
        st.caption(f"{progress}% Complete")
        
        # Stats
        st.markdown("### 📈 Statistics")
        st.metric("Vendors", len(st.session_state.vendors))
        st.metric("Documents", len(st.session_state.rfp_documents))
    
    # Main content
    if st.session_state.test_mode:
        # Show test controls first in test mode
        render_test_controls(manager)
        st.markdown("---")
    
    # Main tabs
    tabs = st.tabs(["⚙️ Workflow", "👥 Vendors", "📊 Evaluation", "🎯 Selection"])
    
    with tabs[0]:
        render_workflow_management(manager)
    
    with tabs[1]:
        render_vendor_dashboard(manager)
    
    with tabs[2]:
        st.header("📊 Vendor Evaluation")
        evaluated = [v for v in st.session_state.vendors.values() if v.status == "Evaluated"]
        
        if evaluated:
            # Create comparison chart
            vendor_names = [v.name[:20] for v in evaluated]
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
            st.info("No vendors evaluated yet. Generate test data and evaluate vendors.")
    
    with tabs[3]:
        st.header("🎯 Vendor Selection")
        evaluated = [v for v in st.session_state.vendors.values() if v.status == "Evaluated"]
        
        if evaluated:
            st.info("Select vendors for each service based on evaluation scores")
            
            # Show top vendors by service model
            consolidated = [v for v in evaluated if v.service_model == ServiceModel.CONSOLIDATED]
            if consolidated:
                st.subheader("Top Consolidated Vendors")
                top_consolidated = sorted(consolidated, key=lambda x: x.overall_score, reverse=True)[:3]
                for vendor in top_consolidated:
                    st.write(f"• **{vendor.name}**: Score {vendor.overall_score:.1f}/100")
            
            st.subheader("Top Standalone Vendors by Service")
            for service in ServiceType.get_all():
                service_vendors = [v for v in evaluated 
                                 if v.service_model == ServiceModel.STANDALONE 
                                 and service in v.services_offered]
                if service_vendors:
                    st.write(f"**{service}:**")
                    top = sorted(service_vendors, key=lambda x: x.overall_score, reverse=True)[0]
                    st.write(f"• {top.name}: Score {top.overall_score:.1f}/100")
        else:
            st.info("No vendors evaluated yet. Complete evaluation before selection.")

if __name__ == "__main__":
    main()
