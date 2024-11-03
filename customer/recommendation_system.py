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
















# import pandas as pd
# from mlxtend.frequent_patterns import apriori, association_rules
# from common.models import OrderItem, Customer

# import csv
# import os
# from django.conf import settings
# from django.http import HttpResponse
# from common.models import Order

# def save_orders_to_csv():
#     # Querying the orders and related order items
#     orders_with_items = Order.objects.prefetch_related('items').values(
#         'order_id',
#         'customer_id',
#         'ordered_at',
#         'items__item_id'
#     )

#     # Specify the file path
#     file_path = os.path.join(settings.MEDIA_ROOT, 'order_data.csv')

#     # Create and write to the CSV file
#     with open(file_path, mode='w', newline='') as file:
#         writer = csv.writer(file)

#         # Write the header row
#         # writer.writerow(['Order ID', 'Customer ID', 'Ordered At', 'Item ID'])

#         # Write the data rows
#         for order in orders_with_items:
#             writer.writerow([
#                 order['order_id'],
#                 order['customer_id'],
#                 order['ordered_at'],
#                 order['items__item_id'],
#             ])

#     return file_path  # You can return the file path if needed


# def generate_recommendations(customer):
#     # Step 1: Load past order items for the customer
#     past_orders = OrderItem.objects.filter(order__customer=customer).order_by('-order__ordered_at')[:3]
#     customer_purchases = [item.item.item_id for item in past_orders]  # Extract item IDs

#     # Step 2: Load the data for generating recommendations (this assumes you have a CSV file of all orders)
#     df = pd.read_csv(save_orders_to_csv())  # Adjust the path as necessary

#     # Step 3: Create the basket DataFrame
#     basket = df.groupby(['order_id', 'item_id'])['item_id'].count().unstack().reset_index().fillna(0).set_index('order_id')
#     basket = basket > 0  # Convert counts to binary (1 for presence, 0 for absence)

#     # Step 4: Apply the Apriori algorithm
#     frequent_itemsets = apriori(basket, min_support=0.01, use_colnames=True)

#     # Step 5: Generate association rules
#     rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

#     # Step 6: Recommend items based on the customer's past purchases
#     return recommend_items(customer_purchases, rules)

# def recommend_items(customer_purchases, rules, top_n=5):
#     # Ensure customer_purchases are in the correct format
#     customer_purchases_set = set(customer_purchases)

#     # Find the rules where the antecedents match the customer's purchases
#     recommendations = rules[rules['antecedents'].apply(lambda x: not customer_purchases_set.isdisjoint(x))]

#     # If there are recommendations, extract the consequent items
#     if not recommendations.empty:
#         # Extract the consequent items from the rules
#         recommended_items = set()
#         for _, row in recommendations.iterrows():
#             recommended_items.update(row['consequents'])
        
#         # Remove items that the customer has already purchased
#         recommended_items -= customer_purchases_set
        
#         # Return the top_n recommendations
#         return list(recommended_items)[:top_n]
#     else:
#         return []























# import pandas as pd
# from collections import defaultdict
# from django.utils import timezone
# from mlxtend.frequent_patterns import apriori, association_rules
# from common.models import Order, Item

# def get_order_data(months=2, batch_size=100):
#     two_months_ago = timezone.now() - timezone.timedelta(days=60)
#     orders = Order.objects.filter(ordered_at__gte=two_months_ago).prefetch_related('items').only('customer_id')
#     total_orders = orders.count()
    
#     customer_orders = defaultdict(list)
#     print(f"Fetched {total_orders} orders from the last {months} months.")
    
#     for batch_start in range(0, total_orders, batch_size):
#         order_batch = orders[batch_start:batch_start + batch_size]
#         for order in order_batch:
#             item_names = order.items.values_list('item__item_name', flat=True)
#             customer_orders[order.customer_id].extend(item_names)
        
#         print(f"Processed batch {batch_start // batch_size + 1} with {len(order_batch)} orders.")
    
#     print("Collected customer orders data.")
#     return customer_orders

# def create_transaction_matrix(customer_orders):
#     data = []
#     for customer_id, items in customer_orders.items():
#         for item_id in set(items):  # Use set to avoid duplicate entries
#             data.append({'customer_id': customer_id, 'item_id': item_id})

#     df = pd.DataFrame(data)

#     # Create a transaction matrix where each entry is 1 if purchased, else 0
#     transaction_matrix = df.pivot_table(index='customer_id', columns='item_id', aggfunc='size', fill_value=0)

