import sys

def check_utf8(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        data.decode('utf-8')
        print("File is valid UTF-8")
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        # Show some context around the error
        start = max(0, e.start - 50)
        end = min(len(data), e.end + 50)
        context = data[start:end]
        print(f"Context (bytes): {context}")
        
        # Try to fix by ignoring errors and re-writing
        print("Attempting to fix by re-saving with utf-8-sig and ignoring errors...")
        clean_data = data.decode('latin-1').encode('utf-8') # Fallback attempt
        with open(file_path, 'wb') as f:
            f.write(clean_data)
        print("File re-saved. Please try checking again.")

if __name__ == "__main__":
    check_utf8('transfer_data.json')
