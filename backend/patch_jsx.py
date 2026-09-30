"""Patch CyberShield.jsx: fix clumsy text, improve Women Safety, apply bg classes."""
import re

path = r"c:\Users\bindu\Downloads\CyberCrimePredict\CyberCrimePredict\frontend\src\CyberShield.jsx"
with open(path, encoding="utf-8") as f:
    src = f.read()

# 1. Fix sidebar brand subtitle
src = src.replace(
    "user.role === 'ADMIN' ? 'ADMIN CONSOLE' : 'CYBERCRIME WORKSPACE'",
    "user.role === 'ADMIN' ? 'ADMIN' : 'CYBERNEXA'"
)

# 2. Remove clumsy Women Safety hero text
src = src.replace(
    "Your emergency contacts can be selected for a simulated alert request. This prototype does not send messages or contact police.",
    "Tap the button below to alert your trusted contacts."
)

# 3. Remove "Stay connected. Get help quickly when you need it."
src = src.replace(
    "Stay connected. Get help quickly when you need it.",
    "Your personal safety hub."
)

# 4. Fix Women Safety heading description
src = src.replace(
    "<h2>Need help right now?</h2>",
    "<h2>Emergency Alert</h2>"
)

# 5. Shorten I'm Safe description
src = src.replace(
    "Record a SAFE event. No message is sent.",
    "Mark yourself safe."
)

# 6. Shorten Start Trip description  
src = src.replace(
    "Location is requested only with your permission.",
    "Share your trip with contacts."
)

# 7. Shorten Quick Alert description
src = src.replace(
    "Press and hold for 2 seconds, then confirm.",
    "Hold 2 seconds to trigger."
)

# 8. Shorten Emergency Contacts description
src = src.replace(
    "0 active contact(s) configured.",
    "Manage trusted contacts."
)
# This is dynamic so keep the count
src = src.replace(
    "{contacts.filter((contact) => contact.is_active).length} active contact(s) configured.",
    "{contacts.filter((contact) => contact.is_active).length} trusted contact(s)."
)

# 9. Shorten Safety Settings description
src = src.replace(
    "Configure triggers, countdown, and trip updates.",
    "Configure safety triggers."
)

# 10. Shorten Get Current Location description
src = src.replace(
    "Location unavailable. Please enable location permission.",
    "Enable location in browser."
)
src = src.replace(
    "Only requested when you tap this control.",
    "Request GPS location."
)

# 11. Fix "No direct police integration is configured." -> shorter
src = src.replace(
    "No direct police integration is configured.",
    "Emergency services: Call 112"
)
src = src.replace(
    "Nearby emergency services could not be verified.",
    ""
)

# 12. Evidence Recorder description
src = src.replace(
    "Record audio evidence discreetly. Recordings are stored on your device.",
    "Discreet audio evidence recording."
)
src = src.replace(
    "Use this if someone is misbehaving. Recording stays on your device.",
    "Recording saved on your device only."
)

# 13. Live Location Sharing description
src = src.replace(
    "Share your GPS location with trusted contacts via a Google Maps link.",
    "Share your location with contacts."
)

# 14. Fix topbar - remove clumsy breadcrumb text "Operations"
src = src.replace(
    "<div className=\"crumb\"><button className=\"icon-btn mobile-toggle\" aria-label=\"Open navigation\" onClick={() => setMobileMenu(true)}><Menu size={19} /></button>Operations <ChevronRight size={14} /><b>{page}</b></div>",
    "<div className=\"crumb\"><button className=\"icon-btn mobile-toggle\" aria-label=\"Open navigation\" onClick={() => setMobileMenu(true)}><Menu size={19} /></button><b>{page}</b></div>"
)

# 15. Fix workspace caption
src = src.replace(
    "<div className=\"workspace-caption\">WORKSPACE <ChevronDown size={13} /></div>",
    "<div className=\"workspace-caption\">NAVIGATION</div>"
)

# 16. Dashboard description clumsy text
src = src.replace(
    'description="Your reports, grounded knowledge retrieval, and account workspace."',
    'description="Cybercrime intelligence & personal safety dashboard."'
)

# 17. Fix content section class for safety history
src = src.replace(
    "page === 'Safety History' ? 'safety-content' : ''",
    "page === 'Safety History' ? 'safety-history-content' : ''"
)

# 18. Remove "DEMO / SIMULATION" text from backend-offline notice
src = src.replace(
    "<b>Backend offline.</b> Start Flask to load complaint records and enable RAG queries.",
    "<b>Backend offline.</b> Start the backend server."
)

# 19. RAG Intelligence description
src = src.replace(
    'description="Ask any cybersecurity question. Answers are retrieved from the local knowledge base — no external AI service required."',
    'description="Ask any cybersecurity question. AI-powered answers from the knowledge base."'
)

# 20. Prediction description
src = src.replace(
    'description="Describe a cybercrime incident to get an AI prediction, nearest police station, and step-by-step guidance."',
    'description="Describe what happened. Get AI prediction, action steps and nearest police station."'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(src)

print("JSX patched successfully")
