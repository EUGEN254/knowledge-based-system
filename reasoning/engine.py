# reasoning_engine.py
import re
from knowledge.rules import (
    execute_all_rules,
    get_priority_level,
    generate_troubleshooting_steps,
    get_preventive_maintenance_advice
)
from typing import List, Dict, Any, Optional

# Comprehensive symptom definitions with patterns and expert advice
SYMPTOM_DEFINITIONS = {
    "random_shutdown": {
        "patterns": [
            "shut down", "shutting down", "turns off", "powers off", 
            "randomly off", "sudden shutdown", "shuts itself off",
            "random restart", "restarts randomly", "rebooting randomly"
        ],
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Random shutdowns are almost always caused by:\n"
                       "1. Overheating → CPU/GPU hits 95–105°C and system protects itself\n"
                       "2. Failing power supply (common on 3+ year old PCs)\n"
                       "3. Bad RAM or motherboard VRMs",
            "category": "Power / Thermal",
            "confidence": "high",
            "priority": "HIGH",
            "rule_advice": [
                "Download HWMonitor or Core Temp → check temps under load",
                "Clean ALL dust from fans and heatsinks (90% of cases fixed here)",
                "Repaste CPU/GPU if system is older than 3 years",
                "Test with a known-good PSU if possible",
                "Run MemTest86 overnight (free)"
            ],
            "troubleshooting_steps": [
                "1. Monitor temperatures immediately",
                "2. Clean dust (most common fix)",
                "3. Check Event Viewer → Kernel-Power Event ID 41",
                "4. Reseat RAM and power cables",
                "5. Test PSU with tester or spare"
            ]
        }
    },
    
    "no_power": {
        "patterns": [
            "won't turn on", "no power", "completely dead", "not powering on", 
            "black screen no power", "no signs of life", "wont turn on" ,"laptop wont turn on"
        ],
        "additional_check": lambda words: "dead" in words,
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "PC completely dead? Follow this exact order:",
            "category": "Power Failure",
            "confidence": "high",
            "priority": "HIGH",
            "rule_advice": [
                "Check power cable & wall socket first",
                "Hold power button 30–60 seconds (drain flea power)",
                "Reseat RAM and CMOS battery",
                "Check front panel connectors",
                "Test with only motherboard + CPU + 1 RAM stick + PSU"
            ],
            "troubleshooting_steps": [
                "1. Verify power cable and outlet work",
                "2. Drain residual power (hold power button 30+ seconds)",
                "3. Check internal power connections",
                "4. Test with minimal hardware configuration",
                "5. Try known-good PSU if available"
            ]
        }
    },
    
    "slow": {
        "patterns": ["slow", "lag", "laggy", "sluggish"],
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "System slow or freezing? 95% of cases:",
            "category": "Performance",
            "confidence": "high",
            "priority": "MEDIUM",
            "rule_advice": [
                "Open Task Manager → End unnecessary processes",
                "Upgrade to SSD if still on HDD",
                "Add more RAM (16GB minimum, 32GB ideal)",
                "Scan with Malwarebytes (free)",
                "Disable startup programs"
            ]
        }
    },
    
    "high_cpu": {
        "patterns": [
            "100%", "high cpu", "cpu usage", "fans spinning fast", "fan spinning fast", "fans loud constantly" ,"fans loud constantly"
        ],
        "expert_advice": {
            "type": "expert_diagnosis", 
            "content": "High CPU usage detected:\n"
                       "• Background processes consuming resources\n"
                       "• Malware or cryptocurrency miners\n"
                       "• Driver conflicts or system file corruption\n"
                       "• Insufficient RAM causing swap thrashing",
            "category": "Performance",
            "confidence": "high",
            "priority": "MEDIUM",
            "rule_advice": [
                "Open Task Manager → Sort by CPU → End high-usage processes",
                "Run full antivirus scan with Malwarebytes",
                "Update all drivers from manufacturer website",
                "Run: sfc /scannow to repair system files",
                "Check for Windows updates"
            ],
            "troubleshooting_steps": [
                "1. Identify process causing high CPU in Task Manager",
                "2. Run antivirus/malware scan",
                "3. Update drivers and Windows",
                "4. Check for overheating issues",
                "5. Consider clean Windows reinstall if persistent"
            ]
        }
    },
    
    "crashing": {
        "patterns": ["crash", "crashing", "freezing", "frozen"],
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "System crashes or freezes typically indicate:\n"
                       "• Driver conflicts (especially GPU drivers)\n" 
                       "• Overheating components\n"
                       "• Failing RAM or storage\n"
                       "• Software conflicts or corrupt system files",
            "category": "Stability",
            "confidence": "high",
            "priority": "HIGH",
            "rule_advice": [
                "Check Event Viewer for error codes",
                "Update ALL drivers (chipset, GPU, audio, network)",
                "Run Windows Memory Diagnostic overnight",
                "Test with different RAM configurations",
                "Run: DISM /Online /Cleanup-Image /RestoreHealth"
            ]
        }
    },
    
    "overheating": {
        "patterns": ["hot", "overheat", "overheating", "burning"],
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "OVERHEATING DETECTED! This can cause permanent damage:\n"
                       "• Dust/clogged cooling system (90% of cases)\n"
                       "• Dried thermal paste (2+ years old)\n"
                       "• Faulty or stopped fans\n"
                       "• Blocked air vents or bad airflow",
            "category": "Thermal Emergency",
            "confidence": "high",
            "priority": "HIGH",
            "rule_advice": [
                "IMMEDIATELY clean dust from all fans/heatsinks",
                "Check temperatures with HWMonitor or Core Temp",
                "Replace thermal paste if 2+ years old",
                "Ensure proper airflow — elevate laptop if needed",
                "Reduce load if temps exceed 85°C"
            ]
        }
    },
    
    "screen_issue": {
        "patterns": [
            "black screen", "no display", "flickering", "glitchy screen"
        ],
        "additional_check": lambda words: any(word in words for word in ["screen", "display"]),
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Display issues can be:\n"
                       "• GPU driver problems (most common)\n"
                       "• Failing graphics card\n"
                       "• Loose display cables\n"
                       "• Backlight or LCD panel failure",
            "category": "Display",
            "confidence": "high",
            "priority": "MEDIUM",
            "rule_advice": [
                "Boot in Safe Mode to test basic display",
                "Update or reinstall GPU drivers with DDU",
                "Check display cable connections",
                "Test with external monitor if possible",
                "Reseat GPU if desktop system"
            ]
        }
    },
    
    "disk_full": {
        "patterns": [
            "no space", "disk full", "storage full", "out of space"
        ],
        "additional_check": lambda words: "full" in words,
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Low disk space causes:\n"
                       "• System slowdown and freezing\n"
                       "• Inability to install updates\n"
                       "• Program crashes and data loss risk",
            "category": "Storage",
            "confidence": "high",
            "priority": "MEDIUM",
            "rule_advice": [
                "Run Disk Cleanup as Administrator",
                "Delete temporary files in %temp%",
                "Uninstall unused programs",
                "Move large files to external storage",
                "Consider upgrading to larger SSD"
            ]
        }
    },
    
    "drive_noise": {
        "patterns": ["clicking", "grinding"],
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "🚨 CRITICAL: Clicking/grinding sounds indicate HARD DRIVE FAILURE!\n"
                       "• Mechanical hard drive is physically failing\n"
                       "• Immediate data backup required\n"
                       "• Drive will completely fail soon",
            "category": "Storage Emergency",
            "confidence": "high",
            "priority": "CRITICAL",
            "rule_advice": [
                "BACKUP IMPORTANT DATA IMMEDIATELY",
                "Do NOT run disk repair tools",
                "Replace drive as soon as possible",
                "Use SSD replacement for better reliability",
                "Consider professional data recovery if critical data"
            ]
        }
    },
    
    "no_internet": {
        "patterns": [
            "no internet", "wifi not working", "can't connect", 
            "limited connectivity", "no wifi"
        ],
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Network connectivity issues:\n"
                       "• Router/modem problems\n"
                       "• Driver issues\n"
                       "• DNS or IP configuration\n"
                       "• Hardware failure",
            "category": "Network",
            "confidence": "high",
            "priority": "MEDIUM",
            "rule_advice": [
                "Restart router and modem",
                "Run Windows Network Troubleshooter",
                "Update network adapter drivers",
                "Try: ipconfig /release → ipconfig /renew",
                "Reset TCP/IP stack: netsh int ip reset"
            ]
        }
    },
    
    "keyboard_issue": {
        "patterns": [],
        "additional_check": lambda words: "keyboard" in words and any(word in words for word in ["not", "working", "stuck", "broken"]),
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Keyboard problems:\n"
                       "• Driver or software conflict\n"
                       "• Physical damage or liquid spill\n"
                       "• Connection issues (for desktop keyboards)",
            "category": "Peripheral",
            "confidence": "medium",
            "priority": "MEDIUM",
            "rule_advice": [
                "Test with On-Screen Keyboard",
                "Update keyboard drivers",
                "Try different USB port",
                "Check for physical damage or debris",
                "Test keyboard on another computer"
            ]
        }
    },
    
    "mouse_issue": {
        "patterns": [],
        "additional_check": lambda words: any(word in words for word in ["mouse", "cursor"]) and any(word in words for word in ["not", "working", "jumping", "broken"]),
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Mouse problems typically:\n"
                       "• Driver issues\n"
                       "• Sensor blockage or surface issues\n"
                       "• Wireless connection problems\n"
                       "• Physical damage",
            "category": "Peripheral",
            "confidence": "medium",
            "priority": "MEDIUM",
            "rule_advice": [
                "Clean mouse sensor with compressed air",
                "Update mouse drivers",
                "Try different surface or mouse pad",
                "Check wireless receiver connection",
                "Test with different USB port"
            ]
        }
    },
    
    "no_sound": {
        "patterns": [
            "no sound", "audio not working", "headphones not working", "speakers silent"
        ],
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Audio issues common causes:\n"
                       "• Driver conflicts or updates needed\n"
                       "• Wrong playback device selected\n"
                       "• Cable or connection problems\n"
                       "• Audio service not running",
            "category": "Audio",
            "confidence": "high",
            "priority": "LOW",
            "rule_advice": [
                "Check volume mixer and device selection",
                "Update audio drivers from manufacturer site",
                "Run Windows Audio Troubleshooter",
                "Check physical connections and cables",
                "Restart Windows Audio service"
            ]
        }
    },
    
    "mic_issue": {
        "patterns": [],
        "additional_check": lambda words: "microphone" in words or ("mic" in words and "not" in words),
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Microphone not working:\n"
                       "• Privacy settings blocking access\n"
                       "• Driver issues\n"
                       "• Wrong input device selected\n"
                       "• Hardware failure",
            "category": "Audio",
            "confidence": "medium",
            "priority": "LOW",
            "rule_advice": [
                "Check microphone privacy settings in Windows",
                "Update audio drivers",
                "Test microphone in Sound settings",
                "Check app-specific microphone permissions",
                "Try different microphone if available"
            ]
        }
    },
    
    "battery_issue": {
        "patterns": [],
        "additional_check": lambda words: "battery" in words and any(word in words for word in ["draining", "not charging", "swollen"]),
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Battery problems:\n"
                       "• Normal wear (2-3 year lifespan)\n"
                       "• Charging circuit failure\n"
                       "• Software/driver issues\n"
                       "• ⚠️ SWOLLEN BATTERY = SAFETY HAZARD",
            "category": "Power",
            "confidence": "high",
            "priority": "HIGH",
            "rule_advice": [
                "Run battery health report: powercfg /batteryreport",
                "Update BIOS and chipset drivers",
                "Calibrate battery (drain fully, charge fully)",
                "⚠️ If swollen: stop using immediately and replace"
            ]
        }
    },
    
    "bsod": {
        "patterns": [
            "blue screen", "bsod", "stop code", "critical process died"
        ],
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Blue Screen of Death analysis:\n"
                       "• Driver conflicts (most common)\n"
                       "• Hardware failure (RAM, storage)\n"
                       "• System file corruption\n"
                       "• Overheating or power issues",
            "category": "System Stability",
            "confidence": "high",
            "priority": "HIGH",
            "rule_advice": [
                "Note the STOP CODE for specific diagnosis",
                "Update ALL drivers, especially GPU and chipset",
                "Run Windows Memory Diagnostic",
                "Check Event Viewer for detailed errors",
                "Run: sfc /scannow and DISM commands"
            ]
        }
    },
    
    "boot_loop": {
        "patterns": [
            "boot loop", "restarting loop", "infinite restart", "keeps restarting"
        ],
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Boot looping indicates:\n"
                       "• Corrupt system files or updates\n"
                       "• Driver conflicts during boot\n"
                       "• Hardware component failure\n"
                       "• Malware or system modification",
            "category": "Boot Issues",
            "confidence": "high",
            "priority": "HIGH",
            "rule_advice": [
                "Boot into Safe Mode or Windows Recovery",
                "Use System Restore to previous point",
                "Run Startup Repair from recovery environment",
                "Check for recently installed hardware/software",
                "Last resort: Reset Windows keeping files"
            ]
        }
    },
    
    "boot_failure": {
        "patterns": [
            "won't boot", "stuck on logo", "automatic repair", "diagnosing your pc"
        ],
        "expert_advice": {
            "type": "expert_diagnosis",
            "content": "Boot failure troubleshooting:\n"
                       "• Corrupt boot configuration\n"
                       "• Failing storage drive\n"
                       "• RAM or motherboard issues\n"
                       "• UEFI/BIOS configuration problems",
            "category": "Boot Issues",
            "confidence": "high",
            "priority": "HIGH",
            "rule_advice": [
                "Try Windows Automatic Repair",
                "Rebuild BCD: bootrec /rebuildbcd",
                "Test with minimal hardware configuration",
                "Check boot order in BIOS/UEFI",
                "Test RAM with MemTest86"
            ]
        }
    },
    
    "emergency": {
        "patterns": [
            "smoke", "fire", "spark", "burning", "water", "liquid", "wet"
        ],
        "expert_advice": None  # Handled separately by check_emergency_situation
    }
}


