#!/usr/bin/env python3
"""
LLM Answer Generator Utility

This utility uses the OpenAI LLM to generate answers for audit questions
and populate answer sheets automatically. It integrates with the answer
sheet converter to create complete test datasets.

Usage:
    python llm_answer_generator.py --input questions.json --output answered_sheet.xlsx
    python llm_answer_generator.py --questions-file questions.xlsx --ai-populate
"""

import pandas as pd
import json
import argparse
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
import time

# Add the parent directory to path to import from the server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("Warning: Langchain not available. Install with: pip install langchain langchain-openai")
    LANGCHAIN_AVAILABLE = False

class LLMAnswerGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        if LANGCHAIN_AVAILABLE:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            self.llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.3,
                api_key=self.api_key
            )
        else:
            self.llm = None
            
    def create_audit_answer_prompt(self) -> ChatPromptTemplate:
        """
        Create a prompt template for generating audit answers
        """
        system_template = """You are an experienced audit professional with expertise in various business processes, compliance, and risk management. Your task is to provide realistic, professional audit findings and responses.

GUIDELINES FOR AUDIT ANSWERS:
1. **Realistic Findings**: Provide answers that reflect real-world audit scenarios
2. **Professional Tone**: Use formal, objective audit language
3. **Specific Details**: Include specific examples, metrics, or evidence when appropriate
4. **Compliance Focus**: Consider regulatory requirements and best practices
5. **Risk Assessment**: Identify potential risks or compliance gaps when relevant
6. **Actionable Insights**: Provide clear, actionable findings

ANSWER STRUCTURE:
- **Current State**: What was found/observed
- **Evidence**: Specific examples or data points
- **Assessment**: Compliance status or risk level
- **Recommendations**: Improvement suggestions (if applicable)

EXAMPLE RESPONSES:
- For access control: "Review of user access matrix revealed 15 users with elevated privileges. All access requests properly documented and approved. Quarterly access reviews completed on schedule."
- For documentation: "Policy documentation is current with last update on [date]. All required policies in place and accessible to staff. Version control maintained through central repository."
- For testing: "Test coverage analysis shows 87% coverage of critical functions. Automated testing implemented for core processes. Manual testing documented with evidence of execution."

Provide detailed, professional audit responses that would be suitable for an actual audit report."""

        human_template = """Generate a professional audit answer for this question:

Process: {process}
Sub-Process: {sub_process}
Question: {question}

Context: This is part of an audit for {context} focusing on {process} processes.

Please provide a detailed, realistic audit finding that addresses the question directly."""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    def generate_answer(self, question: str, process: str = "", sub_process: str = "", context: str = "organizational audit") -> str:
        """
        Generate an audit answer for a single question
        """
        if not LANGCHAIN_AVAILABLE or not self.llm:
            return f"Generated answer for: {question[:50]}... (Langchain not available - this is a placeholder)"
        
        try:
            prompt_template = self.create_audit_answer_prompt()
            
            formatted_prompt = prompt_template.format_messages(
                question=question,
                process=process or "General",
                sub_process=sub_process or "Various",
                context=context
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content.strip()
            
        except Exception as e:
            print(f"Error generating answer for question: {question[:50]}... Error: {e}")
            return f"Error generating answer: {str(e)}"
    
    def process_questions_file(self, input_file: str, output_file: str, context: str = "audit", delay: float = 1.0) -> Dict[str, Any]:
        """
        Process a file of questions and generate answers
        """
        print(f"Loading questions from: {input_file}")
        
        # Determine file type and load data
        file_ext = Path(input_file).suffix.lower()
        
        if file_ext == '.json':
            with open(input_file, 'r') as f:
                data = json.load(f)
                
            # Handle different JSON structures
            if 'questions' in data:
                questions = data['questions']
            elif isinstance(data, list):
                questions = data
            else:
                raise ValueError("JSON file must contain a 'questions' array or be an array of questions")
                
        elif file_ext in ['.xlsx', '.csv']:
            # Use answer sheet converter to read
            from answer_sheet_converter import AnswerSheetConverter
            converter = AnswerSheetConverter()
            df = converter.read_answer_sheet(input_file)
            column_mapping = converter.detect_columns(df)
            test_data = converter.convert_to_test_data(df, column_mapping)
            questions = [
                {
                    'id': item['id'],
                    'question': item['question'],
                    'process': item['process'],
                    'subProcess': item['subProcess'],
                    'questionNumber': item['questionNumber']
                }
                for item in test_data
            ]
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        print(f"Found {len(questions)} questions to process")
        
        # Generate answers
        results = []
        total_questions = len(questions)
        
        for i, question in enumerate(questions, 1):
            print(f"Processing question {i}/{total_questions}: {question.get('questionNumber', question.get('id', i))}")
            
            answer = self.generate_answer(
                question=question.get('question', ''),
                process=question.get('process', ''),
                sub_process=question.get('subProcess', ''),
                context=context
            )
            
            result = {
                'questionId': question.get('id', f'Q{i}'),
                'questionNumber': question.get('questionNumber', question.get('id', f'Q{i}')),
                'process': question.get('process', ''),
                'subProcess': question.get('subProcess', ''),
                'question': question.get('question', ''),
                'generatedAnswer': answer,
                'generatedAt': pd.Timestamp.now().isoformat(),
                'model': 'gpt-4o',
                'context': context
            }
            
            results.append(result)
            
            # Add delay to avoid rate limiting
            if delay > 0 and i < total_questions:
                time.sleep(delay)
        
        # Save results
        self.save_results(results, output_file)
        
        print(f"\nCompleted! Generated {len(results)} answers")
        print(f"Results saved to: {output_file}")
        
        return {
            'total_questions': len(results),
            'results': results,
            'output_file': output_file
        }
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str):
        """
        Save generated answers to file
        """
        output_ext = Path(output_file).suffix.lower()
        
        if output_ext == '.json':
            output_data = {
                'metadata': {
                    'total_questions': len(results),
                    'generated_at': pd.Timestamp.now().isoformat(),
                    'model': 'gpt-4o'
                },
                'answers': results
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                
        elif output_ext == '.xlsx':
            df = pd.DataFrame(results)
            df.to_excel(output_file, index=False, sheet_name='Generated_Answers')
            
        elif output_ext == '.csv':
            df = pd.DataFrame(results)
            df.to_csv(output_file, index=False, encoding='utf-8')
            
        else:
            # Default to JSON
            self.save_results(results, output_file.rsplit('.', 1)[0] + '.json')
    
    def create_populated_answer_sheet(self, original_file: str, output_file: str, context: str = "audit") -> str:
        """
        Create a new answer sheet with LLM-generated answers populated
        """
        print(f"Creating populated answer sheet from: {original_file}")
        
        # First, generate answers
        temp_answers_file = "temp_generated_answers.json"
        self.process_questions_file(original_file, temp_answers_file, context)
        
        # Load generated answers
        with open(temp_answers_file, 'r') as f:
            answers_data = json.load(f)
        
        # Create answer mapping
        answer_mapping = {
            result['questionId']: result['generatedAnswer'] 
            for result in answers_data['answers']
        }
        
        # Read original file and add answers
        file_ext = Path(original_file).suffix.lower()
        
        if file_ext in ['.xlsx', '.csv']:
            from answer_sheet_converter import AnswerSheetConverter
            converter = AnswerSheetConverter()
            df = converter.read_answer_sheet(original_file)
            
            # Add generated answers column
            df['Generated_Answer'] = df.apply(
                lambda row: answer_mapping.get(f"Q{row.name + 1}", "Answer not generated"), 
                axis=1
            )
            
            # Save populated sheet
            if output_file.endswith('.xlsx'):
                df.to_excel(output_file, index=False, sheet_name='Populated_Answers')
            else:
                df.to_csv(output_file, index=False, encoding='utf-8')
        
        # Cleanup temp file
        if os.path.exists(temp_answers_file):
            os.remove(temp_answers_file)
        
        print(f"Populated answer sheet saved to: {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description='Generate audit answers using LLM')
    parser.add_argument('--input', '-i', help='Input questions file (JSON, Excel, CSV)')
    parser.add_argument('--output', '-o', help='Output file for generated answers')
    parser.add_argument('--context', '-c', default='organizational audit', 
                       help='Audit context for better answer generation')
    parser.add_argument('--delay', '-d', type=float, default=1.0, 
                       help='Delay between API calls in seconds (default: 1.0)')
    parser.add_argument('--populate-sheet', action='store_true', 
                       help='Create populated answer sheet instead of separate answers file')
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    
    args = parser.parse_args()
    
    if not args.input:
        print("Error: Input file is required")
        parser.print_help()
        return
    
    if not args.output:
        # Generate default output filename
        input_path = Path(args.input)
        if args.populate_sheet:
            args.output = f"{input_path.stem}_populated{input_path.suffix}"
        else:
            args.output = f"{input_path.stem}_answers.json"
    
    try:
        generator = LLMAnswerGenerator(api_key=args.api_key)
        
        if args.populate_sheet:
            generator.create_populated_answer_sheet(args.input, args.output, args.context)
        else:
            generator.process_questions_file(args.input, args.output, args.context, args.delay)
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())