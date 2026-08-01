#####~~~~RECEIPT SPLITTER V0.1~~~~#####

# Initialise dictionaries
people = {}
items = {}

# Ask for names and strip spaces
names = [name.strip() for name in input("Please enter names on the bill (comma-separated): ").split(",")]

# Create a running total
for name in names:
    people[name] = 0

# Ask how many items on the receipt
num_items = int(input("Please enter the number of items on the receipt: "))

# For each item ask price and who shared it
for i in range(num_items):
    item = input("Please enter name of item: ")
    price = float(input("Please enter price of this item: "))
    shares = [name.strip() for name in input(
    "Please enter the names of the people who shared this item (comma-separated): ").split(",")]
    items[item] = {
        "price": price,
        "shares": shares
    }

# Split equally per item and add to each person's total
for item_name, item_details in items.items():
    for name in item_details["shares"]:
        people[name] += item_details["price"] / len(item_details["shares"])

# Ask if service charge
service = input("Would you like to add a service charge? (y/n): ")
if service.lower() == "y":
    service_rate = float(input("Please enter a percentage for the service charge: ")) / 100
    for name in people:
        people[name] *= (1 + service_rate)

# Return value per person
for name, total in people.items():
    print(f"{name}: {total:.2f}")

print(f"Total: {sum(people.values()):.2f}")