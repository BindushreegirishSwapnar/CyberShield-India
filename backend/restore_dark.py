"""Restore the original dark theme in CyberShield.css"""

path = r"c:\Users\bindu\Downloads\CyberCrimePredict\CyberCrimePredict\frontend\src\CyberShield.css"
with open(path, encoding="utf-8") as f:
    css = f.read()

# 1. Restore :root to dark
old_root = """:root {
  color-scheme: light;
  font-family: 'DM Sans', sans-serif;
  color: #182a38;
  background: #ffffff;
  font-synthesis: none;
  --bg: #f5f7fa;
  --sidebar: #ffffff;
  --panel: rgba(255, 255, 255, 0.95);
  --panel-2: #f0f4f8;
  --line: #dde4ec;
  --text: #182a38;
  --muted: #4a6272;
  --dim: #6b8294;
  --cyan: #0891a8;
  --blue: #4361d8;
  --green: #1a9e6a;
  --amber: #c07a1a;
  --coral: #d44e72;
  --violet: #7c52d4;
}

:root[data-theme='dark'] {
  color-scheme: dark;
  --bg: #080e17;
  --sidebar: #0a111b;
  --panel: rgba(16, 26, 39, .86);
  --panel-2: #111d2a;
  --line: #253548;
  --text: #e8eef6;
  --muted: #91a1b4;
  --dim: #697b8f;
  --cyan: #52d5e4;
  --blue: #738aff;
  --green: #69d3a5;
  --amber: #f2b75e;
  --coral: #f17b98;
  --violet: #ab8cf5;
}

:root[data-theme='light'] {
  color-scheme: light;
  --bg: #f5f7fa;
  --sidebar: #ffffff;
  --panel: rgba(255, 255, 255, 0.95);
  --panel-2: #f0f4f8;
  --line: #dde4ec;
  --text: #182a38;
  --muted: #4a6272;
  --dim: #6b8294;
  --cyan: #0891a8;
  --blue: #4361d8;
  --green: #1a9e6a;
  --amber: #c07a1a;
  --coral: #d44e72;
  --violet: #7c52d4;
}"""

new_root = """:root {
  color-scheme: dark;
  font-family: 'DM Sans', sans-serif;
  color: #e8eef6;
  background: #080e17;
  font-synthesis: none;
  --bg: #080e17;
  --sidebar: #0a111b;
  --panel: rgba(16, 26, 39, .86);
  --panel-2: #111d2a;
  --line: #253548;
  --text: #e8eef6;
  --muted: #91a1b4;
  --dim: #697b8f;
  --cyan: #52d5e4;
  --blue: #738aff;
  --green: #69d3a5;
  --amber: #f2b75e;
  --coral: #f17b98;
  --violet: #ab8cf5;
}

:root[data-theme='light'] {
  color-scheme: light;
  --bg: #eef3f6;
  --sidebar: #f8fafb;
  --panel: rgba(255, 255, 255, .9);
  --panel-2: #f3f7f9;
  --line: #d7e0e7;
  --text: #182a38;
  --muted: #576b7c;
  --dim: #718393;
}"""

if old_root in css:
    css = css.replace(old_root, new_root)
    print("Restored :root to dark theme")
else:
    print("WARNING: root block not found exactly, trying partial match...")
    # Find and replace just the :root block
    import re
    # Replace from :root { to the end of the last :root[data-theme='light'] block
    pattern = r':root \{[^}]+color-scheme: light[^}]+\}.*?:root\[data-theme=\'light\'\] \{[^}]+\}'
    match = re.search(pattern, css, re.DOTALL)
    if match:
        css = css[:match.start()] + new_root + css[match.end():]
        print("Restored via regex")
    else:
        print("ERROR: Could not find root block to restore")

# 2. Restore shell background
css = css.replace(
    ".shell { min-height: 100vh; background: var(--bg); }",
    ".shell { min-height: 100vh; background: radial-gradient(ellipse at 83% 0%, rgba(41, 96, 119, .11), transparent 29%), var(--bg); }"
)

# 3. Restore sidebar
css = css.replace(
    ".sidebar { position: fixed; z-index: 20; inset: 0 auto 0 0; width: 250px; display: flex; flex-direction: column; background: #ffffff; border-right: 1px solid var(--line); padding: 22px 13px 13px; box-shadow: 2px 0 12px rgba(0,0,0,0.06); }",
    ".sidebar { position: fixed; z-index: 20; inset: 0 auto 0 0; width: 250px; display: flex; flex-direction: column; background: var(--sidebar); border-right: 1px solid var(--line); padding: 22px 13px 13px; }"
)

# 4. Restore brand icon
css = css.replace(
    ".brand-icon { width: 37px; height: 37px; display: grid; place-items: center; color: #fff; background: linear-gradient(140deg, #0891a8, #4361d8); border-radius: 11px; box-shadow: 0 4px 14px rgba(8,145,168,0.25); }",
    ".brand-icon { width: 37px; height: 37px; display: grid; place-items: center; color: #07141b; background: linear-gradient(140deg, #65e1e4, #4f9eff); border-radius: 11px; box-shadow: 0 7px 24px #52d5e430; }"
)

