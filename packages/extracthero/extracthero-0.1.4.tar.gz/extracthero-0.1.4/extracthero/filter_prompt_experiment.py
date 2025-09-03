# filter_strategy_experiment.py

# to run python -m extracthero.filter_prompt_experiment

import json
import time
from datetime import datetime
from extracthero.schemas import WhatToRetain
from extracthero.utils import load_html
from extracthero.filterhero import FilterHero

def run_filter_strategy_experiment():
    """
    Run comprehensive filter strategy experiment.
    Tests each strategy 10 times and saves detailed results.
    """
    
    # Setup
    filter_hero = FilterHero()
    specs = [
        WhatToRetain(
            name="voltage",
            desc="all information about voltage",
            include_context_chunk=False,
        )
    ]
    
    html_doc = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")
    filter_strategy_prompts = ["liberal", "inclusive", "contextual", "recall"]
    
    # Results container
    experiment_results = {
        "experiment_info": {
            "timestamp": datetime.now().isoformat(),
            "total_runs": len(filter_strategy_prompts) * 10,
            "strategies_tested": filter_strategy_prompts,
            "iterations_per_strategy": 10,
            "test_spec": {
                "name": "voltage",
                "desc": "all information about voltage",
                "include_context_chunk": False
            },
            "html_source": "extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html"
        },
        "runs": []
    }
    
    print("🧪 Starting Filter Strategy Experiment")
    print(f"📊 Testing {len(filter_strategy_prompts)} strategies × 10 iterations = {len(filter_strategy_prompts) * 10} total runs")
    print("-" * 60)
    
    total_runs = 0
    
    # Run experiments
    for iteration in range(1, 11):  # 1-10
        print(f"\n🔄 Iteration {iteration}/10")
        
        for strategy in filter_strategy_prompts:
            total_runs += 1
            print(f"  📋 Testing {strategy}... ", end="", flush=True)
            
            # Record start time
            run_start_time = time.time()
            
            try:
                # Run the filter operation
                filter_op = filter_hero.run(
                    html_doc, 
                    specs, 
                    text_type="html", 
                    filter_strategy=strategy
                )
                
                # Calculate run duration
                run_duration = time.time() - run_start_time
                
                # Extract comprehensive metrics
                run_result = {
                    "run_id": total_runs,
                    "iteration": iteration,
                    "strategy": strategy,
                    "timestamp": datetime.now().isoformat(),
                    "run_duration_seconds": round(run_duration, 4),
                    
                    # Core results
                    "success": filter_op.success,
                    "content": filter_op.content,
                    "content_length": len(str(filter_op.content)) if filter_op.content else 0,
                    "error": filter_op.error,
                    
                    # Performance metrics
                    "elapsed_time": filter_op.elapsed_time,
                    "filtered_data_token_size": filter_op.filtered_data_token_size,
                    
                    # Usage/cost information
                    "usage": filter_op.usage,
                    
                    # Model information
                    "model_name": getattr(filter_op.generation_result, 'model', None) if filter_op.generation_result else None
                }
                
                # Quick success indicator
                status = "✅" if filter_op.success else "❌"
                content_preview = str(filter_op.content)[:50] + "..." if filter_op.content else "None"
                print(f"{status} ({run_result['content_length']} chars)")
                
            except Exception as e:
                # Handle any errors during execution
                run_result = {
                    "run_id": total_runs,
                    "iteration": iteration,
                    "strategy": strategy,
                    "timestamp": datetime.now().isoformat(),
                    "run_duration_seconds": round(time.time() - run_start_time, 4),
                    "success": False,
                    "content": None,
                    "content_length": 0,
                    "error": str(e),
                    "exception_occurred": True
                }
                print(f"❌ Exception: {str(e)[:50]}...")
            
            # Add to results
            experiment_results["runs"].append(run_result)
    
    # Calculate summary statistics
    strategy_stats = {}
    for strategy in filter_strategy_prompts:
        strategy_runs = [r for r in experiment_results["runs"] if r["strategy"] == strategy]
        
        strategy_stats[strategy] = {
            "total_runs": len(strategy_runs),
            "successful_runs": len([r for r in strategy_runs if r["success"]]),
            "success_rate": len([r for r in strategy_runs if r["success"]]) / len(strategy_runs),
            "average_content_length": sum(r["content_length"] for r in strategy_runs) / len(strategy_runs),
            "average_duration": sum(r["run_duration_seconds"] for r in strategy_runs) / len(strategy_runs),
            "average_tokens": None,
            "total_cost": None
        }
        
        # Calculate token averages (only for successful runs with token data)
        token_runs = [r for r in strategy_runs if r["success"] and r.get("filtered_data_token_size")]
        if token_runs:
            strategy_stats[strategy]["average_tokens"] = sum(r["filtered_data_token_size"] for r in token_runs) / len(token_runs)
        
        # Calculate cost totals (if usage data available)
        cost_runs = [r for r in strategy_runs if r.get("usage") and r["usage"]]
        if cost_runs:
            # This is a simplified cost calculation - adjust based on your actual usage structure
            total_cost = 0
            for run in cost_runs:
                if "cost" in run["usage"]:
                    total_cost += run["usage"]["cost"]
            strategy_stats[strategy]["total_cost"] = total_cost
    
    experiment_results["summary_statistics"] = strategy_stats
    
    # Save results to JSON file
    filename = f"filter_strategy_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(experiment_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Experiment completed!")
    print(f"📁 Results saved to: {filename}")
    print(f"📊 Total runs: {total_runs}")
    
    # Print quick summary
    print("\n📈 Quick Summary:")
    for strategy, stats in strategy_stats.items():
        print(f"  {strategy:12} | Success: {stats['success_rate']:5.1%} | Avg Length: {stats['average_content_length']:6.0f} chars | Avg Time: {stats['average_duration']:.3f}s")
    
    return filename, experiment_results

if __name__ == "__main__":
    filename, results = run_filter_strategy_experiment()
    print(f"\n✨ Upload {filename} for detailed analysis!")