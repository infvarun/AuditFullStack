#!/usr/bin/env python3
import pandas as pd
import os

# Create a simple test Excel file
data = {
    'Question Number': ['Q1', 'Q2', 'Q3', 'Q4'],
    'Process': ['Authentication', 'Authorization', 'Data Processing', 'Logging'],
    'Sub-Process': ['Login', 'Access Control', 'Validation', 'Audit Trail'],
    'Question': [
        'How is user authentication implemented?',
        'What authorization mechanisms are in place?',
        'How is input data validated?',
        'What logging mechanisms are implemented?'
    ]
}

df = pd.DataFrame(data)
df.to_excel('test_audit_questions.xlsx', index=False)
print(f"Created test Excel file: test_audit_questions.xlsx")
print("Columns:", df.columns.tolist())
print("Sample data:")
print(df.head())