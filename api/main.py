from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import uvicorn

load_dotenv()


class Settings(BaseSettings):
    server_script_path: str = "./mcp_server.py"


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        connected = True
        if not connected:
            raise HTTPException(
                status_code=500, detail="Failed to connect to MCP server"
            )
        yield
    except Exception as e:
        print(f"Error during lifespan: {e}")
        raise HTTPException(status_code=500, detail="Error during lifespan") from e
    finally:
        # shutdown
        pass


app = FastAPI(title="MCP Client API", lifespan=lifespan)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class QueryRequest(BaseModel):
    query: str


class Message(BaseModel):
    role: str
    content: Any


class ToolCall(BaseModel):
    name: str
    args: Dict[str, Any]


@app.post("/query", response_model=Dict[str, Any])
async def process_query(request: QueryRequest):
    """Process a query and return the response"""
    try:
        messages = "query"
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def get_tools():
    """Get the list of available tools"""
    try:
        tools = "tools"
        return {
            "tools": [
                {
                    "name": "tools",
                    "description": "tools",
                    "input_schema": "tools",
                },
                {
                    "name": "tools",
                    "description": "tools",
                    "input_schema": "tools",
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
