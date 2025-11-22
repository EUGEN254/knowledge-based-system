# knowledge/rules.py
def hardware_issue_advice(fact, system_metrics=None):
    """
    Rule: Provide advice for hardware issues
    """
    question = fact.get("question", "").lower()
    answer = fact.get("answer", "").lower()
    advice_list = []
    
    # Overheating detection
    if any(word in question for word in ["overheat", "overheating", "temperature", "hot", "thermal", "cooling", "warm"]):
        advice_list.append("🔴 Check CPU/GPU temperatures using monitoring software like HWMonitor")
        advice_list.append("🧹 Clean dust from fans, heatsinks, and vents regularly")
        advice_list.append("💨 Ensure proper case airflow and ventilation")
        advice_list.append("🔧 Consider reapplying thermal paste if temperatures remain high")
    
    # Fan noise issues
    if any(word in question for word in ["fan", "noisy" , "noise", "loud", "whirring", "grinding", "buzzing"]):
        advice_list.append("🎯 Identify which fan is making noise (CPU, GPU, case, PSU)")
        advice_list.append("🧼 Clean the noisy fan and check for obstructions")
        advice_list.append("⚙️ Check fan speed settings in BIOS/UEFI")
    
    # Performance issues
    if any(word in question for word in ["slow", "performance", "lag", "bottleneck", "sluggish", "speed"]):
        advice_list.append("📊 Monitor resource usage in Task Manager (CPU, RAM, disk, GPU)")
        advice_list.append("🔄 Update drivers, especially graphics and chipset")
        advice_list.append("💾 Consider SSD upgrade for significant speed improvement")
    
    # Power issues
    if any(word in question for word in ["power", "shutdown", "restart", "boot", "turn on", "won't start"]):
        advice_list.append("🔌 Check all power connections and cables")
        advice_list.append("⚡ Test with different power outlet and cable")
        advice_list.append("🔋 Verify power supply unit (PSU) health and capacity")
    
    # Memory issues
    if any(word in question for word in ["ram", "memory", "bsod", "blue screen", "bluescreen", "crash"]):
        advice_list.append("🧪 Run Windows Memory Diagnostic or MemTest86")
        advice_list.append("🔧 Reseat RAM modules in their slots")
        advice_list.append("⚡ Check RAM compatibility and running at correct speeds")
    
    # Display issues
    if any(word in question for word in ["screen", "display", "monitor", "lines", "distorted", "flickering"]):
        advice_list.append("🖥️ Check video cable connections and try different cables")
        advice_list.append("🔄 Update graphics drivers to latest version")
        advice_list.append("⚙️ Test with different monitor or input source")
    
    # Emergency hardware issues
    if any(word in question for word in ["burn", "burning", "smoke", "spark", "fire", "water", "spilled"]):
        advice_list.append("🚨 IMMEDIATELY shut down and unplug computer")
        advice_list.append("🔥 Do not attempt to use until professionally inspected")
        advice_list.append("💧 For liquid spills: remove battery if possible, dry thoroughly")
    
    return advice_list


def software_issue_advice(fact, system_metrics=None):
    """
    Rule: Provide advice for software issues
    """
    question = fact.get("question", "").lower()
    advice_list = []
    
    # Installation problems
    if any(word in question for word in ["install", "setup", "compatibility", "won't install", "installation"]):
        advice_list.append("🛡️ Run installer as Administrator")
        advice_list.append("🔒 Temporarily disable antivirus during installation")
        advice_list.append("📋 Check system requirements and compatibility")
    
    # Crash and stability issues
    if any(word in question for word in ["crash", "freeze", "not responding", "hang", "stopped working"]):
        advice_list.append("📱 Update software to latest version")
        advice_list.append("🔧 Check for and install available Windows updates")
        advice_list.append("🔄 Run system file checker: sfc /scannow")
    
    # Virus and malware
    if any(word in question for word in ["virus", "malware", "infected", "ransomware", "trojan", "hacked"]):
        advice_list.append("🚫 Disconnect from internet immediately")
        advice_list.append("🛡️ Run full scan with updated antivirus")
        advice_list.append("🔒 Boot in Safe Mode for thorough cleaning")
    
    # Update problems
    if any(word in question for word in ["update", "upgrade", "windows update", "failed update"]):
        advice_list.append("🔄 Run Windows Update Troubleshooter")
        advice_list.append("🧹 Clear update cache and restart update service")
        advice_list.append("📥 Manually download updates from Microsoft Catalog")
    
    return advice_list


