from django.utils import timezone
from django.db.models import Prefetch
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd
from collections import defaultdict
from common.models import Order, OrderItem, Customer, Item

def get_order_data(months=2):
    # Get orders and related order items from the last two months in fewer queries
    two_months_ago = timezone.now() - timezone.timedelta(days=60)
    orders = Order.objects.filter(ordered_at__gte=two_months_ago).prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.select_related('item'))
    )
    
    # Create a dictionary to store customer orders
    customer_orders = defaultdict(list)
    
    for order in orders:
        customer_orders[order.customer.id].extend([order_item.item.item_name for order_item in order.items.all()])
    
    return customer_orders

def create_transaction_matrix(customer_orders):
    # Create a list of all unique items
    all_items = {item for orders in customer_orders.values() for item in orders}
    
    # Create a transaction DataFrame
    transactions = pd.DataFrame([{item: (item in orders) for item in all_items} for orders in customer_orders.values()])
    
    return transactions

def apply_apriori(df, min_support=0.1, min_confidence=0.5):
    # Apply Apriori algorithm
    frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    
    return rules

def generate_suggestions(customer_id, rules, top_n=5):
    customer = Customer.objects.get(id=customer_id)
    customer_orders = set(OrderItem.objects.filter(order__customer=customer).values_list('item__item_name', flat=True))
    
    # Filter rules based on customer's order history
    relevant_rules = rules[rules['antecedents'].apply(lambda x: x.issubset(customer_orders))]
    
    # Sort rules by lift and get top N suggestions
    relevant_rules = relevant_rules.sort_values('lift', ascending=False)
    suggestions = set()
    for _, rule in relevant_rules.iterrows():
        suggestions.update(rule['consequents'] - customer_orders)
        if len(suggestions) >= top_n:
            break
    
    return list(suggestions)[:top_n]

def get_customer_suggestions(customer_id, top_n=5):
    # Get order data
    customer_orders = get_order_data()
    
    # Create transaction matrix
    df = create_transaction_matrix(customer_orders)
    
    # Apply Apriori algorithm
    rules = apply_apriori(df)
    
    # Generate suggestions
    suggestions = generate_suggestions(customer_id, rules, top_n)
    
    # Get Item objects for the suggestions
    suggested_items = Item.objects.filter(item_name__in=suggestions)
    
    return suggested_items

# Example usage
if __name__ == "__main__":
    customer_id = 1  # Replace with actual customer ID
    suggested_items = get_customer_suggestions(customer_id)
    print(f"Suggested items for customer {customer_id}:")
    for item in suggested_items:
        print(f"- {item.item_name}")

