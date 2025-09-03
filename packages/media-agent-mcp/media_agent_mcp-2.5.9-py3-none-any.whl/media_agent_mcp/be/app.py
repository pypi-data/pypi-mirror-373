from __future__ import annotations

import logging
from flask import Flask

# Register blueprints from modularized routes
from media_agent_mcp.be.routes_media import media_bp
from media_agent_mcp.be.routes_subtitles import subtitles_bp


logger = logging.getLogger(__name__)
app = Flask(__name__)

# Register blueprints (keep original paths unchanged)
app.register_blueprint(media_bp)
app.register_blueprint(subtitles_bp)


if __name__ == "__main__":
    """
    Args:
        None
    
    Returns:
        result: None. Starts the Flask development server with optional host/port overrides
    """
    import argparse

    parser = argparse.ArgumentParser(description="Run Flask backend server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=False)
