from fastapi.testclient import TestClient
import sys

# Import the FastAPI app and the dependency to override
def _import_app_and_dep():
    from main import app, get_current_user_uid
    return app, get_current_user_uid

app, get_current_user_uid = _import_app_and_dep()

# Override the dependency to always return the test UID
TEST_UID = "y6CX6WBguEaG23w9urzz5yznhdW2" # your test user ID
def override_get_current_user_uid():
    return TEST_UID

app.dependency_overrides[get_current_user_uid] = override_get_current_user_uid

client = TestClient(app)

# --- Configuration ---
# The base URL is not needed for TestClient

def test_api_endpoints():
    """
    Runs a series of tests against the FastAPI backend using TestClient:
    1. Fetches the current chat history.
    2. Prompts the user to send a new message.
    3. Fetches the chat history again to see the update.
    """
    print("--- Starting FastAPI Test Client (in-process) ---")

    # 1. Test the GET /chats endpoint (first time)
    print("\nStep 1: Fetching initial chat history...")
    response = client.get("/chats")
    assert response.status_code == 200, f"Failed to fetch chats: {response.text}"
    history = response.json()
    print("Success! Current chat history:")
    if not history:
        print("  (No messages yet)")
    else:
        for msg in history:
            print(f"  - [{msg['role'].capitalize()}] {msg['content']}")

    # 2. Test the POST /chat endpoint
    print("\nStep 2: Sending a new message...")
    user_message = input("Enter a message to send to the echo bot (or press Enter to quit): ")
    if not user_message:
        print("\n--- Test Client Finished ---")
        sys.exit(0)
    payload = {"content": user_message}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200, f"Failed to post message: {response.text}"
    new_messages = response.json()
    print("Success! Server responded:")
    print(f"  - [User] {new_messages['user_message']['content']}")
    print(f"  - [Machine] {new_messages['machine_response']['content']}")

    # 3. Test the GET /chats endpoint again to see the update
    print("\nStep 3: Fetching updated chat history...")
    response = client.get("/chats")
    assert response.status_code == 200, f"Failed to fetch updated chats: {response.text}"
    updated_history = response.json()
    print("Success! Updated chat history:")
    for msg in updated_history:
        print(f"  - [{msg['role'].capitalize()}] {msg['content']}")
    print("\n--- All Tests Passed Successfully! ---")

    print("\nStep 4: Clear chat history?")
    choice = input("Would you like to clear the chat history? (y/n): ").lower()
    if choice == 'y':
        print("  Sending request to clear history...")
        response = client.delete("/chats")
        assert response.status_code == 204, f"Failed to delete chats: {response.text}"
        # 5. Verify that the history is now empty
        print("\nStep 5: Verifying chat history is empty...")
        response = client.get("/chats")
        assert response.status_code == 200, f"Failed to fetch chats after delete: {response.text}"
        final_history = response.json()
        if not final_history:
            print("  Success! Chat history is now empty.")
        else:
            print("  Verification failed. History is not empty.")
    else:
        print("  Skipping history deletion.")
    print("\n--- Test Client Finished Successfully! ---")

if __name__ == "__main__":
    # Ensure your FastAPI server is NOT running separately; this runs in-process.
    test_api_endpoints()