def reason(facts: List[Dict], question: str, system_metrics: Optional[Dict] = None) -> List[Dict]:
    return enhanced_reason(facts, question, system_metrics)


def enhanced_reason(facts: List[Dict], question: str, system_metrics: Optional[Dict] = None) -> List[Dict]:
    answers = []
    q = question.lower().strip()
    original_question = question

    # === 1. INSTANT EMERGENCY DETECTION ===
    emergency = check_emergency_situation(q)
    if emergency:
        return [emergency]

    # === 2. EXTRACT SYMPTOMS (always extract for potential enhancement) ===
    symptoms = extract_all_symptoms(q)

    # === 3. KNOWLEDGE BASE MATCHING ===
    kb_matches = []
    for category_fact in facts:
        if not isinstance(category_fact, dict) or "questions" not in category_fact:
            continue

        category = category_fact.get("category", "General")
        
        # Loop through each question in the questions array
        for qa in category_fact.get("questions", []):
            if not isinstance(qa, dict) or "question" not in qa:
                continue

            fq = qa["question"].lower()
            fq_clean = fq.strip('?.!').strip()
            q_clean = q.strip('?.!').strip()

            similarity = calculate_similarity(q, fq)
            keyword_match = calculate_keyword_match(q, fq)

            # Detect exact or quoted matches
            exact_or_quoted = (
                fq_clean in q_clean or
                q_clean in fq_clean or
                f'"{qa["question"]}"' in original_question or
                f"'{qa['question']}'" in original_question
            )

            combined_score = max(similarity, keyword_match)
            if exact_or_quoted:
                combined_score = 1.0

            # Permissive but safe matching
            if (combined_score > 0.2 or
                keyword_match > 0.3 or
                len(set(q.split()) & set(fq.split())) >= 2 or
                exact_or_quoted):

                confidence = "perfect" if exact_or_quoted else ("high" if combined_score > 0.5 else "medium")
                match_score = 1.0 if exact_or_quoted else combined_score

                # Create a flat fact for rules system
                flat_fact = {
                    "question": qa["question"],
                    "answer": qa.get("answer", ""),
                    "category": category
                }

                kb_matches.append({
                    "type": "kb_match",
                    "content": qa.get("answer", "No detailed answer available."),
                    "category": category,
                    "confidence": confidence,
                    "match_score": round(match_score, 4),
                    "priority": get_priority_level(flat_fact, system_metrics) or "MEDIUM",
                    "rule_advice": execute_all_rules(flat_fact, system_metrics) or [],
                    "troubleshooting_steps": generate_troubleshooting_steps(flat_fact) or [],
                    "source_question": qa["question"]
                })

    # === 4. IMPROVED KB FILTERING WITH EMERGENCY CONTEXT CHECK ===
    best_kb_matches = []
    if kb_matches:
        # Sort by confidence and score
        confidence_order = {"perfect": 4, "high": 3, "medium": 2, "low": 1}
        kb_matches.sort(key=lambda x: (
            confidence_order.get(x["confidence"], 0),
            x["match_score"]
        ), reverse=True)
        
        # === SMART RELEVANCE FILTERING ===
        best_matches = []
        
        # Extract main keywords from the question
        question_keywords = extract_main_keywords(q)
        
        for match in kb_matches:
            # Skip low-confidence matches for common questions
            if match["confidence"] == "low" and match["match_score"] < 0.4:
                continue
            
            # === CRITICAL FIX: Check if emergency content is actually relevant ===
            if not is_emergency_relevant(match, q):
                continue
                
            # Check if match content is actually relevant to the question
            match_text = (match["content"] + " " + match.get("source_question", "")).lower()
            
            # Calculate relevance score based on keyword overlap
            relevance_score = calculate_relevance_score(question_keywords, match_text)
            
            # Only keep highly relevant matches
            if (relevance_score > 0.3 or 
                match["confidence"] in ["perfect", "high"] or 
                match["match_score"] > 0.6):
                
                # Avoid adding multiple matches from the same category unless they're excellent
                existing_categories = [m["category"] for m in best_matches]
                if (match["category"] not in existing_categories or 
                    match["confidence"] in ["perfect", "high"]):
                    best_matches.append(match)
            
            # Stop when we have enough high-quality matches
            if len(best_matches) >= 2 and match["match_score"] > 0.7:
                break
        
        # Final safety: if we have good matches, remove any low-scoring ones
        if len(best_matches) >= 2:
            best_matches = [m for m in best_matches if m["match_score"] > 0.3 or m["confidence"] in ["perfect", "high"]]
        
        # If no good matches found, take top 1-2 by score as fallback
        if not best_matches and kb_matches:
            # But filter out emergency matches for normal queries
            non_emergency_matches = [m for m in kb_matches if is_emergency_relevant(m, q)]
            best_matches = non_emergency_matches[:1] if non_emergency_matches else kb_matches[:1]
        
        # Store the best KB matches separately
        best_kb_matches = best_matches[:2]  # Strict limit to 2 best matches
        for match in best_kb_matches:
            if match["confidence"] == "perfect":
                match["content"] = f"📚 Direct answer:\n{match['content']}"
            else:
                match["content"] = f"💡 Related answer:\n{match['content']}"

    # === 5. SMART ANSWER MERGING: KB + SYMPTOM ADVICE ===
    symptom_advice = master_generate_advice(symptoms, original_question, q, system_metrics)
    
    if best_kb_matches:
        # We have KB matches - prioritize them but enhance with symptom advice
        answers.extend(best_kb_matches)
        
        # Add high-quality symptom advice that provides additional value
        for symptom_adv in symptom_advice:
            if should_enhance_with_symptom_advice(best_kb_matches, symptom_adv):
                answers.append(symptom_adv)
    else:
        # No KB matches - use symptom engine
        answers.extend(symptom_advice)

    # === 6. SYSTEM METRICS ALERTS ===
    if system_metrics:
        metric_alerts = generate_metric_advice(system_metrics)
        # Only add metric alerts if they're relevant to the question
        relevant_metrics = []
        for alert in metric_alerts:
            if symptoms.get("overheating", False) and "temperature" in alert["content"].lower():
                relevant_metrics.append(alert)
            elif symptoms.get("slow", False) and "memory" in alert["content"].lower():
                relevant_metrics.append(alert)
            elif not answers:  # If no answers yet, show all metrics
                relevant_metrics.append(alert)
        answers.extend(relevant_metrics)

    # === 7. CONTEXT-AWARE PREVENTIVE MAINTENANCE ===
    fake_fact = {"question": question, "answer": "", "category": "Maintenance"}
    maint = get_preventive_maintenance_advice(fake_fact)
    
    # Only add preventive if it's relevant to the current issue
    should_add_preventive = False
    if symptoms.get("overheating") and maint and any("clean" in advice.lower() for advice in maint):
        should_add_preventive = True
    elif symptoms.get("slow") and maint and any("update" in advice.lower() or "clean" in advice.lower() for advice in maint):
        should_add_preventive = True
    elif maint and not any(a.get("type") == "preventive" for a in answers):
        should_add_preventive = True
    
    if maint and should_add_preventive:
        answers.append({
            "type": "preventive",
            "content": "🛠️ Long-term prevention tips:",
            "category": "Maintenance",
            "confidence": "medium",
            "priority": "LOW",
            "rule_advice": maint
        })

    # === 8. FALLBACK TO SYMPTOM ENGINE IF KB MATCHES ARE POOR ===
    if not answers or (len(answers) == 1 and answers[0].get("match_score", 0) < 0.4):
        symptom_advice = master_generate_advice(symptoms, original_question, q, system_metrics)
        if symptom_advice:
            # Replace poor KB matches with good symptom advice
            answers = symptom_advice + [a for a in answers if a.get("type") != "kb_match"]

    # === 9. IMPROVED SORTING & DEDUPLICATION ===
    priority_order = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "NORMAL": 1}
    confidence_order = {"perfect": 4, "high": 3, "medium": 2, "low": 1}

    answers.sort(key=lambda x: (
        priority_order.get(x.get("priority", "LOW"), 0),
        confidence_order.get(x.get("confidence", "low"), 0),
        x.get("match_score", 0)
    ), reverse=True)

    seen = set()
    unique = []
    for a in answers:
        # More intelligent deduplication
        content_preview = a["content"][:150].lower()
        key = (a["type"], hash(content_preview))
        if key not in seen:
            seen.add(key)
            unique.append(a)

    return unique[:4] if unique else [fallback_answer()]


