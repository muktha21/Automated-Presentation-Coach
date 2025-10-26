# Speech-Practice-Evaluation-Tool
AI based evaluation tool for speech practice

## Problem Statement & Approach

**Problem:**
- Learners and speakers need fast, actionable feedback during practice; existing tools are single-language and miss segment-level issues.
- Real speech often code-switches; tools must detect and analyze mixed-language sessions accurately.
- Gaps: language-aware marker detection (fillers/hesitations/repetitions), per-segment insights, localized recommendations.

**Approach:**
- Capture with browser SpeechRecognition and track language segments when user switches language.
- Stamp each final transcript chunk with selected language and timestamp (languageSegments).
- Backend (Flask) runs per-segment, language-specific analysis using filler lists and regex markers.
- Compute per-segment confidence; aggregate to overall score and select dominant language for templates.
- Return localized analysis summary, marker counts, flagged low-confidence segments (with language), and recommendations.
