"""
🎯 Enhanced RFP Analysis & Vendor Management System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Complete RFP lifecycle management with AI-powered analysis
Supporting entire RFP document upload and multi-vendor evaluation
"""

import streamlit as st
import anthropic
import PyPDF2
import docx
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

# ========================================
# CONFIGURATION & INITIALIZATION
# ========================================

st.set_page_config(
    page_title="RFP Vendor Management System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    :root {
        --primary: #2C3E50;
        --secondary: #3498DB;
        --success: #27AE60;
        --warning: #F39C12;
        --danger: #E74C3C;
        --info: #16A085;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
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
        border-left-color: #95A5A6;
        opacity: 0.7;
    }
    
    .stage-active {
        border-left-color: var(--warning);
        background: #FFF9E6;
        animation: pulse 2s infinite;
    }
    
    .stage-complete {
        border-left-color: var(--success);
        background: #E8F6F3;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.9; }
    }
    
    .vendor-card {
        background: linear-gradient(to bottom, #ffffff, #f8f9fa);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.25rem;
    }
    
    .score-excellent { background: #D4EDDA; color: #155724; }
    .score-good { background: #D1ECF1; color: #0C5460; }
    .score-fair { background: #FFF3CD; color: #856404; }
    .score-poor { background: #F8D7DA; color: #721C24; }
    
    .document-upload-zone {
        border: 2px dashed var(--secondary);
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #F0F8FF;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 3px solid var(--secondary);
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    
    .user-message {
        background: #E3F2FD;
        margin-left: 20%;
    }
    
    .assistant-message {
        background: #F5F5F5;
        margin-right: 20%;
    }
    
    .timeline-container {
        position: relative;
        padding: 20px 0;
    }
    
    .timeline-item {
        display: flex;
        align-items: center;
        margin: 20px 0;
    }
    
    .timeline-marker {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        margin-right: 20px;
        flex-shrink: 0;
    }
    
    .timeline-content {
        flex-grow: 1;
    }
    
    .progress-bar {
        background: #E0E0E0;
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
</style>
""", unsafe_allow_html=True)

# ========================================
# MOCK DATA GENERATOR
# ========================================

class MockDataGenerator:
    """Generate realistic mock data for demonstration"""
    
    @staticmethod
    def generate_vendor_response():
        """Generate mock vendor RFP response data"""
        companies = ["TechLogistics Inc.", "Global Supply Solutions", "FastTrack Warehousing", 
                     "Premier Distribution Services", "NextGen Fulfillment"]
        
        return {
            "company_profile": {
                "name": random.choice(companies),
                "established": random.randint(1990, 2015),
                "employees": random.randint(500, 5000),
                "locations": random.randint(5, 50),
                "certifications": ["ISO 9001", "ISO 14001", "C-TPAT", "TAPA FSR"],
                "revenue": f"${random.randint(50, 500)}M",
                "clients": random.randint(50, 500)
            },
            "technical_proposal": {
                "warehouse_facilities": f"{random.randint(10, 100)} facilities",
                "total_sqft": f"{random.randint(500000, 5000000):,} sq ft",
                "technology_stack": ["WMS", "TMS", "YMS", "RFID", "IoT Sensors"],
                "automation_level": f"{random.randint(40, 90)}%",
                "order_accuracy": f"{random.uniform(98.5, 99.9):.1f}%",
                "on_time_delivery": f"{random.uniform(95, 99):.1f}%"
            },
            "pricing": {
                "storage_per_pallet": f"${random.uniform(15, 30):.2f}",
                "pick_pack_per_order": f"${random.uniform(3, 8):.2f}",
                "shipping_handling": f"${random.uniform(5, 15):.2f}",
                "monthly_minimum": f"${random.randint(10000, 50000):,}",
                "contract_term": f"{random.choice([12, 24, 36])} months",
                "volume_discounts": "5-15% based on volume"
            },
            "service_capabilities": {
                "warehousing": ["Storage", "Cross-docking", "Transloading", "Kitting", "Assembly"],
                "fulfillment": ["B2B", "B2C", "D2C", "Subscription box", "FBA prep"],
                "value_added": ["Returns processing", "Quality control", "Labeling", "Repackaging"],
                "transportation": ["LTL", "FTL", "Parcel", "White glove", "International"]
            },
            "implementation_plan": {
                "phase1": {"duration": "30 days", "activities": "Setup & Integration"},
                "phase2": {"duration": "30 days", "activities": "Testing & Training"},
                "phase3": {"duration": "30 days", "activities": "Go-live & Stabilization"},
                "total_timeline": "90 days"
            }
        }
    
    @staticmethod
    def generate_evaluation_scores():
        """Generate mock evaluation scores"""
        return {
            "technical_capability": random.randint(70, 95),
            "operational_excellence": random.randint(75, 95),
            "pricing_competitiveness": random.randint(65, 90),
            "compliance_security": random.randint(80, 100),
            "innovation_technology": random.randint(70, 95),
            "customer_service": random.randint(75, 95),
            "financial_stability": random.randint(70, 95),
            "implementation_approach": random.randint(75, 90),
            "risk_management": random.randint(70, 90),
            "sustainability": random.randint(60, 85)
        }

# ========================================
# CORE CLASSES
# ========================================

class WorkflowStage:
    """Represents a stage in the RFP workflow"""
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
        self.assigned_to = None
        self.notes = []
        self.documents = {}
        
    def start(self):
        """Start the workflow stage"""
        self.status = "active"
        self.start_date = datetime.now()
        self.progress = 10
        
    def complete(self):
        """Complete the workflow stage"""
        self.status = "complete"
        self.end_date = datetime.now()
        self.progress = 100
        
    def update_progress(self, progress: int):
        """Update stage progress"""
        self.progress = min(100, max(0, progress))
        if self.progress == 100 and self.status != "complete":
            self.complete()

class VendorProfile:
    """Vendor profile with complete information"""
    def __init__(self, vendor_id: str, name: str, contact_email: str = None):
        self.vendor_id = vendor_id
        self.name = name
        self.contact_email = contact_email or f"vendor@{name.lower().replace(' ', '')}.com"
        self.registration_date = datetime.now()
        self.documents = {}
        self.scores = {}
        self.overall_score = 0
        self.status = "Registered"
        self.submission_date = None
        self.evaluation_date = None
        self.notes = []
        self.strengths = []
        self.weaknesses = []
        self.risks = []
        self.mock_data = MockDataGenerator.generate_vendor_response()
        
    def submit_proposal(self, documents: Dict):
        """Submit vendor proposal"""
        self.documents.update(documents)
        self.submission_date = datetime.now()
        self.status = "Submitted"
        
    def evaluate(self):
        """Evaluate vendor proposal"""
        self.scores = MockDataGenerator.generate_evaluation_scores()
        self.overall_score = sum(self.scores.values()) / len(self.scores)
        self.evaluation_date = datetime.now()
        self.status = "Evaluated"
        
        # Generate strengths and weaknesses
        self.strengths = [
            k.replace('_', ' ').title() 
            for k, v in self.scores.items() if v >= 85
        ]
        self.weaknesses = [
            k.replace('_', ' ').title() 
            for k, v in self.scores.items() if v < 75
        ]

class RFPAnalyzer:
    """Main RFP Analysis Engine"""
    def __init__(self):
        self.workflow_stages = self._initialize_workflow()
        self.vendors = {}
        self.current_rfp = self._generate_rfp_details()
        self.claude_client = None
        self.initialize_claude()
        
    def _generate_rfp_details(self):
        """Generate RFP details"""
        return {
            "rfp_id": f"RFP-2025-{str(uuid.uuid4())[:8].upper()}",
            "title": "Warehouse and Logistics Services RFP",
            "issue_date": datetime.now() - timedelta(days=7),
            "due_date": datetime.now() + timedelta(days=21),
            "budget": "$5,000,000 - $10,000,000",
            "contract_duration": "3 years with 2 optional 1-year extensions",
            "services_required": [
                "Warehousing (500,000+ sq ft)",
                "Order Fulfillment",
                "Transportation Management",
                "Returns Processing",
                "Value-Added Services"
            ],
            "evaluation_criteria": {
                "Technical Capability": 25,
                "Price": 20,
                "Experience": 20,
                "Compliance": 15,
                "Innovation": 10,
                "Sustainability": 10
            }
        }
    
    def initialize_claude(self):
        """Initialize Claude API"""
        try:
            # Try multiple possible secret keys
            api_key = None
            for key in ["CLAUDE_API_KEY", "ANTHROPIC_API_KEY", "claude_api_key", "anthropic_api_key"]:
                try:
                    api_key = st.secrets.get(key)
                    if api_key:
                        break
                except:
                    pass
            
            if api_key:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
                return True
            else:
                # Work without API for demo
                return False
        except Exception as e:
            return False
    
    def _initialize_workflow(self) -> Dict[str, WorkflowStage]:
        """Initialize complete RFP workflow"""
        stages = {}
        
        workflow_definition = [
            {
                "id": "planning",
                "name": "RFP Planning & Strategy",
                "desc": "Define requirements, budget, timeline, and evaluation criteria",
                "docs": ["Business Requirements", "Budget Approval", "Stakeholder Input"],
                "deliverables": ["RFP Strategy Document", "Timeline", "Evaluation Matrix"],
                "duration": "5 days"
            },
            {
                "id": "documentation",
                "name": "RFP Documentation",
                "desc": "Prepare comprehensive RFP package with all specifications",
                "docs": ["Technical Specifications", "SOW Template", "Contract Terms"],
                "deliverables": ["Complete RFP Package", "Attachments", "Q&A Template"],
                "duration": "7 days"
            },
            {
                "id": "vendor_identification",
                "name": "Vendor Identification",
                "desc": "Research and identify qualified vendors for RFP distribution",
                "docs": ["Vendor Database", "Market Research", "Past Performance"],
                "deliverables": ["Qualified Vendor List", "Contact Information"],
                "duration": "3 days"
            },
            {
                "id": "distribution",
                "name": "RFP Distribution",
                "desc": "Distribute RFP to qualified vendors and manage communications",
                "docs": ["RFP Package", "NDA Forms", "Distribution List"],
                "deliverables": ["Distribution Confirmation", "Vendor Acknowledgments"],
                "duration": "2 days"
            },
            {
                "id": "qa_period",
                "name": "Q&A Period",
                "desc": "Address vendor questions and provide clarifications",
                "docs": ["Vendor Questions", "Technical Clarifications"],
                "deliverables": ["Q&A Responses", "Addendums", "Updated RFP"],
                "duration": "5 days"
            },
            {
                "id": "submission",
                "name": "Proposal Submission",
                "desc": "Receive and validate vendor proposals",
                "docs": ["Vendor Proposals", "Technical Documents", "Pricing Sheets"],
                "deliverables": ["Submission Log", "Compliance Check", "Initial Review"],
                "duration": "1 day"
            },
            {
                "id": "evaluation",
                "name": "Proposal Evaluation",
                "desc": "Comprehensive evaluation of all vendor proposals",
                "docs": ["Evaluation Matrix", "Scoring Sheets", "Reference Checks"],
                "deliverables": ["Evaluation Report", "Vendor Scores", "Recommendations"],
                "duration": "10 days"
            },
            {
                "id": "clarification",
                "name": "Vendor Clarifications",
                "desc": "Request and review additional information from shortlisted vendors",
                "docs": ["Clarification Requests", "Vendor Responses"],
                "deliverables": ["Updated Evaluations", "Final Shortlist"],
                "duration": "3 days"
            },
            {
                "id": "negotiation",
                "name": "Negotiation",
                "desc": "Negotiate terms, pricing, and conditions with selected vendors",
                "docs": ["Negotiation Strategy", "Price Analysis", "Terms Matrix"],
                "deliverables": ["Negotiated Terms", "Best and Final Offers"],
                "duration": "7 days"
            },
            {
                "id": "selection",
                "name": "Final Selection",
                "desc": "Select winning vendor and prepare for contract award",
                "docs": ["Final Evaluation", "Executive Approval", "Award Letter"],
                "deliverables": ["Vendor Selection", "Award Notification", "Rejection Letters"],
                "duration": "2 days"
            },
            {
                "id": "contracting",
                "name": "Contract Finalization",
                "desc": "Finalize and execute contract with selected vendor",
                "docs": ["Contract Draft", "Legal Review", "Signatures"],
                "deliverables": ["Executed Contract", "SLAs", "KPIs"],
                "duration": "5 days"
            },
            {
                "id": "implementation",
                "name": "Implementation Planning",
                "desc": "Plan transition and implementation with selected vendor",
                "docs": ["Implementation Plan", "Transition Schedule", "Resource Plan"],
                "deliverables": ["Kickoff Meeting", "Project Plan", "Success Metrics"],
                "duration": "3 days"
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
    
    def move_to_next_stage(self):
        """Move to the next workflow stage"""
        current_active = None
        next_pending = None
        
        for stage_id, stage in self.workflow_stages.items():
            if stage.status == "active" and stage.progress < 100:
                return False, "Complete current stage first"
            elif stage.status == "active" and stage.progress == 100:
                current_active = stage
            elif stage.status == "pending" and next_pending is None:
                next_pending = stage
        
        if current_active:
            current_active.complete()
            
        if next_pending:
            next_pending.start()
            return True, f"Started: {next_pending.name}"
        
        return False, "All stages complete"
    
    def get_workflow_progress(self):
        """Calculate overall workflow progress"""
        total_stages = len(self.workflow_stages)
        completed_stages = sum(1 for s in self.workflow_stages.values() if s.status == "complete")
        
        if total_stages == 0:
            return 0
        
        return int((completed_stages / total_stages) * 100)
    
    def analyze_vendor_proposal(self, vendor: VendorProfile, documents: Dict) -> Dict:
        """Analyze vendor proposal with or without Claude API"""
        analysis_results = {
            "vendor_id": vendor.vendor_id,
            "vendor_name": vendor.name,
            "analysis_date": datetime.now().isoformat(),
            "document_count": len(documents),
            "executive_summary": self._generate_executive_summary(vendor),
            "scores": vendor.scores,
            "overall_score": vendor.overall_score,
            "strengths": vendor.strengths,
            "weaknesses": vendor.weaknesses,
            "risks": self._identify_risks(vendor),
            "recommendations": self._generate_recommendations(vendor),
            "compliance_status": self._check_compliance(vendor),
            "technical_evaluation": self._evaluate_technical(vendor),
            "commercial_evaluation": self._evaluate_commercial(vendor),
            "next_steps": self._suggest_next_steps(vendor)
        }
        
        return analysis_results
    
    def _generate_executive_summary(self, vendor: VendorProfile) -> str:
        """Generate executive summary"""
        return f"""
        {vendor.name} has submitted a comprehensive proposal for warehouse and logistics services.
        The vendor demonstrates {len(vendor.strengths)} key strengths with an overall score of 
        {vendor.overall_score:.1f}/100. They have {vendor.mock_data['company_profile']['locations']} 
        locations and serve {vendor.mock_data['company_profile']['clients']} clients globally.
        Key differentiators include {', '.join(vendor.mock_data['technical_proposal']['technology_stack'][:3])}.
        """
    
    def _identify_risks(self, vendor: VendorProfile) -> List[Dict]:
        """Identify potential risks"""
        risks = []
        
        if vendor.overall_score < 70:
            risks.append({
                "category": "Performance",
                "level": "High",
                "description": "Overall score below acceptable threshold",
                "mitigation": "Request performance guarantees and enhanced SLAs"
            })
        
        if vendor.scores.get("financial_stability", 0) < 75:
            risks.append({
                "category": "Financial",
                "level": "Medium",
                "description": "Financial stability concerns",
                "mitigation": "Request financial guarantees or parent company backing"
            })
        
        if vendor.scores.get("compliance_security", 0) < 80:
            risks.append({
                "category": "Compliance",
                "level": "Medium",
                "description": "Compliance gaps identified",
                "mitigation": "Require compliance roadmap and timeline"
            })
        
        return risks
    
    def _generate_recommendations(self, vendor: VendorProfile) -> List[str]:
        """Generate recommendations"""
        recommendations = []
        
        if vendor.overall_score >= 85:
            recommendations.append("Strong candidate - proceed to final negotiations")
        elif vendor.overall_score >= 75:
            recommendations.append("Qualified candidate - request clarifications on weak areas")
        elif vendor.overall_score >= 65:
            recommendations.append("Marginal candidate - significant improvements needed")
        else:
            recommendations.append("Not recommended - does not meet minimum requirements")
        
        if vendor.strengths:
            recommendations.append(f"Leverage strengths in: {', '.join(vendor.strengths[:3])}")
        
        if vendor.weaknesses:
            recommendations.append(f"Address weaknesses in: {', '.join(vendor.weaknesses[:3])}")
        
        return recommendations
    
    def _check_compliance(self, vendor: VendorProfile) -> Dict:
        """Check compliance status"""
        return {
            "iso_9001": "Compliant" if "ISO 9001" in vendor.mock_data['company_profile']['certifications'] else "Missing",
            "iso_14001": "Compliant" if "ISO 14001" in vendor.mock_data['company_profile']['certifications'] else "Missing",
            "c_tpat": "Compliant" if "C-TPAT" in vendor.mock_data['company_profile']['certifications'] else "Missing",
            "tapa": "Compliant" if "TAPA FSR" in vendor.mock_data['company_profile']['certifications'] else "Missing",
            "data_security": "Compliant" if vendor.scores.get("compliance_security", 0) >= 80 else "Review Required",
            "insurance": "Adequate" if vendor.scores.get("financial_stability", 0) >= 75 else "Review Required"
        }
    
    def _evaluate_technical(self, vendor: VendorProfile) -> Dict:
        """Evaluate technical capabilities"""
        return {
            "warehouse_capacity": vendor.mock_data['technical_proposal']['total_sqft'],
            "technology_score": vendor.scores.get("innovation_technology", 0),
            "automation_level": vendor.mock_data['technical_proposal']['automation_level'],
            "order_accuracy": vendor.mock_data['technical_proposal']['order_accuracy'],
            "on_time_delivery": vendor.mock_data['technical_proposal']['on_time_delivery'],
            "systems_integration": "Advanced" if vendor.scores.get("innovation_technology", 0) >= 80 else "Standard"
        }
    
    def _evaluate_commercial(self, vendor: VendorProfile) -> Dict:
        """Evaluate commercial terms"""
        return {
            "pricing_model": "Competitive" if vendor.scores.get("pricing_competitiveness", 0) >= 75 else "Above Market",
            "contract_flexibility": vendor.mock_data['pricing']['contract_term'],
            "payment_terms": "Net 30",
            "volume_discounts": vendor.mock_data['pricing']['volume_discounts'],
            "price_score": vendor.scores.get("pricing_competitiveness", 0),
            "total_cost_estimate": f"${random.randint(5, 10)}M annually"
        }
    
    def _suggest_next_steps(self, vendor: VendorProfile) -> List[str]:
        """Suggest next steps"""
        steps = []
        
        if vendor.overall_score >= 80:
            steps.extend([
                "Schedule vendor presentation",
                "Conduct site visit",
                "Check references",
                "Begin contract negotiations"
            ])
        elif vendor.overall_score >= 70:
            steps.extend([
                "Request additional information",
                "Clarify pricing structure",
                "Review implementation plan",
                "Assess risk mitigation strategies"
            ])
        else:
            steps.extend([
                "Send regret letter",
                "Provide feedback if requested",
                "Keep vendor in database for future RFPs"
            ])
        
        return steps

# ========================================
# UI COMPONENTS
# ========================================

def render_header():
    """Render application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 RFP Vendor Management System</h1>
        <h3>End-to-End Procurement Workflow with AI-Powered Analysis</h3>
        <p>Streamline your RFP process from planning to contract execution</p>
    </div>
    """, unsafe_allow_html=True)

def render_workflow_timeline(analyzer: RFPAnalyzer):
    """Render interactive workflow timeline"""
    st.subheader("📋 RFP Workflow Timeline")
    
    # Progress bar
    progress = analyzer.get_workflow_progress()
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress}%;">
            {progress}% Complete
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Timeline view
    cols = st.columns(4)
    
    for idx, (stage_id, stage) in enumerate(analyzer.workflow_stages.items()):
        col = cols[idx % 4]
        
        with col:
            # Determine stage styling
            if stage.status == "complete":
                color = "var(--success)"
                icon = "✅"
                card_class = "stage-complete"
            elif stage.status == "active":
                color = "var(--warning)"
                icon = "🔄"
                card_class = "stage-active"
            else:
                color = "#95A5A6"
                icon = "⏳"
                card_class = "stage-pending"
            
            st.markdown(f"""
            <div class="workflow-card {card_class}">
                <div class="timeline-marker" style="background: {color};">
                    {stage.stage_num}
                </div>
                <h4>{icon} {stage.name}</h4>
                <p style="font-size: 0.9em; color: #666;">{stage.description}</p>
                <p style="font-size: 0.85em;">
                    <strong>Duration:</strong> {stage.duration}<br>
                    <strong>Status:</strong> {stage.status.title()}<br>
                    <strong>Progress:</strong> {stage.progress}%
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons for active stages
            if stage.status == "pending":
                if st.button(f"Start Stage", key=f"start_{stage_id}"):
                    # Check if previous stages are complete
                    can_start = True
                    for check_stage in analyzer.workflow_stages.values():
                        if check_stage.stage_num < stage.stage_num and check_stage.status != "complete":
                            can_start = False
                            st.error(f"Complete '{check_stage.name}' first")
                            break
                    
                    if can_start:
                        stage.start()
                        st.success(f"Started: {stage.name}")
                        st.rerun()
            
            elif stage.status == "active":
                # Progress slider
                new_progress = st.slider(
                    "Update Progress",
                    0, 100, stage.progress,
                    key=f"progress_{stage_id}"
                )
                
                if new_progress != stage.progress:
                    stage.update_progress(new_progress)
                    if stage.status == "complete":
                        st.success(f"Completed: {stage.name}")
                    st.rerun()
                
                # Complete button
                if stage.progress < 100:
                    if st.button(f"Complete Stage", key=f"complete_{stage_id}"):
                        stage.complete()
                        st.success(f"Completed: {stage.name}")
                        st.rerun()

def render_document_upload(analyzer: RFPAnalyzer):
    """Render comprehensive document upload interface"""
    st.subheader("📤 Document Upload Center")
    
    tab1, tab2, tab3 = st.tabs(["📄 Upload RFP", "👥 Vendor Proposals", "📁 Supporting Docs"])
    
    with tab1:
        st.markdown("### Upload Complete RFP Package")
        st.info("Upload your entire RFP document or multiple files that comprise the RFP")
        
        # RFP document upload
        rfp_files = st.file_uploader(
            "Select RFP Documents",
            type=['pdf', 'docx', 'doc', 'pptx', 'xlsx'],
            accept_multiple_files=True,
            key="rfp_upload",
            help="Upload complete RFP package including SOW, specifications, terms, etc."
        )
        
        if rfp_files:
            st.success(f"✅ Uploaded {len(rfp_files)} RFP document(s)")
            
            # Display uploaded files
            for file in rfp_files:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📄 {file.name}")
                with col2:
                    st.write(f"{file.size // 1024} KB")
                with col3:
                    if st.button("Remove", key=f"remove_rfp_{file.name}"):
                        st.info("File removed")
            
            if st.button("Process RFP Documents", type="primary"):
                with st.spinner("Processing RFP documents..."):
                    time.sleep(2)
                    st.success("✅ RFP documents processed successfully!")
                    
                    # Update workflow stage
                    analyzer.workflow_stages["documentation"].update_progress(100)
                    st.rerun()
    
    with tab2:
        st.markdown("### Vendor Proposal Submission")
        
        # Vendor selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            vendor_name = st.text_input(
                "Vendor Name",
                placeholder="Enter vendor company name"
            )
        
        with col2:
            vendor_email = st.text_input(
                "Contact Email",
                placeholder="vendor@example.com"
            )
        
        if vendor_name:
            # Generate vendor ID
            vendor_id = f"VND-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            st.info(f"Vendor ID: {vendor_id}")
            
            # Document categories for vendor upload
            st.markdown("#### Required Vendor Documents")
            
            vendor_docs = {}
            
            doc_requirements = {
                "Technical Proposal": "Technical approach, architecture, capabilities",
                "Pricing Proposal": "Detailed pricing, payment terms, discounts",
                "Company Profile": "Company overview, certifications, references",
                "Financial Statements": "Last 3 years financial statements",
                "Implementation Plan": "Timeline, resources, milestones",
                "Compliance Documents": "Certifications, insurance, security"
            }
            
            for doc_type, description in doc_requirements.items():
                with st.expander(f"📁 {doc_type}"):
                    st.caption(description)
                    uploaded_file = st.file_uploader(
                        f"Upload {doc_type}",
                        type=['pdf', 'docx', 'doc', 'pptx', 'xlsx'],
                        key=f"vendor_{doc_type.replace(' ', '_').lower()}"
                    )
                    if uploaded_file:
                        vendor_docs[doc_type] = uploaded_file
                        st.success(f"✅ {uploaded_file.name} uploaded")
            
            # Submit vendor proposal
            if st.button("Submit Vendor Proposal", type="primary", disabled=not vendor_docs):
                with st.spinner(f"Processing proposal from {vendor_name}..."):
                    # Create vendor profile
                    vendor = VendorProfile(vendor_id, vendor_name, vendor_email)
                    vendor.submit_proposal(vendor_docs)
                    vendor.evaluate()  # Auto-evaluate with mock scores
                    
                    # Store vendor
                    if "vendors" not in st.session_state:
                        st.session_state.vendors = {}
                    st.session_state.vendors[vendor_id] = vendor
                    
                    time.sleep(2)
                    st.success(f"✅ Proposal submitted successfully for {vendor_name}!")
                    st.balloons()
                    
                    # Update workflow
                    analyzer.workflow_stages["submission"].update_progress(100)
                    st.rerun()
    
    with tab3:
        st.markdown("### Supporting Documentation")
        
        support_docs = {
            "Market Research": "Upload market analysis, competitor research",
            "Budget Approval": "Upload approved budget documentation",
            "Stakeholder Requirements": "Upload stakeholder input and requirements",
            "Evaluation Templates": "Upload scoring matrices and evaluation forms",
            "Contract Templates": "Upload standard contract templates"
        }
        
        for doc_type, description in support_docs.items():
            with st.expander(f"📎 {doc_type}"):
                st.caption(description)
                file = st.file_uploader(
                    f"Upload {doc_type}",
                    type=['pdf', 'docx', 'doc', 'xlsx'],
                    key=f"support_{doc_type.replace(' ', '_').lower()}"
                )
                if file:
                    st.success(f"✅ {file.name} uploaded")

def render_vendor_evaluation(analyzer: RFPAnalyzer):
    """Render vendor evaluation interface"""
    st.subheader("📊 Vendor Evaluation")
    
    if "vendors" not in st.session_state or not st.session_state.vendors:
        st.info("No vendors to evaluate. Please submit vendor proposals first.")
        return
    
    # Vendor selection
    vendor_names = {v.vendor_id: v.name for v in st.session_state.vendors.values()}
    selected_vendor_id = st.selectbox(
        "Select Vendor to Evaluate",
        options=list(vendor_names.keys()),
        format_func=lambda x: vendor_names[x]
    )
    
    if selected_vendor_id:
        vendor = st.session_state.vendors[selected_vendor_id]
        
        # Analyze vendor
        analysis = analyzer.analyze_vendor_proposal(vendor, vendor.documents)
        
        # Display evaluation results
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = analysis['overall_score']
            if score >= 85:
                badge = "score-excellent"
                label = "EXCELLENT"
            elif score >= 75:
                badge = "score-good"
                label = "GOOD"
            elif score >= 65:
                badge = "score-fair"
                label = "FAIR"
            else:
                badge = "score-poor"
                label = "POOR"
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>Overall Score</h3>
                <div class="score-badge {badge}">
                    {score:.1f}/100
                </div>
                <p>{label}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric("Documents", len(vendor.documents))
        
        with col3:
            st.metric("Strengths", len(vendor.strengths))
        
        with col4:
            st.metric("Status", vendor.status)
        
        # Detailed scores
        st.markdown("### Evaluation Scores")
        
        # Create radar chart
        scores = analysis['scores']
        categories = list(scores.keys())
        values = list(scores.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=[c.replace('_', ' ').title() for c in categories],
            fill='toself',
            name=vendor.name,
            line_color='#3498DB'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title=f"Vendor Evaluation: {vendor.name}"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Evaluation tabs
        tabs = st.tabs(["📝 Summary", "💪 Strengths", "⚠️ Risks", "💰 Commercial", "📋 Compliance", "💬 Recommendations"])
        
        with tabs[0]:  # Summary
            st.markdown("#### Executive Summary")
            st.write(analysis['executive_summary'])
            
            st.markdown("#### Next Steps")
            for step in analysis['next_steps']:
                st.write(f"• {step}")
        
        with tabs[1]:  # Strengths
            st.markdown("#### Key Strengths")
            if vendor.strengths:
                for strength in vendor.strengths:
                    st.success(f"✅ {strength}")
            else:
                st.info("No significant strengths identified")
            
            st.markdown("#### Areas for Improvement")
            if vendor.weaknesses:
                for weakness in vendor.weaknesses:
                    st.warning(f"⚠️ {weakness}")
            else:
                st.success("No major weaknesses identified")
        
        with tabs[2]:  # Risks
            st.markdown("#### Risk Assessment")
            
            risks = analysis['risks']
            if risks:
                for risk in risks:
                    if risk['level'] == "High":
                        st.error(f"🔴 **{risk['category']}**: {risk['description']}")
                    elif risk['level'] == "Medium":
                        st.warning(f"🟡 **{risk['category']}**: {risk['description']}")
                    else:
                        st.info(f"🟢 **{risk['category']}**: {risk['description']}")
                    
                    st.caption(f"Mitigation: {risk['mitigation']}")
            else:
                st.success("No significant risks identified")
        
        with tabs[3]:  # Commercial
            st.markdown("#### Commercial Evaluation")
            
            commercial = analysis['commercial_evaluation']
            for key, value in commercial.items():
                st.write(f"**{key.replace('_', ' ').title()}**: {value}")
        
        with tabs[4]:  # Compliance
            st.markdown("#### Compliance Status")
            
            compliance = analysis['compliance_status']
            
            cols = st.columns(3)
            for idx, (item, status) in enumerate(compliance.items()):
                col = cols[idx % 3]
                with col:
                    if status == "Compliant":
                        st.success(f"✅ {item.upper()}: {status}")
                    elif status == "Missing":
                        st.error(f"❌ {item.upper()}: {status}")
                    else:
                        st.warning(f"⚠️ {item.upper()}: {status}")
        
        with tabs[5]:  # Recommendations
            st.markdown("#### Recommendations")
            
            for rec in analysis['recommendations']:
                st.info(f"💡 {rec}")
        
        # Export options
        st.markdown("### Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export to Excel"):
                st.success("Excel report generated!")
        
        with col2:
            if st.button("📄 Generate PDF"):
                st.success("PDF report generated!")
        
        with col3:
            if st.button("📧 Email Report"):
                st.success("Report sent via email!")

def render_vendor_comparison(analyzer: RFPAnalyzer):
    """Render vendor comparison matrix"""
    st.subheader("📈 Vendor Comparison")
    
    if "vendors" not in st.session_state or len(st.session_state.vendors) < 2:
        st.info("Need at least 2 vendors for comparison. Please add more vendors.")
        return
    
    vendors = list(st.session_state.vendors.values())
    
    # Comparison table
    comparison_data = []
    for vendor in vendors:
        row = {
            "Vendor": vendor.name,
            "Overall Score": vendor.overall_score,
            "Status": vendor.status,
            "Submission Date": vendor.submission_date.strftime("%Y-%m-%d") if vendor.submission_date else "N/A"
        }
        
        # Add individual scores
        for key, value in vendor.scores.items():
            row[key.replace('_', ' ').title()] = value
        
        comparison_data.append(row)
    
    df = pd.DataFrame(comparison_data)
    
    # Highlight best scores
    def highlight_max(s):
        if s.dtype in ['float64', 'int64']:
            is_max = s == s.max()
            return ['background-color: #d4edda' if v else '' for v in is_max]
        return ['' for _ in s]
    
    styled_df = df.style.apply(highlight_max)
    st.dataframe(styled_df, use_container_width=True)
    
    # Comparison chart
    fig = go.Figure()
    
    for vendor in vendors[:5]:  # Limit to 5 vendors for clarity
        categories = [k.replace('_', ' ').title() for k in vendor.scores.keys()]
        values = list(vendor.scores.values())
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=vendor.name
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Vendor Comparison Radar"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ranking
    st.markdown("### 🏆 Vendor Ranking")
    
    ranked_vendors = sorted(vendors, key=lambda x: x.overall_score, reverse=True)
    
    for idx, vendor in enumerate(ranked_vendors[:5], 1):
        if idx == 1:
            emoji = "🥇"
        elif idx == 2:
            emoji = "🥈"
        elif idx == 3:
            emoji = "🥉"
        else:
            emoji = "📊"
        
        st.markdown(f"""
        <div class="vendor-card">
            <h4>{emoji} Rank {idx}: {vendor.name}</h4>
            <p>Score: {vendor.overall_score:.1f}/100 | Status: {vendor.status}</p>
        </div>
        """, unsafe_allow_html=True)

def render_qa_chat(analyzer: RFPAnalyzer):
    """Render Q&A chat interface"""
    st.subheader("💬 Intelligent Q&A Assistant")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Quick questions
    st.markdown("#### Quick Questions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    quick_questions = [
        "What is the RFP timeline?",
        "How many vendors submitted?",
        "Who is the top vendor?",
        "What are the key requirements?"
    ]
    
    for idx, question in enumerate(quick_questions):
        col = [col1, col2, col3, col4][idx]
        with col:
            if st.button(question, key=f"quick_{idx}"):
                # Add to chat
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": question
                })
                
                # Generate response
                if question == "What is the RFP timeline?":
                    response = f"The RFP was issued on {analyzer.current_rfp['issue_date'].strftime('%Y-%m-%d')} and is due on {analyzer.current_rfp['due_date'].strftime('%Y-%m-%d')}. Total duration: 28 days."
                elif question == "How many vendors submitted?":
                    vendor_count = len(st.session_state.get('vendors', {}))
                    response = f"Currently {vendor_count} vendor(s) have submitted proposals."
                elif question == "Who is the top vendor?":
                    if st.session_state.get('vendors'):
                        top_vendor = max(st.session_state.vendors.values(), key=lambda x: x.overall_score)
                        response = f"The top vendor is {top_vendor.name} with a score of {top_vendor.overall_score:.1f}/100."
                    else:
                        response = "No vendors have submitted proposals yet."
                else:
                    response = f"Key requirements include: {', '.join(analyzer.current_rfp['services_required'][:3])}"
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
                st.rerun()
    
    # Chat interface
    st.markdown("#### Ask a Question")
    
    with st.form("chat_form"):
        user_input = st.text_area("Your question:", height=100)
        submitted = st.form_submit_button("Send")
        
        if submitted and user_input:
            # Add to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate response (mock for demo)
            response = f"Thank you for your question about '{user_input[:50]}...'. Based on the RFP documentation and vendor submissions, I can provide detailed insights. The current workflow is {analyzer.get_workflow_progress()}% complete."
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            st.rerun()
    
    # Display chat history
    st.markdown("#### Conversation History")
    
    for message in st.session_state.chat_history[-10:]:  # Show last 10 messages
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
    
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def render_sidebar(analyzer: RFPAnalyzer):
    """Render sidebar navigation"""
    with st.sidebar:
        st.markdown("### 🎯 RFP Management")
        
        # RFP Details
        st.markdown("#### Current RFP")
        st.info(f"**ID:** {analyzer.current_rfp['rfp_id']}")
        st.caption(analyzer.current_rfp['title'])
        
        # Quick Stats
        st.markdown("#### 📊 Quick Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            vendor_count = len(st.session_state.get('vendors', {}))
            st.metric("Vendors", vendor_count)
        
        with col2:
            progress = analyzer.get_workflow_progress()
            st.metric("Progress", f"{progress}%")
        
        # Timeline
        st.markdown("#### ⏱️ Timeline")
        st.write(f"**Issued:** {analyzer.current_rfp['issue_date'].strftime('%b %d')}")
        st.write(f"**Due:** {analyzer.current_rfp['due_date'].strftime('%b %d')}")
        
        days_remaining = (analyzer.current_rfp['due_date'] - datetime.now()).days
        if days_remaining > 0:
            st.success(f"📅 {days_remaining} days remaining")
        else:
            st.error("⚠️ RFP deadline passed")
        
        # Navigation
        st.markdown("---")
        st.markdown("#### 📍 Navigation")
        
        pages = {
            "workflow": "📋 Workflow",
            "upload": "📤 Documents",
            "evaluation": "📊 Evaluation",
            "comparison": "📈 Comparison",
            "qa": "💬 Q&A Assistant"
        }
        
        for page_id, page_name in pages.items():
            if st.button(page_name, use_container_width=True, key=f"nav_{page_id}"):
                st.session_state.current_page = page_id
                st.rerun()
        
        # Help
        st.markdown("---")
        with st.expander("❓ Help"):
            st.markdown("""
            **Quick Guide:**
            1. Start workflow stages
            2. Upload RFP documents
            3. Receive vendor proposals
            4. Evaluate submissions
            5. Compare vendors
            6. Make selection
            7. Finalize contract
            
            **Support:**
            - Email: rfp-support@company.com
            - Phone: 1-800-RFP-HELP
            """)

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    """Main application entry point"""
    
    # Initialize
    analyzer = RFPAnalyzer()
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'workflow'
    
    if 'vendors' not in st.session_state:
        st.session_state.vendors = {}
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar(analyzer)
    
    # Main content area
    if st.session_state.current_page == 'workflow':
        st.header("📋 RFP Workflow Management")
        render_workflow_timeline(analyzer)
        
        # Workflow actions
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⏭️ Move to Next Stage", type="primary"):
                success, message = analyzer.move_to_next_stage()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            if st.button("📊 View Workflow Report"):
                st.info("Generating workflow report...")
        
        with col3:
            if st.button("🔄 Reset Workflow"):
                if st.checkbox("Confirm reset"):
                    analyzer.workflow_stages = analyzer._initialize_workflow()
                    st.success("Workflow reset!")
                    st.rerun()
    
    elif st.session_state.current_page == 'upload':
        st.header("📤 Document Management")
        render_document_upload(analyzer)
    
    elif st.session_state.current_page == 'evaluation':
        st.header("📊 Vendor Evaluation")
        render_vendor_evaluation(analyzer)
    
    elif st.session_state.current_page == 'comparison':
        st.header("📈 Vendor Comparison")
        render_vendor_comparison(analyzer)
    
    elif st.session_state.current_page == 'qa':
        st.header("💬 Q&A Assistant")
        render_qa_chat(analyzer)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>© 2025 RFP Vendor Management System | Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
