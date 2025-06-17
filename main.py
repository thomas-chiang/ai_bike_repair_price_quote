from dotenv import load_dotenv

load_dotenv()

from graph.graph import app as langgraph_app
import firebase_admin
from firebase_admin import credentials, auth, firestore
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import List

# --- Configuration & Initialization ---

# Load environment variables from .env file
# This allows us to use the GOOGLE_APPLICATION_CREDENTIALS path
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Echo Chat Backend",
    description="A FastAPI backend for a chat application using Firebase for auth and data storage.",
    version="1.0.0",
)

# Initialize Firebase Admin SDK
# The SDK will automatically find the credentials via the GOOGLE_APPLICATION_CREDENTIALS env var.
try:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Failed to initialize Firebase Admin SDK: {e}")
    # In a real app, you might want to exit or handle this more gracefully
    # For this example, we'll print the error and continue, but endpoints will fail.

# Get a client for the Firestore database
db = firestore.client()

# --- Pydantic Models (Data Schemas) ---

class ChatMessageInput(BaseModel):
    """Schema for the user's incoming message."""
    content: str

class ChatMessage(BaseModel):
    """Schema for a single chat message stored in Firestore."""
    role: str  # 'user' or 'machine'
    content: str
    timestamp: datetime

class ChatResponse(BaseModel):
    """Schema for the API's response after a new message is posted."""
    user_message: ChatMessage
    machine_response: ChatMessage

# --- Authentication ---

# Setup the security scheme
auth_scheme = HTTPBearer()

async def get_current_user_uid(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> str:
    """
    Dependency function to verify Firebase ID token and get user UID.
    
    This function is injected into endpoints that require authentication.
    It expects a 'Bearer' token in the Authorization header.
    
    Args:
        creds: The HTTP credentials containing the token.
        
    Returns:
        The user's unique Firebase ID (uid).
        
    Raises:
        HTTPException: If the token is missing, invalid, or expired.
    """
    if not creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token missing",
        )
    
    id_token = creds.credentials
    try:
        # Verify the token against the Firebase Auth service
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token.get("uid")
    except Exception as e:
        # Handle various authentication errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )

# --- API Endpoints ---

@app.get("/", summary="Root endpoint for health check")
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Welcome to the Echo Chat Backend!"}

@app.post("/chat", response_model=ChatResponse, summary="Send a message and get an echo response")
async def create_chat(
    message: ChatMessageInput, 
    uid: str = Depends(get_current_user_uid)
):
    """
    Receives a message from an authenticated user, saves it to Firestore,
    generates an response from langgraph, saves it, and returns both messages.
    """
    # 1. Create the user message object
    user_message = ChatMessage(
        role="user",
        content=message.content,
        timestamp=datetime.now(timezone.utc)
    )

    result = (langgraph_app.invoke(input={"question": message.content}))
    # 2. Create the machine's echo response
    machine_response = ChatMessage(
        role="machine",
        content=result.get("generation"),  # Echoing the user's content
        timestamp=datetime.now(timezone.utc)
    )

    # 3. Get reference to the user's chat document in Firestore
    # We use the user's UID as the document ID to uniquely store their chats.
    chat_ref = db.collection("chats").document(uid)

    # 4. Save the new messages to the document
    # We use `firestore.ArrayUnion` to atomically add the new messages to an array.
    # This prevents race conditions and is the recommended way to update lists.
    # The `set` command with `merge=True` will create the document if it doesn't exist.
    chat_ref.set({
        "messages": firestore.ArrayUnion([
            user_message.model_dump(),
            machine_response.model_dump()
        ])
    }, merge=True)

    return {"user_message": user_message, "machine_response": machine_response}

@app.get("/chats", response_model=List[ChatMessage], summary="Retrieve user's chat history")
async def get_chats(uid: str = Depends(get_current_user_uid)):
    """
    Retrieves the entire chat history for the authenticated user from Firestore.
    """
    # Get reference to the user's chat document
    chat_ref = db.collection("chats").document(uid)
    
    # Fetch the document from Firestore
    doc = chat_ref.get()

    if doc.exists:
        # If the document exists, return the 'messages' array.
        chat_data = doc.to_dict()
        messages = chat_data.get("messages", [])
        # Firestore returns dictionaries; we sort them by timestamp to ensure order.
        messages.sort(key=lambda x: x['timestamp'])
        return messages
    else:
        # If the document doesn't exist, the user has no chat history.
        return []

@app.delete("/chats", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user's entire chat history")
async def delete_chats(uid: str = Depends(get_current_user_uid)):
    """
    Deletes the entire chat history for the authenticated user from Firestore.
    This is a destructive operation and cannot be undone.
    """
    try:
        chat_ref = db.collection("chats").document(uid)
        
        # Delete the document. If the document does not exist, this operation
        # will not raise an error.
        chat_ref.delete()
        
        # A 204 No Content response is appropriate here and is handled by FastAPI
        # when the function body is empty or returns None.
        
    except Exception as e:
        # A catch-all for any potential errors during the Firestore operation.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting chat history: {e}",
        )