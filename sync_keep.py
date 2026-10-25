import os
import gkeepapi
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("GOOGLE_KEEP_EMAIL")
password = os.getenv("GOOGLE_KEEP_APP_PASSWORD")

if not email or not password:
    print("Error: GOOGLE_KEEP_EMAIL or GOOGLE_KEEP_APP_PASSWORD missing from .env")
    exit(1)

keep = gkeepapi.Keep()
print(f"Authenticating as {email}...")

try:
    keep.authenticate(email, password)
    print("Authentication successful!")

    # Search for the note titled 'Episodes to add'
    notes = list(keep.find(query="Episodes to add"))
    
    if not notes:
        print("Could not find note with query 'Episodes to add'. Searching all notes...")
        all_notes = list(keep.all())
        print(f"Total notes found: {len(all_notes)}")
        for n in all_notes[:10]:
            print(f"- Title: {n.title}")
    else:
        for idx, note in enumerate(notes):
            print(f"\n--- Found Note {idx+1}: '{note.title}' ---")
            print("Content:")
            # Notes can be plain text or list items
            if hasattr(note, 'items') and note.items:
                for item in note.items:
                    status = "[x]" if item.checked else "[ ]"
                    print(f"  {status} {item.text}")
            else:
                print(note.text)

except Exception as e:
    print(f"Failed to authenticate or fetch notes: {type(e).__name__}: {e}")