def should_enhance_with_symptom_advice(kb_matches: List[Dict], symptom_advice: Dict) -> bool:
    """Determine if symptom advice should be added alongside KB matches"""
    
    # Don't add if we already have too many answers
    if len(kb_matches) >= 3:
        return False
    
    # If KB answer is generic/vague, prioritize symptom advice
    for kb_match in kb_matches:
        kb_content = kb_match.get("content", "")
        
        # Detect generic KB answers (common patterns)
        is_generic = (
            "most commonly caused by" in kb_content.lower() or
            "usually due to" in kb_content.lower() or 
            "typically caused by" in kb_content.lower() or
            "this is often" in kb_content.lower() or
            len(kb_content) < 150  # Very short answers
        )
        
        # If KB answer is generic, definitely include detailed symptom advice
        if is_generic and symptom_advice.get("confidence") == "high":
            return True
    
    symptom_content = symptom_advice.get("content", "").lower()
    
    # Check if symptom advice provides significantly different information
    for kb_match in kb_matches:
        kb_content = kb_match.get("content", "").lower()
        
        # If symptom advice has troubleshooting steps and KB doesn't
        if (symptom_advice.get("troubleshooting_steps") and 
            not kb_match.get("troubleshooting_steps")):
            return True
            
        # If symptom advice is much more detailed
        if len(symptom_content) > len(kb_content) + 100:  # 100+ chars more detailed
            return True
            
        # If symptom advice covers critical safety issues
        if symptom_advice.get("priority") in ["CRITICAL", "HIGH"]:
            return True
            
        # If symptom advice covers different aspects (e.g., drivers vs hardware)
        symptom_text = symptom_advice.get("content", "").lower()
        kb_text = kb_match.get("content", "").lower()
        if ("driver" in symptom_text and "driver" not in kb_text) or \
           ("thermal" in symptom_text and "thermal" not in kb_text) or \
           ("temperature" in symptom_text and "temperature" not in kb_text):
            return True
    
    return False


