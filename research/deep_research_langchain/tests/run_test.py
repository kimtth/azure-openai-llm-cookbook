#!/usr/bin/env python
import os
import subprocess
import sys
import argparse

''' 
Example w/ o3 -- 
python tests/run_test.py --all \
    --supervisor-model "openai:o3" \
    --researcher-model "openai:o3" \
    --planner-provider "openai" \
    --planner-model "o3" \
    --writer-provider "openai" \
    --writer-model "o3" \
    --eval-model "openai:o3" \
    --search-api "tavily"

Example w/ gpt-4.1 -- 
python tests/run_test.py --all \
    --supervisor-model "openai:gpt-4.1" \
    --researcher-model "openai:gpt-4.1" \
    --planner-provider "openai" \
    --planner-model "gpt-4.1" \
    --writer-provider "openai" \
    --writer-model "gpt-4.1" \
    --eval-model "openai:o3" \
    --search-api "tavily"
'''

def main():
    # LangSmith project name for report quality testing
    langsmith_project = "Open Deep Research: Report Quality Testing"

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run report quality tests for different agents")
    parser.add_argument("--rich-output", action="store_true", help="Show rich output in terminal")
    parser.add_argument("--experiment-name", help="Name for the LangSmith experiment")
    parser.add_argument("--agent", choices=["multi_agent", "graph"], help="Run tests for a specific agent")
    parser.add_argument("--all", action="store_true", help="Run tests for all agents")
    
    # Model configuration options
    parser.add_argument("--supervisor-model", help="Model for supervisor agent (e.g., 'anthropic:claude-3-7-sonnet-latest')")
    parser.add_argument("--researcher-model", help="Model for researcher agent (e.g., 'anthropic:claude-3-5-sonnet-latest')")
    parser.add_argument("--planner-provider", help="Provider for planner model (e.g., 'anthropic')")
    parser.add_argument("--planner-model", help="Model for planner in graph-based agent (e.g., 'claude-3-7-sonnet-latest')")
    parser.add_argument("--writer-provider", help="Provider for writer model (e.g., 'anthropic')")
    parser.add_argument("--writer-model", help="Model for writer in graph-based agent (e.g., 'claude-3-5-sonnet-latest')")
    parser.add_argument("--eval-model", help="Model for evaluating report quality (default: openai:gpt-4-turbo)")
    
    # Search API configuration
    parser.add_argument("--search-api", choices=["tavily", "duckduckgo"], 
                        help="Search API to use for content retrieval")
    
    args = parser.parse_args()
    
    # Base pytest options
    base_pytest_options = ["-v", "--disable-warnings", "--langsmith-output"]
    if args.rich_output:
        base_pytest_options.append("--rich-output")
    
    # Define available agents
    agents = ["multi_agent", "graph"]
    
    # Determine which agents to test
    if args.agent:
        if args.agent in agents:
            agents_to_test = [args.agent]
        else:
            print(f"Error: Unknown agent '{args.agent}'")
            print(f"Available agents: {', '.join(agents)}")
            return 1
    elif args.all:
        agents_to_test = agents
    else:
        # Default to testing all agents
        agents_to_test = agents
    
    # Run tests for each agent
    for agent in agents_to_test:
        print(f"\nRunning tests for {agent}...")
        
        # Set up LangSmith environment for this agent
        os.environ["LANGSMITH_PROJECT"] = langsmith_project
        os.environ["LANGSMITH_TEST_SUITE"] = langsmith_project
        
        # Ensure tracing is enabled
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        
        # Create a fresh copy of the pytest options for this run
        pytest_options = base_pytest_options.copy()
        
        # We're now using direct pytest command line arguments instead of environment variables
        # No need to set environment variables for test parameters
        
        # Test file path
        test_file = "tests/test_report_quality.py"
                    
        # Set up experiment name
        experiment_name = args.experiment_name if args.experiment_name else f"Report Quality Test | Agent: {agent}"
        print(f"   Project: {langsmith_project}")
        print(f"   Experiment: {experiment_name}")
        
        os.environ["LANGSMITH_EXPERIMENT"] = experiment_name
        
        print(f"\nℹ️ Test results for {agent} are being logged to LangSmith")
        
        # Run the test with direct pytest arguments instead of environment variables
        cmd = ["python", "-m", "pytest", test_file] + pytest_options + [
            f"--research-agent={agent}"
        ]
        
        # Add model configurations if provided
        if args.supervisor_model:
            cmd.append(f"--supervisor-model={args.supervisor_model}")
        if args.researcher_model:
            cmd.append(f"--researcher-model={args.researcher_model}")
        if args.planner_provider:
            cmd.append(f"--planner-provider={args.planner_provider}")
        if args.planner_model:
            cmd.append(f"--planner-model={args.planner_model}")
        if args.writer_provider:
            cmd.append(f"--writer-provider={args.writer_provider}")
        if args.writer_model:
            cmd.append(f"--writer-model={args.writer_model}")
        if args.eval_model:
            cmd.append(f"--eval-model={args.eval_model}")
        if args.search_api:
            cmd.append(f"--search-api={args.search_api}")
            
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print test output with highlighting for section relevance analysis
        stdout = result.stdout
        
        # Highlight section relevance information with colors if supported
        if "POTENTIAL IRRELEVANT SECTIONS DETECTED" in stdout:
            # Extract and highlight the section relevance analysis
            import re
            section_analysis = re.search(r'⚠️ POTENTIAL IRRELEVANT SECTIONS DETECTED:.*?(?=\n\n|\Z)', 
                                         stdout, re.DOTALL)
            if section_analysis:
                analysis_text = section_analysis.group(0)
                # Use ANSI color codes for highlighting (red for irrelevant sections)
                highlighted_analysis = f"\033[1;31m{analysis_text}\033[0m"
                stdout = stdout.replace(analysis_text, highlighted_analysis)
        
        print(stdout)
        
        if result.stderr:
            print("Errors/warnings:")
            print(result.stderr)
            
        # Print a summary of section relevance issues
        if "POTENTIAL IRRELEVANT SECTIONS DETECTED" in result.stdout:
            print("\n\033[1;33m==== SECTION RELEVANCE ISSUES DETECTED ====\033[0m")
            print("Some sections may not be relevant to the main topic.")
            print("Review the detailed analysis in the test output above.")
            print("Consider updating the prompts to improve section relevance.")
                
if __name__ == "__main__":
    sys.exit(main() or 0)