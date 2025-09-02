"""Modern ASGI server with Quart framework and the original API."""

from quart import Quart, request, jsonify
from loguru import logger
import json

from .database import DatabaseManager
from .handlers.user_handlers import (
    get_user_data_handler,
    change_user_data_handler,
    bind_player_request_handler,
    bind_player_verification_handler
)


def create_app(db_path: str = "./data/user_v3.db", log_level: str = "info", direct_unbind: bool = False, proxy: str = ""):
    """Create and configure the Quart application."""
    import os
    
    # Get log level from environment variable (set by CLI) or use parameter
    actual_log_level = os.environ.get('TSUGU_UDS_LOG_LEVEL', log_level)
    
    app = Quart(__name__)
    
    # Configure logging based on log level
    logger.remove()  # Remove default handler
    
    # Set log level
    level = actual_log_level.upper()
    if level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        level = "INFO"
    
    # Add file handler
    if actual_log_level == "debug":
        logger.add("logs/tsugu_uds_dev.log", rotation="1 MB", retention="3 days", level=level, 
                  format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")
    else:
        logger.add("logs/tsugu_uds.log", rotation="1 MB", retention="10 days", level=level,
                  format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")
    
    # Add colorful console output - always show INFO and above, DEBUG only in debug mode
    import sys
    if actual_log_level == "debug":
        logger.add(sys.stderr, level="DEBUG", colorize=True, 
                  format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    else:
        logger.add(sys.stderr, level="INFO", colorize=True,
                  format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    logger.info(f"🔧 Log level set to: {actual_log_level}")
    
    if actual_log_level == "debug":
        logger.info("🔧 Debug mode enabled")
    
    # Initialize database
    db_manager = DatabaseManager(db_path)
    app.config['db_manager'] = db_manager
    app.config['direct_unbind'] = direct_unbind
    app.config['proxy'] = proxy
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    async def health_check():
        """Health check endpoint."""
        response_data = {
            "status": "healthy",
            "service": "Tsugu User Data Server API",
            "version": "1.0.0",
            "log_level": actual_log_level
        }
        
        logger.debug(f"Health check response: {response_data}")
        return jsonify(response_data), 200
    
    # Original API endpoints
    @app.route('/user/getUserData', methods=['POST'])
    async def get_user_data():
        """Get user data."""
        try:
            data = await request.get_json()
            platform = data.get('platform')
            user_id = data.get('userId')
            
            logger.debug(f"getUserData request: platform={platform}, userId={user_id}")
            
            if not platform or not user_id:
                error_response = {
                    "status": "failed",
                    "message": "Missing platform or userId"
                }
                logger.warning(f"getUserData validation failed: {error_response}")
                return jsonify(error_response), 400
            
            response = get_user_data_handler(app.config['db_manager'], platform, user_id)
            logger.debug(f"getUserData response: {json.dumps(response, ensure_ascii=False)}")
            
            if response.get('status') != 'success':
                return jsonify(response), 422
                
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Error in getUserData: {e}")
            return jsonify({
                "status": "failed",
                "message": "Internal server error"
            }), 500
    
    @app.route('/user/changeUserData', methods=['POST'])
    async def change_user_data():
        """Change user data."""
        try:
            data = await request.get_json()
            platform = data.get('platform')
            user_id = data.get('userId')
            update = data.get('update')
            
            logger.debug(f"changeUserData request: platform={platform}, userId={user_id}, update={json.dumps(update, ensure_ascii=False)}")
            
            if not platform or not user_id or not update:
                error_response = {
                    "status": "failed",
                    "message": "Missing required parameters"
                }
                logger.warning(f"changeUserData validation failed: {error_response}")
                return jsonify(error_response), 400
            
            response = change_user_data_handler(app.config['db_manager'], platform, user_id, update)
            logger.info(f"User data changed: {platform}:{user_id}")
            logger.debug(f"changeUserData response: {json.dumps(response, ensure_ascii=False)}")
            
            if response.get('status') != 'success':
                return jsonify(response), 422
                
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Error in changeUserData: {e}")
            return jsonify({
                "status": "failed",
                "message": "Internal server error"
            }), 500
    
    @app.route('/user/bindPlayerRequest', methods=['POST'])
    async def bind_player_request():
        """Request player binding."""
        try:
            data = await request.get_json()
            platform = data.get('platform')
            user_id = data.get('userId')
            
            logger.debug(f"bindPlayerRequest request: platform={platform}, userId={user_id}")
            
            if not platform or not user_id:
                error_response = {
                    "status": "failed",
                    "message": "Missing platform or userId"
                }
                logger.warning(f"bindPlayerRequest validation failed: {error_response}")
                return jsonify(error_response), 400
            
            response = bind_player_request_handler(app.config['db_manager'], platform, user_id, app.config['direct_unbind'])
            logger.info(f"Player bind request: {platform}:{user_id}")
            logger.debug(f"bindPlayerRequest response: {json.dumps(response, ensure_ascii=False)}")
            
            if response.get('status') != 'success':
                return jsonify(response), 422
                
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Error in bindPlayerRequest: {e}")
            return jsonify({
                "status": "failed",
                "message": "Internal server error"
            }), 500
    
    @app.route('/user/bindPlayerVerification', methods=['POST'])
    async def bind_player_verification():
        """Verify player binding."""
        try:
            data = await request.get_json()
            platform = data.get('platform')
            user_id = data.get('userId')
            server = data.get('server')
            player_id = data.get('playerId')
            binding_action = data.get('bindingAction')
            
            logger.debug(f"bindPlayerVerification request: platform={platform}, userId={user_id}, server={server}, playerId={player_id}, action={binding_action}")
            
            if not all([platform, user_id, server is not None, player_id, binding_action]):
                error_response = {
                    "status": "failed",
                    "message": "Missing required parameters"
                }
                logger.warning(f"bindPlayerVerification validation failed: {error_response}")
                return jsonify(error_response), 400
            
            response = bind_player_verification_handler(
                app.config['db_manager'], platform, user_id, server, player_id, binding_action, app.config['direct_unbind'], app.config['proxy']
            )
            logger.info(f"Player bind verification: {platform}:{user_id}")
            logger.debug(f"bindPlayerVerification response: {json.dumps(response, ensure_ascii=False)}")
            
            if response.get('status') != 'success':
                return jsonify(response), 422
                
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Error in bindPlayerVerification: {e}")
            return jsonify({
                "status": "failed",
                "message": "Internal server error"
            }), 500
    
    # Error handlers
    @app.errorhandler(404)
    async def not_found(error):
        logger.warning(f"404 Not Found: {request.path}")
        return jsonify({
            "status": "failed",
            "message": "Endpoint not found"
        }), 404
    
    @app.errorhandler(405)
    async def method_not_allowed(error):
        logger.warning(f"405 Method Not Allowed: {request.method} {request.path}")
        return jsonify({
            "status": "failed",
            "message": "Method not allowed"
        }), 405
    
    @app.errorhandler(500)
    async def internal_error(error):
        logger.error(f"500 Internal Server Error: {error}")
        return jsonify({
            "status": "failed",
            "message": "Internal server error"
        }), 500
    
    return app