def networking_issue_advice(fact, system_metrics=None):
    """
    Rule: Provide advice for networking issues
    """
    question = fact.get("question", "").lower()
    advice_list = []
    
    # WiFi issues
    if any(word in question for word in ["wifi", "wireless", "connection", "disconnect", "router"]):
        advice_list.append("📶 Restart router and modem")
        advice_list.append("🔧 Update network adapter drivers")
        advice_list.append("🎛️ Change WiFi channel to reduce interference")
    
    # Internet speed
    if any(word in question for word in ["slow internet", "bandwidth", "download speed", "streaming", "speed"]):
        advice_list.append("📊 Run speed test at different times of day")
        advice_list.append("🔍 Check for background downloads or updates")
        advice_list.append("🔄 Restart networking equipment")
    
    # Connectivity issues
    if any(word in question for word in ["no internet", "can't connect", "dns", "proxy", "offline"]):
        advice_list.append("🌐 Flush DNS cache: ipconfig /flushdns")
        advice_list.append("🔌 Reset network settings to default")
        advice_list.append("📋 Renew IP address: ipconfig /renew")
    
    return advice_list


def storage_issue_advice(fact, system_metrics=None):
    """
    Rule: Provide advice for storage issues
    """
    question = fact.get("question", "").lower()
    advice_list = []
    
    # Disk space issues
    if any(word in question for word in ["disk full", "storage", "space", "cleanup", "low space"]):
        advice_list.append("🧹 Run Disk Cleanup utility")
        advice_list.append("📁 Move large files to external storage or cloud")
        advice_list.append("🗑️ Uninstall unused programs and games")
    
    # Hard drive problems
    if any(word in question for word in ["hard drive", "hdd", "ssd", "clicking", "noise", "failing"]):
        advice_list.append("💾 Backup important data immediately")
        advice_list.append("🔍 Run CHKDSK to check for disk errors")
        advice_list.append("📊 Monitor drive health with SMART tools")
    
    # Data recovery
    if any(word in question for word in ["recover", "deleted", "formatted", "lost data", "files gone"]):
        advice_list.append("🚫 Stop using the drive immediately")
        advice_list.append("🔧 Use data recovery software promptly")
        advice_list.append("💾 Restore from backup if available")
    
    return advice_list


def gaming_issue_advice(fact, system_metrics=None):
    """
    Rule: Provide advice for gaming issues
    """
    question = fact.get("question", "").lower()
    advice_list = []
    
    # Performance issues
    if any(word in question for word in ["fps", "frame rate", "lag", "stutter", "gaming performance"]):
        advice_list.append("🎮 Update graphics drivers to latest version")
        advice_list.append("⚙️ Lower in-game graphics settings")
        advice_list.append("🔧 Close background applications while gaming")
    
    # Crash issues
    if any(word in question for word in ["game crash", "won't launch", "directx", "opengl", "not starting"]):
        advice_list.append("🔄 Verify game file integrity through platform (Steam/Epic)")
        advice_list.append("📋 Install latest DirectX and Visual C++ redistributables")
        advice_list.append("🛡️ Add game to antivirus exceptions list")
    
    return advice_list