def is_emergency_relevant(match: Dict, question: str) -> bool:
    """Check if an emergency match is actually relevant to the query"""
    # Emergency indicators that must be present in the question
    emergency_indicators = [
        "smoke", "fire", "spark", "burning", "electrical", "hazard", 
        "flame", "burned", "smoking", "sparked", "safety hazard"
    ]
    
    # Content that indicates emergency response
    emergency_content_indicators = [
        "IMMEDIATE SAFETY HAZARD", "UNPLUG", "CRITICAL SAFETY", 
        "fire", "smoke", "spark", "burning", "electrical hazard"
    ]
    
    question_lower = question.lower()
    match_content = match.get("content", "").lower()
    match_question = match.get("source_question", "").lower()
    
    # If match contains emergency content but question has no emergency words, downgrade it
    has_emergency_content = any(indicator in match_content for indicator in emergency_content_indicators)
    has_emergency_question = any(indicator in match_question for indicator in emergency_content_indicators)
    
    question_has_emergency = any(indicator in question_lower for indicator in emergency_indicators)
    
    # If it's emergency content but question doesn't mention emergencies, skip it
    if (has_emergency_content or has_emergency_question) and not question_has_emergency:
        return False
        
    return True


def extract_main_keywords(question: str) -> List[str]:
    """Extract main keywords from question for relevance checking"""
    stop_words = {"the", "a", "an", "to", "my", "me", "it", "is", "on", "in", "with", 
                  "and", "for", "i", "of", "or", "at", "this", "that", "from", "what",
                  "why", "how", "when", "where", "can", "could", "would", "should",
                  "please", "help", "computer", "laptop", "pc", "desktop", "won't", "wont"}
    
    words = question.lower().split()
    keywords = [w.strip('?.!') for w in words if w not in stop_words and len(w) > 2]
    return keywords


