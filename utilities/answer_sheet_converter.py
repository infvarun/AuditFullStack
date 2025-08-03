#!/usr/bin/env python3
"""
Answer Sheet Converter Utility

This utility converts answer sheets with questions and answers into test data
that can be used for LLM processing and validation. It supports multiple formats
and can generate structured data for the audit application.

Usage:
    python answer_sheet_converter.py --input answers.xlsx --output test_data.json
    python answer_sheet_converter.py --input answers.csv --format validation
"""

import pandas as pd
import json
import argparse
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class AnswerSheetConverter:
    def __init__(self):
        self.supported_formats = ['xlsx', 'csv', 'json']
        
    def detect_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Intelligently detect question and answer columns from the DataFrame
        """
        columns = df.columns.str.lower()
        
        # Common column name patterns
        question_patterns = ['question', 'q', 'audit_question', 'query', 'item']
        answer_patterns = ['answer', 'response', 'result', 'finding', 'evidence', 'a']
        number_patterns = ['number', 'id', 'q_num', 'question_num', 'seq']
        process_patterns = ['process', 'category', 'area', 'domain']
        subprocess_patterns = ['subprocess', 'sub_process', 'subcategory', 'subarea']
        
        mapping = {}
        
        # Find question column
        for col in columns:
            if any(pattern in col for pattern in question_patterns):
                mapping['question'] = df.columns[columns.get_loc(col)]
                break
                
        # Find answer column
        for col in columns:
            if any(pattern in col for pattern in answer_patterns):
                mapping['answer'] = df.columns[columns.get_loc(col)]
                break
                
        # Find question number column
        for col in columns:
            if any(pattern in col for pattern in number_patterns):
                mapping['questionNumber'] = df.columns[columns.get_loc(col)]
                break
                
        # Find process column
        for col in columns:
            if any(pattern in col for pattern in process_patterns):
                mapping['process'] = df.columns[columns.get_loc(col)]
                break
                
        # Find subprocess column
        for col in columns:
            if any(pattern in col for pattern in subprocess_patterns):
                mapping['subProcess'] = df.columns[columns.get_loc(col)]
                break
        
        return mapping
    
    def read_answer_sheet(self, file_path: str) -> pd.DataFrame:
        """
        Read answer sheet from various file formats
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.xlsx':
            return pd.read_excel(file_path)
        elif file_ext == '.csv':
            return pd.read_csv(file_path)
        elif file_ext == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
                return pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def convert_to_test_data(self, df: pd.DataFrame, column_mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Convert DataFrame to structured test data format
        """
        if column_mapping is None:
            column_mapping = self.detect_columns(df)
            
        test_data = []
        
        for index, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.get(column_mapping.get('question', ''), '')):
                continue
                
            test_item = {
                'id': f"Q{index + 1}",
                'questionNumber': str(row.get(column_mapping.get('questionNumber', ''), f"Q{index + 1}")),
                'process': str(row.get(column_mapping.get('process', ''), '')),
                'subProcess': str(row.get(column_mapping.get('subProcess', ''), '')),
                'question': str(row.get(column_mapping.get('question', ''), '')),
                'expectedAnswer': str(row.get(column_mapping.get('answer', ''), '')),
                'metadata': {
                    'source_row': index + 1,
                    'has_answer': not pd.isna(row.get(column_mapping.get('answer', ''), '')),
                    'answer_length': len(str(row.get(column_mapping.get('answer', ''), ''))),
                }
            }
            
            # Add any additional columns as metadata
            for col in df.columns:
                if col not in column_mapping.values():
                    test_item['metadata'][col] = str(row.get(col, ''))
            
            test_data.append(test_item)
            
        return test_data
    
    def generate_llm_validation_format(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate format suitable for LLM validation and testing
        """
        return {
            'metadata': {
                'total_questions': len(test_data),
                'questions_with_answers': len([item for item in test_data if item['metadata']['has_answer']]),
                'generated_at': pd.Timestamp.now().isoformat(),
                'format': 'llm_validation'
            },
            'questions': [
                {
                    'questionId': item['id'],
                    'questionText': item['question'],
                    'process': item['process'],
                    'subProcess': item['subProcess'],
                    'expectedAnswer': item['expectedAnswer'],
                    'context': {
                        'questionNumber': item['questionNumber'],
                        'hasExpectedAnswer': item['metadata']['has_answer']
                    }
                }
                for item in test_data
            ]
        }
    
    def generate_audit_app_format(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate format compatible with the audit application
        """
        return {
            'questions': [
                {
                    'id': item['id'],
                    'questionNumber': item['questionNumber'],
                    'process': item['process'],
                    'subProcess': item['subProcess'],
                    'question': item['question']
                }
                for item in test_data
            ],
            'expectedAnswers': {
                item['id']: item['expectedAnswer'] 
                for item in test_data 
                if item['metadata']['has_answer']
            }
        }
    
    def save_output(self, data: Dict[str, Any], output_path: str, format_type: str = 'json'):
        """
        Save converted data to output file
        """
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        if format_type == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format_type == 'xlsx':
            # Save as Excel with multiple sheets
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                if 'questions' in data:
                    pd.DataFrame(data['questions']).to_excel(writer, sheet_name='Questions', index=False)
                if 'expectedAnswers' in data:
                    answers_df = pd.DataFrame(list(data['expectedAnswers'].items()), 
                                            columns=['QuestionID', 'ExpectedAnswer'])
                    answers_df.to_excel(writer, sheet_name='Expected_Answers', index=False)
    
    def process_answer_sheet(self, input_file: str, output_file: str, 
                           format_type: str = 'audit_app', 
                           column_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Main processing function
        """
        print(f"Reading answer sheet from: {input_file}")
        df = self.read_answer_sheet(input_file)
        
        print(f"Detected {len(df)} rows")
        
        if column_mapping is None:
            detected_mapping = self.detect_columns(df)
            print(f"Auto-detected column mapping: {detected_mapping}")
        else:
            detected_mapping = column_mapping
            print(f"Using provided column mapping: {detected_mapping}")
        
        # Convert to test data
        test_data = self.convert_to_test_data(df, detected_mapping)
        
        # Generate appropriate format
        if format_type == 'llm_validation':
            output_data = self.generate_llm_validation_format(test_data)
        elif format_type == 'audit_app':
            output_data = self.generate_audit_app_format(test_data)
        else:
            output_data = {'test_data': test_data}
        
        # Save output
        output_format = 'xlsx' if output_file.endswith('.xlsx') else 'json'
        self.save_output(output_data, output_file, output_format)
        
        print(f"Converted data saved to: {output_file}")
        print(f"Total questions processed: {len(test_data)}")
        print(f"Questions with answers: {len([item for item in test_data if item['metadata']['has_answer']])}")
        
        return output_data

def main():
    parser = argparse.ArgumentParser(description='Convert answer sheets to test data for LLM processing')
    parser.add_argument('--input', '-i', required=True, help='Input file path (Excel, CSV, or JSON)')
    parser.add_argument('--output', '-o', required=True, help='Output file path')
    parser.add_argument('--format', '-f', choices=['llm_validation', 'audit_app', 'raw'], 
                       default='audit_app', help='Output format type')
    parser.add_argument('--question-col', help='Question column name')
    parser.add_argument('--answer-col', help='Answer column name')
    parser.add_argument('--number-col', help='Question number column name')
    parser.add_argument('--process-col', help='Process column name')
    parser.add_argument('--subprocess-col', help='Sub-process column name')
    parser.add_argument('--preview', action='store_true', help='Preview detected columns without converting')
    
    args = parser.parse_args()
    
    converter = AnswerSheetConverter()
    
    # Build column mapping from arguments
    column_mapping = {}
    if args.question_col:
        column_mapping['question'] = args.question_col
    if args.answer_col:
        column_mapping['answer'] = args.answer_col
    if args.number_col:
        column_mapping['questionNumber'] = args.number_col
    if args.process_col:
        column_mapping['process'] = args.process_col
    if args.subprocess_col:
        column_mapping['subProcess'] = args.subprocess_col
    
    column_mapping = column_mapping if column_mapping else None
    
    if args.preview:
        # Preview mode - just show detected columns
        df = converter.read_answer_sheet(args.input)
        detected = converter.detect_columns(df)
        print(f"File: {args.input}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print(f"Detected mapping: {detected}")
        print("\nFirst few rows:")
        print(df.head().to_string())
    else:
        # Convert the file
        converter.process_answer_sheet(args.input, args.output, args.format, column_mapping)

if __name__ == '__main__':
    main()