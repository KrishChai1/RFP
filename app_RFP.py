"""
🎯 RFP Vendor Evaluation & Selection Platform
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enterprise platform for evaluating and selecting logistics service providers
Supporting Warehouse, Customer Service Operations, and Fulfillment Services
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
        opacity: 0.7;
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
    
    .service-model-card {
        background: linear-gradient(135deg, #f3f4f6 0%, #ffffff 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid #e5e7eb;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .service-model-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-color: var(--secondary);
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
    
    .rfp-info-card {
        background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid var(--info);
    }
    
    .document-upload-zone {
        border: 2px dashed var(--secondary);
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f0f9ff;
        margin: 1rem 0;
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
                "Storage capacity (sq ft)",
                "Temperature-controlled zones",
                "24/7 operations capability",
                "Inventory management systems",
                "Cross-docking capabilities"
            ],
            ServiceType.CSO: [
                "RMA processing",
                "Returns management",
                "Customer support",
                "Replacement fulfillment",
                "Quality inspection"
            ],
            ServiceType.CSG: [
                "Kitting services",
                "Packaging capabilities",
                "Assembly operations",
                "Labeling services",
                "Custom fulfillment"
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
        
    def complete(self):
        self.status = "complete"
        self.end_date = datetime.now()
        self.progress = 100
        
    def update_progress(self, progress: int):
        self.progress = min(100, max(0, progress))
        if self.progress == 100 and self.status != "complete":
            self.complete()

class VendorProfile:
    """Vendor profile for RFP response"""
    def __init__(self, vendor_id: str, name: str, service_model: str):
        self.vendor_id = vendor_id
        self.name = name
        self.service_model = service_model  # Standalone or Consolidated
        self.services_offered = []  # Which services they're bidding for
        self.registration_date = datetime.now()
        self.documents = {}
        self.pricing = {}
        self.scores = {}
        self.overall_score = 0
        self.status = "Registered"  # Registered, Submitted, Evaluated, Shortlisted, Selected, Rejected
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
    
    def submit_proposal(self):
        self.submission_date = datetime.now()
        self.status = "Submitted"
    
    def evaluate(self, scores: Dict):
        self.scores = scores
        self.overall_score = sum(scores.values()) / len(scores) if scores else 0
        self.evaluation_date = datetime.now()
        self.status = "Evaluated"
        
        # Auto-categorize strengths and weaknesses
        self.strengths = [k.replace('_', ' ').title() for k, v in scores.items() if v >= 85]
        self.weaknesses = [k.replace('_', ' ').title() for k, v in scores.items() if v < 70]

class RFPManager:
    """Main RFP management system"""
    def __init__(self):
        self.rfp_details = self._initialize_rfp()
        self.workflow_stages = self._initialize_workflow()
        self.vendors = {}
        self.service_requirements = {}
        self.evaluation_criteria = self._get_evaluation_criteria()
        self.selected_vendors = {}  # Service type -> Vendor ID mapping
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
    
    def register_vendor(self, name: str, service_model: str, services: List[str]) -> VendorProfile:
        """Register a new vendor"""
        vendor_id = f"VND-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        vendor = VendorProfile(vendor_id, name, service_model)
        
        for service in services:
            vendor.add_service(service)
        
        self.vendors[vendor_id] = vendor
        return vendor
    
    def evaluate_vendor(self, vendor_id: str) -> Dict:
        """Evaluate a vendor's proposal"""
        if vendor_id not in self.vendors:
            return {}
        
        vendor = self.vendors[vendor_id]
        
        # Generate scores based on service model
        base_score = 70
        
        # Bonus for consolidated model
        if vendor.service_model == ServiceModel.CONSOLIDATED:
            base_score += 5
        
        # Score each criterion
        scores = {}
        for criterion, details in self.evaluation_criteria.items():
            # Add some variation
            variation = random.uniform(-10, 15)
            scores[criterion] = min(100, max(50, base_score + variation))
        
        vendor.evaluate(scores)
        return scores
    
    def select_vendors(self, selections: Dict[str, str]):
        """Select vendors for services"""
        self.selected_vendors = selections
        
        # Update vendor statuses
        for vendor_id, vendor in self.vendors.items():
            if vendor_id in selections.values():
                vendor.status = "Selected"
                vendor.decision = "Winner"
            elif vendor.status == "Evaluated":
                vendor.status = "Rejected"
                vendor.decision = "Not Selected"
    
    def get_workflow_progress(self) -> int:
        """Calculate overall workflow progress"""
        total_stages = len(self.workflow_stages)
        completed = sum(1 for s in self.workflow_stages.values() if s.status == "complete")
        active_progress = sum(s.progress/100 for s in self.workflow_stages.values() if s.status == "active")
        
        return int(((completed + active_progress) / total_stages) * 100)

