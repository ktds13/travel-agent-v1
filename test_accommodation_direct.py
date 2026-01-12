"""Direct test of accommodation tools"""
from agents.tools.accommodation_tools import search_accommodations, find_accommodation_near_place

# Test 1: Search for hotels in Chiang Mai
print("=" * 80)
print("TEST 1: Search for hotels in Chiang Mai")
print("=" * 80)
results = search_accommodations(location="Chiang Mai", accommodation_type="hotel", limit=5)
print(f"\nFound {len(results)} accommodations:\n")
for acc in results:
    print(f"- {acc['name']} ({acc['type']})")
    print(f"  Region: {acc['region']}, Rating: {acc['rating']}")
    print(f"  Price: ${acc['price_min']}-{acc['price_max']} ({acc['price_range']})")
    print()

# Test 2: Find accommodations near Doi Suthep  
print("\n" + "=" * 80)
print("TEST 2: Find accommodations near Doi Suthep")
print("=" * 80)
result = find_accommodation_near_place("Doi Suthep", radius_km=15, limit=5)
print(result)

# Test 3: Find budget accommodations
print("\n" + "=" * 80)
print("TEST 3: Find budget accommodations in Chiang Mai")
print("=" * 80)
results = search_accommodations(location="Chiang Mai", price_range="budget", limit=5)
print(f"\nFound {len(results)} budget accommodations:\n")
for acc in results:
    print(f"- {acc['name']} ({acc['type']})")
    print(f"  Price: ${acc['price_min']}-{acc['price_max']}")
    print()

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
