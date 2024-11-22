# test_properties.py
from octopus_client import OctopusClient
from config import MAIN_HOUSE, BASEMENT

def test_property(property_config):
    client = OctopusClient(property_config)
    
    print(f"\nTesting {property_config.name}:")
    print("-" * 50)
    
    # Test electricity consumption
    elec = client.get_electricity_consumption()
    if elec:
        print(f"Latest electricity reading: {elec[0]}")
    
    # Test gas consumption
    gas = client.get_gas_consumption()
    if gas:
        print(f"Latest gas reading: {gas[0]}")
    
    # Test rates
    rates = client.get_rates(hours_ahead=4)
    if rates:
        print("\nUpcoming rates:")
        for rate in rates[:3]:
            print(f"Time: {rate['valid_from']} - Price: {rate['value_inc_vat']}p/kWh")

if __name__ == "__main__":
    test_property(MAIN_HOUSE)
    test_property(BASEMENT)