# ========================================
# SAMPLE DATA GENERATOR
# ========================================

class SampleDataGenerator:
    """Generate sample data for testing"""
    
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
        
        self.fake = Faker()
    
    def generate_rfp_document(self, services: List[str] = None) -> bytes:
        """Generate sample RFP document"""
        if not services:
            services = ServiceType.get_all()
        
        doc = Document()
        
        # Title
        title = doc.add_heading('REQUEST FOR PROPOSAL (RFP)', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('Logistics and Warehouse Services', 1)
        
        # RFP Details
        doc.add_paragraph(f"RFP Number: RFP-{datetime.now().year}-{random.randint(1000, 9999)}")
        doc.add_paragraph(f"Issue Date: {datetime.now().strftime('%B %d, %Y')}")
        doc.add_paragraph(f"Due Date: {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')}")
        
        # Executive Summary
        doc.add_heading('1. Executive Summary', 1)
        doc.add_paragraph(
            "We are seeking qualified vendors to provide comprehensive logistics and warehouse services. "
            "Vendors may bid for individual services (Standalone Model) or multiple integrated services "
            "(Consolidated Model)."
        )
        
        # Service Models
        doc.add_heading('2. Service Models', 1)
        
        doc.add_heading('2.1 Standalone Model', 2)
        doc.add_paragraph("Single vendor for one specific service:")
        for service in services:
            doc.add_paragraph(f"• {service} only", style='List Bullet')
        
        doc.add_heading('2.2 Consolidated Model', 2)
        doc.add_paragraph("Single vendor for multiple integrated services:")
        doc.add_paragraph(f"• All services: {', '.join(services)}", style='List Bullet')
        
        # Service Requirements
        doc.add_heading('3. Service Requirements', 1)
        
        for service in services:
            doc.add_heading(f'3.{services.index(service)+1} {service}', 2)
            requirements = ServiceType.get_requirements(service)
            for req in requirements:
                doc.add_paragraph(f"• {req}", style='List Bullet')
        
        # Evaluation Criteria
        doc.add_heading('4. Evaluation Criteria', 1)
        criteria_list = [
            "Technical Capability (25%)",
            "Operational Excellence (20%)",
            "Pricing Competitiveness (20%)",
            "Compliance & Security (15%)",
            "Experience & References (10%)",
            "Innovation & Flexibility (10%)"
        ]
        for criterion in criteria_list:
            doc.add_paragraph(f"• {criterion}", style='List Bullet')
        
        # Submission Requirements
        doc.add_heading('5. Submission Requirements', 1)
        doc.add_paragraph("Vendors must submit:")
        submission_items = [
            "Technical Proposal",
            "Pricing Proposal (Standalone and/or Consolidated)",
            "Company Profile",
            "Financial Statements",
            "Certifications (ISO, C-TPAT, TAPA)",
            "Implementation Plan",
            "References (minimum 3)"
        ]
        for item in submission_items:
            doc.add_paragraph(f"• {item}", style='List Bullet')
        
        # Save to bytes
        doc_io = io.BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)
        return doc_io.getvalue()
    
    def generate_vendor_proposals(self, vendor_name: str, service_model: str, 
                                 services: List[str]) -> Dict[str, bytes]:
        """Generate vendor proposal documents"""
        proposals = {}
        
        # 1. Technical Proposal
        tech_doc = Document()
        tech_doc.add_heading(f'{vendor_name}', 0)
        tech_doc.add_heading('Technical Proposal', 1)
        
        tech_doc.add_heading('Service Model', 2)
        tech_doc.add_paragraph(f"We are proposing a {service_model} service model")
        
        tech_doc.add_heading('Services Offered', 2)
        for service in services:
            tech_doc.add_paragraph(f"• {service}", style='List Bullet')
        
        tech_doc.add_heading('Technical Capabilities', 2)
        
        if ServiceType.WAREHOUSE in services:
            tech_doc.add_heading('Warehouse Capabilities', 3)
            tech_doc.add_paragraph(f"• Total capacity: {random.randint(100000, 1000000):,} sq ft")
            tech_doc.add_paragraph(f"• Locations: {random.randint(5, 50)} facilities")
            tech_doc.add_paragraph("• Temperature-controlled zones available")
            tech_doc.add_paragraph("• WMS: SAP EWM / Manhattan / Blue Yonder")
        
        if ServiceType.CSO in services:
            tech_doc.add_heading('Customer Service Operations', 3)
            tech_doc.add_paragraph("• RMA processing capability")
            tech_doc.add_paragraph("• 24/7 customer support")
            tech_doc.add_paragraph(f"• Average response time: {random.randint(1, 4)} hours")
            tech_doc.add_paragraph("• Returns processing: Same-day")
        
        if ServiceType.CSG in services:
            tech_doc.add_heading('Consumer Solutions Group', 3)
            tech_doc.add_paragraph("• Kitting and assembly services")
            tech_doc.add_paragraph("• Custom packaging capabilities")
            tech_doc.add_paragraph("• Labeling and branding services")
            tech_doc.add_paragraph(f"• Capacity: {random.randint(10000, 100000)} units/day")
        
        tech_io = io.BytesIO()
        tech_doc.save(tech_io)
        tech_io.seek(0)
        proposals['Technical_Proposal.docx'] = tech_io.getvalue()
        
        # 2. Pricing Proposal
        pricing_doc = Document()
        pricing_doc.add_heading(f'{vendor_name}', 0)
        pricing_doc.add_heading('Pricing Proposal', 1)
        
        pricing_doc.add_heading(f'{service_model} Model Pricing', 2)
        
        # Create pricing table
        table = pricing_doc.add_table(rows=1, cols=3)
        table.style = 'Light Grid Accent 1'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Service'
        hdr_cells[1].text = 'Unit'
        hdr_cells[2].text = 'Price'
        
        if ServiceType.WAREHOUSE in services:
            row_cells = table.add_row().cells
            row_cells[0].text = 'Warehouse Storage'
            row_cells[1].text = 'Per pallet/month'
            row_cells[2].text = f'${random.uniform(15, 30):.2f}'
            
            row_cells = table.add_row().cells
            row_cells[0].text = 'Handling'
            row_cells[1].text = 'Per unit'
            row_cells[2].text = f'${random.uniform(1, 3):.2f}'
        
        if ServiceType.CSO in services:
            row_cells = table.add_row().cells
            row_cells[0].text = 'RMA Processing'
            row_cells[1].text = 'Per return'
            row_cells[2].text = f'${random.uniform(5, 15):.2f}'
            
            row_cells = table.add_row().cells
            row_cells[0].text = 'Customer Support'
            row_cells[1].text = 'Per ticket'
            row_cells[2].text = f'${random.uniform(2, 8):.2f}'
        
        if ServiceType.CSG in services:
            row_cells = table.add_row().cells
            row_cells[0].text = 'Kitting'
            row_cells[1].text = 'Per kit'
            row_cells[2].text = f'${random.uniform(2, 5):.2f}'
            
            row_cells = table.add_row().cells
            row_cells[0].text = 'Custom Packaging'
            row_cells[1].text = 'Per unit'
            row_cells[2].text = f'${random.uniform(1, 4):.2f}'
        
        # Add volume discounts
        pricing_doc.add_heading('Volume Discounts', 3)
        if service_model == ServiceModel.CONSOLIDATED:
            pricing_doc.add_paragraph("• 10% discount for consolidated services")
        pricing_doc.add_paragraph("• 5% discount for volumes over 10,000 units/month")
        pricing_doc.add_paragraph("• 10% discount for volumes over 50,000 units/month")
        
        pricing_io = io.BytesIO()
        pricing_doc.save(pricing_io)
        pricing_io.seek(0)
        proposals['Pricing_Proposal.docx'] = pricing_io.getvalue()
        
        # 3. Company Profile (PowerPoint)
        prs = Presentation()
        
        # Title slide
        title_slide = prs.slides.add_slide(prs.slide_layouts[0])
        title_slide.shapes.title.text = vendor_name
        title_slide.placeholders[1].text = f"Company Profile - {service_model} Services Provider"
        
        # Overview slide
        overview_slide = prs.slides.add_slide(prs.slide_layouts[1])
        overview_slide.shapes.title.text = 'Company Overview'
        body = overview_slide.placeholders[1]
        tf = body.text_frame
        tf.text = f'• Established: {random.randint(1980, 2015)}'
        tf.add_paragraph().text = f'• Employees: {random.randint(500, 10000):,}'
        tf.add_paragraph().text = f'• Annual Revenue: ${random.randint(50, 500)}M'
        tf.add_paragraph().text = f'• Service Model: {service_model}'
        tf.add_paragraph().text = f'• Services: {", ".join(services)}'
        
        # Certifications slide
        cert_slide = prs.slides.add_slide(prs.slide_layouts[1])
        cert_slide.shapes.title.text = 'Certifications & Compliance'
        body = cert_slide.placeholders[1]
        tf = body.text_frame
        certs = ['• ISO 9001:2015', '• ISO 14001:2015', '• C-TPAT Certified', 
                '• TAPA FSR Level A', '• SOC 2 Type II']
        tf.text = certs[0]
        for cert in certs[1:]:
            tf.add_paragraph().text = cert
        
        ppt_io = io.BytesIO()
        prs.save(ppt_io)
        ppt_io.seek(0)
        proposals['Company_Profile.pptx'] = ppt_io.getvalue()
        
        return proposals
    
    def generate_test_vendors(self, count: int = 5) -> List[Dict]:
        """Generate test vendor data"""
        vendors = []
        
        # Mix of standalone and consolidated vendors
        for i in range(count):
            if i < 2:  # First 2 are consolidated
                service_model = ServiceModel.CONSOLIDATED
                services = ServiceType.get_all()
            else:  # Rest are standalone
                service_model = ServiceModel.STANDALONE
                services = [random.choice(ServiceType.get_all())]
            
            vendor_data = {
                "name": self.vendor_names[i % len(self.vendor_names)],
                "service_model": service_model,
                "services": services,
                "proposals": self.generate_vendor_proposals(
                    self.vendor_names[i % len(self.vendor_names)],
                    service_model,
                    services
                )
            }
            vendors.append(vendor_data)
        
        return vendors

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

