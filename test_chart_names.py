import requests
import json

def test_chart_api():
    """
    Test if the chart API is returning real user names instead of generic ones.
    """
    
    try:
        print("🧪 Testing Chart API...")
        
        # Test the chart aggregation endpoint
        response = requests.get("http://localhost:5000/api/transactions/charts/aggregated", timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check users data
            users_data = data.get('dados_por_usuario', {})
            print(f"👥 Found {len(users_data)} users")
            
            for user_id, user_info in users_data.items():
                user_name = user_info.get('nome', 'No name')
                total_spent = user_info.get('total_gasto', 0)
                print(f"  - User {user_id}: {user_name} (R$ {total_spent:.2f})")
                
                # Check if we're getting real names or generic ones
                if user_name.startswith('Usuário ') and user_name == f'Usuário {user_id}':
                    print(f"    ⚠️  Still using generic name for user {user_id}")
                else:
                    print(f"    ✅ Real name found for user {user_id}")
            
            # Check card data
            cards_data = data.get('dados_por_cartao', {})
            print(f"💳 Found {len(cards_data)} card types")
            
            for card_type, card_info in cards_data.items():
                total_spent = card_info.get('total_gasto', 0)
                print(f"  - {card_type}: R$ {total_spent:.2f}")
            
            print("✅ Chart API test completed successfully!")
            
        else:
            print(f"❌ API returned error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure services are running")
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chart_api()