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
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="RFP Analysis & Scoring Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .score-excellent {
        color: #16a34a;
        font-weight: bold;
    }
    
    .score-good {
        color: #2563eb;
        font-weight: bold;
    }
    
    .score-fair {
        color: #ca8a04;
        font-weight: bold;
    }
    
    .score-poor {
        color: #dc2626;
        font-weight: bold;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9ff;
    }
    
    .risk-high {
        background-color: #fee2e2;
        color: #dc2626;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
    }
    
    .risk-medium {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
    }
    
    .risk-low {
        background-color: #dcfce7;
        color: #166534;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

class RFPAnalyzer:
    def __init__(self):
        self.claude_client = None
        self.initialize_claude()
        
    def initialize_claude(self):
        """Initialize Claude API client"""
        try:
            api_key = st.secrets.get("CLAUDE_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")
            if api_key:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
            else:
                st.error("Claude API key not found in secrets. Please add CLAUDE_API_KEY to your Streamlit secrets.")
        except Exception as e:
            st.error(f"Error initializing Claude API: {str(e)}")
    
    def extract_text_from_file(self, uploaded_file):
        """Extract text from uploaded file based on file type"""
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                return self.extract_pdf_text(uploaded_file)
            elif file_extension in ['doc', 'docx']:
                return self.extract_docx_text(uploaded_file)
            elif file_extension in ['ppt', 'pptx']:
                return self.extract_pptx_text(uploaded_file)
            else:
                st.error("Unsupported file type. Please upload PDF, Word, or PowerPoint files.")
                return None
                
        except Exception as e:
            st.error(f"Error extracting text from file: {str(e)}")
            return None
    
    def extract_pdf_text(self, pdf_file):
        """Extract text from PDF file"""
        text = ""
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def extract_docx_text(self, docx_file):
        """Extract text from Word document"""
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def extract_pptx_text(self, pptx_file):
        """Extract text from PowerPoint presentation"""
        prs = Presentation(pptx_file)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    
    def get_rfp_knowledge_base(self):
        """Return knowledge base about RFP structure and evaluation criteria"""
        return """
        RFP (Request for Proposal) Analysis Knowledge Base:
        
        1. DOCUMENT STRUCTURE ANALYSIS:
        - Executive Summary: High-level overview of requirements
        - Scope of Work: Detailed project requirements and deliverables
        - Technical Requirements: Functional and non-functional specifications
        - Timeline: Project schedule and milestones
        - Budget/Pricing: Cost structure and payment terms
        - Vendor Qualifications: Required experience and capabilities
        - Evaluation Criteria: How proposals will be scored
        
        2. KEY EVALUATION DIMENSIONS:
        - Technical Approach (25%): Solution design, architecture, methodology
        - Team Experience (20%): Relevant experience, team qualifications, past performance
        - Pricing Competitiveness (15%): Cost effectiveness, value proposition
        - Risk Management (15%): Risk identification, mitigation strategies
        - Implementation Plan (15%): Project plan, timeline, deliverables
        - Compliance & Security (10%): Meeting requirements, security measures
        
        3. SCORING CRITERIA:
        - 90-100: Excellent - Exceeds requirements significantly
        - 80-89: Good - Meets requirements well with some enhancements
        - 70-79: Fair - Meets basic requirements
        - 60-69: Poor - Partially meets requirements
        - Below 60: Inadequate - Does not meet requirements
        
        4. RED FLAGS TO IDENTIFY:
        - Unrealistic timelines or budgets
        - Lack of relevant experience
        - Vague technical solutions
        - Poor risk management
        - Non-compliance with requirements
        - Weak project management approach
        
        5. TECHNICAL ANALYSIS AREAS:
        - Architecture and design quality
        - Technology stack appropriateness
        - Scalability and performance considerations
        - Security measures
        - Integration capabilities
        - Maintenance and support approach
        
        6. BUSINESS ANALYSIS AREAS:
        - ROI and business value
        - Cost-benefit analysis
        - Implementation timeline feasibility
        - Resource requirements
        - Change management approach
        - Success metrics and KPIs
        """
    
    def analyze_rfp_with_claude(self, document_text):
        """Analyze RFP document using Claude API"""
        if not self.claude_client:
            st.error("Claude API not initialized. Please check your API key.")
            return None
            
        knowledge_base = self.get_rfp_knowledge_base()
        
        prompt = f"""
        You are an expert RFP (Request for Proposal) analyst with extensive experience in evaluating technology proposals. 
        
        Please analyze the following RFP document and provide a comprehensive assessment:

        KNOWLEDGE BASE FOR REFERENCE:
        {knowledge_base}
        
        RFP DOCUMENT TO ANALYZE:
        {document_text}
        
        Please provide a detailed analysis in the following JSON format:
        {{
            "document_summary": {{
                "title": "Brief title of the RFP",
                "type": "Type of project (e.g., Software Development, System Integration, etc.)",
                "organization": "Client organization name",
                "scope": "High-level scope description",
                "estimated_value": "Estimated project value if mentioned",
                "timeline": "Project timeline if specified"
            }},
            "key_requirements": [
                "Requirement 1",
                "Requirement 2",
                "Requirement 3"
            ],
            "technical_analysis": {{
                "technology_stack": "Proposed/required technology stack",
                "architecture": "System architecture approach",
                "complexity_level": "High/Medium/Low",
                "integration_requirements": "Integration needs",
                "scalability_requirements": "Scalability needs",
                "security_requirements": "Security considerations"
            }},
            "business_analysis": {{
                "business_objectives": "Primary business goals",
                "success_metrics": "KPIs and success measures",
                "roi_potential": "Return on investment potential",
                "stakeholders": "Key stakeholders involved",
                "business_impact": "Expected business impact"
            }},
            "pricing_analysis": {{
                "pricing_model": "Fixed price/Time & materials/etc.",
                "cost_breakdown": "Cost structure if available",
                "budget_range": "Budget range if specified",
                "payment_terms": "Payment terms if mentioned",
                "cost_drivers": "Main cost drivers"
            }},
            "risk_assessment": {{
                "high_risks": [
                    "High risk item 1",
                    "High risk item 2"
                ],
                "medium_risks": [
                    "Medium risk item 1",
                    "Medium risk item 2"
                ],
                "low_risks": [
                    "Low risk item 1"
                ],
                "mitigation_strategies": [
                    "Strategy 1",
                    "Strategy 2"
                ]
            }},
            "scoring": {{
                "technical_approach": 85,
                "team_experience": 78,
                "pricing_competitiveness": 82,
                "risk_management": 75,
                "implementation_plan": 88,
                "compliance_security": 90,
                "overall_score": 83
            }},
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2",
                "Recommendation 3"
            ],
            "next_steps": [
                "Next step 1",
                "Next step 2"
            ]
        }}
        
        Ensure all scores are between 0-100 and provide realistic, detailed analysis based on the actual content.
        """
        
        try:
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from response
            response_text = response.content[0].text
            # Find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            else:
                st.error("Could not parse analysis results. Please try again.")
                return None
                
        except Exception as e:
            st.error(f"Error analyzing document with Claude: {str(e)}")
            return None
    
    def ask_question_about_rfp(self, question, document_text, analysis_results):
        """Ask a specific question about the RFP document"""
        if not self.claude_client:
            return "Claude API not available. Please check your API key."
        
        context = f"""
        RFP Document Analysis Context:
        {json.dumps(analysis_results, indent=2)}
        
        Original Document Text (first 3000 chars):
        {document_text[:3000]}...
        """
        
        prompt = f"""
        You are an expert RFP analyst assistant. Based on the RFP document analysis and content provided, 
        please answer the following question in a clear, professional manner:
        
        Question: {question}
        
        Context: {context}
        
        Provide a detailed, helpful response based on the actual document content and analysis.
        If the question cannot be answered from the available information, please indicate what 
        additional information would be needed.
        """
        
        try:
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error getting response: {str(e)}"

def create_scoring_chart(scores):
    """Create a radar chart for scoring visualization"""
    categories = ['Technical\nApproach', 'Team\nExperience', 'Pricing\nCompetitiveness', 
                 'Risk\nManagement', 'Implementation\nPlan', 'Compliance &\nSecurity']
    
    values = [
        scores.get('technical_approach', 0),
        scores.get('team_experience', 0),
        scores.get('pricing_competitiveness', 0),
        scores.get('risk_management', 0),
        scores.get('implementation_plan', 0),
        scores.get('compliance_security', 0)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='RFP Scores',
        line_color='rgb(102, 126, 234)',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="RFP Analysis Scoring Breakdown",
        title_x=0.5
    )
    
    return fig

def create_cost_breakdown_chart(cost_data):
    """Create a pie chart for cost breakdown if available"""
    if not cost_data or 'cost_breakdown' not in cost_data:
        return None
    
    # Sample cost breakdown - in real implementation, parse from document
    labels = ['Development', 'Testing', 'Analysis', 'Support', 'Infrastructure']
    values = [40, 25, 15, 15, 5]
    
    fig = px.pie(values=values, names=labels, title="Cost Breakdown Analysis")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def get_score_color_class(score):
    """Return CSS class based on score"""
    if score >= 90:
        return "score-excellent"
    elif score >= 80:
        return "score-good"
    elif score >= 70:
        return "score-fair"
    else:
        return "score-poor"

def get_score_badge(score):
    """Return score badge text"""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Good"
    elif score >= 70:
        return "Fair"
    else:
        return "Poor"

def main():
    # Initialize the analyzer
    analyzer = RFPAnalyzer()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 RFP Analysis & Scoring Tool</h1>
        <p>Upload your RFP documents for intelligent analysis, scoring, and insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'document_text' not in st.session_state:
        st.session_state.document_text = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📄 Upload RFP Document")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'doc', 'pptx', 'ppt'],
            help="Upload PDF, Word, or PowerPoint files (Max 50MB)"
        )
        
        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")
            
            if st.button("🔍 Analyze Document", type="primary"):
                with st.spinner("Extracting text from document..."):
                    document_text = analyzer.extract_text_from_file(uploaded_file)
                
                if document_text:
                    st.session_state.document_text = document_text
                    
                    with st.spinner("Analyzing RFP with AI... This may take a moment."):
                        analysis_results = analyzer.analyze_rfp_with_claude(document_text)
                        st.session_state.analysis_results = analysis_results
                    
                    if analysis_results:
                        st.success("Analysis complete!")
                        st.rerun()
                    else:
                        st.error("Analysis failed. Please try again.")
        
        # Analysis status
        if st.session_state.analysis_results:
            st.success("✅ Document analyzed successfully")
            overall_score = st.session_state.analysis_results.get('scoring', {}).get('overall_score', 0)
            st.metric("Overall Score", f"{overall_score}/100")
        
        # Quick stats
        if uploaded_file:
            st.subheader("📊 File Info")
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
            st.write(f"**Type:** {uploaded_file.type}")
    
    # Main content area
    if st.session_state.analysis_results is None:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="upload-box">
                <h3>🚀 Get Started</h3>
                <p>Upload your RFP document using the sidebar to begin analysis</p>
                <p><strong>Supported formats:</strong> PDF, Word (.docx), PowerPoint (.pptx)</p>
                <p><strong>What you'll get:</strong></p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Comprehensive RFP analysis</li>
                    <li>Detailed scoring across 6 dimensions</li>
                    <li>Risk assessment and recommendations</li>
                    <li>Interactive Q&A about the document</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Display analysis results
        results = st.session_state.analysis_results
        
        # Overview metrics
        st.subheader("📊 Analysis Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        scores = results.get('scoring', {})
        overall_score = scores.get('overall_score', 0)
        
        with col1:
            score_class = get_score_color_class(overall_score)
            st.markdown(f"""
            <div class="metric-card">
                <h3>Overall Score</h3>
                <h1 class="{score_class}">{overall_score}/100</h1>
                <p>{get_score_badge(overall_score)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            doc_summary = results.get('document_summary', {})
            st.markdown(f"""
            <div class="metric-card">
                <h3>Project Type</h3>
                <p><strong>{doc_summary.get('type', 'N/A')}</strong></p>
                <p>{doc_summary.get('organization', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            technical_score = scores.get('technical_approach', 0)
            tech_class = get_score_color_class(technical_score)
            st.markdown(f"""
            <div class="metric-card">
                <h3>Technical Score</h3>
                <h2 class="{tech_class}">{technical_score}/100</h2>
                <p>Technical Approach</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            risk_score = scores.get('risk_management', 0)
            risk_class = get_score_color_class(risk_score)
            st.markdown(f"""
            <div class="metric-card">
                <h3>Risk Score</h3>
                <h2 class="{risk_class}">{risk_score}/100</h2>
                <p>Risk Management</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Tabs for detailed analysis
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Summary", "⚙️ Technical", "💰 Pricing", "⚠️ Risks", "💬 Q&A"])
        
        with tab1:
            st.subheader("Document Summary")
            doc_summary = results.get('document_summary', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Project Title:**", doc_summary.get('title', 'N/A'))
                st.write("**Organization:**", doc_summary.get('organization', 'N/A'))
                st.write("**Timeline:**", doc_summary.get('timeline', 'N/A'))
                st.write("**Estimated Value:**", doc_summary.get('estimated_value', 'N/A'))
            
            with col2:
                st.write("**Scope:**")
                st.write(doc_summary.get('scope', 'N/A'))
            
            st.subheader("Key Requirements")
            requirements = results.get('key_requirements', [])
            for i, req in enumerate(requirements, 1):
                st.write(f"{i}. {req}")
            
            st.subheader("Scoring Breakdown")
            fig = create_scoring_chart(scores)
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed scoring table
            scoring_data = []
            for category, score in scores.items():
                if category != 'overall_score':
                    category_name = category.replace('_', ' ').title()
                    scoring_data.append({
                        'Category': category_name,
                        'Score': score,
                        'Rating': get_score_badge(score)
                    })
            
            if scoring_data:
                df = pd.DataFrame(scoring_data)
                st.dataframe(df, use_container_width=True)
        
        with tab2:
            st.subheader("Technical Analysis")
            
            tech_analysis = results.get('technical_analysis', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Technology Stack:**")
                st.write(tech_analysis.get('technology_stack', 'N/A'))
                
                st.write("**Architecture:**")
                st.write(tech_analysis.get('architecture', 'N/A'))
                
                st.write("**Complexity Level:**")
                complexity = tech_analysis.get('complexity_level', 'N/A')
                if complexity.lower() == 'high':
                    st.error(f"🔴 {complexity}")
                elif complexity.lower() == 'medium':
                    st.warning(f"🟡 {complexity}")
                else:
                    st.success(f"🟢 {complexity}")
            
            with col2:
                st.write("**Integration Requirements:**")
                st.write(tech_analysis.get('integration_requirements', 'N/A'))
                
                st.write("**Scalability Requirements:**")
                st.write(tech_analysis.get('scalability_requirements', 'N/A'))
                
                st.write("**Security Requirements:**")
                st.write(tech_analysis.get('security_requirements', 'N/A'))
            
            # Business Analysis
            st.subheader("Business Analysis")
            business_analysis = results.get('business_analysis', {})
            
            st.write("**Business Objectives:**")
            st.write(business_analysis.get('business_objectives', 'N/A'))
            
            st.write("**Success Metrics:**")
            st.write(business_analysis.get('success_metrics', 'N/A'))
            
            st.write("**Expected Business Impact:**")
            st.write(business_analysis.get('business_impact', 'N/A'))
        
        with tab3:
            st.subheader("Pricing Analysis")
            
            pricing_analysis = results.get('pricing_analysis', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Pricing Model:**")
                st.write(pricing_analysis.get('pricing_model', 'N/A'))
                
                st.write("**Budget Range:**")
                st.write(pricing_analysis.get('budget_range', 'N/A'))
                
                st.write("**Payment Terms:**")
                st.write(pricing_analysis.get('payment_terms', 'N/A'))
            
            with col2:
                st.write("**Cost Breakdown:**")
                st.write(pricing_analysis.get('cost_breakdown', 'N/A'))
                
                st.write("**Main Cost Drivers:**")
                cost_drivers = pricing_analysis.get('cost_drivers', 'N/A')
                if isinstance(cost_drivers, list):
                    for driver in cost_drivers:
                        st.write(f"• {driver}")
                else:
                    st.write(cost_drivers)
            
            # Cost breakdown chart
            cost_chart = create_cost_breakdown_chart(pricing_analysis)
            if cost_chart:
                st.plotly_chart(cost_chart, use_container_width=True)
        
        with tab4:
            st.subheader("Risk Assessment")
            
            risk_assessment = results.get('risk_assessment', {})
            
            # High risks
            high_risks = risk_assessment.get('high_risks', [])
            if high_risks:
                st.write("**🔴 High Risks:**")
                for risk in high_risks:
                    st.markdown(f'<div class="risk-high">⚠️ {risk}</div>', unsafe_allow_html=True)
            
            # Medium risks
            medium_risks = risk_assessment.get('medium_risks', [])
            if medium_risks:
                st.write("**🟡 Medium Risks:**")
                for risk in medium_risks:
                    st.markdown(f'<div class="risk-medium">⚡ {risk}</div>', unsafe_allow_html=True)
            
            # Low risks
            low_risks = risk_assessment.get('low_risks', [])
            if low_risks:
                st.write("**🟢 Low Risks:**")
                for risk in low_risks:
                    st.markdown(f'<div class="risk-low">ℹ️ {risk}</div>', unsafe_allow_html=True)
            
            # Mitigation strategies
            st.subheader("🛡️ Mitigation Strategies")
            mitigation_strategies = risk_assessment.get('mitigation_strategies', [])
            for i, strategy in enumerate(mitigation_strategies, 1):
                st.write(f"{i}. {strategy}")
            
            # Recommendations
            st.subheader("💡 Recommendations")
            recommendations = results.get('recommendations', [])
            for i, recommendation in enumerate(recommendations, 1):
                st.write(f"{i}. {recommendation}")
        
        with tab5:
            st.subheader("💬 Ask Questions About This RFP")
            
            # Display chat history
            for i, (question, answer) in enumerate(st.session_state.chat_history):
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {question}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>AI Assistant:</strong> {answer}
                </div>
                """, unsafe_allow_html=True)
            
            # Question input
            question = st.text_input(
                "Ask a question about the RFP:",
                placeholder="e.g., What are the main technical risks? How competitive is the pricing?"
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Send Question", type="primary"):
                    if question.strip():
                        with st.spinner("Getting answer..."):
                            answer = analyzer.ask_question_about_rfp(
                                question, 
                                st.session_state.document_text, 
                                st.session_state.analysis_results
                            )
                            st.session_state.chat_history.append((question, answer))
                            st.rerun()
            
            # Quick question buttons
            st.subheader("Quick Questions")
            quick_questions = [
                "What are the main technical risks?",
                "How competitive is the pricing?",
                "What is the implementation timeline?",
                "What are the key requirements?",
                "How experienced is the proposed team?",
                "What are the next steps?"
            ]
            
            cols = st.columns(2)
            for i, q in enumerate(quick_questions):
                with cols[i % 2]:
                    if st.button(q, key=f"quick_{i}"):
                        with st.spinner("Getting answer..."):
                            answer = analyzer.ask_question_about_rfp(
                                q, 
                                st.session_state.document_text, 
                                st.session_state.analysis_results
                            )
                            st.session_state.chat_history.append((q, answer))
                            st.rerun()

if __name__ == "__main__":
    main()
