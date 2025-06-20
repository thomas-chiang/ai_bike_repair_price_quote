
import requests
import sys

# --- Configuration ---
# The base URL of your running FastAPI application.
BASE_URL = "http://localhost:8000"  # Change this to your actual FastAPI URL if needed
# BASE_URL = "https://superbench-818901082584.asia-east1.run.app"

def test_api_endpoints():
    """
    Runs a series of tests against the FastAPI backend:
    1. Gets a user ID token.
    2. Fetches the current chat history.
    3. Prompts the user to send a new message.
    4. Fetches the chat history again to see the update.
    """
    print("--- Starting FastAPI Test Client ---")

    # 1. Get the user's ID token for authentication.
    print("\nStep 1: Authenticating user...")
    id_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjNiZjA1MzkxMzk2OTEzYTc4ZWM4MGY0MjcwMzM4NjM2NDA2MTBhZGMiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiVGhvbWFzIEMiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jSl93V1hiTjlGbUd6d0MtVk0yS1RKaVJQQXlaTUZZTVdVQ1dORjZBQlhGS292MkJ3PXM5Ni1jIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL3N1cGVyYmVuY2gtdGhvbWFzIiwiYXVkIjoic3VwZXJiZW5jaC10aG9tYXMiLCJhdXRoX3RpbWUiOjE3NTA0NTE4NjYsInVzZXJfaWQiOiJ5NkNYNldCZ3VFYUcyM3c5dXJ6ejV5em5oZFcyIiwic3ViIjoieTZDWDZXQmd1RWFHMjN3OXVyeno1eXpuaGRXMiIsImlhdCI6MTc1MDQ1MTg2NiwiZXhwIjoxNzUwNDU1NDY2LCJlbWFpbCI6InQ3aGlhbmdAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZ29vZ2xlLmNvbSI6WyIxMTE2Nzk4NzgxNTc5OTk4OTM4NTciXSwiZW1haWwiOlsidDdoaWFuZ0BnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJnb29nbGUuY29tIn19.gE7Eyezki90KVGIjqdFNMYNeQAKnG9A0PX2GXy11riLMDa-OXOU0C4bdrct1hCfE47ztUknfPFhh0efJdBE49WDrNWJAoaSNFgG7pifBXohTIKC2LybGaGUikGFHukL8pMmbFSnrrhqMsgzI48CCeMRWWri5h9ut2wN0AuH9Oh-Mo9z9QZ9ZmD0Mu9E6jyraCaz-a22uMJsXBxo_M4i15POMrBP_GyqkqRYrimVxP2AXuWFqWrvn39LKJ-JK-fWr1taQ7CNQfOwc1isMNuYM3v0hHAW6r1fVFdHJivtCoFV3BpQeS1aI8eby7VNuOmQ4ncQ0aHVbz9T1nZRsRIwW0g'

    if not id_token:
        print("\n--- Test Failed ---")
        print("Could not obtain an ID token. Please check your Google Auth setup and the 'client_secrets.json' file.")
        sys.exit(1) # Exit the script if auth fails

    # Prepare the authorization header for all subsequent requests.
    headers = {
        "Authorization": f"Bearer {id_token}"
    }

    # 2. Test the GET /chats endpoint (first time)
    print("\nStep 2: Fetching initial chat history...")
    try:
        response = requests.get(f"{BASE_URL}/chats", headers=headers)
        
        # Check if the request was successful
        response.raise_for_status() 
        
        history = response.json()
        print("Success! Current chat history:")
        if not history:
            print("  (No messages yet)")
        else:
            for msg in history:
                print(f"  - [{msg['role'].capitalize()}] {msg['content']}")

    except requests.exceptions.RequestException as e:
        print(f"\n--- Test Failed ---")
        print(f"An error occurred while fetching chats: {e}")
        print(f"Server response: {response.text if 'response' in locals() else 'N/A'}")
        sys.exit(1)


    # 3. Test the POST /chat endpoint
    print("\nStep 3: Sending a new message...")
    try:
        # Prompt the user for a message to send
        user_message = input("Enter a message to send to the echo bot (or press Enter to quit): ")

        if not user_message:
            print("\n--- Test Client Finished ---")
            sys.exit(0)

        payload = {"content": user_message}
        response = requests.post(f"{BASE_URL}/chat", headers=headers, json=payload)

        response.raise_for_status()

        new_messages = response.json()
        print("Success! Server responded:")
        print(f"  - [User] {new_messages['user_message']['content']}")
        print(f"  - [Machine] {new_messages['machine_response']['content']}")

    except requests.exceptions.RequestException as e:
        print(f"\n--- Test Failed ---")
        print(f"An error occurred while posting a message: {e}")
        print(f"Server response: {response.text if 'response' in locals() else 'N/A'}")
        sys.exit(1)


    # 4. Test the GET /chats endpoint again to see the update
    print("\nStep 4: Fetching updated chat history...")
    try:
        response = requests.get(f"{BASE_URL}/chats", headers=headers)
        response.raise_for_status()
        
        updated_history = response.json()
        print("Success! Updated chat history:")
        for msg in updated_history:
             print(f"  - [{msg['role'].capitalize()}] {msg['content']}")
        
        print("\n--- All Tests Passed Successfully! ---")

    except requests.exceptions.RequestException as e:
        print(f"\n--- Test Failed ---")
        print(f"An error occurred while fetching updated chats: {e}")
        print(f"Server response: {response.text if 'response' in locals() else 'N/A'}")
        sys.exit(1)

    print("\nStep 4: Clear chat history?")
    choice = input("Would you like to clear the chat history? (y/n): ").lower()

    if choice == 'y':
        print("  Sending request to clear history...")
        try:
            response = requests.delete(f"{BASE_URL}/chats", headers=headers)
            response.raise_for_status()
            # delete_response = response.json()
            # print(f"  Success! Server says: {delete_response['message']}")

            # 5. Verify that the history is now empty
            print("\nStep 5: Verifying chat history is empty...")
            response = requests.get(f"{BASE_URL}/chats", headers=headers)
            response.raise_for_status()
            final_history = response.json()
            if not final_history:
                print("  Success! Chat history is now empty.")
            else:
                print("  Verification failed. History is not empty.")

        except requests.exceptions.RequestException as e:
            print(f"\n--- Test Failed ---")
            print(f"An error occurred while deleting chats: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Server response: {e.response.text}")
            sys.exit(1)
    else:
        print("  Skipping history deletion.")

    print("\n--- Test Client Finished Successfully! ---")


if __name__ == "__main__":
    # Ensure your FastAPI server is running before executing this script.
    # Command: uvicorn main:app --reload
    test_api_endpoints()

