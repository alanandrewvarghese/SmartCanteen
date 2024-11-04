import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from common.models import OrderItem, Customer

import csv
import os
from django.conf import settings
from django.http import HttpResponse
from common.models import Order

def save_orders_to_csv():
    # Querying the orders and related order items
    orders_with_items = Order.objects.prefetch_related('items').values(
        'order_id',
        'customer_id',
        'ordered_at',
        'items__item_id'
    )
    
    print(f"Fetched {len(orders_with_items)} orders with items.")

    # Specify the file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'order_data.csv')
    print(f"Saving orders to CSV at {file_path}")

    # Create and write to the CSV file
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(['order_id', 'customer_id', 'ordered_at', 'item_id'])
        # writer.writerow(['Order ID', 'Customer ID', 'Ordered At', 'Item ID'])

        # Write the data rows
        for order in orders_with_items:
            writer.writerow([
                order['order_id'],
                order['customer_id'],
                order['ordered_at'],
                order['items__item_id'],
            ])
    
    print("CSV file has been created successfully.")
    return file_path  # You can return the file path if needed


def generate_recommendations(customer):
    print(f"Generating recommendations for customer ID: {customer}")

    # Step 1: Load past order items for the customer
    past_orders = OrderItem.objects.filter(order__customer=customer).order_by('-order__ordered_at')[:3]
    customer_purchases = [item.item.item_id for item in past_orders]  # Extract item IDs

    print(f"Customer has made {len(customer_purchases)} recent purchases: {customer_purchases}")

    # Step 2: Load the data for generating recommendations
    df = pd.read_csv(save_orders_to_csv())  # Adjust the path as necessary
    print(f"Loaded order data with {df.shape[0]} rows and {df.shape[1]} columns.")

    # Step 3: Create the basket DataFrame
    basket = df.groupby(['order_id', 'item_id'])['item_id'].count().unstack().reset_index().fillna(0).set_index('order_id')
    basket = basket > 0  # Convert counts to binary (1 for presence, 0 for absence)
    
    print(f"Basket DataFrame created with shape {basket.shape}.")

    # Step 4: Apply the Apriori algorithm
    frequent_itemsets = apriori(basket, min_support=0.01, use_colnames=True)
    print(f"Found {len(frequent_itemsets)} frequent itemsets.")

    # Step 5: Generate association rules
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
    print(f"Generated {len(rules)} association rules.")

    # Step 6: Recommend items based on the customer's past purchases
    return recommend_items(customer_purchases, rules)

def recommend_items(customer_purchases, rules, top_n=5):
    print(f"Recommending items based on purchases: {customer_purchases}")

    # Ensure customer_purchases are in the correct format
    customer_purchases_set = set(customer_purchases)

    # Find the rules where the antecedents match the customer's purchases
    recommendations = rules[rules['antecedents'].apply(lambda x: not customer_purchases_set.isdisjoint(x))]
    print(f"Found {len(recommendations)} recommendations based on the rules.")

    # If there are recommendations, extract the consequent items
    if not recommendations.empty:
        # Extract the consequent items from the rules
        recommended_items = set()
        for _, row in recommendations.iterrows():
            recommended_items.update(row['consequents'])
        
        # Remove items that the customer has already purchased
        recommended_items -= customer_purchases_set
        
        print(f"Recommended items after filtering: {recommended_items}")

        # Return the top_n recommendations
        return list(recommended_items)[:top_n]
    else:
        print("No recommendations available.")
        return []