# 5. Restore brand text
css = css.replace(
    ".brand b { display: block; font: 700 16px 'Space Grotesk', sans-serif; white-space: nowrap; color: #182a38; }",
    ".brand b { display: block; font: 700 16px 'Space Grotesk', sans-serif; white-space: nowrap; }"
)
css = css.replace(
    ".brand small { display: block; margin-top: 3px; color: #6b8294; font-size: 9px; letter-spacing: 1.2px; }",
    ".brand small { display: block; margin-top: 3px; color: var(--dim); font-size: 9px; letter-spacing: 1.2px; }"
)
css = css.replace(
    ".workspace-caption { display: flex; justify-content: space-between; align-items: center; color: #9bb0bc; font-size: 9px; letter-spacing: 1.25px; padding: 0 10px 11px; }",
    ".workspace-caption { display: flex; justify-content: space-between; align-items: center; color: var(--dim); font-size: 9px; letter-spacing: 1.25px; padding: 0 10px 11px; }"
)

# 6. Restore nav items
css = css.replace(
    ".nav-item { border: 0; width: 100%; min-height: 38px; padding: 0 10px; border-radius: 7px; display: flex; align-items: center; gap: 11px; text-align: left; color: #5a7285; background: transparent; cursor: pointer; font-size: 12px; transition: color .16s ease, background .16s ease; }",
    ".nav-item { border: 0; width: 100%; min-height: 38px; padding: 0 10px; border-radius: 6px; display: flex; align-items: center; gap: 11px; text-align: left; color: #97a7b9; background: transparent; cursor: pointer; font-size: 12px; transition: color .16s ease, background .16s ease, transform .16s ease; }"
)
css = css.replace(
    ".nav-item:hover { color: #182a38; background: #f0f4f8; }",
    ".nav-item:hover { color: var(--text); background: #172535; transform: translateX(2px); }"
)
css = css.replace(
    ".nav-item.active { background: #e8f4f8; color: #0891a8; font-weight: 600; border-left: 3px solid #0891a8; }",
    ".nav-item.active { background: linear-gradient(100deg, #17313d, #19263c); color: #8de9ef; box-shadow: inset 2px 0 #59dbe5; }"
)

# 7. Restore connection box
css = css.replace(
    ".connection { border: 1px solid var(--line); border-radius: 7px; padding: 10px 8px; display: flex; align-items: center; gap: 9px; background: #f8fbfc; }",
    ".connection { border: 1px solid var(--line); border-radius: 7px; padding: 10px 8px; display: flex; align-items: center; gap: 9px; }"
)
css = css.replace(
    ".connection b, .analyst b { font-size: 10px; font-weight: 600; color: #182a38; }",
    ".connection b, .analyst b { font-size: 10px; font-weight: 600; }"
)

# 8. Restore pulse
css = css.replace(
    ".pulse { display: inline-block; width: 7px; height: 7px; flex: 0 0 auto; border-radius: 50%; background: #1a9e6a; box-shadow: 0 0 8px rgba(26,158,106,0.4); }",
    ".pulse { display: inline-block; width: 7px; height: 7px; flex: 0 0 auto; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px #69d3a566; }"
)
css = css.replace(
    ".pulse.offline { background: #c07a1a; box-shadow: 0 0 8px rgba(192,122,26,0.4); }",
    ".pulse.offline { background: var(--amber); box-shadow: 0 0 10px #f2b75e66; }"
)

# 9. Restore avatar
css = css.replace(
    ".avatar { width: 28px; height: 28px; display: inline-grid; place-items: center; border-radius: 50%; color: #fff; background: linear-gradient(140deg, #0891a8, #4361d8); font-size: 9px; font-weight: 700; flex: 0 0 auto; }",
    ".avatar { width: 28px; height: 28px; display: inline-grid; place-items: center; border-radius: 50%; color: #101522; background: linear-gradient(140deg, #f5c77e, #ec869e); font-size: 9px; font-weight: 700; flex: 0 0 auto; }"
)

# 10. Restore topbar
css = css.replace(
    ".topbar { height: 60px; position: sticky; top: 0; z-index: 10; display: flex; justify-content: space-between; align-items: center; padding: 0 28px; border-bottom: 1px solid var(--line); background: rgba(255,255,255,0.95); backdrop-filter: blur(12px); box-shadow: 0 1px 8px rgba(0,0,0,0.05); }",
    ".topbar { height: 65px; position: sticky; top: 0; z-index: 10; display: flex; justify-content: space-between; align-items: center; padding: 0 33px; border-bottom: 1px solid var(--line); background: color-mix(in srgb, var(--bg) 91%, transparent); backdrop-filter: blur(15px); }"
)
css = css.replace(
    ".crumb, .top-actions { display: flex; align-items: center; gap: 10px; color: #6b8294; font-size: 12px; font-weight: 600; }",
    ".crumb, .top-actions { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: 11px; }"
)
css = css.replace(
    ".crumb b { color: #182a38; }",
    ".crumb b { color: var(--text); font-weight: 600; }"
)
css = css.replace(
    ".top-actions { gap: 14px; }",
    ".top-actions { gap: 15px; }"
)
css = css.replace(
    ".search { height: 33px; width: 220px; display: flex; align-items: center; gap: 8px; padding: 0 9px; border: 1px solid var(--line); background: #f5f7fa; border-radius: 6px; color: #6b8294; }",
    ".search { height: 33px; width: 230px; display: flex; align-items: center; gap: 8px; padding: 0 9px; border: 1px solid var(--line); background: var(--panel); border-radius: 5px; color: var(--muted); }"
)
css = css.replace(
    ".search input { width: 100%; border: 0; outline: 0; color: #182a38; background: transparent; font-size: 11px; }",
    ".search input { width: 100%; border: 0; outline: 0; color: var(--text); background: transparent; font-size: 11px; }"
)
css = css.replace(
    ".system-badge { display: flex; align-items: center; gap: 7px; color: #6b8294; font-size: 10px; white-space: nowrap; }",
    ".system-badge { display: flex; align-items: center; gap: 7px; color: var(--muted); font-size: 10px; white-space: nowrap; }"
)

