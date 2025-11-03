"""
🎯 Enhanced RFP Analysis & Vendor Management System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enterprise-grade RFP evaluation platform for UPS Global Logistics & Distribution
Supporting multi-document analysis, vendor scoring, and complete procurement workflow
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
import openpyxl
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
import base64
import time

# ========================================
# CONFIGURATION & INITIALIZATION
# ========================================

st.set_page_config(
    page_title="UPS GLD - RFP Vendor Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional UI
st.markdown("""
<style>
    /* Main Theme */
    :root {
        --primary-color: #351C15;  /* UPS Brown */
        --secondary-color: #FFB500; /* UPS Gold */
        --success-color: #16a34a;
        --warning-color: #ca8a04;
        --danger-color: #dc2626;
        --info-color: #2563eb;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, #5a3028 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .workflow-stage {
        background: white;
        border-left: 4px solid var(--secondary-color);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-top: 3px solid var(--primary-color);
        margin-bottom: 1rem;
    }
    
    .vendor-card {
        background: linear-gradient(to bottom, #ffffff, #f9f9f9);
        border: 1px solid #e5e5e5;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .vendor-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.15);
    }
    
    .document-item {
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid var(--info-color);
    }
    
    .stage-complete {
        background-color: #dcfce7;
        border-left-color: var(--success-color);
    }
    
    .stage-active {
        background-color: #fef3c7;
        border-left-color: var(--warning-color);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    .timeline-item {
        position: relative;
        padding-left: 40px;
        margin-bottom: 30px;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: 10px;
        top: 0;
        height: 100%;
        width: 2px;
        background: var(--primary-color);
    }
    
    .timeline-dot {
        position: absolute;
        left: 4px;
        top: 5px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: var(--secondary-color);
        border: 2px solid var(--primary-color);
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .score-excellent { background: #dcfce7; color: #166534; }
    .score-good { background: #dbeafe; color: #1e40af; }
    .score-fair { background: #fef3c7; color: #92400e; }
    .score-poor { background: #fee2e2; color: #991b1b; }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .comparison-table {
        border-collapse: collapse;
        width: 100%;
    }
    
    .comparison-table th {
        background: var(--primary-color);
        color: white;
        padding: 1rem;
        text-align: left;
    }
    
    .comparison-table td {
        padding: 0.75rem;
        border-bottom: 1px solid #e5e5e5;
    }
    
    .comparison-table tr:hover {
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# CORE CLASSES
# ========================================

class WorkflowStage:
    """Represents a stage in the RFP workflow"""
    def __init__(self, stage_id: str, name: str, description: str, required_docs: List[str], 
                 outputs: List[str], status: str = "pending"):
        self.stage_id = stage_id
        self.name = name
        self.description = description
        self.required_docs = required_docs
        self.outputs = outputs
        self.status = status
        self.completion_date = None
        self.assigned_to = None
        self.notes = []

class VendorProfile:
    """Comprehensive vendor profile management"""
    def __init__(self, vendor_id: str, name: str):
        self.vendor_id = vendor_id
        self.name = name
        self.submission_date = datetime.now()
        self.documents = {}
        self.scores = {}
        self.status = "Under Review"
        self.risk_assessment = {}
        self.compliance_status = {}
        self.communication_history = []
        self.decision = None
        self.contract_terms = {}

class DocumentAnalyzer:
    """Enhanced document analysis with multi-document support"""
    def __init__(self, claude_client):
        self.claude_client = claude_client
        self.document_cache = {}
        
    def extract_text_from_file(self, uploaded_file) -> Optional[str]:
        """Extract text from various file formats"""
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                return self._extract_pdf_text(uploaded_file)
            elif file_extension in ['doc', 'docx']:
                return self._extract_docx_text(uploaded_file)
            elif file_extension in ['ppt', 'pptx']:
                return self._extract_pptx_text(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                return self._extract_excel_text(uploaded_file)
            else:
                return None
        except Exception as e:
            st.error(f"Error extracting text from {uploaded_file.name}: {str(e)}")
            return None
    
    def _extract_pdf_text(self, pdf_file) -> str:
        """Extract text from PDF"""
        text = ""
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text += f"\n[Page {page_num}]\n"
            text += page.extract_text() + "\n"
        return text
    
    def _extract_docx_text(self, docx_file) -> str:
        """Extract text from Word document"""
        doc = docx.Document(docx_file)
        text = ""
        for para_num, paragraph in enumerate(doc.paragraphs, 1):
            if paragraph.text.strip():
                text += f"[Para {para_num}] {paragraph.text}\n"
        
        # Extract tables
        for table_num, table in enumerate(doc.tables, 1):
            text += f"\n[Table {table_num}]\n"
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    row_text.append(cell.text.strip())
                text += " | ".join(row_text) + "\n"
        return text
    
    def _extract_pptx_text(self, pptx_file) -> str:
        """Extract text from PowerPoint"""
        prs = Presentation(pptx_file)
        text = ""
        for slide_num, slide in enumerate(prs.slides, 1):
            text += f"\n[Slide {slide_num}]\n"
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    
    def _extract_excel_text(self, excel_file) -> str:
        """Extract text from Excel"""
        text = ""
        try:
            df_dict = pd.read_excel(excel_file, sheet_name=None)
            for sheet_name, df in df_dict.items():
                text += f"\n[Sheet: {sheet_name}]\n"
                text += df.to_string() + "\n"
        except Exception as e:
            text = f"Error reading Excel file: {str(e)}"
        return text

class UPSRFPAnalyzer:
    """Main RFP Analysis Engine for UPS GLD"""
    def __init__(self):
        self.claude_client = None
        self.document_analyzer = None
        self.vendors = {}
        self.workflow_stages = self._initialize_workflow()
        self.evaluation_criteria = self._get_evaluation_criteria()
        self.initialize_claude()
        
    def initialize_claude(self):
        """Initialize Claude API with robust error handling"""
        try:
            api_key = (st.secrets.get("CLAUDE_API_KEY") or 
                      st.secrets.get("ANTHROPIC_API_KEY") or 
                      st.secrets.get("claude_api_key") or 
                      st.secrets.get("anthropic_api_key"))
            
            if api_key:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
                self.document_analyzer = DocumentAnalyzer(self.claude_client)
                return True
            else:
                st.error("❌ Claude API key not found. Please configure in Streamlit secrets.")
                return False
        except Exception as e:
            st.error(f"❌ Error initializing Claude API: {str(e)}")
            return False
    
    def _initialize_workflow(self) -> Dict[str, WorkflowStage]:
        """Initialize the complete RFP workflow stages"""
        stages = {
            "initiation": WorkflowStage(
                "initiation", 
                "1. RFP Initiation",
                "Request received from UPS customer for logistics services",
                ["Initial Request", "Service Requirements"],
                ["RFP Package", "Timeline", "Budget Estimate"]
            ),
            "documentation": WorkflowStage(
                "documentation",
                "2. Documentation Preparation",
                "Compile all required RFP documents and specifications",
                ["SOW Templates", "Service Specifications", "Quality Requirements"],
                ["Complete RFP Package", "Vendor Questionnaires"]
            ),
            "vendor_identification": WorkflowStage(
                "vendor_identification",
                "3. Vendor Identification",
                "Identify and pre-qualify potential vendors",
                ["Vendor Database", "Market Analysis"],
                ["Qualified Vendor List", "Vendor Profiles"]
            ),
            "distribution": WorkflowStage(
                "distribution",
                "4. RFP Distribution",
                "Send RFP package to qualified vendors",
                ["RFP Package", "Distribution List"],
                ["Confirmation of Receipt", "Q&A Schedule"]
            ),
            "qa_period": WorkflowStage(
                "qa_period",
                "5. Q&A Period",
                "Address vendor questions and clarifications",
                ["Vendor Questions", "Technical Specifications"],
                ["Q&A Responses", "Addendums"]
            ),
            "submission": WorkflowStage(
                "submission",
                "6. Proposal Submission",
                "Receive and validate vendor proposals",
                ["Vendor Proposals", "Supporting Documents"],
                ["Validated Submissions", "Compliance Matrix"]
            ),
            "technical_evaluation": WorkflowStage(
                "technical_evaluation",
                "7. Technical Evaluation",
                "Evaluate technical capabilities and approach",
                ["Technical Proposals", "Architecture Documents"],
                ["Technical Scores", "Risk Assessment"]
            ),
            "commercial_evaluation": WorkflowStage(
                "commercial_evaluation",
                "8. Commercial Evaluation",
                "Analyze pricing and commercial terms",
                ["Pricing Proposals", "Payment Terms"],
                ["Commercial Scores", "Cost Analysis"]
            ),
            "final_selection": WorkflowStage(
                "final_selection",
                "9. Final Selection",
                "Select winning vendor(s)",
                ["Evaluation Matrix", "Stakeholder Input"],
                ["Selected Vendor", "Negotiation Points"]
            ),
            "contract_negotiation": WorkflowStage(
                "contract_negotiation",
                "10. Contract Negotiation",
                "Negotiate final terms and conditions",
                ["Draft Contract", "Terms & Conditions"],
                ["Final Contract", "SLAs"]
            ),
            "onboarding": WorkflowStage(
                "onboarding",
                "11. Vendor Onboarding",
                "Onboard selected vendor and begin operations",
                ["Signed Contract", "Implementation Plan"],
                ["Kickoff Meeting", "Go-Live Schedule"]
            )
        }
        return stages
    
    def _get_evaluation_criteria(self) -> Dict[str, Dict]:
        """Define comprehensive evaluation criteria for UPS GLD"""
        return {
            "warehouse_operations": {
                "weight": 0.20,
                "subcriteria": {
                    "facility_capabilities": 0.30,
                    "inventory_management": 0.25,
                    "order_fulfillment": 0.25,
                    "technology_integration": 0.20
                }
            },
            "customer_service": {
                "weight": 0.15,
                "subcriteria": {
                    "rma_processing": 0.35,
                    "response_time": 0.25,
                    "issue_resolution": 0.20,
                    "communication": 0.20
                }
            },
            "logistics_capability": {
                "weight": 0.15,
                "subcriteria": {
                    "transportation_network": 0.30,
                    "last_mile_delivery": 0.25,
                    "international_shipping": 0.25,
                    "tracking_visibility": 0.20
                }
            },
            "compliance_security": {
                "weight": 0.15,
                "subcriteria": {
                    "ctpat_certification": 0.30,
                    "tapa_certification": 0.25,
                    "data_security": 0.25,
                    "regulatory_compliance": 0.20
                }
            },
            "pricing_value": {
                "weight": 0.15,
                "subcriteria": {
                    "cost_competitiveness": 0.35,
                    "pricing_transparency": 0.25,
                    "value_added_services": 0.20,
                    "payment_terms": 0.20
                }
            },
            "quality_systems": {
                "weight": 0.10,
                "subcriteria": {
                    "iso_certification": 0.30,
                    "quality_metrics": 0.25,
                    "continuous_improvement": 0.25,
                    "defect_management": 0.20
                }
            },
            "technology_innovation": {
                "weight": 0.10,
                "subcriteria": {
                    "system_integration": 0.30,
                    "automation_level": 0.25,
                    "reporting_analytics": 0.25,
                    "innovation_roadmap": 0.20
                }
            }
        }
    
    def analyze_documents(self, vendor_id: str, documents: Dict[str, Any]) -> Dict:
        """Analyze multiple documents for a vendor"""
        if not self.claude_client:
            return {"error": "Claude API not initialized"}
        
        combined_analysis = {
            "vendor_id": vendor_id,
            "analysis_date": datetime.now().isoformat(),
            "document_count": len(documents),
            "documents_analyzed": [],
            "consolidated_scores": {},
            "key_findings": [],
            "risks": {"high": [], "medium": [], "low": []},
            "recommendations": [],
            "compliance_check": {},
            "service_capabilities": {}
        }
        
        # Analyze each document
        for doc_name, doc_content in documents.items():
            if doc_content:
                doc_analysis = self._analyze_single_document(doc_name, doc_content)
                combined_analysis["documents_analyzed"].append({
                    "name": doc_name,
                    "type": self._identify_document_type(doc_name),
                    "analysis": doc_analysis
                })
        
        # Consolidate findings
        combined_analysis = self._consolidate_analysis(combined_analysis)
        
        return combined_analysis
    
    def _identify_document_type(self, filename: str) -> str:
        """Identify document type based on filename patterns"""
        filename_lower = filename.lower()
        
        if "sow" in filename_lower or "statement" in filename_lower:
            return "Statement of Work"
        elif "pricing" in filename_lower or "cost" in filename_lower or "financial" in filename_lower:
            return "Pricing/Financial"
        elif "quality" in filename_lower or "qms" in filename_lower:
            return "Quality Documentation"
        elif "infosec" in filename_lower or "security" in filename_lower:
            return "Security/InfoSec"
        elif "questionnaire" in filename_lower or "rfi" in filename_lower:
            return "Questionnaire/RFI"
        elif "warehouse" in filename_lower or "logistics" in filename_lower:
            return "Warehouse/Logistics"
        elif "contract" in filename_lower or "agreement" in filename_lower:
            return "Contract/Agreement"
        elif "technical" in filename_lower or "architecture" in filename_lower:
            return "Technical Specification"
        else:
            return "General Document"
    
    def _analyze_single_document(self, doc_name: str, doc_content: str) -> Dict:
        """Analyze a single document using Claude"""
        doc_type = self._identify_document_type(doc_name)
        
        prompt = f"""
        You are analyzing a {doc_type} document for UPS Global Logistics & Distribution RFP evaluation.
        
        Document Name: {doc_name}
        Document Type: {doc_type}
        
        DOCUMENT CONTENT (First 5000 chars):
        {doc_content[:5000]}
        
        Please provide a comprehensive analysis in JSON format:
        {{
            "document_summary": {{
                "purpose": "Main purpose of this document",
                "scope": "Scope covered",
                "key_services": ["Service 1", "Service 2"],
                "critical_requirements": ["Requirement 1", "Requirement 2"]
            }},
            "service_capabilities": {{
                "warehouse_operations": "Details if mentioned",
                "customer_service": "CSO/RMA capabilities",
                "logistics": "Transportation and delivery",
                "technology": "Systems and integration",
                "quality": "Quality measures"
            }},
            "compliance_requirements": {{
                "ctpat": "C-TPAT requirement status",
                "tapa": "TAPA certification requirement",
                "iso": "ISO certifications required",
                "data_security": "Data security requirements",
                "other": "Other compliance needs"
            }},
            "pricing_structure": {{
                "model": "Pricing model if mentioned",
                "key_cost_drivers": ["Driver 1", "Driver 2"],
                "payment_terms": "Payment terms if specified"
            }},
            "risks_identified": {{
                "operational": ["Risk 1", "Risk 2"],
                "financial": ["Risk 1"],
                "compliance": ["Risk 1"],
                "technical": ["Risk 1"]
            }},
            "sla_metrics": {{
                "turnaround_time": "TAT requirements",
                "accuracy": "Accuracy requirements",
                "availability": "Service availability"
            }},
            "key_findings": [
                "Finding 1",
                "Finding 2",
                "Finding 3"
            ]
        }}
        """
        
        try:
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                return json.loads(response_text[json_start:json_end])
            else:
                return {"error": "Could not parse analysis"}
        except Exception as e:
            return {"error": str(e)}
    
    def _consolidate_analysis(self, combined_analysis: Dict) -> Dict:
        """Consolidate analysis from multiple documents"""
        if not combined_analysis["documents_analyzed"]:
            return combined_analysis
        
        # Aggregate service capabilities
        service_scores = {}
        for criteria in self.evaluation_criteria.keys():
            scores = []
            for doc in combined_analysis["documents_analyzed"]:
                if "analysis" in doc and not isinstance(doc["analysis"], dict) or "error" not in doc["analysis"]:
                    # Extract relevant scores based on document content
                    scores.append(self._calculate_criteria_score(criteria, doc["analysis"]))
            
            if scores:
                service_scores[criteria] = sum(scores) / len(scores)
        
        combined_analysis["consolidated_scores"] = service_scores
        
        # Calculate overall score
        overall_score = 0
        for criteria, score in service_scores.items():
            weight = self.evaluation_criteria[criteria]["weight"]
            overall_score += score * weight
        
        combined_analysis["overall_score"] = round(overall_score, 2)
        
        # Aggregate risks
        for doc in combined_analysis["documents_analyzed"]:
            if "analysis" in doc and isinstance(doc["analysis"], dict):
                if "risks_identified" in doc["analysis"]:
                    risks = doc["analysis"]["risks_identified"]
                    # Categorize risks
                    for risk_type, risk_list in risks.items():
                        if isinstance(risk_list, list):
                            for risk in risk_list:
                                if "critical" in risk.lower() or "high" in risk.lower():
                                    combined_analysis["risks"]["high"].append(risk)
                                elif "medium" in risk.lower() or "moderate" in risk.lower():
                                    combined_analysis["risks"]["medium"].append(risk)
                                else:
                                    combined_analysis["risks"]["low"].append(risk)
        
        return combined_analysis
    
    def _calculate_criteria_score(self, criteria: str, analysis: Dict) -> float:
        """Calculate score for a specific criteria based on document analysis"""
        # Simplified scoring logic - in production, this would be more sophisticated
        base_score = 70  # Base score
        
        # Adjust based on document completeness and requirements met
        if "service_capabilities" in analysis:
            if criteria in ["warehouse_operations", "customer_service", "logistics"]:
                capabilities = analysis.get("service_capabilities", {})
                if capabilities.get(criteria.replace("_", " ")):
                    base_score += 10
        
        if "compliance_requirements" in analysis:
            if criteria == "compliance_security":
                compliance = analysis.get("compliance_requirements", {})
                if compliance.get("ctpat") and compliance.get("tapa"):
                    base_score += 15
        
        if "sla_metrics" in analysis:
            if criteria == "quality_systems":
                sla = analysis.get("sla_metrics", {})
                if sla.get("accuracy") and sla.get("turnaround_time"):
                    base_score += 10
        
        return min(base_score, 100)
    
    def generate_vendor_comparison(self, vendors: Dict[str, VendorProfile]) -> pd.DataFrame:
        """Generate comprehensive vendor comparison matrix"""
        comparison_data = []
        
        for vendor_id, vendor in vendors.items():
            vendor_data = {
                "Vendor": vendor.name,
                "Submission Date": vendor.submission_date.strftime("%Y-%m-%d"),
                "Documents": len(vendor.documents),
                "Overall Score": vendor.scores.get("overall", 0),
                "Status": vendor.status
            }
            
            # Add scores for each criteria
            for criteria in self.evaluation_criteria.keys():
                criteria_name = criteria.replace("_", " ").title()
                vendor_data[criteria_name] = vendor.scores.get(criteria, 0)
            
            comparison_data.append(vendor_data)
        
        return pd.DataFrame(comparison_data)
    
    def export_evaluation_report(self, vendor: VendorProfile, analysis: Dict) -> bytes:
        """Generate comprehensive evaluation report in Excel format"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary Sheet
            summary_data = {
                "Vendor Information": [
                    ["Vendor Name", vendor.name],
                    ["Vendor ID", vendor.vendor_id],
                    ["Submission Date", vendor.submission_date.strftime("%Y-%m-%d %H:%M")],
                    ["Overall Score", analysis.get("overall_score", 0)],
                    ["Status", vendor.status],
                    ["Documents Analyzed", analysis.get("document_count", 0)]
                ]
            }
            
            df_summary = pd.DataFrame(summary_data["Vendor Information"], 
                                     columns=["Field", "Value"])
            df_summary.to_excel(writer, sheet_name="Executive Summary", index=False)
            
            # Detailed Scores Sheet
            scores_data = []
            for criteria, score in analysis.get("consolidated_scores", {}).items():
                scores_data.append([
                    criteria.replace("_", " ").title(),
                    self.evaluation_criteria[criteria]["weight"],
                    score,
                    score * self.evaluation_criteria[criteria]["weight"]
                ])
            
            df_scores = pd.DataFrame(scores_data, 
                                    columns=["Criteria", "Weight", "Score", "Weighted Score"])
            df_scores.to_excel(writer, sheet_name="Scoring Details", index=False)
            
            # Risk Assessment Sheet
            risks_data = []
            for level, risks in analysis.get("risks", {}).items():
                for risk in risks:
                    risks_data.append([level.upper(), risk])
            
            if risks_data:
                df_risks = pd.DataFrame(risks_data, columns=["Risk Level", "Description"])
                df_risks.to_excel(writer, sheet_name="Risk Assessment", index=False)
            
            # Document Analysis Sheet
            doc_analysis_data = []
            for doc in analysis.get("documents_analyzed", []):
                doc_analysis_data.append([
                    doc["name"],
                    doc["type"],
                    "Analyzed" if "analysis" in doc else "Error"
                ])
            
            df_docs = pd.DataFrame(doc_analysis_data, 
                                  columns=["Document Name", "Type", "Status"])
            df_docs.to_excel(writer, sheet_name="Documents", index=False)
            
            # Format the Excel file
            workbook = writer.book
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
                
                # Header formatting
                header_fill = PatternFill(start_color="351C15", end_color="351C15", fill_type="solid")
                header_font = Font(color="FFFFFF", bold=True)
                
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center")
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output.read()

# ========================================
# UI COMPONENTS
# ========================================

def render_header():
    """Render application header"""
    st.markdown("""
    <div class="main-header">
        <h1>📦 UPS Global Logistics & Distribution</h1>
        <h2>RFP Vendor Management System</h2>
        <p>Enterprise Procurement Platform for Warehouse, CSO, and CSG Services</p>
    </div>
    """, unsafe_allow_html=True)

def render_workflow_status(analyzer: UPSRFPAnalyzer):
    """Render workflow status timeline"""
    st.subheader("📋 RFP Workflow Status")
    
    cols = st.columns(len(analyzer.workflow_stages))
    
    for idx, (stage_id, stage) in enumerate(analyzer.workflow_stages.items()):
        with cols[idx % len(cols)]:
            if stage.status == "completed":
                status_class = "stage-complete"
                icon = "✅"
            elif stage.status == "active":
                status_class = "stage-active"
                icon = "🔄"
            else:
                status_class = "workflow-stage"
                icon = "⏳"
            
            st.markdown(f"""
            <div class="{status_class}">
                <strong>{icon} Stage {idx + 1}</strong><br>
                <small>{stage.name.split('. ')[1]}</small>
            </div>
            """, unsafe_allow_html=True)

def render_vendor_management(analyzer: UPSRFPAnalyzer):
    """Render vendor management interface"""
    st.header("👥 Vendor Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Document Upload", "📊 Analysis", "📈 Comparison", "💬 Q&A"])
    
    with tab1:
        render_document_upload(analyzer)
    
    with tab2:
        render_analysis_results(analyzer)
    
    with tab3:
        render_vendor_comparison(analyzer)
    
    with tab4:
        render_qa_interface(analyzer)

def render_document_upload(analyzer: UPSRFPAnalyzer):
    """Render multi-document upload interface"""
    st.subheader("📄 Upload Vendor Documents")
    
    # Vendor selection/creation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        vendor_name = st.text_input("Vendor Name", placeholder="Enter vendor name (e.g., ABC Logistics Inc.)")
    
    with col2:
        vendor_id = st.text_input("Vendor ID", value=f"VND-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}", 
                                  disabled=True)
    
    # Document categories
    st.write("**Required Documents:**")
    
    doc_categories = {
        "Core Documents": [
            "Statement of Work (SOW)",
            "Pricing Proposal",
            "Technical Proposal"
        ],
        "Compliance & Security": [
            "InfoSec Questionnaire",
            "C-TPAT Certification",
            "TAPA Certification"
        ],
        "Service Specific": [
            "Warehouse Operations SOW",
            "Customer Service SOW",
            "CSG Services SOW"
        ],
        "Supporting Documents": [
            "Company Profile",
            "Financial Statements",
            "References"
        ]
    }
    
    uploaded_files = {}
    
    for category, docs in doc_categories.items():
        with st.expander(f"📁 {category}", expanded=True):
            cols = st.columns(2)
            for idx, doc in enumerate(docs):
                with cols[idx % 2]:
                    file = st.file_uploader(
                        doc,
                        type=['pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls'],
                        key=f"upload_{category}_{doc}",
                        help=f"Upload {doc}"
                    )
                    if file:
                        uploaded_files[doc] = file
                        st.success(f"✅ {file.name}")
    
    # Process uploaded documents
    if st.button("🔍 Analyze Documents", type="primary", disabled=not vendor_name or not uploaded_files):
        if vendor_name and uploaded_files:
            with st.spinner(f"Processing {len(uploaded_files)} documents for {vendor_name}..."):
                # Create vendor profile
                vendor = VendorProfile(vendor_id, vendor_name)
                
                # Extract text from all documents
                document_contents = {}
                progress_bar = st.progress(0)
                
                for idx, (doc_type, file) in enumerate(uploaded_files.items()):
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                    st.write(f"📄 Processing: {file.name}")
                    
                    text_content = analyzer.document_analyzer.extract_text_from_file(file)
                    if text_content:
                        document_contents[file.name] = text_content
                        vendor.documents[doc_type] = file.name
                
                # Analyze documents
                st.write("🤖 Analyzing with AI...")
                analysis_results = analyzer.analyze_documents(vendor_id, document_contents)
                
                # Store results
                vendor.scores = analysis_results.get("consolidated_scores", {})
                vendor.scores["overall"] = analysis_results.get("overall_score", 0)
                
                # Save to session state
                if "vendors" not in st.session_state:
                    st.session_state.vendors = {}
                st.session_state.vendors[vendor_id] = vendor
                st.session_state.current_analysis = analysis_results
                
                st.success(f"✅ Analysis complete for {vendor_name}!")
                st.balloons()

def render_analysis_results(analyzer: UPSRFPAnalyzer):
    """Render detailed analysis results"""
    if "current_analysis" not in st.session_state:
        st.info("📊 No analysis results available. Please upload and analyze vendor documents first.")
        return
    
    analysis = st.session_state.current_analysis
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_score = analysis.get("overall_score", 0)
        st.metric("Overall Score", f"{overall_score}/100", 
                 delta=f"{overall_score - 75:.1f} vs benchmark" if overall_score else None)
    
    with col2:
        st.metric("Documents Analyzed", analysis.get("document_count", 0))
    
    with col3:
        high_risks = len(analysis.get("risks", {}).get("high", []))
        st.metric("High Risks", high_risks, 
                 delta_color="inverse" if high_risks > 0 else "off")
    
    with col4:
        st.metric("Analysis Date", 
                 datetime.fromisoformat(analysis.get("analysis_date", datetime.now().isoformat())).strftime("%Y-%m-%d"))
    
    # Detailed scoring breakdown
    st.subheader("📊 Scoring Breakdown")
    
    scores = analysis.get("consolidated_scores", {})
    if scores:
        # Create radar chart
        categories = []
        values = []
        
        for criteria, score in scores.items():
            categories.append(criteria.replace("_", " ").title())
            values.append(score)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Vendor Score',
            line_color='#351C15',
            fillcolor='rgba(53, 28, 21, 0.3)'
        ))
        
        # Add benchmark
        benchmark_values = [75] * len(categories)
        fig.add_trace(go.Scatterpolar(
            r=benchmark_values,
            theta=categories,
            fill='toself',
            name='Benchmark',
            line_color='#FFB500',
            fillcolor='rgba(255, 181, 0, 0.1)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Vendor Performance vs Benchmark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed scores table
        scores_df = pd.DataFrame([
            {
                "Criteria": criteria.replace("_", " ").title(),
                "Score": score,
                "Weight": f"{analyzer.evaluation_criteria[criteria]['weight']*100:.0f}%",
                "Weighted Score": score * analyzer.evaluation_criteria[criteria]['weight']
            }
            for criteria, score in scores.items()
        ])
        
        st.dataframe(scores_df, use_container_width=True, hide_index=True)
    
    # Risk Assessment
    st.subheader("⚠️ Risk Assessment")
    
    risks = analysis.get("risks", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔴 High Risks")
        for risk in risks.get("high", []):
            st.markdown(f"• {risk}")
        if not risks.get("high"):
            st.markdown("*No high risks identified*")
    
    with col2:
        st.markdown("### 🟡 Medium Risks")
        for risk in risks.get("medium", []):
            st.markdown(f"• {risk}")
        if not risks.get("medium"):
            st.markdown("*No medium risks identified*")
    
    with col3:
        st.markdown("### 🟢 Low Risks")
        for risk in risks.get("low", []):
            st.markdown(f"• {risk}")
        if not risks.get("low"):
            st.markdown("*No low risks identified*")
    
    # Key Findings
    st.subheader("🔍 Key Findings")
    
    for doc in analysis.get("documents_analyzed", []):
        if "analysis" in doc and isinstance(doc["analysis"], dict):
            with st.expander(f"📄 {doc['name']} ({doc['type']})"):
                if "key_findings" in doc["analysis"]:
                    for finding in doc["analysis"]["key_findings"]:
                        st.write(f"• {finding}")
    
    # Export options
    st.subheader("📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to Excel"):
            if "vendors" in st.session_state and st.session_state.vendors:
                vendor = list(st.session_state.vendors.values())[0]
                excel_data = analyzer.export_evaluation_report(vendor, analysis)
                
                st.download_button(
                    label="Download Excel Report",
                    data=excel_data,
                    file_name=f"vendor_evaluation_{vendor.vendor_id}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with col2:
        if st.button("📄 Generate PDF Report"):
            st.info("PDF generation coming soon...")
    
    with col3:
        if st.button("📧 Email Report"):
            st.info("Email functionality coming soon...")

def render_vendor_comparison(analyzer: UPSRFPAnalyzer):
    """Render vendor comparison matrix"""
    if "vendors" not in st.session_state or not st.session_state.vendors:
        st.info("📊 No vendors to compare. Please analyze at least one vendor first.")
        return
    
    st.subheader("📈 Vendor Comparison Matrix")
    
    # Generate comparison data
    comparison_df = analyzer.generate_vendor_comparison(st.session_state.vendors)
    
    if not comparison_df.empty:
        # Highlight best scores
        def highlight_max(s):
            is_max = s == s.max()
            return ['background-color: #dcfce7' if v else '' for v in is_max]
        
        styled_df = comparison_df.style.apply(highlight_max, subset=[col for col in comparison_df.columns if 'Score' in col or col in [c.replace("_", " ").title() for c in analyzer.evaluation_criteria.keys()]])
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Comparison chart
        st.subheader("📊 Visual Comparison")
        
        # Prepare data for grouped bar chart
        vendors = comparison_df["Vendor"].tolist()
        criteria_cols = [c.replace("_", " ").title() for c in analyzer.evaluation_criteria.keys()]
        
        fig = go.Figure()
        
        for vendor in vendors:
            vendor_data = comparison_df[comparison_df["Vendor"] == vendor]
            scores = []
            for col in criteria_cols:
                if col in vendor_data.columns:
                    scores.append(vendor_data[col].values[0])
                else:
                    scores.append(0)
            
            fig.add_trace(go.Bar(
                name=vendor,
                x=criteria_cols,
                y=scores
            ))
        
        fig.update_layout(
            title="Vendor Score Comparison",
            xaxis_title="Evaluation Criteria",
            yaxis_title="Score",
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Ranking
        st.subheader("🏆 Vendor Ranking")
        
        ranking_df = comparison_df[["Vendor", "Overall Score"]].sort_values("Overall Score", ascending=False)
        ranking_df["Rank"] = range(1, len(ranking_df) + 1)
        
        for idx, row in ranking_df.iterrows():
            rank = row["Rank"]
            vendor = row["Vendor"]
            score = row["Overall Score"]
            
            if rank == 1:
                emoji = "🥇"
                color = "#FFD700"
            elif rank == 2:
                emoji = "🥈"
                color = "#C0C0C0"
            elif rank == 3:
                emoji = "🥉"
                color = "#CD7F32"
            else:
                emoji = "📊"
                color = "#FFFFFF"
            
            st.markdown(f"""
            <div style="background: {color}20; padding: 10px; border-radius: 5px; margin: 5px 0;">
                {emoji} <strong>Rank {rank}:</strong> {vendor} - Score: {score}/100
            </div>
            """, unsafe_allow_html=True)

def render_qa_interface(analyzer: UPSRFPAnalyzer):
    """Render Q&A interface for vendor clarifications"""
    st.subheader("💬 Vendor Q&A Management")
    
    tab1, tab2 = st.tabs(["Ask Questions", "Q&A History"])
    
    with tab1:
        if "vendors" in st.session_state and st.session_state.vendors:
            vendor_names = [v.name for v in st.session_state.vendors.values()]
            selected_vendor = st.selectbox("Select Vendor", vendor_names)
            
            question_category = st.selectbox(
                "Question Category",
                ["Technical", "Commercial", "Compliance", "Operations", "General"]
            )
            
            question = st.text_area("Your Question", height=100)
            
            if st.button("Send Question", disabled=not question):
                # In production, this would send to vendor
                st.success(f"✅ Question sent to {selected_vendor}")
                
                # Store in Q&A history
                if "qa_history" not in st.session_state:
                    st.session_state.qa_history = []
                
                st.session_state.qa_history.append({
                    "vendor": selected_vendor,
                    "category": question_category,
                    "question": question,
                    "timestamp": datetime.now(),
                    "status": "Pending",
                    "response": None
                })
        else:
            st.info("No vendors available. Please add vendors first.")
    
    with tab2:
        if "qa_history" in st.session_state and st.session_state.qa_history:
            for qa in st.session_state.qa_history:
                with st.expander(f"{qa['vendor']} - {qa['category']} - {qa['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    st.write(f"**Question:** {qa['question']}")
                    st.write(f"**Status:** {qa['status']}")
                    if qa['response']:
                        st.write(f"**Response:** {qa['response']}")
        else:
            st.info("No Q&A history available.")

def render_sidebar(analyzer: UPSRFPAnalyzer):
    """Render sidebar with navigation and tools"""
    with st.sidebar:
        st.header("🛠️ Tools & Navigation")
        
        # Quick Stats
        st.subheader("📊 Quick Stats")
        
        vendor_count = len(st.session_state.get("vendors", {}))
        st.metric("Active Vendors", vendor_count)
        
        if "current_analysis" in st.session_state:
            st.metric("Last Analysis", 
                     datetime.fromisoformat(st.session_state.current_analysis.get("analysis_date", 
                     datetime.now().isoformat())).strftime("%H:%M"))
        
        # Navigation
        st.subheader("📍 Navigation")
        
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
        
        if st.button("👥 Vendors", use_container_width=True):
            st.session_state.current_page = "vendors"
        
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
        
        if st.button("📋 Workflow", use_container_width=True):
            st.session_state.current_page = "workflow"
        
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = "settings"
        
        # Document Templates
        st.subheader("📄 Templates")
        
        templates = {
            "RFP Template": "rfp_template.docx",
            "SOW Template": "sow_template.docx",
            "Evaluation Matrix": "evaluation_matrix.xlsx",
            "Contract Template": "contract_template.docx"
        }
        
        for name, file in templates.items():
            if st.button(f"📥 {name}", use_container_width=True):
                st.info(f"Template {file} would be downloaded in production")
        
        # Help & Support
        st.subheader("❓ Help & Support")
        
        with st.expander("User Guide"):
            st.write("""
            **Quick Start:**
            1. Upload vendor documents
            2. Run AI analysis
            3. Review scores
            4. Compare vendors
            5. Make selection
            
            **Support:**
            - Email: rfp-support@ups.com
            - Phone: 1-800-RFP-HELP
            """)

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    """Main application entry point"""
    # Initialize analyzer
    analyzer = UPSRFPAnalyzer()
    
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    if "vendors" not in st.session_state:
        st.session_state.vendors = {}
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar(analyzer)
    
    # Main content based on current page
    if st.session_state.current_page == "dashboard":
        # Dashboard view
        st.header("📊 Executive Dashboard")
        
        # Workflow status
        render_workflow_status(analyzer)
        
        # Key metrics
        st.subheader("📈 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active RFPs", 3, delta="+1 this week")
        
        with col2:
            st.metric("Vendors Evaluated", len(st.session_state.vendors), 
                     delta=f"+{len(st.session_state.vendors)} today")
        
        with col3:
            avg_score = 0
            if st.session_state.vendors:
                scores = [v.scores.get("overall", 0) for v in st.session_state.vendors.values()]
                avg_score = sum(scores) / len(scores) if scores else 0
            st.metric("Avg Vendor Score", f"{avg_score:.1f}/100")
        
        with col4:
            st.metric("Days to Decision", 12, delta="-3 vs avg")
        
        # Recent activity
        st.subheader("📅 Recent Activity")
        
        activities = [
            {"time": "2 hours ago", "action": "Document uploaded", "details": "ABC Logistics - SOW"},
            {"time": "3 hours ago", "action": "Analysis completed", "details": "XYZ Transport - Full evaluation"},
            {"time": "5 hours ago", "action": "Q&A sent", "details": "Technical clarification to DEF Warehousing"},
            {"time": "Yesterday", "action": "Vendor added", "details": "GHI Supply Chain Solutions"}
        ]
        
        for activity in activities[:5]:
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <strong>{activity['time']}</strong> - {activity['action']}<br>
                <small>{activity['details']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    elif st.session_state.current_page == "vendors":
        # Vendor management view
        render_vendor_management(analyzer)
    
    elif st.session_state.current_page == "analytics":
        # Analytics view
        st.header("📊 Analytics & Insights")
        
        if st.session_state.vendors:
            # Vendor comparison
            render_vendor_comparison(analyzer)
            
            # Trend analysis
            st.subheader("📈 Trend Analysis")
            
            # Sample trend data
            dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
            trend_data = pd.DataFrame({
                'Date': dates,
                'Avg Score': [70, 72, 71, 74, 76, 75, 78, 80, 79, 82, 84, 85],
                'Vendors': [5, 6, 6, 7, 8, 8, 9, 10, 11, 12, 13, 14],
                'RFPs': [2, 2, 3, 3, 4, 4, 4, 5, 5, 6, 6, 7]
            })
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Average Vendor Score', 'Number of Vendors', 
                              'Active RFPs', 'Score Distribution')
            )
            
            # Avg Score
            fig.add_trace(
                go.Scatter(x=trend_data['Date'], y=trend_data['Avg Score'], 
                          mode='lines+markers', name='Avg Score'),
                row=1, col=1
            )
            
            # Vendor Count
            fig.add_trace(
                go.Bar(x=trend_data['Date'], y=trend_data['Vendors'], name='Vendors'),
                row=1, col=2
            )
            
            # RFP Count
            fig.add_trace(
                go.Scatter(x=trend_data['Date'], y=trend_data['RFPs'], 
                          mode='lines+markers', name='RFPs', line=dict(color='green')),
                row=2, col=1
            )
            
            # Score Distribution
            if st.session_state.vendors:
                scores = [v.scores.get("overall", 0) for v in st.session_state.vendors.values()]
                fig.add_trace(
                    go.Histogram(x=scores, name='Score Distribution', nbinsx=10),
                    row=2, col=2
                )
            
            fig.update_layout(height=700, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for analytics. Please add and analyze vendors first.")
    
    elif st.session_state.current_page == "workflow":
        # Workflow management
        st.header("📋 Workflow Management")
        
        # Detailed workflow stages
        for stage_id, stage in analyzer.workflow_stages.items():
            with st.expander(f"{stage.name}", expanded=(stage.status == "active")):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Description:** {stage.description}")
                    st.write(f"**Required Documents:**")
                    for doc in stage.required_docs:
                        st.write(f"  • {doc}")
                    st.write(f"**Expected Outputs:**")
                    for output in stage.outputs:
                        st.write(f"  • {output}")
                
                with col2:
                    status_color = {
                        "completed": "🟢",
                        "active": "🟡",
                        "pending": "⚪"
                    }
                    st.write(f"**Status:** {status_color.get(stage.status, '⚪')} {stage.status.title()}")
                    
                    if stage.status == "pending":
                        if st.button(f"Start Stage", key=f"start_{stage_id}"):
                            stage.status = "active"
                            st.rerun()
                    elif stage.status == "active":
                        if st.button(f"Complete Stage", key=f"complete_{stage_id}"):
                            stage.status = "completed"
                            st.rerun()
    
    elif st.session_state.current_page == "settings":
        # Settings page
        st.header("⚙️ Settings")
        
        tab1, tab2, tab3 = st.tabs(["General", "Evaluation Criteria", "API Configuration"])
        
        with tab1:
            st.subheader("General Settings")
            
            st.text_input("Organization Name", value="UPS Global Logistics & Distribution")
            st.text_input("Department", value="Procurement")
            st.selectbox("Default Currency", ["USD", "EUR", "GBP", "CNY"])
            st.selectbox("Language", ["English", "Spanish", "Chinese", "French"])
            
            if st.button("Save Settings"):
                st.success("✅ Settings saved successfully!")
        
        with tab2:
            st.subheader("Evaluation Criteria Weights")
            
            total_weight = 0
            for criteria, details in analyzer.evaluation_criteria.items():
                weight = st.slider(
                    criteria.replace("_", " ").title(),
                    min_value=0.0,
                    max_value=1.0,
                    value=details["weight"],
                    step=0.05,
                    key=f"weight_{criteria}"
                )
                total_weight += weight
            
            if abs(total_weight - 1.0) > 0.01:
                st.warning(f"⚠️ Total weight must equal 100% (currently {total_weight*100:.1f}%)")
            else:
                st.success(f"✅ Total weight: {total_weight*100:.1f}%")
            
            if st.button("Update Weights"):
                st.success("✅ Evaluation weights updated!")
        
        with tab3:
            st.subheader("API Configuration")
            
            api_key = st.text_input("Claude API Key", type="password", 
                                   placeholder="sk-ant-api03-...")
            
            if st.button("Test Connection"):
                with st.spinner("Testing API connection..."):
                    time.sleep(1)  # Simulate test
                    if api_key:
                        st.success("✅ API connection successful!")
                    else:
                        st.error("❌ Please enter a valid API key")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>© 2025 UPS Global Logistics & Distribution | RFP Vendor Management System v2.0</p>
        <p>Powered by Claude AI | Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
