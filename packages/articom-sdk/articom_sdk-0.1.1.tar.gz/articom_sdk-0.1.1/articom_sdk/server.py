import os
import hmac
import hashlib
from typing import Any, Type
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .skill import _SKILL_METADATA_KEY

# Load environment variables from .env file
load_dotenv()

async def verify_signature(request: Request, x_articom_signature: str = Header(None)):
    """Dependency to verify the HMAC signature of the request."""
    signing_secret = os.getenv("ARTICOM_SIGNING_SECRET")
    if not signing_secret:
        # In a real production environment, you might want to fail open or closed
        # depending on security policy. Failing closed is safer.
        raise HTTPException(status_code=500, detail="Signing secret is not configured on the skill server.")

    if not x_articom_signature:
        raise HTTPException(status_code=403, detail="Signature missing.")
    
    body = await request.body()
    expected_signature = hmac.new(
        key=signing_secret.encode(),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, x_articom_signature):
        raise HTTPException(status_code=403, detail="Invalid signature.")

def create_app(skill_class: Type[Any]) -> FastAPI:
    """Creates a FastAPI application for the given skill class."""
    if not hasattr(skill_class, _SKILL_METADATA_KEY):
        raise TypeError("The provided class is not a valid Articom skill. Please use the @ArticomSkill decorator.")

    skill_instance = skill_class()
    skill_metadata = getattr(skill_class, _SKILL_METADATA_KEY)
    
    app = FastAPI(
        title=skill_metadata.name,
        description=skill_metadata.description,
        version=skill_metadata.version
    )
    
    @app.get("/manifest", summary="Get Skill Manifest")
    async def get_manifest():
        """Returns the skill's manifest (skill.json)."""
        return JSONResponse(content=skill_instance.generate_manifest())

    @app.get("/health", summary="Health Check")
    async def health_check():
        """A simple health check endpoint."""
        return {"status": "ok"}

    # Dynamically create endpoints for each tool
    for tool_name, tool_data in skill_metadata.tools.items():
        # Need to capture variables in a closure
        def create_tool_endpoint(t_name, t_data):
            handler = getattr(skill_instance, t_data['handler'].__name__)
            
            # Get the Pydantic model from the function's type hints
            input_model_type = t_data['handler'].__annotations__['data']
            
            async def tool_endpoint(request: Request, data: input_model_type):
                # The dependency will run first
                await verify_signature(request, request.headers.get("x-articom-signature"))
                try:
                    result = handler(data)
                    return result
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error executing tool '{t_name}': {str(e)}")

            # Add the endpoint to the app
            app.post(
                f"/execute/{t_name}", 
                summary=f"Execute: {t_name}",
                description=t_data['description']
            )(tool_endpoint)
        
        create_tool_endpoint(tool_name, tool_data)

    return app