#     # Convert counts to binary values (1 for purchased, 0 for not purchased)
#     transaction_matrix[transaction_matrix > 0] = 1
    
#     # Ensure all values are of integer type (0 or 1)
#     transaction_matrix = transaction_matrix.astype(int)

#     return transaction_matrix

# def apply_apriori(df):
#     # Convert to boolean DataFrame (True/False)
#     df_bool = df.astype(bool)

#     # Debugging: print the DataFrame structure and types
#     print("Transaction Matrix:\n", df.head())
#     print("Data types:\n", df.dtypes)

#     # Generate frequent itemsets
#     frequent_itemsets = apriori(df_bool, min_support=0.01, use_colnames=True)
#     # Generate association rules
#     rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
#     return rules

# def generate_suggestions(customer_id, rules, top_n=5):
#     # Get rules where the antecedent contains the customer_id's purchased items
#     customer_rules = rules[rules['antecedents'].apply(lambda x: customer_id in x)]

#     # Sort the rules by confidence and return the top N items
#     suggested_items = customer_rules.sort_values(by='confidence', ascending=False).head(top_n)

#     return suggested_items['consequents'].tolist()

# def get_customer_suggestions(customer_id, top_n=5):
#     print("Starting to get customer suggestions.")
    
#     customer_orders = get_order_data()
#     transaction_matrix = create_transaction_matrix(customer_orders)
#     rules = apply_apriori(transaction_matrix)
#     suggestions = generate_suggestions(customer_id, rules, top_n)
    
#     # Fetch suggested items from the database
#     suggested_items = Item.objects.filter(item_name__in=suggestions).only('item_name')
#     print(f"Suggested items for customer {customer_id}: {[item.item_name for item in suggested_items]}")
    
#     return suggested_items












# from django.utils import timezone
# from django.db.models import Q
# from mlxtend.frequent_patterns import apriori, association_rules
# import pandas as pd
# from collections import defaultdict
# from common.models import Order, OrderItem, Customer, Item
# from django.core.cache import cache

# def get_order_data(months=2, batch_size=100):
#     two_months_ago = timezone.now() - timezone.timedelta(days=60)
#     orders = Order.objects.filter(ordered_at__gte=two_months_ago).prefetch_related('items').only('customer_id')
#     total_orders = orders.count()
    
#     customer_orders = defaultdict(list)
#     print(f"Fetched {total_orders} orders from the last {months} months.")
    
#     for batch_start in range(0, total_orders, batch_size):
#         order_batch = orders[batch_start:batch_start + batch_size]
#         for order in order_batch:
#             item_names = order.items.values_list('item__item_name', flat=True)
#             customer_orders[order.customer_id].extend(item_names)
        
#         print(f"Processed batch {batch_start // batch_size + 1} with {len(order_batch)} orders.")
    
#     print("Collected customer orders data.")
#     return customer_orders

# def create_transaction_matrix(customer_orders):
#     all_items = sorted(set(item for items in customer_orders.values() for item in items))
#     print(f"Unique items across all orders: {len(all_items)} items found.")
    
#     transactions = []
#     for items in customer_orders.values():
#         customer_items = set(items)
#         transactions.append([1 if item in customer_items else 0 for item in all_items])
    
#     transaction_matrix = pd.DataFrame(transactions, columns=all_items).astype(bool)
#     print("Transaction matrix created with shape:", transaction_matrix.shape)
    
#     return transaction_matrix

# def apply_apriori(df, min_support=0.3, min_confidence=0.7, max_len=3):
#     cache_key = f"apriori_rules_{min_support}_{min_confidence}_{max_len}"
#     rules = cache.get(cache_key)
    
#     if rules is None:
#         print(f"Applying Apriori algorithm with min_support={min_support}, min_confidence={min_confidence}, and max_len={max_len}.")
#         frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True, max_len=max_len)
#         print(f"Found {len(frequent_itemsets)} frequent itemsets.")
        
#         rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
#         cache.set(cache_key, rules, timeout=3600)
#         print(f"Generated {len(rules)} association rules.")
#     else:
#         print("Loaded rules from cache.")
    
#     return rules

# def generate_suggestions(customer_id, rules, top_n=5):
#     customer_items = set(
#         OrderItem.objects.filter(order__customer_id=customer_id).values_list('item__item_name', flat=True)
#     )
#     print(f"Customer {customer_id} has previously ordered items: {customer_items}")
    
