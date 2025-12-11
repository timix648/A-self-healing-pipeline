id: self-healing-pipeline
namespace: devops.agentic

tasks:
  - id: autonomous_devops_agent
    type: io.kestra.plugin.scripts.python.Script
    containerImage: nikolaik/python-nodejs:python3.11-nodejs20
    
    taskRunner:
      type: io.kestra.plugin.scripts.runner.docker.Docker
      volumes:
        - kestra_npm_cache:/root/.npm
        - kestra_pip_cache:/root/.cache/pip

    beforeCommands:
      - pip install google-generativeai python-dotenv
      - git config --global user.email "kestra-agent@example.com"
      - git config --global user.name "Kestra Self-Healing Agent"

    env:
      GEMINI_API_KEY: "{{ secret('GEMINI_API_KEY') }}"
      GITHUB_TOKEN: "{{ secret('GITHUB_TOKEN') }}"
      REPO_URL: "https://github.com/timix648/A-self-healing-pipeline.git"
      
    script: |
      import os
      import subprocess
      import shutil

      # --- 1. CLONE ---
      print("🤖 AGENT: Initializing Workspace...")
      repo_url = os.getenv("REPO_URL")
      token = os.getenv("GITHUB_TOKEN")
      auth_url = repo_url.replace("https://", f"https://timix648:{token}@")
      clone_dir = "project_code"
      
      if os.path.exists(clone_dir):
          shutil.rmtree(clone_dir)

      subprocess.run(["git", "clone", "--depth", "1", auth_url, clone_dir], check=True)
      REPO_DIR = os.path.abspath(clone_dir)
      
      # --- 2. INSTALL DEPS ---
      # We need dependencies installed so the Python script can run 'npm run build'
      APP_DIR = os.path.join(REPO_DIR, "broken-app")
      print(f"📦 AGENT: Installing Node dependencies...")
      subprocess.run("npm install", shell=True, cwd=APP_DIR)

      # --- 3. HANDOFF TO PYTHON ---
      print("🧠 AGENT: Handing control to recursive auto_fixer.py...")
      # We execute the script inside the cloned folder
      result = subprocess.run(["python3", "auto_fixer.py"], cwd=REPO_DIR)
      
      if result.returncode != 0:
          exit(1)