# 11. Restore page heading h1
css = css.replace(
    ".page-heading h1 { font: 600 24px 'Space Grotesk', sans-serif; letter-spacing: 0; margin: 7px 0 5px; color: #182a38; }",
    ".page-heading h1 { font: 600 25px 'Space Grotesk', sans-serif; letter-spacing: 0; margin: 7px 0 5px; }"
)

# 12. Restore buttons
css = css.replace(
    ".button { min-height: 34px; border: 1px solid transparent; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; gap: 7px; padding: 0 14px; font-size: 11px; font-weight: 600; cursor: pointer; transition: transform .15s ease, filter .15s ease, box-shadow .15s ease; }",
    ".button { min-height: 34px; border: 1px solid transparent; border-radius: 5px; display: inline-flex; align-items: center; justify-content: center; gap: 7px; padding: 0 12px; font-size: 11px; font-weight: 600; cursor: pointer; transition: transform .15s ease, filter .15s ease, border-color .15s ease; }"
)
css = css.replace(
    ".button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }",
    ".button:hover { transform: translateY(-1px); filter: brightness(1.08); }"
)
css = css.replace(
    ".button.primary { color: #fff; background: linear-gradient(100deg, #0891a8, #4361d8); border-color: transparent; }",
    ".button.primary { color: #07141a; background: linear-gradient(100deg, #65dfe6, #72b6ff); box-shadow: 0 4px 14px #52d5e422; }"
)
css = css.replace(
    ".button.secondary { border-color: var(--line); color: #182a38; background: #fff; }",
    ".button.secondary { border-color: var(--line); color: var(--text); background: var(--panel); }"
)
css = css.replace(
    ".button.secondary:hover { background: #f0f4f8; }",
    ""
)

# 13. Restore icon-btn
css = css.replace(
    ".icon-btn { width: 30px; height: 30px; border: 0; border-radius: 6px; display: inline-grid; place-items: center; color: #6b8294; background: transparent; cursor: pointer; }",
    ".icon-btn { width: 29px; height: 29px; border: 0; border-radius: 5px; display: inline-grid; place-items: center; color: var(--muted); background: transparent; cursor: pointer; }"
)
css = css.replace(
    ".icon-btn:hover { color: #182a38; background: #f0f4f8; }",
    ".icon-btn:hover { color: var(--text); background: var(--panel-2); }"
)

# 14. Restore notice
css = css.replace(
    ".notice { min-height: 44px; border: 1px solid #e8c87a; border-left: 3px solid #c07a1a; border-radius: 6px; background: #fffbf0; padding: 10px 12px; display: flex; align-items: center; gap: 10px; color: #7a5018; font-size: 11px; line-height: 1.5; margin-bottom: 17px; }",
    ".notice { min-height: 44px; border: 1px solid #745d35; border-left: 3px solid var(--amber); border-radius: 5px; background: #28231770; padding: 10px 12px; display: flex; align-items: center; gap: 10px; color: #d9c69f; font-size: 11px; line-height: 1.5; margin-bottom: 17px; }"
)
css = css.replace(
    ".notice svg { color: #c07a1a; flex: 0 0 auto; }",
    ".notice svg { color: var(--amber); flex: 0 0 auto; }"
)

# 15. Restore stat cards
css = css.replace(
    ".stat { min-width: 0; padding: 16px 18px 14px; border: 1px solid var(--line); border-radius: 10px; background: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: transform .18s ease, box-shadow .18s ease; }",
    ".stat { min-width: 0; padding: 15px 16px 13px; border: 1px solid var(--line); border-radius: 7px; background: linear-gradient(145deg, color-mix(in srgb, var(--panel) 98%, white), var(--panel)); box-shadow: 0 10px 30px #0000000b; transition: transform .18s ease, border-color .18s ease; }"
)
css = css.replace(
    ".stat:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.10); }",
    ".stat:hover { transform: translateY(-2px); border-color: #456177; }"
)
css = css.replace(
    ".stat > div:first-child { display: flex; justify-content: space-between; align-items: center; color: #6b8294; font-size: 10px; }",
    ".stat > div:first-child { display: flex; justify-content: space-between; align-items: center; color: var(--muted); font-size: 10px; }"
)
css = css.replace(
    ".stat-icon.cyan { color: #0891a8; background: #e5f6f9; }",
    ".stat-icon.cyan { color: var(--cyan); background: #52d5e41b; }"
)
css = css.replace(
    ".stat-icon.violet { color: #7c52d4; background: #ede8f8; }",
    ".stat-icon.violet { color: var(--violet); background: #ab8cf51b; }"
)
css = css.replace(
    ".stat-icon.coral { color: #d44e72; background: #fdeef2; }",
    ".stat-icon.coral { color: var(--coral); background: #f17b981a; }"
)
css = css.replace(
    ".stat-icon.blue { color: #4361d8; background: #eaedfc; }",
    ".stat-icon.blue { color: var(--blue); background: #738aff1b; }"
)
css = css.replace(
    ".stat-icon.amber { color: #c07a1a; background: #fdf3e3; }",
    ".stat-icon.amber { color: var(--amber); background: #f2b75e1b; }"
)
css = css.replace(
    ".stat-icon.green { color: #1a9e6a; background: #e4f7ef; }",
    ".stat-icon.green { color: var(--green); background: #69d3a51b; }"
)
css = css.replace(
    ".stat > strong { display: block; margin: 10px 0 5px; font: 600 24px 'Space Grotesk', sans-serif; color: #182a38; }",
    ".stat > strong { display: block; margin: 9px 0 5px; font: 600 24px 'Space Grotesk', sans-serif; }"
)
css = css.replace(
    ".stat > small { color: #6b8294; font-size: 9px; }",
    ".stat > small { color: var(--dim); font-size: 9px; }"
)