def render_rfp_overview(manager: RFPManager):
    """Render RFP overview section"""
    st.header("📋 Current RFP Overview")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="rfp-info-card">
            <h3>{manager.rfp_details['title']}</h3>
            <p><strong>RFP ID:</strong> {manager.rfp_details['rfp_id']}</p>
            <p><strong>Issue Date:</strong> {manager.rfp_details['issue_date'].strftime('%B %d, %Y')}</p>
            <p><strong>Due Date:</strong> {manager.rfp_details['due_date'].strftime('%B %d, %Y')}</p>
            <p><strong>Budget Range:</strong> {manager.rfp_details['budget_range']}</p>
            <p><strong>Contract Duration:</strong> {manager.rfp_details['contract_duration']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Services Required")
        for service in manager.rfp_details['services_required']:
            if service == ServiceType.WAREHOUSE:
                tag_class = "service-warehouse"
            elif service == ServiceType.CSO:
                tag_class = "service-cso"
            else:
                tag_class = "service-csg"
            
            st.markdown(f'<span class="service-tag {tag_class}">{service}</span>', 
                       unsafe_allow_html=True)
        
        st.markdown("### Service Models")
        st.info("✅ Standalone (Single Service)")
        st.info("✅ Consolidated (Multiple Services)")

def render_workflow_management(manager: RFPManager):
    """Render workflow management section"""
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
    for idx, (stage_id, stage) in enumerate(manager.workflow_stages.items()):
        prev_stage = list(manager.workflow_stages.values())[idx - 1] if idx > 0 else None
        
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
                    progress_val = st.slider(
                        "Progress", 0, 100, stage.progress,
                        key=f"progress_{stage_id}"
                    )
                    if progress_val != stage.progress:
                        stage.update_progress(progress_val)
                        st.rerun()
            
            with col2:
                st.write("**Required Documents:**")
                for doc in stage.required_docs[:3]:
                    st.caption(f"• {doc}")
            
            with col3:
                if stage.status == "pending":
                    if st.button(f"Start Stage", key=f"start_{stage_id}"):
                        if stage.can_start(prev_stage):
                            stage.start()
                            st.success(f"Started: {stage.name}")
                            st.rerun()
                        else:
                            st.error("Complete previous stage first!")
                
                elif stage.status == "active" and stage.progress == 100:
                    if st.button(f"Complete Stage", key=f"complete_{stage_id}"):
                        stage.complete()
                        st.success(f"Completed: {stage.name}")
                        st.rerun()

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
                st.rerun()
    
    # Display vendors
    if manager.vendors:
        st.subheader("Registered Vendors")
        
        # Group by service model
        consolidated_vendors = [v for v in manager.vendors.values() 
                               if v.service_model == ServiceModel.CONSOLIDATED]
        standalone_vendors = [v for v in manager.vendors.values() 
                             if v.service_model == ServiceModel.STANDALONE]
        
        if consolidated_vendors:
            st.markdown("### 🔗 Consolidated Service Vendors")
            for vendor in consolidated_vendors:
                render_vendor_card(vendor, manager)
        
        if standalone_vendors:
            st.markdown("### 📦 Standalone Service Vendors")
            for vendor in standalone_vendors:
                render_vendor_card(vendor, manager)
    else:
        st.info("No vendors registered yet. Use test mode or register vendors above.")

def render_vendor_card(vendor: VendorProfile, manager: RFPManager):
    """Render individual vendor card"""
    # Determine card styling
    if vendor.status == "Selected":
        card_class = "vendor-selected"
    elif vendor.status == "Evaluated":
        card_class = "vendor-card"
    else:
        card_class = "vendor-card"
    
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            st.markdown(f"**{vendor.name}**")
            st.caption(f"ID: {vendor.vendor_id}")
            
            # Service tags
            for service in vendor.services_offered:
                if service == ServiceType.WAREHOUSE:
                    tag_class = "service-warehouse"
                elif service == ServiceType.CSO:
                    tag_class = "service-cso"
                else:
                    tag_class = "service-csg"
                st.markdown(f'<span class="service-tag {tag_class}">{service}</span>', 
                           unsafe_allow_html=True)
        
        with col2:
            st.write(f"**Model:** {vendor.service_model}")
            st.write(f"**Status:** {vendor.status}")
        
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
            col_a, col_b = st.columns(2)
            
            with col_a:
                if vendor.status == "Submitted":
                    if st.button("📊 Evaluate", key=f"eval_{vendor.vendor_id}"):
                        scores = manager.evaluate_vendor(vendor.vendor_id)
                        st.success(f"Evaluated: {vendor.overall_score:.1f}/100")
                        st.rerun()
            
            with col_b:
                if st.button("📄 Details", key=f"details_{vendor.vendor_id}"):
                    st.session_state.selected_vendor = vendor.vendor_id
        
        st.markdown("---")

def render_evaluation_comparison(manager: RFPManager):
    """Render vendor evaluation and comparison"""
    st.header("📊 Vendor Evaluation & Comparison")
    
    evaluated_vendors = [v for v in manager.vendors.values() if v.status in ["Evaluated", "Selected"]]
    
    if not evaluated_vendors:
        st.info("No vendors evaluated yet. Please evaluate vendors first.")
        return
    
    # Service model comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Consolidated Model Vendors")
        consolidated = [v for v in evaluated_vendors if v.service_model == ServiceModel.CONSOLIDATED]
        if consolidated:
            for vendor in sorted(consolidated, key=lambda x: x.overall_score, reverse=True):
                st.write(f"**{vendor.name}**: {vendor.overall_score:.1f}/100")
                st.progress(vendor.overall_score / 100)
        else:
            st.info("No consolidated vendors evaluated")
    
    with col2:
        st.subheader("Standalone Model Vendors")
        
        # Group by service
        for service in ServiceType.get_all():
            service_vendors = [v for v in evaluated_vendors 
                              if v.service_model == ServiceModel.STANDALONE 
                              and service in v.services_offered]
            if service_vendors:
                st.write(f"**{service}:**")
                for vendor in sorted(service_vendors, key=lambda x: x.overall_score, reverse=True):
                    st.write(f"• {vendor.name}: {vendor.overall_score:.1f}/100")
    
    # Comparison chart
    if len(evaluated_vendors) >= 2:
        st.subheader("Score Comparison")
        
        # Prepare data for chart
        vendor_names = [v.name for v in evaluated_vendors]
        scores = [v.overall_score for v in evaluated_vendors]
        models = [v.service_model for v in evaluated_vendors]
        
        fig = go.Figure()
        
        # Add bars
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
            yaxis_range=[0, 100],
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_vendor_selection(manager: RFPManager):
    """Render vendor selection interface"""
    st.header("🎯 Vendor Selection")
    
    evaluated_vendors = [v for v in manager.vendors.values() if v.status == "Evaluated"]
    
    if not evaluated_vendors:
        st.info("No vendors ready for selection. Please evaluate vendors first.")
        return
    
    st.subheader("Select Vendors for Services")
    
    selections = {}
    
    # Option 1: Select consolidated vendor
    st.markdown("### Option 1: Consolidated Service Model")
    consolidated_vendors = [v for v in evaluated_vendors 
                           if v.service_model == ServiceModel.CONSOLIDATED]
    
    if consolidated_vendors:
        selected_consolidated = st.selectbox(
            "Select vendor for ALL services",
            ["None"] + [v.vendor_id for v in consolidated_vendors],
            format_func=lambda x: "None" if x == "None" else 
                       f"{manager.vendors[x].name} (Score: {manager.vendors[x].overall_score:.1f})"
        )
        
        if selected_consolidated != "None":
            for service in ServiceType.get_all():
                selections[service] = selected_consolidated
    
    # Option 2: Select standalone vendors
    if not selections:  # Only show if consolidated not selected
        st.markdown("### Option 2: Standalone Service Model")
        
        for service in ServiceType.get_all():
            service_vendors = [v for v in evaluated_vendors 
                              if v.service_model == ServiceModel.STANDALONE 
                              and service in v.services_offered]
            
            if service_vendors:
                selected = st.selectbox(
                    f"Select vendor for {service}",
                    ["None"] + [v.vendor_id for v in service_vendors],
                    format_func=lambda x: "None" if x == "None" else 
                               f"{manager.vendors[x].name} (Score: {manager.vendors[x].overall_score:.1f})",
                    key=f"select_{service}"
                )
                
                if selected != "None":
                    selections[service] = selected
    
    # Confirm selection
    if st.button("Confirm Selection", type="primary", disabled=len(selections) == 0):
        manager.select_vendors(selections)
        st.success("✅ Vendors selected successfully!")
        
        # Show selection summary
        st.subheader("Selection Summary")
        for service, vendor_id in selections.items():
            vendor = manager.vendors[vendor_id]
            st.write(f"**{service}:** {vendor.name}")
        
        st.balloons()

def render_sidebar(manager: RFPManager):
    """Render sidebar"""
    with st.sidebar:
        st.markdown("### 🎯 RFP Management")
        
        # Test Mode
        test_mode = st.checkbox(
            "Enable Test Mode",
            value=st.session_state.get('test_mode', False),
            help="Load sample vendors for testing"
        )
        
        if test_mode != st.session_state.get('test_mode', False):
            st.session_state.test_mode = test_mode
            if test_mode:
                # Generate test vendors
                generator = SampleDataGenerator()
                test_vendors = generator.generate_test_vendors(5)
                
                for vendor_data in test_vendors:
                    vendor = manager.register_vendor(
                        vendor_data['name'],
                        vendor_data['service_model'],
                        vendor_data['services']
                    )
                    vendor.submit_proposal()
                    manager.evaluate_vendor(vendor.vendor_id)
                
                st.success(f"Loaded {len(test_vendors)} test vendors!")
                st.rerun()
        
        st.markdown("---")
        
        # RFP Info
        st.markdown("### 📋 RFP Details")
        st.caption(f"**ID:** {manager.rfp_details['rfp_id']}")
        st.caption(f"**Due:** {manager.rfp_details['due_date'].strftime('%b %d')}")
        
        days_remaining = (manager.rfp_details['due_date'] - datetime.now()).days
        if days_remaining > 0:
            st.success(f"📅 {days_remaining} days remaining")
        else:
            st.error("⚠️ RFP overdue")
        
        # Progress
        st.markdown("### 📊 Progress")
        progress = manager.get_workflow_progress()
        st.progress(progress / 100)
        st.caption(f"{progress}% Complete")
        
        # Stats
        st.markdown("### 📈 Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Vendors", len(manager.vendors))
        with col2:
            evaluated = sum(1 for v in manager.vendors.values() 
                          if v.status in ["Evaluated", "Selected"])
            st.metric("Evaluated", evaluated)
        
        # Download sample RFP
        st.markdown("---")
        st.markdown("### 📥 Downloads")
        
        generator = SampleDataGenerator()
        rfp_doc = generator.generate_rfp_document()
        
        st.download_button(
            "📄 Sample RFP Document",
            data=rfp_doc,
            file_name=f"Sample_RFP_{datetime.now().strftime('%Y%m%d')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

def render_test_mode_banner():
    """Render test mode banner"""
    if st.session_state.get('test_mode', False):
        st.markdown("""
        <div class="test-mode-banner">
            🧪 TEST MODE - Sample vendors loaded for demonstration
        </div>
        """, unsafe_allow_html=True)

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    """Main application"""
    
    # Initialize
    manager = RFPManager()
    
    # Initialize session state
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 0
    
    # Render UI
    render_header()
    render_test_mode_banner()
    render_sidebar(manager)
    
    # Main content tabs
    tabs = st.tabs([
        "📋 RFP Overview",
        "⚙️ Workflow",
        "👥 Vendors",
        "📊 Evaluation",
        "🎯 Selection"
    ])
    
    with tabs[0]:
        render_rfp_overview(manager)
        
        # Show service requirements
        st.subheader("📝 Service Requirements")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"### {ServiceType.WAREHOUSE}")
            for req in ServiceType.get_requirements(ServiceType.WAREHOUSE):
                st.write(f"• {req}")
        
        with col2:
            st.markdown(f"### {ServiceType.CSO}")
            for req in ServiceType.get_requirements(ServiceType.CSO):
                st.write(f"• {req}")
        
        with col3:
            st.markdown(f"### {ServiceType.CSG}")
            for req in ServiceType.get_requirements(ServiceType.CSG):
                st.write(f"• {req}")
    
    with tabs[1]:
        render_workflow_management(manager)
    
    with tabs[2]:
        render_vendor_management(manager)
    
    with tabs[3]:
        render_evaluation_comparison(manager)
    
    with tabs[4]:
        render_vendor_selection(manager)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>RFP Vendor Evaluation Platform v2.0</p>
        <p>Supporting Standalone and Consolidated Service Models</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
