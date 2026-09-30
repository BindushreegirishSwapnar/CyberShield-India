"""Patch remaining dark-theme CSS in CyberShield.css to light."""
path = r"c:\Users\bindu\Downloads\CyberCrimePredict\CyberCrimePredict\frontend\src\CyberShield.css"
with open(path, encoding="utf-8") as f:
    css = f.read()

replacements = [
    # Safety modal
    ('.safety-modal-backdrop { position: fixed; z-index: 50; inset: 0; overflow: auto; padding: 18px; display: grid; place-items: center; background: #030810c9; }',
     '.safety-modal-backdrop { position: fixed; z-index: 50; inset: 0; overflow: auto; padding: 18px; display: grid; place-items: center; background: rgba(0,0,0,0.45); }'),
    ('.safety-modal { width: min(480px, 100%); max-height: min(90vh, 780px); overflow: auto; padding: 19px; border: 1px solid var(--line); border-radius: 8px; background: #111d2a; box-shadow: 0 20px 60px #0009; }',
     '.safety-modal { width: min(480px, 100%); max-height: min(90vh, 780px); overflow: auto; padding: 20px; border: 1px solid var(--line); border-radius: 12px; background: #ffffff; box-shadow: 0 16px 50px rgba(0,0,0,0.15); }'),
    # Safety modal head
    ('.safety-modal-head > span { color: #e18b8f; }',
     '.safety-modal-head > span { color: #d44e72; }'),
    # Contact form
    ('.contact-form input { min-height: 33px; padding: 0 8px; border: 1px solid var(--line); border-radius: 4px; color: var(--text); background: #0a111b; font-size: 9px; }',
     '.contact-form input { min-height: 33px; padding: 0 8px; border: 1px solid var(--line); border-radius: 4px; color: #182a38; background: #ffffff; font-size: 9px; }'),
    # Setting input
    ('.setting-input select { min-height: 30px; max-width: 160px; padding: 0 8px; border: 1px solid var(--line); border-radius: 4px; color: var(--text); background: #0a111b; font-size: 9px; }',
     '.setting-input select { min-height: 30px; max-width: 160px; padding: 0 8px; border: 1px solid var(--line); border-radius: 4px; color: #182a38; background: #ffffff; font-size: 9px; }'),
    # Table select
    ('.table-wrap select { max-width: 105px; padding: 5px 7px; border: 1px solid var(--line); border-radius: 4px; color: var(--text); background: var(--panel-2); font-size: 9px; }',
     '.table-wrap select { max-width: 105px; padding: 5px 7px; border: 1px solid var(--line); border-radius: 4px; color: #182a38; background: #ffffff; font-size: 9px; }'),
    # History controls select
    ('.history-controls select { border: 1px solid var(--line); border-radius: 5px; padding: 0 8px; color: var(--text); background: var(--bg); font-size: 9px; }',
     '.history-controls select { border: 1px solid var(--line); border-radius: 5px; padding: 0 8px; color: #182a38; background: #ffffff; font-size: 9px; }'),
    # Admin health
    ('.admin-health span { display: inline-flex; align-items: center; gap: 7px; }',
     '.admin-health span { display: inline-flex; align-items: center; gap: 7px; color: #4a6272; }'),
    # Empty
    ('.empty { min-height: 155px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; color: var(--dim); text-align: center; }.empty svg { color: #586a7d; }.empty b { color: var(--muted); font-size: 11px; }.empty span { max-width: 290px; font-size: 10px; line-height: 1.5; }',
     '.empty { min-height: 155px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; color: #6b8294; text-align: center; }.empty svg { color: #9bb0bc; }.empty b { color: #4a6272; font-size: 11px; }.empty span { max-width: 290px; font-size: 10px; line-height: 1.5; }'),
    # No-results
    ('.no-results { padding: 12px; border-radius: 5px; color: var(--dim); background: var(--panel-2); font-size: 10px; }',
     '.no-results { padding: 12px; border-radius: 6px; color: #6b8294; background: #f5f7fa; border: 1px solid var(--line); font-size: 10px; }'),
    # Profile form input
    ('.profile-form input { min-height: 35px; padding: 0 9px; border: 1px solid var(--line); border-radius: 4px; color: var(--text); background: var(--bg); font-size: 10px; }',
     '.profile-form input { min-height: 35px; padding: 0 9px; border: 1px solid var(--line); border-radius: 6px; color: #182a38; background: #ffffff; font-size: 10px; }'),
    # Setting toggle
    ('.setting-toggle { width: 34px; height: 19px; border: 1px solid var(--line); border-radius: 12px; padding: 2px; background: #1a2836; cursor: pointer; transition: background .15s ease; }',
     '.setting-toggle { width: 34px; height: 19px; border: 1px solid var(--line); border-radius: 12px; padding: 2px; background: #dde4ec; cursor: pointer; transition: background .15s ease; }'),
    ('.setting-toggle i { display: block; width: 13px; height: 13px; border-radius: 50%; background: #96a7b8; transition: transform .15s ease, background .15s ease; }',
     '.setting-toggle i { display: block; width: 13px; height: 13px; border-radius: 50%; background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.2); transition: transform .15s ease, background .15s ease; }'),
    ('.setting-toggle.on { background: #18636a; border-color: #328994; }',
     '.setting-toggle.on { background: #0891a8; border-color: #0891a8; }'),
    ('.setting-toggle.on i { transform: translateX(14px); background: #a4f0ef; }',
     '.setting-toggle.on i { transform: translateX(14px); background: #ffffff; }'),
    # Chart tooltip already has hardcoded dark bg - that's fine
    # Safety hero
    ('.safety-hero { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(210px, .8fr); gap: 22px; align-items: center; padding: 21px; border: 1px solid #594044; border-left: 4px solid #b5444b; border-radius: 7px; background: linear-gradient(110deg, #211c23, color-mix(in srgb, var(--panel) 90%, #471f27)); }',
     '.safety-hero { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(210px, .8fr); gap: 22px; align-items: center; padding: 21px; border: 1px solid #f4b8cc; border-left: 4px solid #d44e72; border-radius: 10px; background: linear-gradient(110deg, #fff5f8, #ffffff); box-shadow: 0 2px 12px rgba(212,78,114,0.08); }'),
    # Safety hero text colors
    ('.safety-hero-copy > span { color: #e09ba0;',
     '.safety-hero-copy > span { color: #d44e72;'),
    ('.safety-hero p { max-width: 450px; margin: 0 0 14px; color: var(--muted);',
     '.safety-hero p { max-width: 450px; margin: 0 0 14px; color: #4a6272;'),
    ('.safety-hero-copy > small { display: block; margin-top: 8px; color: #b8a6a8;',
     '.safety-hero-copy > small { display: block; margin-top: 8px; color: #8a7a80;'),
    # Safety actions
    ('.safety-action { min-height: 66px; padding: 11px; display: flex; align-items: flex-start; gap: 10px; border: 1px solid var(--line); border-radius: 6px; color: var(--text); background: var(--panel);',
     '.safety-action { min-height: 66px; padding: 11px; display: flex; align-items: flex-start; gap: 10px; border: 1px solid var(--line); border-radius: 8px; color: #182a38; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.05);'),
    ('.safety-action:hover:not(:disabled) { border-color: #587084; background: var(--panel-2); }',
     '.safety-action:hover:not(:disabled) { border-color: #0891a8; background: #f5fbfc; }'),
    # Safety panels
    ('.safety-panel { min-width: 0; padding: 14px; border: 1px solid var(--line); border-radius: 6px; background: var(--panel); }',
     '.safety-panel { min-width: 0; padding: 16px; border: 1px solid var(--line); border-radius: 10px; background: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }'),
    # Emergency button
    ('.emergency-button { min-height: 48px; width: min(100%, 360px); border: 1px solid #d77a7d; border-radius: 5px; padding: 0 18px; display: inline-flex; align-items: center; justify-content: center; gap: 10px; color: #fff; background: #a6323a;',
     '.emergency-button { min-height: 52px; width: min(100%, 360px); border: none; border-radius: 10px; padding: 0 18px; display: inline-flex; align-items: center; justify-content: center; gap: 10px; color: #fff; background: linear-gradient(135deg, #e53e6a, #c02050);'),
    ('.emergency-button:hover { background: #922931;',
     '.emergency-button:hover { background: linear-gradient(135deg, #c02050, #a01840);'),
    # Safety status box
    ('.safety-status-box { min-height: 84px; padding: 13px; display: flex; align-items: center; gap: 11px; border: 1px solid var(--line); border-radius: 6px; background: #0b121b88; }',
     '.safety-status-box { min-height: 84px; padding: 14px; display: flex; align-items: center; gap: 11px; border: 1px solid var(--line); border-radius: 8px; background: #f8fbfc; }'),
    # Safety error
    ('.safety-error { display: flex; align-items: center; gap: 8px; margin-bottom: 11px; padding: 9px 11px; border: 1px solid #8b4947; border-radius: 5px; color: #f0c2c3; background: #432427;',
     '.safety-error { display: flex; align-items: center; gap: 8px; margin-bottom: 11px; padding: 9px 11px; border: 1px solid #f4b8cc; border-radius: 6px; color: #b03060; background: #fdeef2;'),
    # Safety result
    ('.safety-result { display: flex; justify-content: space-between; align-items: center; gap: 15px; margin-top: 11px; padding: 14px; border: 1px solid #745d35; border-radius: 6px; background: #28231770; }',
     '.safety-result { display: flex; justify-content: space-between; align-items: center; gap: 15px; margin-top: 11px; padding: 14px; border: 1px solid #b8e5ed; border-radius: 8px; background: #f0fbfd; }'),
    # Location readout
    ('.location-readout { display: flex; align-items: center; gap: 9px; margin: 8px 1px 14px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 5px; color: var(--cyan); background: var(--panel); }',
     '.location-readout { display: flex; align-items: center; gap: 9px; margin: 8px 1px 14px; padding: 10px 12px; border: 1px solid #b8e5ed; border-radius: 6px; color: #0891a8; background: #e5f6f9; }'),
    # Welcome callout
    ('.welcome-callout { display: flex; align-items: flex-start; gap: 13px; padding: 14px 16px; margin-bottom: 14px; border: 1px solid #2e4a5c; border-left: 3px solid var(--cyan); border-radius: 6px; background: color-mix(in srgb, var(--panel) 90%, #0e2a3a); }',
     '.welcome-callout { display: flex; align-items: flex-start; gap: 13px; padding: 14px 16px; margin-bottom: 14px; border: 1px solid #b8e5ed; border-left: 3px solid #0891a8; border-radius: 8px; background: #f0fbfd; }'),
    ('.welcome-callout svg { color: var(--cyan);',
     '.welcome-callout svg { color: #0891a8;'),
    # Alarm buttons
    ('.alarm-start, .alarm-stop { min-height: 35px; margin-top: 11px; padding: 0 10px; display: inline-flex; align-items: center; gap: 7px; border: 1px solid #675b3d; border-radius: 4px; color: #f2d394; background: #332b1c;',
     '.alarm-start, .alarm-stop { min-height: 35px; margin-top: 11px; padding: 0 10px; display: inline-flex; align-items: center; gap: 7px; border: 1px solid #d4a820; border-radius: 6px; color: #7a5010; background: #fdf5d8;'),
    ('.alarm-stop { border-color: #d17e83; color: #fff; background: #a6323a; }',
     '.alarm-stop { border-color: #d44e72; color: #fff; background: #e53e6a; }'),
]

count = 0
for old, new in replacements:
    if old in css:
        css = css.replace(old, new)
        count += 1
    else:
        print(f"NOT FOUND: {old[:60]}")

with open(path, "w", encoding="utf-8") as f:
    f.write(css)

print(f"Patched {count}/{len(replacements)} replacements")
