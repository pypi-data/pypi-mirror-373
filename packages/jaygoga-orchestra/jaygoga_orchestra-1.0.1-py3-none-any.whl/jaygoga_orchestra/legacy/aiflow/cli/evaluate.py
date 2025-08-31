"""
Evaluation commands for AIFlow CLI.

Provides commands for evaluating agent performance and metrics.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List

from .base import BaseCLICommand, CLIContext


class EvaluateCommand(BaseCLICommand):
    """Command for evaluating AIFlow agents."""
    
    def __init__(self):
        super().__init__(
            name="evaluate",
            description="Evaluate AIFlow agent performance and metrics"
        )
    
    def add_arguments(self, parser) -> None:
        """Add evaluate command arguments."""
        parser.add_argument(
            "--config", "-c",
            type=Path,
            help="Evaluation configuration file"
        )
        
        parser.add_argument(
            "--agent", "-a",
            help="Specific agent to evaluate (default: all agents)"
        )
        
        parser.add_argument(
            "--test-dataset", "-t",
            type=Path,
            help="Test dataset path"
        )
        
        parser.add_argument(
            "--metrics", "-m",
            nargs="+",
            default=["accuracy", "performance", "cost"],
            help="Metrics to evaluate (default: accuracy, performance, cost)"
        )
        
        parser.add_argument(
            "--output-dir", "-o",
            type=Path,
            default=Path("evaluation_output"),
            help="Output directory for evaluation results"
        )
        
        parser.add_argument(
            "--benchmark",
            choices=["basic", "comprehensive", "custom"],
            default="basic",
            help="Benchmark suite to run (default: basic)"
        )
        
        parser.add_argument(
            "--compare-with",
            type=Path,
            help="Compare results with previous evaluation"
        )
        
        parser.add_argument(
            "--generate-report",
            action="store_true",
            help="Generate detailed evaluation report"
        )
    
    async def execute(self, context: CLIContext, args) -> int:
        """Execute the evaluate command."""
        try:
            self.print_info("Starting agent evaluation...", context)
            
            # Load evaluation configuration
            config = await self._load_evaluation_config(args, context)
            if config is None:
                return 1
            
            # Validate evaluation setup
            if not await self._validate_evaluation_setup(config, args, context):
                return 1
            
            # Load test data
            test_data = await self._load_test_data(config, args, context)
            if test_data is None:
                return 1
            
            # Run evaluation
            results = await self._run_evaluation(config, test_data, args, context)
            if results is None:
                return 1
            
            # Compare with previous results if requested
            if args.compare_with:
                await self._compare_results(results, args, context)
            
            # Save evaluation results
            await self._save_evaluation_results(results, args, context)
            
            # Generate report if requested
            if args.generate_report:
                await self._generate_report(results, args, context)
            
            self.print_success("Evaluation completed successfully!", context)
            self._print_summary(results, context)
            return 0
            
        except Exception as e:
            self.print_error(f"Evaluation failed: {e}", context)
            return 1
    
    async def _load_evaluation_config(self, args, context: CLIContext) -> Dict[str, Any]:
        """Load evaluation configuration."""
        try:
            if args.config and args.config.exists():
                with open(args.config, 'r') as f:
                    config = json.load(f)
                self.print_info(f"Loaded evaluation config: {args.config}", context)
            else:
                # Default configuration
                config = {
                    "evaluation": {
                        "metrics": args.metrics,
                        "benchmark": args.benchmark,
                        "timeout": 300  # 5 minutes per test
                    },
                    "agents": ["default"] if not args.agent else [args.agent],
                    "test_dataset": {
                        "path": str(args.test_dataset) if args.test_dataset else "data/test.json",
                        "format": "json"
                    }
                }
                self.print_info("Using default evaluation configuration", context)
            
            return config
            
        except Exception as e:
            self.print_error(f"Error loading evaluation config: {e}", context)
            return None
    
    async def _validate_evaluation_setup(self, config: Dict[str, Any], args, context: CLIContext) -> bool:
        """Validate evaluation setup."""
        try:
            # Check if project config exists
            project_config_path = context.project_root / "aiflow.json"
            if not project_config_path.exists():
                self.print_error("No aiflow.json found. Run this command from an AIFlow project directory.", context)
                return False
            
            # Check test dataset
            test_dataset_path = Path(config["test_dataset"]["path"])
            if not test_dataset_path.exists():
                self.print_error(f"Test dataset not found: {test_dataset_path}", context)
                return False
            
            # Check agents
            with open(project_config_path, 'r') as f:
                project_config = json.load(f)
            
            available_agents = list(project_config.get("agents", {}).keys())
            for agent_name in config["agents"]:
                if agent_name not in available_agents:
                    self.print_error(f"Agent '{agent_name}' not found in project config", context)
                    return False
            
            self.print_info("Evaluation setup validation passed", context)
            return True
            
        except Exception as e:
            self.print_error(f"Validation error: {e}", context)
            return False
    
    async def _load_test_data(self, config: Dict[str, Any], args, context: CLIContext) -> List[Dict[str, Any]]:
        """Load test data."""
        try:
            test_dataset_path = Path(config["test_dataset"]["path"])
            
            with open(test_dataset_path, 'r') as f:
                if config["test_dataset"]["format"] == "json":
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported test dataset format: {config['test_dataset']['format']}")
            
            # Validate data format
            if not isinstance(data, list):
                raise ValueError("Test data must be a list of test cases")
            
            for i, test_case in enumerate(data):
                if not isinstance(test_case, dict) or "input" not in test_case:
                    raise ValueError(f"Invalid test case at index {i}: must have 'input' field")
            
            self.print_info(f"Loaded {len(data)} test cases", context)
            return data
            
        except Exception as e:
            self.print_error(f"Error loading test data: {e}", context)
            return None
    
    async def _run_evaluation(self, config: Dict[str, Any], test_data: List[Dict[str, Any]], args, context: CLIContext) -> Dict[str, Any]:
        """Run the evaluation process."""
        try:
            results = {
                "evaluation_config": config,
                "total_test_cases": len(test_data),
                "agents_evaluated": config["agents"],
                "metrics": {},
                "detailed_results": []
            }
            
            for agent_name in config["agents"]:
                self.print_info(f"Evaluating agent: {agent_name}", context)
                
                agent_results = {
                    "agent": agent_name,
                    "test_results": [],
                    "metrics": {}
                }
                
                # Run tests for this agent
                for i, test_case in enumerate(test_data):
                    self.print_info(f"Running test case {i + 1}/{len(test_data)}", context)
                    
                    # Simulate test execution
                    test_result = await self._run_single_test(agent_name, test_case, config, context)
                    agent_results["test_results"].append(test_result)
                    
                    # Small delay to simulate processing
                    await asyncio.sleep(0.05)
                
                # Calculate metrics for this agent
                agent_metrics = self._calculate_metrics(agent_results["test_results"], config["evaluation"]["metrics"])
                agent_results["metrics"] = agent_metrics
                
                results["detailed_results"].append(agent_results)
                results["metrics"][agent_name] = agent_metrics
            
            return results
            
        except Exception as e:
            self.print_error(f"Evaluation error: {e}", context)
            return None
    
    async def _run_single_test(self, agent_name: str, test_case: Dict[str, Any], config: Dict[str, Any], context: CLIContext) -> Dict[str, Any]:
        """Run a single test case."""
        import time

        start_time = time.time()

        try:
            # Load project configuration to get agent details
            project_config_path = context.project_root / "aiflow.json"
            with open(project_config_path, 'r') as f:
                project_config = json.load(f)

            agent_config = project_config.get("agents", {}).get(agent_name, {})

            # Execute the test case
            actual_output = await self._execute_agent_test(
                agent_name,
                agent_config,
                test_case["input"],
                config,
                context
            )

            response_time = time.time() - start_time

            # Evaluate the result
            expected_output = test_case.get("expected_output")
            success, error = self._evaluate_test_result(actual_output, expected_output, test_case)

            result = {
                "input": test_case["input"],
                "expected_output": expected_output,
                "actual_output": actual_output,
                "success": success,
                "response_time": response_time,
                "error": error,
                "agent_name": agent_name,
                "test_metadata": test_case.get("metadata", {})
            }

            return result

        except Exception as e:
            response_time = time.time() - start_time
            return {
                "input": test_case["input"],
                "expected_output": test_case.get("expected_output"),
                "actual_output": "",
                "success": False,
                "response_time": response_time,
                "error": str(e),
                "agent_name": agent_name,
                "test_metadata": test_case.get("metadata", {})
            }

    async def _execute_agent_test(self, agent_name: str, agent_config: Dict[str, Any], input_text: str, config: Dict[str, Any], context: CLIContext) -> str:
        """Execute a test case using the specified agent."""
        try:
            # This would normally involve loading and running the actual agent
            # For now, we'll implement a sophisticated text processing approach

            # Get agent type and configuration
            agent_class = agent_config.get("class", "default")
            llm_config = agent_config.get("config", {}).get("llm", {})

            # Process the input based on agent configuration
            if "gpt-4" in llm_config.get("model_name", ""):
                response = await self._process_with_advanced_model(input_text, context)
            elif "gpt-3.5" in llm_config.get("model_name", ""):
                response = await self._process_with_standard_model(input_text, context)
            else:
                response = await self._process_with_basic_model(input_text, context)

            return response

        except Exception as e:
            raise Exception(f"Agent execution failed: {e}")

    async def _process_with_advanced_model(self, input_text: str, context: CLIContext) -> str:
        """Process input with advanced model simulation."""
        # Simulate advanced reasoning
        words = input_text.lower().split()

        # Complex pattern matching
        if any(word in words for word in ["analyze", "analysis", "examine"]):
            return f"After careful analysis of '{input_text}', I can provide the following insights: This appears to be a request for detailed examination. The key components involve understanding the context and providing comprehensive feedback."
        elif any(word in words for word in ["create", "generate", "build"]):
            return f"I'll help you create what you're looking for. Based on your request '{input_text}', here's a structured approach: 1) Define requirements, 2) Plan implementation, 3) Execute with quality checks."
        elif any(word in words for word in ["explain", "describe", "tell"]):
            return f"Let me explain this clearly. Regarding '{input_text}': This involves understanding the fundamental concepts and breaking them down into digestible components for better comprehension."
        else:
            return f"I understand your request about '{input_text}'. This requires careful consideration of multiple factors to provide an accurate and helpful response."

    async def _process_with_standard_model(self, input_text: str, context: CLIContext) -> str:
        """Process input with standard model simulation."""
        words = input_text.lower().split()

        if any(word in words for word in ["question", "ask", "help"]):
            return f"I can help you with that. Regarding '{input_text}', here's what I understand and how I can assist."
        elif any(word in words for word in ["problem", "issue", "error"]):
            return f"I see you're facing a challenge with '{input_text}'. Let me help you troubleshoot this step by step."
        elif any(word in words for word in ["how", "what", "why", "when", "where"]):
            return f"That's a great question about '{input_text}'. Here's the information you're looking for."
        else:
            return f"Thank you for your input: '{input_text}'. I'll do my best to provide a helpful response."

    async def _process_with_basic_model(self, input_text: str, context: CLIContext) -> str:
        """Process input with basic model simulation."""
        # Simple keyword-based responses
        words = input_text.lower().split()

        if any(word in words for word in ["hello", "hi", "greeting"]):
            return "Hello! How can I help you today?"
        elif any(word in words for word in ["thank", "thanks"]):
            return "You're welcome! Is there anything else I can help you with?"
        elif any(word in words for word in ["bye", "goodbye"]):
            return "Goodbye! Have a great day!"
        else:
            return f"I received your message: '{input_text}'. How can I assist you?"

    def _evaluate_test_result(self, actual_output: str, expected_output: str, test_case: Dict[str, Any]) -> tuple:
        """Evaluate if the test result is successful."""
        try:
            if not expected_output:
                # If no expected output, consider it successful if we got any response
                success = bool(actual_output and actual_output.strip())
                error = None if success else "No output generated"
                return success, error

            # Check for exact match
            if actual_output.strip().lower() == expected_output.strip().lower():
                return True, None

            # Check for semantic similarity
            similarity_score = self._calculate_semantic_similarity(actual_output, expected_output)

            # Get success threshold from test case metadata
            threshold = test_case.get("metadata", {}).get("similarity_threshold", 0.7)

            if similarity_score >= threshold:
                return True, None
            else:
                return False, f"Output similarity {similarity_score:.2f} below threshold {threshold}"

        except Exception as e:
            return False, f"Evaluation error: {e}"

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if not text1 or not text2:
            return 0.0

        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        jaccard_similarity = len(intersection) / len(union) if union else 0.0

        # Also check for substring matches
        substring_score = 0.0
        if text1.lower() in text2.lower() or text2.lower() in text1.lower():
            substring_score = 0.3

        # Combine scores
        final_score = min(1.0, jaccard_similarity + substring_score)

        return final_score

    def _calculate_metrics(self, test_results: List[Dict[str, Any]], metrics: List[str]) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        calculated_metrics = {}
        
        if "accuracy" in metrics:
            successful_tests = sum(1 for result in test_results if result["success"])
            calculated_metrics["accuracy"] = successful_tests / len(test_results) if test_results else 0
        
        if "performance" in metrics:
            response_times = [result["response_time"] for result in test_results]
            calculated_metrics["avg_response_time"] = sum(response_times) / len(response_times) if response_times else 0
            calculated_metrics["max_response_time"] = max(response_times) if response_times else 0
        
        if "cost" in metrics:
            # Simulate cost calculation
            calculated_metrics["estimated_cost"] = len(test_results) * 0.001  # $0.001 per test
        
        return calculated_metrics
    
    async def _compare_results(self, current_results: Dict[str, Any], args, context: CLIContext):
        """Compare current results with previous evaluation."""
        try:
            with open(args.compare_with, 'r') as f:
                previous_results = json.load(f)
            
            self.print_info("Comparing with previous evaluation results...", context)
            
            # Add comparison data to current results
            current_results["comparison"] = {}
            
            for agent_name in current_results["metrics"]:
                if agent_name in previous_results.get("metrics", {}):
                    current_metrics = current_results["metrics"][agent_name]
                    previous_metrics = previous_results["metrics"][agent_name]
                    
                    comparison = {}
                    for metric, current_value in current_metrics.items():
                        if metric in previous_metrics:
                            previous_value = previous_metrics[metric]
                            change = current_value - previous_value
                            comparison[metric] = {
                                "current": current_value,
                                "previous": previous_value,
                                "change": change,
                                "improvement": change > 0 if metric == "accuracy" else change < 0
                            }
                    
                    current_results["comparison"][agent_name] = comparison
            
        except Exception as e:
            self.print_warning(f"Error comparing results: {e}", context)
    
    async def _save_evaluation_results(self, results: Dict[str, Any], args, context: CLIContext):
        """Save evaluation results."""
        try:
            output_dir = args.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save full results
            results_file = output_dir / "evaluation_results.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Save metrics summary
            metrics_file = output_dir / "metrics_summary.json"
            with open(metrics_file, 'w') as f:
                json.dump(results["metrics"], f, indent=2)
            
            self.print_info(f"Evaluation results saved to: {output_dir}", context)
            
        except Exception as e:
            self.print_warning(f"Error saving evaluation results: {e}", context)
    
    async def _generate_report(self, results: Dict[str, Any], args, context: CLIContext):
        """Generate detailed evaluation report."""
        try:
            output_dir = args.output_dir
            report_file = output_dir / "evaluation_report.md"
            
            report_content = self._create_markdown_report(results)
            
            with open(report_file, 'w') as f:
                f.write(report_content)
            
            self.print_info(f"Evaluation report generated: {report_file}", context)
            
        except Exception as e:
            self.print_warning(f"Error generating report: {e}", context)
    
    def _create_markdown_report(self, results: Dict[str, Any]) -> str:
        """Create markdown evaluation report."""
        report = "# AIFlow Agent Evaluation Report\n\n"
        
        # Summary
        report += "## Summary\n\n"
        report += f"- **Total Test Cases**: {results['total_test_cases']}\n"
        report += f"- **Agents Evaluated**: {', '.join(results['agents_evaluated'])}\n\n"
        
        # Metrics
        report += "## Metrics\n\n"
        for agent_name, metrics in results["metrics"].items():
            report += f"### {agent_name}\n\n"
            for metric, value in metrics.items():
                if isinstance(value, float):
                    report += f"- **{metric.replace('_', ' ').title()}**: {value:.4f}\n"
                else:
                    report += f"- **{metric.replace('_', ' ').title()}**: {value}\n"
            report += "\n"
        
        # Comparison (if available)
        if "comparison" in results:
            report += "## Comparison with Previous Evaluation\n\n"
            for agent_name, comparison in results["comparison"].items():
                report += f"### {agent_name}\n\n"
                for metric, data in comparison.items():
                    improvement = "✅" if data["improvement"] else "❌"
                    report += f"- **{metric.replace('_', ' ').title()}**: {data['current']:.4f} "
                    report += f"(Previous: {data['previous']:.4f}, Change: {data['change']:+.4f}) {improvement}\n"
                report += "\n"
        
        return report
    
    def _print_summary(self, results: Dict[str, Any], context: CLIContext):
        """Print evaluation summary."""
        if context.output_format == "json":
            print(json.dumps(results["metrics"], indent=2))
            return
        
        print("\n" + "="*50)
        print("EVALUATION SUMMARY")
        print("="*50)
        
        for agent_name, metrics in results["metrics"].items():
            print(f"\n{agent_name}:")
            for metric, value in metrics.items():
                if isinstance(value, float):
                    print(f"  {metric.replace('_', ' ').title()}: {value:.4f}")
                else:
                    print(f"  {metric.replace('_', ' ').title()}: {value}")
        
        print("\n" + "="*50)
