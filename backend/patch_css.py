import re

css_path = r"c:\Users\bindu\Downloads\CyberCrimePredict\CyberCrimePredict\frontend\src\CyberShield.css"

with open(css_path, encoding="utf-8") as f:
    css = f.read()

# Find start and end of the old background section
start_marker = ".dashboard-content, .rag-content, .dataset-content, .predict-content, .threat-content"
end_marker = ".dataset-attribution"

start = css.find(start_marker)
end = css.find(end_marker)

if start == -1 or end == -1:
    print(f"Markers not found! start={start} end={end}")
    exit(1)

new_block = """.dashboard-content, .rag-content, .dataset-content, .predict-content, .threat-content,
.safety-content, .history-content, .reports-content, .profile-content, .admin-content,
.knowledge-content, .settings-content, .safety-history-content, .stats-content
{ position: relative; isolation: isolate; }

/* Dashboard + Profile + RAG = AI face circuit (bg-profile.jpg) */
.dashboard-content::before, .rag-content::before, .profile-content::before {
  position: fixed; z-index: -1; inset: 0; content: '';
  background: url('/images/bg-profile.jpg') center center / cover no-repeat;
  opacity: 0.07; pointer-events: none;
}

/* Prediction History = binary tunnel blue (bg-history.jpg) */
.history-content::before, .predict-content::before, .dataset-content::before {
  position: fixed; z-index: -1; inset: 0; content: '';
  background: url('/images/bg-history.jpg') center center / cover no-repeat;
  opacity: 0.08; pointer-events: none;
}

/* Threat Intelligence + Admin = hacker 3 screens (bg-admin.jpg) */
.threat-content::before, .admin-content::before {
  position: fixed; z-index: -1; inset: 0; content: '';
  background: url('/images/bg-admin.jpg') center center / cover no-repeat;
  opacity: 0.07; pointer-events: none;
}

/* My Reports + Settings + Knowledge Base = hacker virus (bg-reports.jpg) */
.reports-content::before, .settings-content::before, .knowledge-content::before {
  position: fixed; z-index: -1; inset: 0; content: '';
  background: url('/images/bg-reports.jpg') center center / cover no-repeat;
  opacity: 0.07; pointer-events: none;
}

/* Crime Statistics = AI dashboard (bg-dashboard.jpg) */
.stats-content::before {
  position: fixed; z-index: -1; inset: 0; content: '';
  background: url('/images/bg-dashboard.jpg') center center / cover no-repeat;
  opacity: 0.07; pointer-events: none;
}

/* Women Safety = woman breaking chains (bg-women-new.jpg) */
.safety-content::before {
  position: fixed; z-index: -1; inset: 0; content: '';
  background: url('/images/bg-women-new.jpg') center center / cover no-repeat;
  opacity: 0.12; pointer-events: none;
}

/* Safety History = Women Safety poster (bg-safety-history.jpg) */
.safety-history-content::before {
  position: fixed; z-index: -1; inset: 0; content: '';
  background: url('/images/bg-safety-history.jpg') center center / cover no-repeat;
  opacity: 0.09; pointer-events: none;
}

/* Auth bg-safety for SafetyLogin page */
.auth-bg-safety {
  position: fixed; inset: 0; z-index: 0;
  background: url('/images/bg-women-new.jpg') center center / cover no-repeat;
}

"""

new_css = css[:start] + new_block + css[end:]

with open(css_path, "w", encoding="utf-8") as f:
    f.write(new_css)

print("CSS patched successfully")