# 16. Restore panel
css = css.replace(
    ".panel { min-width: 0; border: 1px solid var(--line); border-radius: 10px; padding: 18px; background: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }",
    ".panel { min-width: 0; border: 1px solid var(--line); border-radius: 7px; padding: 16px; background: linear-gradient(145deg, var(--panel), color-mix(in srgb, var(--panel) 94%, #173345)); box-shadow: 0 10px 30px #00000010; }"
)

# 17. Restore panel title h2
css = css.replace(
    ".panel-title h2 { margin: 0; font: 600 13px 'Space Grotesk', sans-serif; color: #182a38; }",
    ".panel-title h2 { margin: 0; font: 600 13px 'Space Grotesk', sans-serif; }"
)

# 18. Restore text-btn
css = css.replace(
    ".text-btn { display: inline-flex; align-items: center; gap: 5px; padding: 3px 0; border: 0; color: var(--cyan); background: transparent; font-size: 10px; cursor: pointer; font-weight: 600; }",
    ".text-btn { display: inline-flex; align-items: center; gap: 5px; padding: 3px 0; border: 0; color: var(--cyan); background: transparent; font-size: 10px; cursor: pointer; }"
)

# 19. Restore table
css = css.replace(
    ".table-wrap th { padding: 9px 8px; color: #6b8294; border-bottom: 2px solid var(--line); font-size: 8px; font-weight: 700; letter-spacing: .4px; text-transform: uppercase; background: #f8fbfc; }",
    ".table-wrap th { padding: 9px 8px; color: var(--dim); border-bottom: 1px solid var(--line); font-size: 8px; font-weight: 600; letter-spacing: .4px; text-transform: uppercase; }"
)
css = css.replace(
    ".table-wrap td { padding: 10px 8px; border-bottom: 1px solid var(--line); color: #4a6272; font-size: 9px; }",
    ".table-wrap td { padding: 10px 8px; border-bottom: 1px solid color-mix(in srgb, var(--line) 72%, transparent); color: var(--muted); font-size: 9px; }"
)
css = css.replace(
    ".table-wrap tbody tr:hover { background: #f5f9fb; }",
    ".table-wrap tbody tr:hover { background: #ffffff04; }"
)
css = css.replace(
    ".table-wrap .mono { font-family: 'Space Grotesk', sans-serif; color: #0891a8; }",
    ".table-wrap .mono { font-family: 'Space Grotesk', sans-serif; color: #b0c1d1; }"
)

# 20. Restore tags
css = css.replace(
    """.tag { width: fit-content; display: inline-flex; align-items: center; padding: 4px 8px; border-radius: 5px; color: #4a6272; background: #f0f4f8; font-size: 8px; font-weight: 700; letter-spacing: .3px; white-space: nowrap; border: 1px solid #dde4ec; }
.tag.cyan { color: #0891a8; background: #e5f6f9; border-color: #b8e5ed; }
.tag.green { color: #1a7a52; background: #e4f7ef; border-color: #b0e0cc; }
.tag.high, .tag.critical { color: #b03060; background: #fdeef2; border-color: #f4b8cc; }
.tag.medium { color: #a06010; background: #fdf3e3; border-color: #f0d090; }
.tag.low { color: #1a7a52; background: #e4f7ef; border-color: #b0e0cc; }
.tag.amber { color: #a06010; background: #fdf3e3; border-color: #f0d090; }
.tag.neutral { color: #4a6272; background: #f0f4f8; border-color: #dde4ec; }""",
    """.tag { width: fit-content; display: inline-flex; align-items: center; padding: 4px 7px; border-radius: 4px; color: #b4c1ce; background: #8b9bab19; font-size: 8px; font-weight: 700; letter-spacing: .3px; white-space: nowrap; }.tag.cyan { color: #80e3eb; background: #52d5e41c; }.tag.green { color: #7de1b6; background: #69d3a51b; }.tag.high, .tag.critical { color: #ff97ac; background: #f17b981c; }.tag.medium { color: #f2c373; background: #f2b75e1c; }.tag.low { color: #81dcb3; background: #69d3a51b; }"""
)