#     relevant_rules = rules[rules['antecedents'].apply(lambda x: x.issubset(customer_items))]
#     print(f"Found {len(relevant_rules)} relevant rules based on customer's history.")
    
#     relevant_rules = relevant_rules.sort_values('lift', ascending=False)
#     suggestions = []
#     for _, rule in relevant_rules.iterrows():
#         consequents = set(rule['consequents']) - customer_items
#         suggestions.extend(consequents)
#         if len(suggestions) >= top_n:
#             break
    
#     print(f"Top {top_n} suggestions for customer {customer_id}: {suggestions[:top_n]}")
#     return suggestions[:top_n]

# def get_customer_suggestions(customer_id, top_n=5):
#     print("Starting to get customer suggestions.")
    
#     customer_orders = get_order_data()
#     df = create_transaction_matrix(customer_orders)
#     rules = apply_apriori(df)
#     suggestions = generate_suggestions(customer_id, rules, top_n)
    
#     suggested_items = Item.objects.filter(item_name__in=suggestions).only('item_name')
#     print(f"Suggested items for customer {customer_id}: {[item.item_name for item in suggested_items]}")
    
#     return suggested_items





















# from django.utils import timezone
# from django.db.models import Q
# from mlxtend.frequent_patterns import apriori, association_rules
# import pandas as pd
# from collections import defaultdict
# from common.models import Order, OrderItem, Customer, Item

# def get_order_data(months=2):
#     # Get orders from the last two months
#     two_months_ago = timezone.now() - timezone.timedelta(days=60)
#     orders = Order.objects.filter(ordered_at__gte=two_months_ago).prefetch_related('items')  # Change here
#     print(f"Fetched {orders.count()} orders from the last {months} months.")
    
#     # Create a dictionary to store customer orders
#     customer_orders = defaultdict(list)

#     for order in orders:
#         # Use only the item names to reduce memory usage
#         customer_orders[order.customer.id].append([item.item.item_name for item in order.items.all()])  # Change here
    
#     print("Collected customer orders data.")
#     for customer_id, items in customer_orders.items():
#         print(f"Customer {customer_id}: Orders - {items}")
    
#     return customer_orders

# def create_transaction_matrix(customer_orders):
#     # Create a set of all unique items
#     all_items = set(item for orders in customer_orders.values() for order in orders for item in order)
#     print(f"Unique items across all orders: {len(all_items)} items found.")

#     # Create a binary matrix for transactions using a more memory-efficient approach
#     transactions = []
#     for orders in customer_orders.values():
#         customer_items = set(item for order in orders for item in order)
#         transactions.append([1 if item in customer_items else 0 for item in all_items])
    
#     transaction_matrix = pd.DataFrame(transactions, columns=list(all_items)).astype(bool)
#     print("Transaction matrix created with shape:", transaction_matrix.shape)
    
#     return transaction_matrix

# def apply_apriori(df, min_support=0.8, min_confidence=0.8):
#     print(f"Applying Apriori algorithm with min_support={min_support} and min_confidence={min_confidence}.")
    
#     # Apply Apriori algorithm
#     frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
#     print(f"Found {len(frequent_itemsets)} frequent itemsets.")
    
#     rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
#     print(f"Generated {len(rules)} association rules.")
    
#     return rules

# def generate_suggestions(customer_id, rules, top_n=5):
#     customer = Customer.objects.get(id=customer_id)
#     customer_orders = OrderItem.objects.filter(order__customer=customer).values_list('item__item_name', flat=True)
#     customer_items = set(customer_orders)
#     print(f"Customer {customer_id} has previously ordered items: {customer_items}")
    
#     # Filter rules based on customer's order history
#     relevant_rules = rules[rules['antecedents'].apply(lambda x: set(x).issubset(customer_items))]
#     print(f"Found {len(relevant_rules)} relevant rules based on customer's history.")
    
#     # Sort rules by lift and get top N suggestions
#     relevant_rules = relevant_rules.sort_values('lift', ascending=False)
#     suggestions = []
#     for _, rule in relevant_rules.iterrows():
#         consequents = set(rule['consequents']) - customer_items
#         suggestions.extend(consequents)
#         if len(suggestions) >= top_n:
#             break
    
#     print(f"Top {top_n} suggestions for customer {customer_id}: {suggestions[:top_n]}")
#     return suggestions[:top_n]

# def get_customer_suggestions(customer_id, top_n=5):
#     print("Starting to get customer suggestions.")
    
#     # Get order data
#     customer_orders = get_order_data()
    