def calculate_relevance_score(question_keywords: List[str], match_text: str) -> float:
    """Calculate how relevant a match is to the question"""
    if not question_keywords:
        return 0.0
    
    matches = 0
    for keyword in question_keywords:
        if keyword in match_text:
            matches += 1
    
    return matches / len(question_keywords)


def extract_all_symptoms(q: str) -> Dict[str, bool]:
    """Extract symptoms using the centralized symptom definitions"""
    q_lower = q.lower()
    words = set(q_lower.split())
    
    symptoms = {}
    
    for symptom_name, definition in SYMPTOM_DEFINITIONS.items():
        # Check pattern matches
        pattern_match = any(phrase in q_lower for phrase in definition["patterns"])
        
        # Check additional conditions if they exist
        additional_match = False
        if "additional_check" in definition:
            additional_match = definition["additional_check"](words)
        
        # Symptom is detected if either patterns match OR additional conditions are met
        symptoms[symptom_name] = pattern_match or additional_match
    
    return symptoms


def master_generate_advice(symptoms: Dict[str, bool], original_question: str, q: str, metrics: Optional[Dict]) -> List[Dict]:
    """Generate expert advice based on detected symptoms"""
    advice = []

    # EMERGENCY should have been caught already, but double-check
    if symptoms["emergency"]:
        emergency_advice = check_emergency_situation(q)
        if emergency_advice:
            return [emergency_advice]

    # Generate advice for all detected symptoms
    for symptom_name, is_detected in symptoms.items():
        if is_detected and symptom_name != "emergency":  # Emergency handled separately
            symptom_def = SYMPTOM_DEFINITIONS[symptom_name]
            if symptom_def["expert_advice"]:
                # Create a copy to avoid modifying the original
                advice_entry = symptom_def["expert_advice"].copy()
                advice.append(advice_entry)

    # Final fallback if nothing specific matched
    if not advice:
        advice.append({
            "type": "expert_generic",
            "content": f"Based on your description — \"{original_question}\" — here are the most likely causes and fixes:",
            "category": "General Diagnosis",
            "confidence": "medium",
            "priority": "MEDIUM",
            "rule_advice": [
                "Restart in Safe Mode to isolate software vs hardware",
                "Run Windows Memory Diagnostic",
                "Check Device Manager for yellow triangles",
                "Update all drivers from manufacturer site (not Windows Update)",
                "Run: sfc /scannow and DISM /Online /Cleanup-Image /RestoreHealth"
            ],
            "troubleshooting_steps": [
                "1. Note exact error messages or behavior",
                "2. Try Safe Mode (hold Shift + Restart)",
                "3. Run hardware diagnostics if available",
                "4. Backup important data first"
            ]
        })

    return advice