# 21. Restore form inputs
css = css.replace(
    ".form input, .form select, .form textarea, .chat-form textarea { width: 100%; border: 1px solid var(--line); border-radius: 6px; padding: 9px 10px; color: #182a38; background: #ffffff; outline: none; font-size: 10px; resize: vertical; }",
    ".form input, .form select, .form textarea, .chat-form textarea { width: 100%; border: 1px solid var(--line); border-radius: 5px; padding: 9px 10px; color: var(--text); background: var(--bg); outline: none; font-size: 10px; resize: vertical; }"
)
css = css.replace(
    ".form input:focus, .form select:focus, .form textarea:focus, .chat-form textarea:focus { border-color: #0891a8; box-shadow: 0 0 0 2px rgba(8,145,168,0.1); }",
    ".form input:focus, .form select:focus, .form textarea:focus, .chat-form textarea:focus { border-color: var(--cyan); }"
)
css = css.replace(
    ".hint { color: #6b8294; font-size: 9px; line-height: 1.5; }",
    ".hint { color: var(--dim); font-size: 9px; line-height: 1.5; }"
)

# 22. Restore form label
css = css.replace(
    ".form label { display: grid; gap: 6px; color: #182a38; font-size: 10px; font-weight: 600; }",
    ".form label { display: grid; gap: 6px; color: var(--text); font-size: 10px; font-weight: 600; }"
)

# 23. Restore logout
css = css.replace(
    ".logout-link { width: 100%; min-height: 31px; margin-top: 7px; padding: 0 8px; display: flex; align-items: center; gap: 8px; border: 0; border-top: 1px solid var(--line); color: #6b8294; background: transparent; text-align: left; font-size: 10px; cursor: pointer; }.logout-link:hover { color: #d44e72; }",
    ".logout-link { width: 100%; min-height: 31px; margin-top: 7px; padding: 0 8px; display: flex; align-items: center; gap: 8px; border: 0; border-top: 1px solid var(--line); color: var(--muted); background: transparent; text-align: left; font-size: 10px; cursor: pointer; }.logout-link:hover { color: var(--coral); }"
)
css = css.replace(
    ".top-user { display: inline-flex; align-items: center; gap: 7px; padding: 0; border: 0; color: #182a38; background: transparent; cursor: pointer; font-size: 9px; font-weight: 600; }",
    ".top-user { display: inline-flex; align-items: center; gap: 7px; padding: 0; border: 0; color: var(--text); background: transparent; cursor: pointer; font-size: 9px; }"
)

# 24. Restore toast
css = css.replace(
    ".toast { position: fixed; z-index: 40; right: 24px; bottom: 22px; max-width: min(480px, calc(100vw - 32px)); min-height: 44px; display: flex; align-items: center; gap: 9px; padding: 10px 14px; border: 1px solid #b8e5ed; border-radius: 8px; color: #182a38; background: #ffffff; box-shadow: 0 8px 30px rgba(0,0,0,0.12); font-size: 11px; animation: rise .2s ease-out; }.toast > svg { color: #1a9e6a; flex: 0 0 auto; }.toast button { display: grid; place-items: center; margin-left: auto; border: 0; color: #6b8294; background: transparent; cursor: pointer; }",
    ".toast { position: fixed; z-index: 40; right: 24px; bottom: 22px; max-width: min(480px, calc(100vw - 32px)); min-height: 44px; display: flex; align-items: center; gap: 9px; padding: 10px 12px; border: 1px solid #3e586a; border-radius: 6px; color: var(--text); background: #142433; box-shadow: 0 10px 35px #0008; font-size: 10px; animation: rise .2s ease-out; }.toast > svg { color: var(--green); flex: 0 0 auto; }.toast button { display: grid; place-items: center; margin-left: auto; border: 0; color: var(--muted); background: transparent; cursor: pointer; }"
)

# 25. Restore modal
css = css.replace(
    ".modal-scrim, .scrim { position: fixed; z-index: 30; inset: 0; border: 0; background: rgba(0,0,0,0.4); }.modal-scrim { display: grid; place-items: center; padding: 16px; }.modal { width: min(560px, 100%); padding: 24px; border: 1px solid var(--line); border-radius: 12px; background: #ffffff; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }",
    ".modal-scrim, .scrim { position: fixed; z-index: 30; inset: 0; border: 0; background: #02050bbd; }.modal-scrim { display: grid; place-items: center; padding: 16px; }.modal { width: min(560px, 100%); padding: 20px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel-2); box-shadow: 0 22px 70px #0009; }"
)
css = css.replace(
    ".modal-title h2 { margin: 5px 0 0; font: 600 18px 'Space Grotesk', sans-serif; color: #182a38; }",
    ".modal-title h2 { margin: 5px 0 0; font: 600 18px 'Space Grotesk', sans-serif; }"
)
css = css.replace(
    ".modal-fields > span { display: grid; gap: 5px; color: #6b8294; font-size: 9px; }",
    ".modal-fields > span { display: grid; gap: 5px; color: var(--dim); font-size: 9px; }"
)
css = css.replace(
    ".modal-fields b { color: #182a38; font-size: 10px; }",
    ".modal-fields b { color: var(--text); font-size: 10px; }"
)
css = css.replace(
    ".modal-description { padding: 12px; border-radius: 6px; color: #4a6272; background: #f5f7fa; border: 1px solid var(--line); font-size: 10px; line-height: 1.6; }",
    ".modal-description { padding: 12px; border-radius: 5px; color: var(--muted); background: var(--bg); font-size: 10px; line-height: 1.6; }"
)