#     # Create transaction matrix
#     df = create_transaction_matrix(customer_orders)
    
#     # Apply Apriori algorithm
#     rules = apply_apriori(df)
    
#     # Generate suggestions
#     suggestions = generate_suggestions(customer_id, rules, top_n)
    
#     # Get Item objects for the suggestions
#     suggested_items = Item.objects.filter(item_name__in=suggestions)
#     print(f"Suggested items for customer {customer_id}: {[item.item_name for item in suggested_items]}")
    
#     return suggested_items

# from django.utils import timezone
# from django.db.models import Q
# from mlxtend.frequent_patterns import fpgrowth, association_rules
# import pandas as pd
# from collections import defaultdict
# from common.models import Order, OrderItem, Customer, Item

# def get_order_data(months=2):
#     # Get orders from the last two months
#     two_months_ago = timezone.now() - timezone.timedelta(days=60)
#     orders = Order.objects.filter(ordered_at__gte=two_months_ago).prefetch_related('items')
#     print(f"Fetched {orders.count()} orders from the last {months} months.")
    
#     # Create a dictionary to store customer orders
#     customer_orders = defaultdict(list)

#     for order in orders:
#         # Use only the item names to reduce memory usage
#         customer_orders[order.customer.id].append([item.item.item_name for item in order.items.all()])
    
#     print("Collected customer orders data.")
#     return customer_orders

# def create_transaction_matrix(customer_orders):
#     # Create a set of all unique items
#     all_items = set(item for orders in customer_orders.values() for order in orders for item in order)
#     print(f"Unique items across all orders: {len(all_items)} items found.")

#     # Create a binary matrix for transactions
#     transactions = []
#     for orders in customer_orders.values():
#         customer_items = set(item for order in orders for item in order)
#         transactions.append([1 if item in customer_items else 0 for item in all_items])
    
#     transaction_matrix = pd.DataFrame(transactions, columns=list(all_items)).astype(bool)
#     print("Transaction matrix created with shape:", transaction_matrix.shape)
    
#     return transaction_matrix

# def apply_fp_growth(df, min_support=0.1):
#     print(f"Applying FP-Growth algorithm with min_support={min_support}.")
    
#     # Apply FP-Growth algorithm
#     frequent_itemsets = fpgrowth(df, min_support=min_support, use_colnames=True)
#     print(f"Found {len(frequent_itemsets)} frequent itemsets.")
    
#     return frequent_itemsets

# def generate_association_rules(frequent_itemsets, min_confidence=0.5):
#     print(f"Generating association rules with min_confidence={min_confidence}.")
#     rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
#     print(f"Generated {len(rules)} association rules.")
    
#     return rules

# def generate_suggestions(customer_id, rules, top_n=5):
#     customer_orders = OrderItem.objects.filter(order__customer_id=customer_id).values_list('item__item_name', flat=True)
#     customer_items = set(customer_orders)
#     print(f"Customer {customer_id} has previously ordered items: {customer_items}")

#     # Filter rules based on customer's order history
#     relevant_rules = rules[rules['antecedents'].apply(lambda x: set(x).issubset(customer_items))]
#     print(f"Found {len(relevant_rules)} relevant rules based on customer's history.")

#     # Sort rules by lift and get top N suggestions
#     relevant_rules = relevant_rules.sort_values('lift', ascending=False)
#     suggestions = []
#     for _, rule in relevant_rules.iterrows():
#         consequents = set(rule['consequents']) - customer_items
#         suggestions.extend(consequents)
#         if len(suggestions) >= top_n:
#             break
    
#     print(f"Top {top_n} suggestions for customer {customer_id}: {suggestions[:top_n]}")
#     return suggestions[:top_n]

# def get_customer_suggestions(customer_id, top_n=5):
#     print("Starting to get customer suggestions.")
    
#     # Get order data
#     customer_orders = get_order_data()
    
#     # Create transaction matrix
#     df = create_transaction_matrix(customer_orders)
    
#     # Apply FP-Growth algorithm
#     frequent_itemsets = apply_fp_growth(df)
    
#     # Generate association rules
#     rules = generate_association_rules(frequent_itemsets)
    
#     # Generate suggestions
#     suggestions = generate_suggestions(customer_id, rules)
    
#     # Get Item objects for the suggestions
#     suggested_items = Item.objects.filter(item_name__in=suggestions)
#     print(f"Suggested items for customer {customer_id}: {[item.item_name for item in suggested_items]}")
    
#     return suggested_items