def check_emergency_situation(q: str) -> Optional[Dict]:
    """More precise emergency detection with word boundaries"""
    emergency_patterns = [
        r'\bsmoke\b', r'\bfire\b', r'\bspark\b', r'\bburning smell\b',
        r'\bspilled water\b', r'\bliquid\b', r'\bwet laptop\b', 
        r'\bdropped in water\b', r'\belectrical fire\b', r'\bsmoking\b',
        r'\bflame\b', r'\bburned\b', r'\belectrical hazard\b'
    ]
    
    for pattern in emergency_patterns:
        if re.search(pattern, q, re.IGNORECASE):
            return {
                "type": "emergency",
                "content": "🚨 CRITICAL SAFETY EMERGENCY - IMMEDIATE ACTION REQUIRED! 🚨\n\n"
                           "• UNPLUG FROM POWER IMMEDIATELY\n"
                           "• DO NOT TOUCH if smoking or sparking\n"
                           "• NO WATER on electrical fires\n"
                           "• If liquid spilled: power off → remove battery → dry 72+ hours\n"
                           "• Contact professional technician before reuse",
                "priority": "CRITICAL",
                "confidence": "perfect",
                "rule_advice": [
                    "UNPLUG POWER CORD NOW",
                    "Move away from flammable materials",
                    "Call emergency services if fire develops",
                    "Do not attempt to use until professionally inspected"
                ],
                "troubleshooting_steps": [
                    "1. SAFETY FIRST - Unplug immediately",
                    "2. Evacuate area if heavy smoke",
                    "3. Contact professional repair service",
                    "4. Do not attempt DIY repair on electrical hazards"
                ]
            }
    return None


