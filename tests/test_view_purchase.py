import requests

def test_view_purchase():
    base_url = 'http://127.0.0.1:5000'

    print("Testing purchase view functionality...")

    try:
        # Test viewing purchase detail for ID 1
        response = requests.get(f'{base_url}/purchase_detail/1')
        print(f"View purchase detail status: {response.status_code}")

        if response.status_code == 200:
            print("Purchase detail view loaded successfully")
            # Check if the response contains expected content
            if 'purchase_detail.html' in response.text or 'purchase' in response.text.lower():
                print("Purchase detail page rendered correctly")
            else:
                print("Warning: Purchase detail page may not be rendering correctly")
        else:
            print(f"Failed to view purchase detail. Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == '__main__':
    test_view_purchase()
