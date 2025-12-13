# The Self-Healing DevOps Pipeline

## A Project for AssembleHack25 (Targeting 4 Areas)

### Project Overview

The **Self-Healing DevOps Pipeline** is a fully autonomous, closed-loop system designed to detect production build failures, diagnose the root cause, generate the code fix, and push the fix for automatic redeployment, all without human intervention.

This project directly addresses the hackathon's mandate for **Agentic Engineering** by integrating orchestration, code generation, version control, and continuous delivery.

### Targeted AssembleHack25 Awards

This project was engineered to satisfy the mandatory requirements for four distinct prize categories simultaneously:


| Sponsor Tech | My Implementation |
| :--- | :--- |
| Kestra | **Cognitive Orchestration:** Kestra is the central controller, using its Python Agent to execute the entire autonomous workflow (clone, build, analyze, fix) on a fixed schedule. |
| Cline | **Autonomous Coding (Functional Replacement):** Due to technical issues i had with the Cline CLI/MCP, the core functionality is achieved by a dedicated **Gemini Agent** (`auto_fixer.py`) that analyzes error logs and synthesizes code fixes. |
| CodeRabbit | **AI-Reviewed Workflow:** The Gemini Agent pushes the fix to a new branch, triggering a Pull Request (PR). The `.coderabbit.yaml` file ensures the autonomous fix is reviewed by CodeRabbit before merging. |
| Vercel | **Live Deployment:** Vercel hosts the application. Upon merging the CodeRabbit-approved fix, the CI/CD pipeline triggers an automatic redeployment of the healthy code. |

-----

## How the Pipeline Works

The system operates on a simple, continuous loop orchestrated by Kestra:

1.  **Schedule Trigger:** Kestra triggers the `self-healing-pipeline` every minute (via a `Schedule` trigger).
2.  **Run Build:** The Kestra flow executes a Dockerized Python script that clones the Git repository and runs `npm run build`.
3.  **Failure Detection:** If the build fails (e.g., due to the intentional syntax error in `page.tsx`), the Python script captures the error output into `build.log`.
4.  **Autonomous Fix:** The script executes **`auto_fixer.py`**, which uses the Gemini API to analyze the error logs and the broken code, then writes the corrected code back to the file system.
5.  **Git Commit:** The agent performs three actions: `git checkout -b fix/auto-repair-...`, `git commit`, and `git push`.
6.  **Human/AI Validation:** The Git push creates a Pull Request (PR) on GitHub, where **CodeRabbit** provides an automatic review.
7.  **Final Deployment:** Once the human merges the PR (approving the agent's work), Vercel automatically deploys the fixed code, completing the self-healing loop.

-----

## Setup and Execution Guide

### Prerequisites

You must have the following installed on your system (tested in WSL/Ubuntu on Windows):

1.  **Git**
2.  **Docker & Docker Compose**
3.  **A GitHub Repository** configured with:
      * Vercel Deployment connected to the `main` branch.
      * CodeRabbit Integration enabled.

### 1\. Environment Setup (Secrets)

For Kestra to connect to Git and Gemini, you must set up your secrets.

1.  **Create a `.env_encoded` file** in your project root with your base64-encoded credentials. (The uploaded file contents contain the correct base64 format.)
    ```yaml
    # In .env_encoded
    SECRET_GEMINI_API_KEY=...
    SECRET_GITHUB_TOKEN=... 
    ```
2.  **NOTE:** The Gemini API Key must have the necessary permissions. The GitHub Token must have **`repo`** scope (read/write access) to allow the agent to push the fix branch.

### 2\. Start Kestra & PostgreSQL

In your project directory, run:

```bash
docker compose up -d
```

*Wait for both services to show **Up** and/or **healthy**.*

### 3\. Deploy the Kestra Flow

1.  Access the Kestra UI at `http://localhost:8080`.
2.  Go to **Flows** and upload the contents of **`kestra.txt`**.
3.  Wait for the flow to be scheduled (or manually trigger it).

### 4\. Initiate the Self-Healing Demo

To see the system fix itself, ensure your code is currently broken:

1.  **Commit the broken code** (`page.tsx` with errors like `expot` or `<dive>`) to your main branch.
2.  **Monitor the Kestra logs:**
    ```bash
    docker compose logs -f kestra
    ```
3.  **Watch for the Sequence:** The logs will show the build failure (` NPM INSTALL FAILED`), the execution of `auto_fixer.py`, and the success message: `AGENT: Process Complete.`
4.  **Check GitHub:** A new branch (`fix/auto-repair-timestamp`) will appear, and a new Pull Request will be ready for review.

### 5\. Validation and Success

1.  **Review the PR:** Check the CodeRabbit review on the PR, and confirm the fix is correct.
2.  **Merge the PR:** Merge the PR into `main`.
3.  **Verify Vercel:** Check your Vercel dashboard to ensure the new commit triggers a successful, live deployment of the fixed code.

-----

### File Manifest

| File Name | Purpose |
| :--- | :--- |
| `docker-compose.yml` | Defines the Kestra and PostgreSQL services and volumes. |
| `kestra.txt` | The Kestra flow definition, orchestrating the repair logic. |
| `auto_fixer.py` | The autonomous Gemini Agent that performs error analysis and code generation. |
| `run_build.sh` | Script executed by Kestra to run the build process and capture the log. |
| `.env_encoded` | Kestra secrets for Gemini API and GitHub Token. |
| `.coderabbit.yaml` | Configuration for the AI code reviewer. |
| `page.tsx` | The application file that contains the intentional syntax error for the demo. |