# 26. Restore empty
css = css.replace(
    ".empty { min-height: 155px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; color: #6b8294; text-align: center; }.empty svg { color: #9bb0bc; }.empty b { color: #4a6272; font-size: 11px; }.empty span { max-width: 290px; font-size: 10px; line-height: 1.5; }",
    ".empty { min-height: 155px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; color: var(--dim); text-align: center; }.empty svg { color: #586a7d; }.empty b { color: var(--muted); font-size: 11px; }.empty span { max-width: 290px; font-size: 10px; line-height: 1.5; }"
)

# 27. Restore no-results
css = css.replace(
    ".no-results { padding: 12px; border-radius: 6px; color: #6b8294; background: #f5f7fa; border: 1px solid var(--line); font-size: 10px; }",
    ".no-results { padding: 12px; border-radius: 5px; color: var(--dim); background: var(--panel-2); font-size: 10px; }"
)

# 28. Restore profile form
css = css.replace(
    ".profile-form input { min-height: 35px; padding: 0 9px; border: 1px solid var(--line); border-radius: 6px; color: #182a38; background: #ffffff; font-size: 10px; }",
    ".profile-form input { min-height: 35px; padding: 0 9px; border: 1px solid var(--line); border-radius: 4px; color: var(--text); background: var(--bg); font-size: 10px; }"
)

# 29. Restore chatbot
css = css.replace(
    ".chatbot-panel { width: 340px; max-height: 480px; display: flex; flex-direction: column; border-radius: 14px; border: 1px solid var(--line); background: #ffffff; box-shadow: 0 12px 40px rgba(0,0,0,0.15); overflow: hidden; }",
    ".chatbot-panel { width: 340px; max-height: 480px; display: flex; flex-direction: column; border-radius: 14px; border: 1px solid var(--line); background: var(--panel-2); box-shadow: 0 20px 60px rgba(0,0,0,0.4); overflow: hidden; }"
)
css = css.replace(
    ".chatbot-header { display: flex; align-items: center; gap: 8px; padding: 12px 14px; border-bottom: 1px solid var(--line); background: #f5f7fa; }",
    ".chatbot-header { display: flex; align-items: center; gap: 8px; padding: 12px 14px; border-bottom: 1px solid var(--line); background: var(--sidebar); }"
)
css = css.replace(
    ".chatbot-header b { flex: 1; font-size: 12px; color: #182a38; }",
    ".chatbot-header b { flex: 1; font-size: 12px; color: var(--text); }"
)
css = css.replace(
    ".chatbot-messages { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px; scrollbar-width: thin; background: #fafcfd; }",
    ".chatbot-messages { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px; scrollbar-width: thin; }"
)
css = css.replace(
    ".chat-bubble.user { align-self: flex-end; background: #e5f6f9; border: 1px solid #b8e5ed; color: #182a38; }",
    ".chat-bubble.user { align-self: flex-end; background: rgba(82,213,228,0.15); border: 1px solid rgba(82,213,228,0.25); color: var(--text); }"
)
css = css.replace(
    ".chat-bubble.bot { align-self: flex-start; background: #ffffff; border: 1px solid var(--line); color: #4a6272; }",
    ".chat-bubble.bot { align-self: flex-start; background: var(--panel); border: 1px solid var(--line); color: var(--muted); }"
)
css = css.replace(
    ".chat-bubble small { display: block; margin-top: 5px; color: #6b8294; font-size: 8px; }",
    ".chat-bubble small { display: block; margin-top: 5px; color: var(--dim); font-size: 8px; }"
)
css = css.replace(
    ".chatbot-input { display: flex; gap: 6px; padding: 10px; border-top: 1px solid var(--line); background: #f5f7fa; }",
    ".chatbot-input { display: flex; gap: 6px; padding: 10px; border-top: 1px solid var(--line); background: var(--sidebar); }"
)
css = css.replace(
    ".chatbot-input input { flex: 1; border: 1px solid var(--line); border-radius: 6px; padding: 7px 10px; background: #ffffff; color: #182a38; font-size: 11px; outline: none; }",
    ".chatbot-input input { flex: 1; border: 1px solid var(--line); border-radius: 6px; padding: 7px 10px; background: var(--bg); color: var(--text); font-size: 11px; outline: none; }"
)
css = css.replace(
    ".chatbot-input input:focus { border-color: #0891a8; }",
    ".chatbot-input input:focus { border-color: var(--cyan); }"
)
css = css.replace(
    ".chatbot-input button { width: 32px; height: 32px; border-radius: 7px; background: #0891a8; color: #fff; display: grid; place-items: center; border: none; cursor: pointer; flex-shrink: 0; }",
    ".chatbot-input button { width: 32px; height: 32px; border-radius: 7px; background: var(--cyan); color: #04111e; display: grid; place-items: center; border: none; cursor: pointer; flex-shrink: 0; }"
)

