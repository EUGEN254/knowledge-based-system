# ui/app.py

import streamlit as st
import json
import os
import sys
from datetime import datetime
import time

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from reasoning.engine import reason
    
    # Create a simple detailed analysis function
    def get_detailed_analysis(facts, question, system_metrics=None):
        answers = reason(facts, question, system_metrics)
        categories = {}
        confidences = {}
        
        for answer in answers:
            cat = answer.get("category", "General")
            conf = answer.get("confidence", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            confidences[conf] = confidences.get(conf, 0) + 1
            
        return {
            "original_question": question,
            "total_answers": len(answers),
            "answers_by_type": {"kb_match": len(answers)},
            "answers_by_confidence": confidences,
            "answers_by_category": categories,
            "processing_metrics": {
                "rules_applied": len(answers),
                "symptoms_detected": 0,
                "categories_involved": list(categories.keys())
            },
            "detailed_answers": answers
        }
        
except ImportError as e:
    st.error(f"Import Error: {e}")
    # Enhanced fallback implementation with advanced options support
    def reason(facts, question, system_metrics=None):
        answers = []
        q_lower = question.lower()
        
        # Get advanced options from system_metrics
        search_depth = system_metrics.get('search_depth', 'Standard') if system_metrics else 'Standard'
        debug_mode = system_metrics.get('debug_mode', False) if system_metrics else False
        user_category = system_metrics.get('user_selected_category', None) if system_metrics else None
        
        # Apply search depth settings
        max_results = {
            'Basic': 3,
            'Standard': 6,
            'Comprehensive': 10
        }.get(search_depth, 6)
        
        # Emergency detection (critical for safety) - always highest priority
        emergency_keywords = ["fire", "smoke", "spark", "burning", "electrical", "shock", "water", "spilled"]
        if any(word in q_lower for word in emergency_keywords):
            answers.append({
                "type": "emergency",
                "content": "🚨 CRITICAL SAFETY ISSUE - Unplug immediately and contact professional help! Do not attempt to use the device.",
                "category": "Emergency",
                "confidence": "high",
                "priority": "CRITICAL",
                "match_score": 0.95,
                "rule_advice": [
                    "UNPLUG FROM POWER IMMEDIATELY",
                    "Do not touch if smoking or sparking",
                    "Contact professional technician",
                    "Safety first - risk of electrical hazard"
                ]
            })
            return answers
        
        # Enhanced keyword matching with categories and scoring
        for fact in facts:
            category_name = fact.get("category", "General")
            
            # Filter by user-selected category if specified
            if user_category and user_category.lower() not in category_name.lower():
                continue
                
            if "questions" in fact:
                for qa in fact["questions"]:
                    fact_q_lower = qa["question"].lower()
                    fact_answer = qa["answer"]
                    
                    # Calculate match score based on multiple factors
                    match_score = 0
                    
                    # Exact phrase match
                    if q_lower in fact_q_lower:
                        match_score += 0.7
                    
                    # Keyword overlap
                    question_words = set(q_lower.split())
                    fact_words = set(fact_q_lower.split())
                    common_words = question_words & fact_words
                    
                    if common_words:
                        match_score += len(common_words) * 0.1
                    
                    # Category bonus if user selected this category
                    if user_category and user_category.lower() in category_name.lower():
                        match_score += 0.2
                    
                    # Only include matches above threshold
                    if match_score >= 0.2:
                        confidence = "high" if match_score > 0.5 else "medium" if match_score > 0.3 else "low"
                        priority = "HIGH" if match_score > 0.6 else "MEDIUM" if match_score > 0.4 else "LOW"
                        
                        answers.append({
                            "type": "kb_match",
                            "content": fact_answer,
                            "category": category_name,
                            "confidence": confidence,
                            "priority": priority,
                            "match_score": min(0.95, match_score),  # Cap at 0.95
                            "source_question": qa["question"],
                            "search_depth": search_depth
                        })
        
        # Sort by match score and limit results
        answers.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        # Debug information if enabled
        if debug_mode:
            answers.append({
                "type": "debug_info",
                "content": f"🔍 DEBUG: Search depth '{search_depth}', Found {len([a for a in answers if a['type'] != 'debug_info'])} matches, User category: {user_category}",
                "category": "Debug",
                "confidence": "debug",
                "priority": "LOW",
                "match_score": 1.0
            })
        
        return answers[:max_results]

    def get_detailed_analysis(facts, question, system_metrics=None):
        results = reason(facts, question, system_metrics)
        
        # Calculate statistics
        categories = {}
        confidences = {}
        match_scores = []
        
        for answer in results:
            if answer.get("type") == "debug_info":
                continue
            cat = answer.get("category", "General")
            conf = answer.get("confidence", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            confidences[conf] = confidences.get(conf, 0) + 1
            match_scores.append(answer.get("match_score", 0))
        
        avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0
        
        return {
            "original_question": question,
            "total_answers": len([a for a in results if a.get("type") != "debug_info"]),
            "answers_by_type": {"kb_match": len(results)},
            "answers_by_confidence": confidences,
            "answers_by_category": categories,
            "average_match_score": avg_match_score,
            "processing_metrics": {
                "rules_applied": len(results),
                "categories_involved": list(categories.keys()),
                "search_depth": system_metrics.get('search_depth', 'Standard') if system_metrics else 'Standard'
            },
            "detailed_answers": results
        }

# ---- Load Knowledge Base ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACTS_FILE = os.path.join(BASE_DIR, "..", "knowledge", "facts.json")

try:
    with open(FACTS_FILE, "r") as f:
        facts = json.load(f)
except FileNotFoundError:
    facts = []
    st.error("⚠️ facts.json not found! Please create it in the knowledge folder.")
except json.JSONDecodeError:
    facts = []
    st.error("⚠️ facts.json is empty or has invalid JSON!")

# ---- Initialize Session State ----
if "recent_questions" not in st.session_state:
    st.session_state.recent_questions = []
if "system_metrics" not in st.session_state:
    st.session_state.system_metrics = {}  # Simplified - no fake metrics
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_input_category" not in st.session_state:
    st.session_state.selected_input_category = None

# ---- Custom CSS for Professional Styling ----
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .quick-question-btn {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin: 4px 0;
        transition: all 0.3s ease;
        background: white;
    }
    .quick-question-btn:hover {
        background: #f8f9fa;
        border-color: #1f77b4;
        transform: translateY(-2px);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .answer-card {
        border-left: 4px solid #1f77b4;
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .priority-critical { background-color: #ff4444; color: white; }
    .priority-high { background-color: #ff6b35; color: white; }
    .priority-medium { background-color: #ffa726; color: white; }
    .priority-low { background-color: #66bb6a; color: white; }
    .priority-normal { background-color: #42a5f5; color: white; }
    .category-btn {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 12px 8px;
        margin: 5px 0;
        transition: all 0.3s ease;
        background: white;
        text-align: center;
        height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .category-btn:hover {
        border-color: #1f77b4;
        background: #f0f8ff;
        transform: translateY(-2px);
    }
    .category-btn.selected {
        border-color: #1f77b4;
        background: #1f77b4;
        color: white;
    }
    .match-score-bar {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        height: 8px;
        border-radius: 4px;
        margin: 5px 0;
    }
    .debug-info {
        background: #f8f9fa;
        border-left: 4px solid #6c757d;
        padding: 10px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# ---- Helper Functions ----
def get_categories_count():
    """Get count of unique categories"""
    categories_set = set()
    for fact in facts:
        categories_set.add(fact.get("category", "Uncategorized"))
    return len(categories_set)

def get_total_questions():
    """Get total number of questions across all categories"""
    return sum(len(category.get("questions", [])) for category in facts)

# ---- Sidebar ----
with st.sidebar:
    st.markdown('<div class="sidebar-header">💻 IT Knowledge System</div>', unsafe_allow_html=True) 
    
    st.markdown("---")
    
    # Recent Questions
    st.markdown("### 🔄 Recent Questions")
    if st.session_state.recent_questions:
        for i, q in enumerate(reversed(st.session_state.recent_questions[-5:])):
            if st.button(f"💬 {q[:30]}...", key=f"recent_{i}", use_container_width=True):
                st.session_state.quick_question = q
                st.rerun()
    else:
        st.caption("No recent questions yet")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Clear History", use_container_width=True):
        st.session_state.recent_questions = []
        st.session_state.chat_history = []
        st.session_state.selected_input_category = None
        st.rerun()
    
    if st.button("📊 System Info", use_container_width=True):
        st.session_state.show_system_info = True

# ---- Main Area ----
st.markdown('<div class="main-header">💻 IT Knowledge-Based System</div>', unsafe_allow_html=True)
st.markdown("Ask any IT-related question about computers, hardware, networking, or software.")

# ---- Question Input Section ----
st.markdown("### 💬 Ask Your Question")
st.markdown("*Type your specific IT question below or use the quick questions above*")

default_question = ""
if "quick_question" in st.session_state:
    default_question = st.session_state.quick_question
    del st.session_state.quick_question

question = st.text_area(
    "**Describe your IT issue or question:**",
    value=default_question,
    placeholder="Examples:\n• My computer is overheating and shutting down randomly\n• How to fix slow internet connection?\n• What's the best way to clean my laptop from viruses?\n• Computer won't boot after Windows update\n• I smell burning from my PC",
    height=100,
    key="question_input"
)

# ---- Optional Category Selection ----
st.markdown("#### 🏷️ Optional: Select a Category")
st.markdown("*Choose a category to help focus your question (optional)*")

# Define common categories with icons and descriptions
common_categories = [
    {"icon": "🔧", "name": "Hardware", "description": "CPU, RAM, Motherboard, Cooling, Peripherals"},
    {"icon": "💻", "name": "Software", "description": "Installation, Updates, Compatibility, Errors"},
    {"icon": "🌐", "name": "Networking", "description": "WiFi, Internet, Router, Connection Issues"},
    {"icon": "⚡", "name": "Performance", "description": "Slow Computer, Lag, Optimization, Speed"},
    {"icon": "🛡️", "name": "Security", "description": "Viruses, Malware, Privacy, Antivirus"},
    {"icon": "💾", "name": "Storage", "description": "Hard Drives, SSD, Memory, Data Recovery"},
    {"icon": "🎮", "name": "Gaming", "description": "Graphics, FPS, Game Crashes, Performance"},
    {"icon": "🔋", "name": "Power", "description": "Battery, Charging, Power Supply, Shutdowns"},
    {"icon": "🖨️", "name": "Printing", "description": "Printers, Scanner, Driver Issues"},
    {"icon": "🔊", "name": "Audio", "description": "Sound, Speakers, Microphone, Drivers"},
    {"icon": "🚨", "name": "Emergency", "description": "Smoke, Fire, Water Damage, Electrical Hazards"},
    {"icon": "🔄", "name": "Boot Issues", "description": "Startup, BIOS, Windows Won't Start"}
]

# Display categories in a responsive grid
cat_cols = st.columns(4)
selected_category = None

for i, category in enumerate(common_categories):
    with cat_cols[i % 4]:
        is_selected = st.session_state.selected_input_category == category['name']
        button_type = "primary" if is_selected else "secondary"
        
        if st.button(
            f"{category['icon']}\n**{category['name']}**",
            key=f"input_cat_{category['name']}",
            use_container_width=True,
            type=button_type,
            help=category['description']
        ):
            st.session_state.selected_input_category = category['name']
            st.rerun()

# Show currently selected category
if st.session_state.selected_input_category:
    st.success(f"🗂️ **Selected Category:** {st.session_state.selected_input_category}")
    col_clear1, col_clear2, col_clear3 = st.columns([1, 2, 1])
    with col_clear2:
        if st.button("❌ Clear Category Selection", use_container_width=True):
            st.session_state.selected_input_category = None
            st.rerun()

# Advanced options in a clean expander - CLEANED UP VERSION
with st.expander("⚙️ **Advanced Options**", expanded=False):
    col_adv1, col_adv2, col_adv3 = st.columns(3)
    
    with col_adv1:
        show_detailed_analysis = st.checkbox("Detailed Analysis", value=False, 
                                           help="Show comprehensive breakdown of answers")
        show_match_scores = st.checkbox("Match Scores", value=False, 
                                      help="Display relevance scores for answers")
    
    with col_adv2:
        show_raw_data = st.checkbox("Raw Data", value=False, 
                                  help="Show JSON response data")
        enable_debug = st.checkbox("Debug Mode", value=False, 
                                 help="Enable debugging information")
    
    with col_adv3:
        search_depth = st.select_slider(
            "Search Depth",
            options=["Basic", "Standard", "Comprehensive"],
            value="Standard",
            help="How thoroughly to search the knowledge base"
        )

# Action button with improved styling
col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
with col_btn2:
    if st.button(
        "🎯 **Get Expert Answer**", 
        type="primary", 
        use_container_width=True,
        disabled=not question.strip()
    ):
        if not question.strip():
            st.warning("⚠️ Please enter a question first.")
        else:
            # Add to recent questions
            if question not in st.session_state.recent_questions:
                st.session_state.recent_questions.append(question)
            
            # Prepare system metrics with advanced options
            system_metrics = {}
            
            # Add search configuration
            system_metrics['search_depth'] = search_depth
            system_metrics['show_match_scores'] = show_match_scores
            system_metrics['debug_mode'] = enable_debug
            
            if st.session_state.selected_input_category:
                system_metrics['user_selected_category'] = st.session_state.selected_input_category
            
            # Show loading state with better UX
            with st.spinner("🔍 **Analyzing your question and searching knowledge base...**"):
                start_time = time.time()
                # Use reasoning engine with enhanced metrics
                answers = reason(facts, question, system_metrics)
                processing_time = time.time() - start_time
            
            # Add to chat history
            if answers:
                answer_text = answers[0].get("content", "Answer found")[:100] + "..."
            else:
                answer_text = "No specific answer found"
            
            st.session_state.chat_history.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "question": question,
                "answer": answer_text,
                "user_category": st.session_state.selected_input_category,
                "processing_time": f"{processing_time:.2f}s",
                "search_depth": search_depth
            })
            
            # Store answers for display
            st.session_state.last_answers = answers
            st.session_state.last_question = question
            st.session_state.last_processing_time = processing_time
            st.session_state.last_system_metrics = system_metrics.copy()
            st.rerun()

# ---- Display Results ----
if "last_answers" in st.session_state and st.session_state.last_question == question:
    answers = st.session_state.last_answers
    processing_time = st.session_state.last_processing_time
    system_metrics = st.session_state.last_system_metrics
    
    if answers:
        st.markdown("---")
        st.markdown(f'### 💡 **Answers Found** ({len([a for a in answers if a.get("type") != "debug_info"])})')
        
        # Show search configuration
        col_conf1, col_conf2, col_conf3 = st.columns(3)
        with col_conf1:
            st.info(f"🔍 **Search Depth:** {system_metrics.get('search_depth', 'Standard')}")
        with col_conf2:
            if st.session_state.selected_input_category:
                st.info(f"🏷️ **Category:** {st.session_state.selected_input_category}")
       
        
        for i, answer in enumerate(answers, 1):
            answer_type = answer.get("type", "unknown")
            
            # Skip debug info in main display (handled separately)
            if answer_type == "debug_info":
                continue
                
            confidence = answer.get("confidence", "unknown")
            answer_category = answer.get("category", "General")
            content = answer.get("content", "")
            match_score = answer.get("match_score", 0)
            priority = answer.get("priority", "NORMAL")
            
            # Create styled answer cards
            with st.container():
                # Confidence-based border color
                border_color = {
                    "high": "4px solid #28a745",
                    "medium": "4px solid #17a2b8", 
                    "low": "4px solid #ffc107",
                    "perfect": "4px solid #28a745",
                    "debug": "4px solid #6c757d"
                }.get(confidence, "4px solid #6c757d")
                
                # Priority-based background
                priority_bg = {
                    "CRITICAL": "#ff4444",
                    "HIGH": "#ff6b35",
                    "MEDIUM": "#ffa726", 
                    "LOW": "#66bb6a",
                    "NORMAL": "#42a5f5"
                }.get(priority, "#f8f9fa")
                
                st.markdown(f"""
                <div style="border-left: {border_color}; background: {priority_bg}; padding: 20px; border-radius: 8px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 10px 0; color: #333; line-height: 1.4;">{content}</h4>
                            <div style="display: flex; gap: 15px; font-size: 0.9em; color: #666;">
                                <span>📁 <strong>{answer_category}</strong></span>
                                <span>🎯 <strong>{confidence.upper()} confidence</strong></span>
                                <span>⚡ <strong>{priority}</strong> priority</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Display match score if enabled
            if show_match_scores and match_score > 0:
                score_percentage = min(100, int(match_score * 100))
                st.write(f"**Relevance Score:** {score_percentage}%")
                st.progress(match_score, text=f"Match: {score_percentage}%")
            
            # Display rule-based advice if available
            if "rule_advice" in answer and answer["rule_advice"]:
                with st.expander(f"🎯 **Expert Advice & Rules** ({len(answer['rule_advice'])} recommendations)", expanded=False):
                    for advice in answer["rule_advice"]:
                        st.write(f"• {advice}")
            
            # Display troubleshooting steps if available
            if "troubleshooting_steps" in answer and answer["troubleshooting_steps"]:
                with st.expander(f"🔧 **Troubleshooting Steps** ({len(answer['troubleshooting_steps'])} steps)", expanded=False):
                    for j, step in enumerate(answer["troubleshooting_steps"], 1):
                        st.write(f"{j}. {step}")
            
            st.markdown("---")
        
        # Display debug information if available and enabled
        debug_answers = [a for a in answers if a.get("type") == "debug_info"]
        if enable_debug and debug_answers:
            st.markdown("#### 🔍 Debug Information")
            for debug_answer in debug_answers:
                st.markdown(f'<div class="debug-info">{debug_answer.get("content", "")}</div>', unsafe_allow_html=True)
                
            with st.expander("📊 Search Configuration"):
                st.json(system_metrics)
        
        # Detailed Analysis Section
        if show_detailed_analysis:
            st.markdown("---")
            st.subheader("📊 **Detailed Analysis**")
            analysis = get_detailed_analysis(facts, question, system_metrics)
            
            col_ana1, col_ana2, col_ana3 = st.columns(3)
            with col_ana1:
                st.metric("Total Answers", analysis["total_answers"])
                st.metric("Average Match Score", f"{analysis.get('average_match_score', 0)*100:.1f}%")
                with st.expander("Answers by Type"):
                    for answer_type, count in analysis["answers_by_type"].items():
                        st.write(f"• **{answer_type.replace('_', ' ').title()}**: {count}")
            
            with col_ana2:
                st.metric("Search Depth", search_depth)
                with st.expander("Confidence Levels"):
                    for confidence_level, count in analysis["answers_by_confidence"].items():
                        st.write(f"• **{confidence_level.title()}**: {count}")
                
                with st.expander("Categories Found"):
                    if "answers_by_category" in analysis:
                        for category, count in analysis["answers_by_category"].items():
                            st.write(f"• **{category}**: {count}")
            
            with col_ana3:
                if "processing_metrics" in analysis:
                    st.metric("Rules Applied", analysis["processing_metrics"].get("rules_applied", 0))
                    with st.expander("Processing Info"):
                        st.write(f"• **Search Depth**: {analysis['processing_metrics'].get('search_depth', 'Standard')}")
                        st.write(f"• **Categories Involved**: {len(analysis['processing_metrics'].get('categories_involved', []))}")
                        if st.session_state.selected_input_category:
                            st.write(f"• **User Selected Category**: {st.session_state.selected_input_category}")
                else:
                    st.metric("Processing", "Complete")
        
        # Raw Data Section
        if show_raw_data:
            st.markdown("---")
            st.subheader("🔧 **Raw Response Data**")
            with st.expander("View JSON Response"):
                st.json(answers)
                
    else:
        st.markdown("---")
        st.info("""
        ### 🤔 No Specific Answer Found
        
        I couldn't find a direct match in our knowledge base. Try:
        - Rephrasing your question with more specific details
        - Using different keywords related to your issue
        - Checking if your question matches common IT categories
        - Breaking down complex problems into smaller questions
        - Adjusting search depth to 'Comprehensive' in Advanced Options
        """)

# ---- Knowledge Base Statistics ----
st.markdown("---")
st.subheader("📚 **Knowledge Base Overview**")

# Calculate actual counts
total_categories = len(facts)
total_questions = get_total_questions()

# Enhanced metrics with icons
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    st.markdown(f'<div class="metric-card">📊<br>Total Questions<br><h3>{total_questions}</h3></div>', unsafe_allow_html=True)
with col_stat2:
    st.markdown(f'<div class="metric-card">📁<br>Categories<br><h3>{total_categories}</h3></div>', unsafe_allow_html=True)
with col_stat3:
    st.markdown(f'<div class="metric-card">💬<br>Recent Questions<br><h3>{len(st.session_state.recent_questions)}</h3></div>', unsafe_allow_html=True)
with col_stat4:
    st.markdown(f'<div class="metric-card">🔄<br>Session History<br><h3>{len(st.session_state.chat_history)}</h3></div>', unsafe_allow_html=True)

# ---- Footer ----
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p style='font-size: 0.9rem;'>Advanced IT Troubleshooting System</p>
        <p style='font-size: 0.8rem; color: #999;'>Real-time Diagnostics • Professional IT Support • Knowledge-Driven Solutions</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---- System Info Modal ----
if st.session_state.get('show_system_info', False):
    with st.sidebar:
        st.markdown("### 🖥️ System Information")
        st.write(f"**Facts Loaded:** {len(facts)}")
        st.write(f"**Total Questions:** {total_questions}")
        st.write(f"**Categories:** {total_categories}")
        st.write(f"**Session Questions:** {len(st.session_state.recent_questions)}")
        st.write(f"**Chat History:** {len(st.session_state.chat_history)}")
        if st.session_state.selected_input_category:
            st.write(f"**Current Category:** {st.session_state.selected_input_category}")
        st.write(f"**Current Search Depth:** {search_depth}")
        
        if st.button("Close System Info"):
            st.session_state.show_system_info = False
            st.rerun()