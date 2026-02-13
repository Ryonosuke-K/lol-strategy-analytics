# lol-strategy-analytics

## 1. Project Objective
The objective of this project is to perform advanced data analysis, currently unavailable to the LoL community, by leveraging large-scale match data from the Riot API.

We will concurrently analyze three core themes:
1.  **The strategic value of objectives** (Dragons/Grubs)
2.  **The behavioral traits of players who consistently "climb" in rank**
3.  **The accuracy of pre-game win prediction models**

**Note on API Key Requirement:**
A **Production API Key** is essential for this project. These analyses require millions of match data points for statistical reliability and are designed to run as a 24/7 data pipeline on a cloud server. The Development Key's rate limits are insufficient for this scale of data ingestion.

## 2. Core Analysis Themes
We will simultaneously focus on the following three analysis themes that provide direct value to the community.

### Analysis 1: Objective Value Quantification (Dragon vs. Grubs)
* **Goal:** To determine the precise win-rate impact of securing Dragons (and Souls) versus Void Grubs.
* **Method:** Model the value of these objectives, including breakdowns by specific champions and game state (e.g., value when ahead vs. behind).

### Analysis 2: Identifying Traits of "Climbers"
* **Goal:** To identify the key behavioral and statistical markers that correlate with a sustained increase in MMR.
* **Method:** Go beyond KDA to analyze patterns in vision score, control ward purchases, champion pool diversity, and death timing to find what truly separates "climbers" from "stuck" players.

### Analysis 3: Pre-Game Win Prediction
* **Goal:** To validate the accuracy of machine learning models in predicting match outcomes based *only* on pre-game data (picks, bans, team synergy, summoner spells, and player mastery).
* **Method:** Quantify which factors in the draft phase have the greatest impact on the win probability.

> **Analysis Extensibility:** While these three themes are our core focus, our analysis will not be limited to them. The data infrastructure built with the Production Key will allow us to flexibly tackle new analysis topics (e.g., detailed item build paths) in response to meta shifts and community feedback.

## 3. Technology, Security & Deployment Plan

* **Technology:** Python (Pandas, Scikit-learn, Requests), SQL Database.
* **API Key Security:** The API key will **never** be hard-coded. It is loaded only from a secure environment variable (`os.environ`) or a cloud secret manager.
* **Rate Limit Compliance:** We use a robust request handler (see `analyze_prototype.py`) that fully respects all API rate limits by automatically handling `429` errors and the `Retry-After` header.
* **Deployment Plan:** The production application will be deployed on a **cloud server (GCP or AWS)**, running as a persistent 24/7 automated data pipeline.

## 4. Community Contribution
Our primary goal is to provide value to the community, not commercialization (Ad revenue will adhere to Riot's ToS). We will actively share the insights from Analyses 1, 2, and 3 with the community through the following platforms:

1.  **YouTube Channel**
    We will create and publish video content that explains and visualizes our analysis findings (e.g., *"The True Value of 3 Grubs vs. 1 Dragon, Backed by Data,"* *"The Vision Score Secret Shared by High-ELO Climbers"*).
2.  **Technical Blog (note, Medium, GitHub Pages, etc.)**
    We will publish articles detailing the data, methodologies, and deeper insights behind our YouTube videos, contributing to players and developers who seek more in-depth information.

## 5. How to Run the Prototype
*(This section, along with `analyze_prototype.py`, demonstrates technical reliability.)*

1.  **Install dependencies:**
    ```bash
    pip install requests
    ```

2.  **Set your API Key:**
    * **macOS/Linux:**
        ```bash
        export RIOT_API_KEY='YOUR_DEV_KEY_HERE'
        ```
    * **Windows (Command Prompt):**
        ```cmd
        set RIOT_API_KEY='YOUR_DEV_KEY_HERE'
        ```
    * **Windows (PowerShell):**
        ```powershell
        $env:RIOT_API_KEY='YOUR_DEV_KEY_HERE'
        ```

3.  **Run the script:**
    ```bash
    python analyze_prototype.py
    ```

## 6. Generate a Real API Snapshot for Review
To provide concrete evidence of actual API usage, generate a fresh snapshot file and publish it in the demo page.

1. Set a valid Riot API key in `RIOT_API_KEY`
2. Run:
   ```bash
   python generate_snapshot.py
   ```
3. This creates:
   - `docs/data/live-snapshot.json`
   - `docs/data/live-snapshot.md`

These files are displayed from `docs/index.html` under "Live API Snapshot (Recent Sample)".
If your development key expires (401), issue a new key from the Riot Developer Portal and run again.
## 7. Public Demo Page for Riot Review
To provide a verifiable public link and user flow, this repository includes a static demo page at `docs/index.html`.

Pages:
- Public insights page: `docs/index.html`

Access policy:
- Public user-facing experience is `docs/index.html`.
- In production, analysis data will be stored in SQL and detailed sections on this page will be populated from SQL-derived outputs.

### GitHub Pages Setup
1. Go to repository **Settings** -> **Pages**
2. Under **Build and deployment**, set:
   - **Source**: Deploy from a branch
   - **Branch**: `main` / `/docs`
3. Save and wait for deployment
4. The public URL will be:
   - `https://Ryonosuke-K.github.io/lol-strategy-analytics/`

### Reviewer Flow Link
After deployment, provide the URL above in your Riot application reply as the working public link.
