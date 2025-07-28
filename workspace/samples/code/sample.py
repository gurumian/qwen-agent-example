#!/usr/bin/env python3
"""
Sample Python Code for Testing

This is a sample Python script that can be used to test the code interpreter
capabilities of the Qwen-Agent Chatbot System.
"""

import math
import random
from typing import List, Dict, Any

def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def calculate_pi(precision: int = 1000) -> float:
    """Calculate π using the Leibniz formula."""
    pi = 0
    for i in range(precision):
        pi += (-1) ** i / (2 * i + 1)
    return 4 * pi

def generate_random_data(size: int = 10) -> List[Dict[str, Any]]:
    """Generate random data for testing."""
    data = []
    for i in range(size):
        data.append({
            'id': i,
            'name': f'Item_{i}',
            'value': random.randint(1, 100),
            'category': random.choice(['A', 'B', 'C'])
        })
    return data

def analyze_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the generated data."""
    if not data:
        return {}
    
    values = [item['value'] for item in data]
    categories = [item['category'] for item in data]
    
    return {
        'count': len(data),
        'mean_value': sum(values) / len(values),
        'max_value': max(values),
        'min_value': min(values),
        'unique_categories': len(set(categories)),
        'category_counts': {cat: categories.count(cat) for cat in set(categories)}
    }

if __name__ == "__main__":
    # Example usage
    print("Fibonacci(10):", fibonacci(10))
    print("π approximation:", calculate_pi(1000))
    
    data = generate_random_data(20)
    analysis = analyze_data(data)
    
    print("\nData Analysis:")
    for key, value in analysis.items():
        print(f"  {key}: {value}") 