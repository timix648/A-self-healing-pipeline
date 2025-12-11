import os
import subprocess
import time
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY is missing.")
    exit(1)

genai.configure(api_key=api_key)

BUILD_COMMAND = "npm run build" 
MAX_RETRIES = 5
BRANCH_PREFIX = "fix/auto-repair"

# Your requested priority list. 
# The script will try 2.5 first. If it fails/doesn't exist, it auto-switches to the others.
MODEL_PRIORITY_LIST = [
    "gemini-2.5-flash",     
    "gemini-2.0-flash-exp", 
    "gemini-1.5-flash",
    "gemini-1.5-pro"   
]

def run_shell(command):
    """Runs a shell command and returns (exit_code, output)."""
    # Smart directory switching
    work_dir = "."
    if command.startswith("npm") and os.path.exists("broken-app"):
        work_dir = "broken-app"
        
    try:
        result = subprocess.run(
            command, 
            cwd=work_dir,
            shell=True, 
            capture_output=True, 
            text=True
        )
        return result.returncode, result.stdout + "\n" + result.stderr
    except Exception as e:
        return 1, str(e)

def remove_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def detect_broken_file(log_content):
    clean_log = remove_ansi_codes(log_content)
    regex = r"([a-zA-Z0-9_\-\./]+\.(tsx?|jsx?|css|json|py))"
    matches = re.findall(regex, clean_log)
    
    unique_files = set()
    for match in matches:
        raw_path = match[0]
        if os.path.exists(os.path.join("broken-app", raw_path)):
            unique_files.add(os.path.join("broken-app", raw_path))
        elif os.path.exists(raw_path):
            unique_files.add(raw_path)
            
    if unique_files:
        # Pick the file with the shortest path (usually the source file)
        return sorted(list(unique_files), key=len)[0]
    return None

def generate_fix(error_log, target_file, current_code):
    short_log = remove_ansi_codes(error_log[-2000:])
    
    prompt = f"""
    You are a Senior DevOps Auto-Fixer.
    CONTEXT: The build failed.
    ERROR LOGS: {short_log}
    BROKEN FILE ({target_file}):
    {current_code}
    
    TASK:
    1. Identify the syntax error in the code based on the log.
    2. Fix the code.
    3. RETURN ONLY THE FIXED CODE. NO MARKDOWN.
    """

    for model_name in MODEL_PRIORITY_LIST:
        print(f"🧠 AGENT: Asking {model_name} for a fix...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            text = response.text
            text = text.replace("```typescript", "").replace("```tsx", "")
            text = text.replace("```javascript", "").replace("```js", "")
            text = text.replace("```", "").strip()
            
            return text
        except Exception as e:
            print(f"⚠️ {model_name} failed: {e}. Trying next...")
            time.sleep(1)
            
    return None

def push_to_github():
    timestamp = int(time.time())
    branch_name = f"{BRANCH_PREFIX}-{timestamp}"
    
    print(f"🚀 AGENT: Pushing cumulative fixes to {branch_name}...")
    run_shell("git config user.email 'agent@kestra.io'")
    run_shell("git config user.name 'Self-Healing Agent'")
    run_shell(f"git checkout -b {branch_name}")
    run_shell("git add .")
    run_shell("git commit -m 'fix: recursive auto-repair (clean build)'")
    
    # 'origin' token is handled by Kestra's clone step
    exit_code, out = run_shell(f"git push origin {branch_name}")
    if exit_code == 0:
        print("✅ Success! PR created.")
    else:
        print(f"❌ Push failed: {out}")

def main():
    print("🔄 AGENT: Starting Recursive Self-Healing Loop...")
    
    attempt = 0
    fixes_applied = False
    
    # THIS IS THE LOOP THAT KEEPS YOUR REPO CLEAN
    while attempt < MAX_RETRIES:
        attempt += 1
        print(f"\n--- 🔨 Build Attempt {attempt}/{MAX_RETRIES} ---")
        
        # 1. Check if the code compiles
        exit_code, logs = run_shell(BUILD_COMMAND)
        
        if exit_code == 0:
            print("✅ Build Passed! System is stable.")
            if fixes_applied:
                # We only push if we actually fixed something
                push_to_github()
            else:
                print("No repairs were needed.")
            return

        print(f"🚨 Build Failed. Analyzing logs...")
        
        # 2. Find the broken file
        target_file = detect_broken_file(logs)
        if not target_file:
            print("❌ AGENT: Could not identify broken file from logs.")
            exit(1)
            
        # 3. Read current code
        with open(target_file, "r") as f:
            current_code = f.read()
            
        # 4. Generate Fix (Uses your 2.5 Flash logic)
        fixed_code = generate_fix(logs, target_file, current_code)
        
        if not fixed_code:
            print("❌ AGENT: AI could not generate a fix.")
            exit(1)
            
        # 5. Apply Fix Locally
        with open(target_file, "w") as f:
            f.write(fixed_code)
            
        print(f"🛠️ Fix applied to {target_file}. Re-verifying...")
        fixes_applied = True
        
        # The loop repeats immediately to check if the fix worked!

    print("❌ AGENT: Max retries reached. I couldn't fix everything.")
    exit(1)

if __name__ == "__main__":
    main()
