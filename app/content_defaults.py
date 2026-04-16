PAGES = {
    "dashboard": {
        "label": "Dashboard",
        "sections": [
            {
                "section_key": "hero_intro",
                "title": "Welcome to the Student Conduct Team",
                "body": "This internal portal guides Graduate Assistants through systems training, hearing prep, case management, sanctions tracking, parent letter workflows, and escalation protocol.",
                "metadata_json": {"layout": "hero"},
            },
            {
                "section_key": "who_we_work_with",
                "title": "Who We Work With",
                "body": "Executive Director of Student Conduct — Dave Stender\nGIPP Grad\nPublic Safety Officer — Tim Humiston\nHealth and Wellness — Jack Bushnell",
                "metadata_json": {"layout": "list"},
            },
            {
                "section_key": "handbook_cta",
                "title": "Go Through Handbook",
                "body": "Review the current Student Handbook before moving forward with hearings, sanctions, and conduct workflows.",
                "metadata_json": {"link": "https://www.hartford.edu/current-students/_files/6.5_current_students_student_handbook.pdf", "link_label": "Open Handbook"},
            },
        ],
    },
    "office-overview": {
        "label": "Office Overview",
        "sections": [
            {"section_key": "mission", "title": "Mission & Standards", "body": "The Office of Student Conduct supports student development through accountability, educational sanctions, and procedural fairness.", "metadata_json": None},
            {"section_key": "resident_directors", "title": "Current Resident Directors", "body": "Lucrecia Acosta Larrama — Resident Director (A & B)\nKiara Opoku — Resident Director (C & E)\nJames Clary — Resident Director (Village Apartments)\nRadeana Hastings — Resident Director (D & F)\nKyle Thompson — Resident Director (Regents Park, Park River)", "metadata_json": {"layout": "list"}},
        ],
    },
    "training-flow": {
        "label": "Training Flow",
        "sections": [
            {"section_key": "orientation", "title": "Orientation", "body": "Review office mission, confidentiality expectations, and support pathways.", "metadata_json": {"phase": 1}},
            {"section_key": "systems", "title": "Systems", "body": "Learn Maxient workflows, shared drives, and task trackers.", "metadata_json": {"phase": 2}},
            {"section_key": "daily_responsibilities", "title": "Daily Responsibilities", "body": "Intake triage, hearings support, communication follow-up, and record keeping.", "metadata_json": {"phase": 3}},
            {"section_key": "case_handling", "title": "Case Handling", "body": "Case prep, documentation quality, and hearing readiness review.", "metadata_json": {"phase": 4}},
            {"section_key": "communication", "title": "Communication", "body": "Professional tone, response SLAs, and FERPA-aware messaging.", "metadata_json": {"phase": 5}},
            {"section_key": "sanctions", "title": "Sanctions", "body": "Assign, track, verify completion, and process hold release logic.", "metadata_json": {"phase": 6}},
            {"section_key": "independent_readiness", "title": "Independent Readiness", "body": "Final readiness check for independent GA support during office operations.", "metadata_json": {"phase": 7}},
        ],
    },
}

for slug, label in [
    ("systems", "Systems"),
    ("responsibilities", "Responsibilities"),
    ("case-handling", "Case Handling"),
    ("hearing", "Hearing"),
    ("sanctions", "Sanctions"),
    ("parent-letters", "Parent Letters"),
    ("ai-chat", "AI Chat"),
    ("escalation", "Escalation"),
    ("quick-reference", "Quick Reference"),
]:
    PAGES[slug] = {
        "label": label,
        "sections": [
            {
                "section_key": "overview",
                "title": f"{label} Overview",
                "body": f"Editable guidance for {label.lower()} workflows, checklists, and standards.",
                "metadata_json": None,
            },
            {
                "section_key": "best_practices",
                "title": f"{label} Best Practices",
                "body": "Capture decisions clearly, route escalations early, and maintain FERPA-safe records.",
                "metadata_json": None,
            },
        ],
    }
