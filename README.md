# ✏️ Multiplication Worksheet Studio (Grade 3)

A pedagogical, high-engagement multiplication fact practice generator built specifically for 3rd-grade classrooms. Aligned to the **Washington State Learning Standards for Mathematics (WA CCSS-M)** and the **Clear Math** instructional framework.

Designed for effortless school printing with **Paper-Saver 2-Up Half-Page Mode** and one-click **8.5" × 11" B&W vector PDF** export.

---

## 🌟 Key Features

### 1. Engaging, Low-Anxiety Practice Formats
- **Secret Code Riddle Decoder**: Students solve facts to unlock letters and reveal classic, kid-tested jokes from a human-verified repository (no AI nonsense). Self-checking: if words don't make sense, students self-correct!
- **Math Detective ("Sneaky Pete's Error Hunt")**: Models authentic 3rd-grade student misconceptions (the additive slip, off-by-one group, double errors). Students act as detectives, circling Pete's mistakes and writing the true products (CCSS Mathematical Practice **SMP 3**).
- **Multiples Pathfinder Maze**: Algorithmic DFS-generated maze with a guaranteed solvable path where students step only on valid multiples or equations for the chosen numbers.

### 2. Built for Classroom Copiers
- **Strictly Ink-Friendly B&W**: Pure black `#000000` with crisp 1.5pt–2pt line weights that never wash out on low-toner school copiers.
- **Paper-Saver 2-Up Mode**:
  - **Twin Mode**: 2 identical copies on one sheet with a dashed center cutting line (`✂ CUT HERE ✂`). Cut once on the paper cutter to produce a class set with 50% paper savings.
  - **Anti-Peeking Mode (Form A & B)**: Left side prints Form A and right side prints Form B with different problems and jokes, preventing neighboring kids from peeking.
- **Header for Multi-Class Cohorts**: `Name: ____________________  Class/Room: _______  Date: _________`.

### 3. Standards & Clear Math Fidelity
- **WA CCSS-M Core**: `3.OA.A.1` (equal groups), `3.OA.A.4` (missing factors), `3.OA.B.5` (properties), and `3.OA.C.7` (fluency).
- **Clear Math Strategy Clusters**:
  - Foundations ($0, 1, 2, 5, 10$)
  - Doubles & Double-Doubles ($2, 4, 8$)
  - Decomposition & Distributive ($3, 6, 7, 9$)
  - Upper Extensions ($11, 12$)
- **Optional Strategy Helper Box**: Prints visual anchor tips (skip-counting lines, array hints, doubling reminders).
- **Student Fonts**: Toggles for **Lexend** (dyslexia & reading flow) and **Comic Neue** (elementary print).
- **Automatic Teacher Answer Key**: Complete solutions and pedagogical rationale included by default.

---

## 🚀 Running Locally

```bash
# 1. Activate the virtual environment
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Mac/Linux

# 2. Run the Streamlit application
streamlit run app.py
```

The app will launch immediately at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Community Cloud (For Classroom Printing Anywhere)

To allow access and printing from any school computer, district laptop, or phone:

1. Create a repository on your **GitHub** account (e.g. `multiplication-worksheet-studio`).
2. Push this project:
   ```bash
   git remote add origin https://github.com/<your-username>/multiplication-worksheet-studio.git
   git push -u origin main
   ```
3. Go to [share.streamlit.io](https://share.streamlit.io/) and log in.
4. Click **"New App"**, select your repository, set the main file path to `app.py`, and click **Deploy**.
5. Your wife can now bookmark the live URL on her school computer and print in one click from anywhere!
