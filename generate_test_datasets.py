import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_directory():
    os.makedirs('test_datasets', exist_ok=True)
    print("Created test_datasets directory.")

def generate_sales_clean(num_rows=50000):
    """Generates a clean dataset to test high quality score and large files."""
    print(f"Generating clean sales data ({num_rows} rows)...")
    np.random.seed(42)
    dates = [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(num_rows)]
    data = {
        'transaction_id': [f"TRX-{i:06d}" for i in range(1, num_rows + 1)],
        'date': dates,
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Home', 'Beauty', 'Sports'], size=num_rows),
        'quantity': np.random.randint(1, 10, size=num_rows),
        'unit_price': np.round(np.random.uniform(10.0, 500.0), 2),
    }
    df = pd.DataFrame(data)
    df['total_amount'] = np.round(df['quantity'] * df['unit_price'], 2)
    df.to_csv('test_datasets/sales_data_clean_large.csv', index=False)
    print(" -> Saved sales_data_clean_large.csv")

def generate_customer_messy(num_rows=20000):
    """Generates a messy dataset with nulls, duplicates, and mixed types."""
    print(f"Generating messy customer data ({num_rows} rows)...")
    np.random.seed(99)
    
    # Base data
    ids = np.random.randint(1000, 9000, size=num_rows)
    names = [f"Customer {i}" for i in ids]
    emails = [f"cust{i}@example.com" if np.random.rand() > 0.05 else None for i in ids] # 5% nulls
    
    # Introduce messy ages (strings, floats, ints, nulls)
    ages = []
    for _ in range(num_rows):
        r = np.random.rand()
        if r < 0.1: ages.append(np.nan)
        elif r < 0.2: ages.append(str(np.random.randint(18, 80)))
        elif r < 0.3: ages.append(float(np.random.randint(18, 80)))
        else: ages.append(np.random.randint(18, 80))
        
    signup_dates = []
    for _ in range(num_rows):
        if np.random.rand() < 0.15:
            signup_dates.append(np.nan)
        else:
            dt = datetime(2020, 1, 1) + timedelta(days=np.random.randint(0, 1000))
            # Mix date formats
            if np.random.rand() > 0.5:
                signup_dates.append(dt.strftime("%Y-%m-%d"))
            else:
                signup_dates.append(dt.strftime("%m/%d/%Y"))
                
    # Income with random spaces and string types
    incomes = [f" {np.random.randint(30, 150)}000 " if np.random.rand() > 0.1 else np.nan for _ in range(num_rows)]

    df = pd.DataFrame({
        'Cust ID': ids,
        'Name': names,
        'Email Address': emails,
        'Age ': ages, # trailing space in column name
        'Signup-Date': signup_dates,
        'AnnualIncome': incomes
    })
    
    # Add exact duplicate rows to test deduplication
    duplicates = df.sample(frac=0.15, replace=True) 
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Add fully null rows
    null_rows = pd.DataFrame(np.nan, index=range(500), columns=df.columns)
    df = pd.concat([df, null_rows], ignore_index=True)

    # Shuffle
    df = df.sample(frac=1).reset_index(drop=True)
    
    df.to_csv('test_datasets/customer_data_messy.csv', index=False)
    print(" -> Saved customer_data_messy.csv")

def generate_inventory_json(num_rows=15000):
    """Generates a JSON dataset to test JSON file support."""
    print(f"Generating inventory JSON data ({num_rows} rows)...")
    np.random.seed(24)
    data = []
    for i in range(1, num_rows + 1):
        item = {
            "sku": f"SKU-{np.random.randint(100000, 999999)}",
            "warehouse_location": np.random.choice(["NY", "CA", "TX", "WA", "FL"]),
            "stock_level": int(np.random.randint(0, 500)),
            "reorder_point": int(np.random.randint(10, 100)),
            "last_restocked": (datetime.now() - timedelta(days=np.random.randint(1, 30))).isoformat()
        }
        data.append(item)
    
    df = pd.DataFrame(data)
    df.to_json('test_datasets/inventory_data.json', orient='records')
    print(" -> Saved inventory_data.json")

def generate_financial_excel(num_rows=10000):
    """Generates an Excel dataset using openpyxl."""
    print(f"Generating financial Excel data ({num_rows} rows)...")
    np.random.seed(7)
    df = pd.DataFrame({
        'TransactionDate': [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(num_rows)],
        'Department': np.random.choice(['HR', 'IT', 'Marketing', 'Sales', 'Finance'], size=num_rows),
        'ExpenseCategory': np.random.choice(['Software', 'Travel', 'Equipment', 'Services'], size=num_rows),
        'Amount_USD': np.round(np.random.exponential(scale=1000, size=num_rows), 2),
        'Approved': np.random.choice([True, False], size=num_rows, p=[0.8, 0.2])
    })
    
    try:
        df.to_excel('test_datasets/financial_data.xlsx', index=False, engine='openpyxl')
        print(" -> Saved financial_data.xlsx")
    except Exception as e:
        print(f" -> Failed to save Excel file (is openpyxl installed?): {e}")

if __name__ == "__main__":
    print("Starting test dataset generation...\n")
    create_directory()
    generate_sales_clean()
    generate_customer_messy()
    generate_inventory_json()
    generate_financial_excel()
    print("\nGeneration complete! Files are available in the 'test_datasets' folder.")