def calculate_similarity(a: str, b: str) -> float:
    wa, wb = set(a.split()), set(b.split())
    return len(wa & wb) / len(wa | wb) if wa and wb else 0.0


def calculate_keyword_match(q: str, fq: str) -> float:
    stop = {"the", "a", "an", "to", "my", "me", "it", "is", "on", "in", "with", "and", "for", "i", "of", "or", "at", "this", "that", "from"}
    qw = {w for w in q.split() if w not in stop and len(w) > 2}
    fw = {w for w in fq.split() if w not in stop and len(w) > 2}
    if not qw:
        return 0.0
    return min(len(qw & fw) / len(qw), 1.0)


def generate_metric_advice(metrics: Dict) -> List[Dict]:
    alerts = []
    if metrics.get("cpu_temp", 0) > 92:
        alerts.append({
            "type": "metric_alert",
            "content": f"🔥 CRITICAL: CPU temperature {metrics['cpu_temp']}°C - Risk of permanent damage!",
            "category": "Thermal Emergency",
            "confidence": "high",
            "priority": "CRITICAL"
        })
    if metrics.get("gpu_temp", 0) > 88:
        alerts.append({
            "type": "metric_alert", 
            "content": f"🌡️ GPU Overheating: {metrics['gpu_temp']}°C",
            "category": "Thermal",
            "confidence": "high",
            "priority": "HIGH"
        })
    if metrics.get("memory_usage", 0) > 92:
        alerts.append({
            "type": "metric_alert",
            "content": "💾 RAM nearly full → Close apps or upgrade",
            "category": "Performance", 
            "confidence": "medium",
            "priority": "HIGH"
        })
    return alerts