# 30. Restore safety modal
css = css.replace(
    ".safety-modal-backdrop { position: fixed; z-index: 50; inset: 0; overflow: auto; padding: 18px; display: grid; place-items: center; background: rgba(0,0,0,0.45); }",
    ".safety-modal-backdrop { position: fixed; z-index: 50; inset: 0; overflow: auto; padding: 18px; display: grid; place-items: center; background: #030810c9; }"
)
css = css.replace(
    ".safety-modal { width: min(480px, 100%); max-height: min(90vh, 780px); overflow: auto; padding: 20px; border: 1px solid var(--line); border-radius: 12px; background: #ffffff; box-shadow: 0 16px 50px rgba(0,0,0,0.15); }",
    ".safety-modal { width: min(480px, 100%); max-height: min(90vh, 780px); overflow: auto; padding: 19px; border: 1px solid var(--line); border-radius: 8px; background: #111d2a; box-shadow: 0 20px 60px #0009; }"
)
css = css.replace(
    ".safety-modal-head > span { color: #d44e72; }",
    ".safety-modal-head > span { color: #e18b8f; }"
)

# 31. Restore contact form input
css = css.replace(
    ".contact-form input { min-height: 33px; padding: 0 8px; border: 1px solid var(--line); border-radius: 4px; color: #182a38; background: #ffffff; font-size: 9px; }",
    ".contact-form input { min-height: 33px; padding: 0 8px; border: 1px solid var(--line); border-radius: 4px; color: var(--text); background: #0a111b; font-size: 9px; }"
)

# 32. Restore setting input select
css = css.replace(
    ".setting-input select { min-height: 30px; max-width: 160px; padding: 0 8px; border: 1px solid var(--line); border-radius: 4px; color: #182a38; background: #ffffff; font-size: 9px; }",
    ".setting-input select { min-height: 30px; max-width: 160px; padding: 0 8px; border: 1px solid var(--line); border-radius: 4px; color: var(--text); background: #0a111b; font-size: 9px; }"
)

# 33. Restore table select
css = css.replace(
    ".table-wrap select { max-width: 105px; padding: 5px 7px; border: 1px solid var(--line); border-radius: 4px; color: #182a38; background: #ffffff; font-size: 9px; }",
    ".table-wrap select { max-width: 105px; padding: 5px 7px; border: 1px solid var(--line); border-radius: 4px; color: var(--text); background: var(--panel-2); font-size: 9px; }"
)

# 34. Restore history controls select
css = css.replace(
    ".history-controls select { border: 1px solid var(--line); border-radius: 5px; padding: 0 8px; color: #182a38; background: #ffffff; font-size: 9px; }",
    ".history-controls select { border: 1px solid var(--line); border-radius: 5px; padding: 0 8px; color: var(--text); background: var(--bg); font-size: 9px; }"
)

# 35. Restore admin health
css = css.replace(
    ".admin-health span { display: inline-flex; align-items: center; gap: 7px; color: #4a6272; }",
    ".admin-health span { display: inline-flex; align-items: center; gap: 7px; }"
)

# 36. Restore setting toggle
css = css.replace(
    ".setting-toggle { width: 34px; height: 19px; border: 1px solid var(--line); border-radius: 12px; padding: 2px; background: #dde4ec; cursor: pointer; transition: background .15s ease; }",
    ".setting-toggle { width: 34px; height: 19px; border: 1px solid var(--line); border-radius: 12px; padding: 2px; background: #1a2836; cursor: pointer; transition: background .15s ease; }"
)
css = css.replace(
    ".setting-toggle i { display: block; width: 13px; height: 13px; border-radius: 50%; background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.2); transition: transform .15s ease, background .15s ease; }",
    ".setting-toggle i { display: block; width: 13px; height: 13px; border-radius: 50%; background: #96a7b8; transition: transform .15s ease, background .15s ease; }"
)
css = css.replace(
    ".setting-toggle.on { background: #0891a8; border-color: #0891a8; }",
    ".setting-toggle.on { background: #18636a; border-color: #328994; }"
)
css = css.replace(
    ".setting-toggle.on i { transform: translateX(14px); background: #ffffff; }",
    ".setting-toggle.on i { transform: translateX(14px); background: #a4f0ef; }"
)

# 37. Restore safety hero
css = css.replace(
    ".safety-hero { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(210px, .8fr); gap: 22px; align-items: center; padding: 21px; border: 1px solid #f4b8cc; border-left: 4px solid #d44e72; border-radius: 10px; background: linear-gradient(110deg, #fff5f8, #ffffff); box-shadow: 0 2px 12px rgba(212,78,114,0.08); }",
    ".safety-hero { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(210px, .8fr); gap: 22px; align-items: center; padding: 21px; border: 1px solid #594044; border-left: 4px solid #b5444b; border-radius: 7px; background: linear-gradient(110deg, #211c23, color-mix(in srgb, var(--panel) 90%, #471f27)); }"
)
css = css.replace(
    ".safety-hero-copy > span { color: #d44e72;",
    ".safety-hero-copy > span { color: #e09ba0;"
)
css = css.replace(
    ".safety-hero p { max-width: 450px; margin: 0 0 14px; color: #4a6272;",
    ".safety-hero p { max-width: 450px; margin: 0 0 14px; color: var(--muted);"
)
css = css.replace(
    ".safety-hero-copy > small { display: block; margin-top: 8px; color: #8a7a80;",
    ".safety-hero-copy > small { display: block; margin-top: 8px; color: #b8a6a8;"
)

