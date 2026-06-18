import docker
import os
import tempfile

try:
    client = docker.from_env()
except Exception:
    # If docker daemon is not running or not installed, fallback to a dummy client 
    # to avoid crashing on import. Real errors will be thrown on execution.
    client = None

def execute_code_in_sandbox(code: str, db_path: str) -> dict:
    """
    Executes the provided Python code in a secure Docker container.
    Returns a dict with 'stdout', 'stderr', and 'success'.
    """
    if not client:
        return {"stdout": "", "stderr": "Docker is not running or available.", "success": False}
        
    script = f"""
import sys
import duckdb
import pandas as pd
import json

try:
{code}
except Exception as e:
    import traceback
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
"""
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, "script.py")
            with open(script_path, "w") as f:
                f.write(script)
                
            # Create data.duckdb locally if it somehow doesn't exist yet
            if not os.path.exists(db_path):
                open(db_path, 'a').close()
                
            volumes = {
                temp_dir: {'bind': '/app', 'mode': 'ro'},
                db_path: {'bind': '/data/data.duckdb', 'mode': 'ro'}
            }
                
            container = client.containers.run(
                "python:3.10-slim",
                command='bash -c "pip install pandas duckdb > /dev/null 2>&1 && python /app/script.py"',
                volumes=volumes,
                working_dir='/app',
                detach=True,
                remove=False,
                mem_limit="512m",
                network_mode="bridge" # Needed for pip install. In production, use a pre-built image with network_mode="none"
            )
            
            result = container.wait(timeout=60)
            logs = container.logs(stdout=True, stderr=False).decode('utf-8')
            err_logs = container.logs(stdout=False, stderr=True).decode('utf-8')
            
            container.remove(force=True)
            
            success = result['StatusCode'] == 0
            
            return {
                "stdout": logs,
                "stderr": err_logs,
                "success": success
            }
            
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "success": False
        }