def fallback_answer() -> Dict:
    return {
        "type": "need_more_info",
        "content": "I can definitely help you! To give the best advice, please tell me:\n"
                   "• Exact error message (if any)\n"
                   "• When did it start happening?\n"
                   "• Laptop or desktop? Brand & model?\n"
                   "• What changed recently (updates, new software, drop, spill)?",
        "category": "Clarification Needed",
        "confidence": "high",
        "priority": "MEDIUM"
    }


def get_detailed_analysis(facts, question, system_metrics=None):
    """Simple detailed analysis for the UI"""
    answers = reason(facts, question, system_metrics)
    return {
        "original_question": question,
        "total_answers": len(answers),
        "answers_by_type": {},
        "answers_by_confidence": {},
        "detailed_answers": answers
    }


# === DEBUG FUNCTION ===
def debug_reasoning(facts, question, system_metrics=None):
    """Debug function to see what's happening in the reasoning process"""
    q = question.lower().strip()
    print(f"🔍 DEBUG for: '{question}'")
    print(f"📋 Query: {q}")
    
    # Check emergency detection
    emergency = check_emergency_situation(q)
    print(f"🚨 Emergency detected: {bool(emergency)}")
    
    # Extract symptoms
    symptoms = extract_all_symptoms(q)
    active_symptoms = [k for k, v in symptoms.items() if v]
    print(f"📊 Active symptoms: {active_symptoms}")
    
    # Simulate KB matching
    kb_matches = []
    for category_fact in facts:
        if not isinstance(category_fact, dict) or "questions" not in category_fact:
            continue
            
        for qa in category_fact.get("questions", []):
            if not isinstance(qa, dict) or "question" not in qa:
                continue
                
            fq = qa["question"].lower()
            similarity = calculate_similarity(q, fq)
            keyword_match = calculate_keyword_match(q, fq)
            combined_score = max(similarity, keyword_match)
            
            if combined_score > 0.2:
                kb_matches.append({
                    "question": qa["question"],
                    "score": round(combined_score, 3),
                    "category": category_fact.get("category", "Unknown"),
                    "emergency_content": "IMMEDIATE SAFETY" in qa.get("answer", "").upper()
                })
    
    print(f"📚 KB matches found: {len(kb_matches)}")
    for match in sorted(kb_matches, key=lambda x: x["score"], reverse=True)[:3]:
        emergency_flag = " 🚨" if match["emergency_content"] else ""
        print(f"   - {match['score']}: '{match['question']}' [{match['category']}]{emergency_flag}")
    
    # Run actual reasoning
    result = reason(facts, question, system_metrics)
    print(f"🎯 Final answers: {len(result)}")
    for i, answer in enumerate(result):
        print(f"   {i+1}. {answer.get('type', 'unknown')} - {answer.get('confidence', 'unknown')} confidence")
    
    return result