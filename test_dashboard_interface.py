import requests
import time

def test_dashboard_interface():
    """
    Test if the dashboard loads charts automatically without manual buttons.
    """
    
    try:
        print("🧪 Testing Dashboard Interface...")
        
        # Test the main page loads
        print("📡 Testing main page...")
        response = requests.get("http://localhost:5000", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check if buttons are removed
            button_tests = [
                ("🔄 Recarregar Gráficos", "Reload Charts button"),
                ("🎭 Modo Demo", "Demo Mode button"), 
                ("🧪 Teste Manual", "Manual Test button")
            ]
            
            buttons_found = []
            for button_text, description in button_tests:
                if button_text in content:
                    buttons_found.append(description)
            
            if buttons_found:
                print(f"⚠️  Found buttons that should be removed: {', '.join(buttons_found)}")
            else:
                print("✅ All buttons successfully removed from dashboard")
            
            # Check if chart elements exist
            chart_elements = [
                ("Visualização de Dados", "Chart section header"),
                ("Valor Gasto por Usuário", "User value chart"),
                ("Valor por Tipo de Cartão", "Card type chart"),
                ("userValueChart", "User chart canvas"),
                ("cardTypeChart", "Card chart canvas")
            ]
            
            missing_elements = []
            for element_text, description in chart_elements:
                if element_text not in content:
                    missing_elements.append(description)
            
            if missing_elements:
                print(f"❌ Missing chart elements: {', '.join(missing_elements)}")
            else:
                print("✅ All chart elements present")
            
            # Test the chart API endpoint
            print("📊 Testing chart API endpoint...")
            chart_response = requests.get("http://localhost:5000/api/transactions/charts/aggregated", timeout=15)
            
            if chart_response.status_code == 200:
                chart_data = chart_response.json()
                user_count = len(chart_data.get('dados_por_usuario', {}))
                card_count = len(chart_data.get('dados_por_cartao', {}))
                print(f"✅ Chart API working: {user_count} users, {card_count} card types")
            else:
                print(f"❌ Chart API error: {chart_response.status_code}")
            
            print("🎉 Dashboard interface test completed!")
            
        else:
            print(f"❌ Main page error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure services are running")
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dashboard_interface()