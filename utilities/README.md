# Answer Sheet Converter Utility

This utility converts answer sheets containing questions and answers into structured test data that can be used for LLM processing and validation in the audit application.

## Features

- **Auto-detect columns**: Automatically identifies question, answer, and metadata columns
- **Multiple input formats**: Supports Excel (.xlsx), CSV, and JSON files
- **Multiple output formats**: 
  - `audit_app`: Compatible with the audit application format
  - `llm_validation`: Structured for LLM testing and validation
  - `raw`: Basic converted data structure
- **Flexible column mapping**: Manual override for column detection
- **Preview mode**: Inspect files before conversion

## Installation

The utility uses standard Python libraries included with the audit application:
- pandas
- openpyxl (for Excel support)
- json
- argparse

## Usage Examples

### Basic Conversion
```bash
# Convert Excel file to audit app format
python utilities/answer_sheet_converter.py --input my_answers.xlsx --output test_data.json

# Convert CSV to LLM validation format
python utilities/answer_sheet_converter.py --input answers.csv --output validation_data.json --format llm_validation
```

### Preview Mode
```bash
# Preview file structure and detected columns
python utilities/answer_sheet_converter.py --input my_answers.xlsx --preview
```

### Manual Column Mapping
```bash
# Specify exact column names
python utilities/answer_sheet_converter.py \
  --input answers.xlsx \
  --output test_data.json \
  --question-col "Audit Question" \
  --answer-col "Expected Response" \
  --number-col "Q#" \
  --process-col "Process Area"
```

## Input File Format

Your answer sheet should contain these columns (names can vary):

| Column Type | Example Names | Description |
|-------------|---------------|-------------|
| Question Number | `Q#`, `Number`, `ID` | Question identifier |
| Process | `Process`, `Category`, `Area` | Process or category |
| Sub-Process | `Sub-Process`, `Subcategory` | Sub-process area |
| Question | `Question`, `Audit Question` | The actual question text |
| Answer | `Answer`, `Response`, `Finding` | Expected answer/response |

### Example Input (Excel/CSV):
```
Q# | Process | Sub-Process | Question | Answer
1  | Security | Access Control | Review user permissions | All users have appropriate access levels
2  | Compliance | Documentation | Check policy updates | Policies updated quarterly
```

## Output Formats

### Audit App Format
Generates data compatible with the audit application:
```json
{
  "questions": [
    {
      "id": "Q1",
      "questionNumber": "1",
      "process": "Security",
      "subProcess": "Access Control",
      "question": "Review user permissions"
    }
  ],
  "expectedAnswers": {
    "Q1": "All users have appropriate access levels"
  }
}
```

### LLM Validation Format
Structured for testing LLM responses:
```json
{
  "metadata": {
    "total_questions": 2,
    "questions_with_answers": 2,
    "generated_at": "2025-01-01T12:00:00"
  },
  "questions": [
    {
      "questionId": "Q1",
      "questionText": "Review user permissions",
      "expectedAnswer": "All users have appropriate access levels",
      "context": {
        "process": "Security",
        "subProcess": "Access Control"
      }
    }
  ]
}
```

## Integration with Audit Application

### 1. Generate Test Data
```bash
python utilities/answer_sheet_converter.py \
  --input your_answer_sheet.xlsx \
  --output test_questions.json \
  --format audit_app
```

### 2. Use for LLM Testing
The generated data can be used to:
- Test AI analysis accuracy
- Validate tool recommendations
- Create automated test suites
- Generate benchmark datasets

### 3. Answer Sheet Population
Create a script to populate answer columns using LLM responses:

```python
# Example integration script
import json
from utilities.answer_sheet_converter import AnswerSheetConverter

# Load your converted test data
with open('test_questions.json', 'r') as f:
    test_data = json.load(f)

# Use the questions in your audit application
# Compare LLM responses with expected answers
# Generate accuracy metrics
```

## Advanced Usage

### Custom Processing
You can extend the converter for specific needs:

```python
from utilities.answer_sheet_converter import AnswerSheetConverter

converter = AnswerSheetConverter()

# Custom column mapping
mapping = {
    'question': 'Custom Question Column',
    'answer': 'Custom Answer Column',
    'process': 'Business Area'
}

# Process with custom settings
result = converter.process_answer_sheet(
    'input.xlsx', 
    'output.json', 
    format_type='llm_validation',
    column_mapping=mapping
)
```

### Batch Processing
Process multiple files:

```bash
# Process all Excel files in a directory
for file in *.xlsx; do
    python utilities/answer_sheet_converter.py --input "$file" --output "${file%.xlsx}_converted.json"
done
```

## Best Practices

1. **Column Names**: Use clear, descriptive column headers in your answer sheets
2. **Data Quality**: Ensure answers are complete and accurate for better LLM training
3. **Format Consistency**: Keep question and answer formats consistent across sheets
4. **Preview First**: Always use `--preview` to check column detection before conversion
5. **Backup Data**: Keep original answer sheets as backup before conversion

## Troubleshooting

### Common Issues

1. **Column Detection Failed**: Use manual column mapping with `--question-col`, `--answer-col`, etc.
2. **Empty Output**: Check if your input file has the expected structure
3. **Encoding Issues**: Ensure your CSV files use UTF-8 encoding
4. **Excel Errors**: Make sure openpyxl is installed: `pip install openpyxl`

### Getting Help

```bash
# Show all available options
python utilities/answer_sheet_converter.py --help

# Preview file structure
python utilities/answer_sheet_converter.py --input your_file.xlsx --preview
```