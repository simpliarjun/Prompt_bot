# Prompt_bot (CGMS) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate Ponytail bloat, fix backend config/security edge cases via TDD, eradicate 10 Impeccable UI slop violations, and rewrite README with strict zero em-dashes.

**Architecture:** Refactor FastAPI backend settings and middleware to validate environment variables safely. Replace arbitrary AI violet/indigo gradients in React components with a clean Swiss palette (#2563EB primary, #0F172A text, #F8FAFC surface). Add hermetic unittest suite.

**Tech Stack:** Python 3 (FastAPI, Pydantic, unittest), React (Vite, Tailwind CSS), Impeccable detector.

**Spec:** Multi-repository audit findings for `Prompt_bot` (CGMS).

## Global Constraints
- Python: No external test dependencies required; all test assertions run via standard library `unittest`.
- Frontend: Zero Impeccable slop violations (`impeccable detect` must return 0 findings).
- Documentation: Strict zero em-dash (`—`) rule in README.md.

---

### Task 1: Ponytail Dead Code & Cache Cleanup

**Files:**
- Modify: `.gitignore`
- Delete: `backend/tests/__pycache__/`, `backend/__pycache__/`

- [ ] **Step 1: Check and remove cached bytecode**
Run git commands to clean up any tracked or untracked `.pyc` files and verify `.gitignore` covers them.

- [ ] **Step 2: Commit clean tree**
`git commit -m "chore: remove python cache artifacts"`

---

### Task 2: TDD Backend Configuration & Origin Parsing

**Files:**
- Create: `backend/tests/test_config_unit.py`
- Modify: `backend/config.py`

**Interfaces:**
- Consumes: `config.Settings`
- Produces: `parse_cors_origins() -> list[str]`

- [ ] **Step 1: Write failing unit test**
Write `backend/tests/test_config_unit.py` testing CORS origin string parsing with trailing slashes, empty strings, and whitespace.

- [ ] **Step 2: Run test to verify failure**
`python -m unittest backend/tests/test_config_unit.py`

- [ ] **Step 3: Implement robust parser in `backend/config.py`**
Normalize and strip entries, ensuring localhost and frontend URLs parse cleanly.

- [ ] **Step 4: Run test to verify pass**
`python -m unittest backend/tests/test_config_unit.py`

- [ ] **Step 5: Commit**
`git commit -m "fix(backend): sanitize CORS origins parsing via TDD"`

---

### Task 3: TDD Rate Limiter & Security Invariants

**Files:**
- Create: `backend/tests/test_security_unit.py`
- Modify: `backend/services/rate_limiter.py`

**Interfaces:**
- Consumes: `rate_limiter.InMemoryRateLimiter`
- Produces: `is_allowed(client_id: str) -> bool`

- [ ] **Step 1: Write failing unit test**
Write test exercising rate limit threshold, burst allowance, and window resets.

- [ ] **Step 2: Run test to verify failure**

- [ ] **Step 3: Implement minimal clean rate limit logic in `backend/services/rate_limiter.py`**

- [ ] **Step 4: Run test to verify pass**

- [ ] **Step 5: Commit**
`git commit -m "feat(security): add verified rate limiting with unit tests"`

---

### Task 4: Impeccable UI Overhaul & Anti-Slop (10 Violations Fixed)

**Files:**
- Modify: `frontend/src/components/GrievanceCard.jsx`
- Modify: `frontend/src/components/GrievanceForm.jsx`
- Modify: `frontend/src/components/GrievanceLetterEditor.jsx`
- Modify: `frontend/src/components/Navbar.jsx`

- [ ] **Step 1: Run baseline Impeccable detect**
Verify 10 violations found across the 4 files.

- [ ] **Step 2: Replace purple/indigo gradient slop with Swiss Palette**
- `GrievanceCard.jsx`: Replace `text-indigo-400` with `text-slate-900 dark:text-slate-100 font-semibold`.
- `GrievanceForm.jsx`: Replace `from-indigo-500 to-indigo-600` with `bg-blue-600 hover:bg-blue-700`.
- `GrievanceLetterEditor.jsx`: Replace `from-indigo-500` card headers with clean borders `#E2E8F0`.
- `Navbar.jsx`: Replace gradient brand text with solid crisp typography.

- [ ] **Step 3: Run Impeccable detect to verify 0 violations**
`impeccable detect frontend/src --json`

- [ ] **Step 4: Commit**
`git commit -m "refactor(ui): eradicate ai-color-palette slop with Swiss design tokens"`

---

### Task 5: README Anti-Slop Rewrite (Humanizer & Strict Zero Em-Dash)

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rewrite README.md**
Eliminate buzzwords ("leverages", "cutting-edge"), remove all em-dashes (`—`), clarify project as CGMS.

- [ ] **Step 2: Verify zero em-dashes**
Run regex search for `—` in `README.md`.

- [ ] **Step 3: Commit**
`git commit -m "docs: rewrite README with high-signal opening and zero slop"`

---

### Task 6: Verification & Ponytail Gain Measurement

- [ ] **Step 1: Run complete test suite**
- [ ] **Step 2: Run git diff --stat to measure net lines deleted**
