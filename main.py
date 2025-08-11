-- a/main.py
+++ b/main.py
@@
 from pathlib import Path
 
 # Add the project root to Python path
 project_root = Path(__file__).parent
 sys.path.insert(0, str(project_root))
 
 # Import all components
 from clean_video_wall_system import *
 from samsung_lh55_api_endpoints import *
 
+# Ensure these names exist even if not re-exported by the modules above
+from flask import jsonify, send_from_directory
+from datetime import datetime
+
 # Web interface route
 @app.route('/')
 def index():