def execute_all_rules(fact, system_metrics=None):
    """
    Execute all rules against a fact and return combined advice
    """
    advice_list = []
    
    rules = [
        hardware_issue_advice,
        software_issue_advice, 
        networking_issue_advice,
        storage_issue_advice,
        gaming_issue_advice,
    ]
    
    for rule in rules:
        advice = rule(fact, system_metrics)
        if advice:
            advice_list.extend(advice)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_advice = []
    for item in advice_list:
        # Use content without emojis for comparison
        content_core = ' '.join(item.split()[1:]) if item.split() else item
        if content_core not in seen:
            seen.add(content_core)
            unique_advice.append(item)
    
    return unique_advice[:8]  # Limit to top 8 most relevant


def get_priority_level(fact, system_metrics=None):
    """
    Rule: Determine priority level for issues
    """
    question = fact.get("question", "").lower()
    
    # Critical issues
    if any(word in question for word in ["fire", "smoke", "spark", "burn", "burning", "water", "spilled", "electrical", "hazard"]):
        return "CRITICAL"
    
    # High priority issues
    if any(word in question for word in ["data loss", "backup", "recovery", "ransomware", "virus", "hacked", "compromised", "won't boot"]):
        return "HIGH"
    
    # Medium priority issues
    if any(word in question for word in ["blue screen", "crash", "freeze", "not working", "error"]):
        return "MEDIUM"
    
    # Low priority issues
    if any(word in question for word in ["slow", "performance", "optimization", "cleanup", "maintenance"]):
        return "LOW"
    
    return "NORMAL"


def generate_troubleshooting_steps(fact):
    """
    Rule: Generate step-by-step troubleshooting guide
    """
    question = fact.get("question", "").lower()
    steps = []
    
    # General troubleshooting steps
    steps.append("1. 🔄 Restart the computer and test again")
    steps.append("2. 📋 Check for recent changes or updates")
    steps.append("3. 🔍 Look for specific error messages or codes")
    
    # Hardware-specific steps
    if any(word in question for word in ["hardware", "component", "device", "peripheral", "usb", "display"]):
        steps.append("4. 🔌 Check all physical connections")
        steps.append("5. 🧹 Clean components and ensure proper ventilation")
        steps.append("6. 🔧 Update device drivers and firmware")
    
    # Software-specific steps
    if any(word in question for word in ["software", "program", "application", "game", "install", "crash"]):
        steps.append("4. 🛡️ Run as Administrator")
        steps.append("5. 🔒 Check antivirus and firewall settings")
        steps.append("6. 📥 Reinstall or repair the application")
    
    # Network-specific steps
    if any(word in question for word in ["network", "wifi", "internet", "router", "connection"]):
        steps.append("4. 🌐 Restart router and modem")
        steps.append("5. 🔧 Update network adapter drivers")
        steps.append("6. 📶 Test with Ethernet cable if possible")
    
    return steps[:6]  # Limit to 6 steps


def get_preventive_maintenance_advice(fact):
    """
    Rule: Provide preventive maintenance advice based on issue type
    """
    question = fact.get("question", "").lower()
    maintenance_advice = []
    
    # Hardware maintenance
    if any(word in question for word in ["overheat", "fan", "noise", "dust", "clean"]):
        maintenance_advice.append("• Clean dust every 3-6 months")
        maintenance_advice.append("• Monitor temperatures regularly")
        maintenance_advice.append("• Ensure proper ventilation")
    
    # Software maintenance
    if any(word in question for word in ["slow", "crash", "update", "virus"]):
        maintenance_advice.append("• Keep system and drivers updated")
        maintenance_advice.append("• Run regular antivirus scans")
        maintenance_advice.append("• Clean temporary files weekly")
    
    # Data maintenance
    if any(word in question for word in ["backup", "recovery", "lost", "deleted"]):
        maintenance_advice.append("• Maintain regular backups")
        maintenance_advice.append("• Use cloud storage for important files")
        maintenance_advice.append("• Test backup restoration periodically")
    
    return maintenance_advice if maintenance_advice else []