# 38. Restore emergency button
css = css.replace(
    ".emergency-button { min-height: 52px; width: min(100%, 360px); border: none; border-radius: 10px; padding: 0 18px; display: inline-flex; align-items: center; justify-content: center; gap: 10px; color: #fff; background: linear-gradient(135deg, #e53e6a, #c02050);",
    ".emergency-button { min-height: 48px; width: min(100%, 360px); border: 1px solid #d77a7d; border-radius: 5px; padding: 0 18px; display: inline-flex; align-items: center; justify-content: center; gap: 10px; color: #fff; background: #a6323a;"
)
css = css.replace(
    ".emergency-button:hover { background: linear-gradient(135deg, #c02050, #a01840);",
    ".emergency-button:hover { background: #922931;"
)

# 39. Restore safety actions
css = css.replace(
    ".safety-action { min-height: 66px; padding: 11px; display: flex; align-items: flex-start; gap: 10px; border: 1px solid var(--line); border-radius: 8px; color: #182a38; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.05);",
    ".safety-action { min-height: 66px; padding: 11px; display: flex; align-items: flex-start; gap: 10px; border: 1px solid var(--line); border-radius: 6px; color: var(--text); background: var(--panel);"
)
css = css.replace(
    ".safety-action:hover:not(:disabled) { border-color: #0891a8; background: #f5fbfc; }",
    ".safety-action:hover:not(:disabled) { border-color: #587084; background: var(--panel-2); }"
)

# 40. Restore safety panel
css = css.replace(
    ".safety-panel { min-width: 0; padding: 16px; border: 1px solid var(--line); border-radius: 10px; background: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }",
    ".safety-panel { min-width: 0; padding: 14px; border: 1px solid var(--line); border-radius: 6px; background: var(--panel); }"
)

# 41. Restore safety status box
css = css.replace(
    ".safety-status-box { min-height: 84px; padding: 14px; display: flex; align-items: center; gap: 11px; border: 1px solid var(--line); border-radius: 8px; background: #f8fbfc; }",
    ".safety-status-box { min-height: 84px; padding: 13px; display: flex; align-items: center; gap: 11px; border: 1px solid var(--line); border-radius: 6px; background: #0b121b88; }"
)

# 42. Restore safety error
css = css.replace(
    ".safety-error { display: flex; align-items: center; gap: 8px; margin-bottom: 11px; padding: 9px 11px; border: 1px solid #f4b8cc; border-radius: 6px; color: #b03060; background: #fdeef2;",
    ".safety-error { display: flex; align-items: center; gap: 8px; margin-bottom: 11px; padding: 9px 11px; border: 1px solid #8b4947; border-radius: 5px; color: #f0c2c3; background: #432427;"
)

# 43. Restore safety result
css = css.replace(
    ".safety-result { display: flex; justify-content: space-between; align-items: center; gap: 15px; margin-top: 11px; padding: 14px; border: 1px solid #b8e5ed; border-radius: 8px; background: #f0fbfd; }",
    ".safety-result { display: flex; justify-content: space-between; align-items: center; gap: 15px; margin-top: 11px; padding: 14px; border: 1px solid #745d35; border-radius: 6px; background: #28231770; }"
)

# 44. Restore location readout
css = css.replace(
    ".location-readout { display: flex; align-items: center; gap: 9px; margin: 8px 1px 14px; padding: 10px 12px; border: 1px solid #b8e5ed; border-radius: 6px; color: #0891a8; background: #e5f6f9; }",
    ".location-readout { display: flex; align-items: center; gap: 9px; margin: 8px 1px 14px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 5px; color: var(--cyan); background: var(--panel); }"
)

# 45. Restore welcome callout
css = css.replace(
    ".welcome-callout { display: flex; align-items: flex-start; gap: 13px; padding: 14px 16px; margin-bottom: 14px; border: 1px solid #b8e5ed; border-left: 3px solid #0891a8; border-radius: 8px; background: #f0fbfd; }",
    ".welcome-callout { display: flex; align-items: flex-start; gap: 13px; padding: 14px 16px; margin-bottom: 14px; border: 1px solid #2e4a5c; border-left: 3px solid var(--cyan); border-radius: 6px; background: color-mix(in srgb, var(--panel) 90%, #0e2a3a); }"
)
css = css.replace(
    ".welcome-callout svg { color: #0891a8;",
    ".welcome-callout svg { color: var(--cyan);"
)

# 46. Restore alarm buttons
css = css.replace(
    ".alarm-start, .alarm-stop { min-height: 35px; margin-top: 11px; padding: 0 10px; display: inline-flex; align-items: center; gap: 7px; border: 1px solid #d4a820; border-radius: 6px; color: #7a5010; background: #fdf5d8;",
    ".alarm-start, .alarm-stop { min-height: 35px; margin-top: 11px; padding: 0 10px; display: inline-flex; align-items: center; gap: 7px; border: 1px solid #675b3d; border-radius: 4px; color: #f2d394; background: #332b1c;"
)
css = css.replace(
    ".alarm-stop { border-color: #d44e72; color: #fff; background: #e53e6a; }",
    ".alarm-stop { border-color: #d17e83; color: #fff; background: #a6323a; }"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(css)

print("Dark theme fully restored!")
