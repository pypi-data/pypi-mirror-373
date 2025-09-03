# ask_ai_to_analze.py


# to run python -m extracthero.ask_ai_to_analyze

import json
import sys
from datetime import datetime
from extracthero.myllmservice import MyLLMService

def analyze_filter_experiment(json_file_path):
    """
    Analyze filter strategy experiment results using LLM analysis.
    
    Parameters
    ----------
    json_file_path : str
        Path to the experiment results JSON file
    """
    
    print("🔬 Starting Filter Strategy Experiment Analysis")
    print(f"📁 Reading experiment data from: {json_file_path}")
    
    # Load experiment data
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            experiment_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File {json_file_path} not found!")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file - {e}")
        return
    
    # Initialize LLM service
    llm = MyLLMService()
    
    # Get experiment runs
    experiments = experiment_data.get("runs", [])
    total_experiments = len(experiments)
    
    print(f"📊 Found {total_experiments} experiment runs")
    print(f"🧪 Experiment info: {experiment_data.get('experiment_info', {}).get('timestamp', 'Unknown')}")
    print("-" * 60)
    
    # Analyze individual experiments
    print("🔍 Analyzing individual experiments...")
    individual_results = []
    
    for i, exp in enumerate(experiments, 1):
        print(f"  📋 Analyzing run {i}/{total_experiments} (Strategy: {exp.get('strategy', 'Unknown')}, Iteration: {exp.get('iteration', 'Unknown')})... ", end="", flush=True)
        
        try:
            # Call individual analysis
            generation_result = llm.analyze_individual_filter_prompt_experiment(exp)
            individual_result = generation_result.content
            individual_results.append({
                "run_id": exp.get("run_id"),
                "strategy": exp.get("strategy"),
                "iteration": exp.get("iteration"),
                "analysis": individual_result,
                "success": generation_result.success,
                "timestamp": datetime.now().isoformat()
            })
            
            status = "✅" if generation_result.success else "❌"
            print(f"{status}")
            
        except Exception as e:
            print(f"❌ Exception: {str(e)[:50]}...")
            individual_results.append({
                "run_id": exp.get("run_id"),
                "strategy": exp.get("strategy"), 
                "iteration": exp.get("iteration"),
                "analysis": None,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    # Save individual results for debugging
    individual_results_filename = f"individual_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    print(f"\n💾 Saving individual analysis results to: {individual_results_filename}")
    
    with open(individual_results_filename, 'w', encoding='utf-8') as f:
        json.dump({
            "source_experiment": json_file_path,
            "analysis_timestamp": datetime.now().isoformat(),
            "total_analyses": len(individual_results),
            "successful_analyses": len([r for r in individual_results if r["success"]]),
            "individual_results": individual_results
        }, f, indent=2, ensure_ascii=False)
    
    # Merge individual results with delimiters
    print("🔗 Merging individual results for overall analysis...")
    
    merged_results = []
    for i, result in enumerate(individual_results, 1):
        strategy = result.get("strategy", "unknown")
        iteration = result.get("iteration", "unknown")
        run_id = result.get("run_id", "unknown")
        analysis = result.get("analysis", "Analysis failed")
        
        delimiter = f"----exp{i}---- (Strategy: {strategy}, Iteration: {iteration}, Run ID: {run_id})"
        merged_results.append(delimiter)
        merged_results.append(str(analysis))
        merged_results.append("")  # Empty line for readability
    
    merged_string = "\n".join(merged_results)
    
    # Perform overall analysis
    print("🧠 Performing overall experiment analysis...")
    
    try:
        generation_result = llm.analyze_filter_prompt_experiment(merged_string)
        overall_result = generation_result.content
        
        print("\n" + "="*80)
        print("🎯 OVERALL ANALYSIS RESULTS")
        print("="*80)
        print(overall_result)
        print("="*80)
        
        # Save overall analysis
        overall_filename = f"overall_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(overall_filename, 'w', encoding='utf-8') as f:
            f.write("Filter Strategy Experiment - Overall Analysis\n")
            f.write("="*60 + "\n\n")
            f.write(f"Source Data: {json_file_path}\n")
            f.write(f"Analysis Date: {datetime.now().isoformat()}\n")
            f.write(f"Total Experiments Analyzed: {len(individual_results)}\n")
            f.write(f"Successful Individual Analyses: {len([r for r in individual_results if r['success']])}\n\n")
            f.write("OVERALL ANALYSIS:\n")
            f.write("-"*20 + "\n")
            f.write(overall_result)
        
        print(f"\n📁 Overall analysis saved to: {overall_filename}")
        print(f"📁 Individual analyses saved to: {individual_results_filename}")
        
        return {
            "overall_result": overall_result,
            "individual_results": individual_results,
            "overall_filename": overall_filename,
            "individual_filename": individual_results_filename
        }
        
    except Exception as e:
        print(f"❌ Error in overall analysis: {e}")
        return None
    

def run_overall_analyze_only(individual_results_json, overall_results_filename=None):
    """
    Run overall analysis part only using previously generated individual results.
    
    Parameters
    ----------
    individual_results_json : str
        Path to the individual analysis results JSON file
    overall_results_filename : str, optional
        Custom filename for overall analysis results. If None, auto-generates timestamp-based name.
    """
    
    print("🔬 Starting Overall Analysis Only")
    print(f"📁 Reading individual analysis results from: {individual_results_json}")
    
    # Load individual analysis results
    try:
        with open(individual_results_json, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File {individual_results_json} not found!")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file - {e}")
        return
    
    # Initialize LLM service
    llm = MyLLMService()
    
    # Extract individual results
    individual_results = analysis_data.get("individual_results", [])
    total_results = len(individual_results)
    
    if total_results == 0:
        print("❌ Error: No individual results found in the JSON file!")
        return
    
    print(f"📊 Found {total_results} individual analysis results")
    successful_analyses = len([r for r in individual_results if r.get("success", False)])
    print(f"✅ {successful_analyses}/{total_results} analyses were successful")
    
    # Merge individual results with delimiters
    print("🔗 Merging individual results for overall analysis...")
    
    merged_results = []
    for i, result in enumerate(individual_results, 1):
        strategy = result.get("strategy", "unknown")
        iteration = result.get("iteration", "unknown")
        run_id = result.get("run_id", "unknown")
        analysis = result.get("analysis", "Analysis not available")
        success = result.get("success", False)
        
        # Create delimiter with experiment info
        delimiter = f"----exp{i}---- (Strategy: {strategy}, Iteration: {iteration}, Run ID: {run_id}, Success: {success})"
        merged_results.append(delimiter)
        merged_results.append(str(analysis))
        merged_results.append("")  # Empty line for readability
    
    merged_string = "\n".join(merged_results)
    
    # Perform overall analysis
    print("🧠 Performing overall experiment analysis...")
    
    try:
        
        generation_result = llm.analyze_filter_prompt_experiment_overall(merged_string)
        overall_result = generation_result.content
        
        print("\n" + "="*80)
        print("🎯 OVERALL ANALYSIS RESULTS")
        print("="*80)
        print(overall_result)
        print("="*80)
        
        # Determine output filename
        if overall_results_filename is None:
            overall_filename = f"overall_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        else:
            overall_filename = overall_results_filename
        
        # Save overall analysis
        with open(overall_filename, 'w', encoding='utf-8') as f:
            f.write("Filter Strategy Experiment - Overall Analysis\n")
            f.write("="*60 + "\n\n")
            f.write(f"Source Data: {individual_results_json}\n")
            f.write(f"Analysis Date: {datetime.now().isoformat()}\n")
            f.write(f"Total Individual Analyses: {total_results}\n")
            f.write(f"Successful Individual Analyses: {successful_analyses}\n")
            f.write(f"Source Experiment Info: {analysis_data.get('source_experiment', 'Unknown')}\n\n")
            f.write("OVERALL ANALYSIS:\n")
            f.write("-"*20 + "\n")
            f.write(overall_result)
        
        print(f"\n📁 Overall analysis saved to: {overall_filename}")
        
        return {
            "overall_result": overall_result,
            "overall_filename": overall_filename,
            "total_analyses": total_results,
            "successful_analyses": successful_analyses,
            "source_file": individual_results_json
        }
        
    except Exception as e:
        print(f"❌ Error in overall analysis: {e}")
        return None
    



def main_overall_only():
    """Main function to run overall analysis only."""
    
   
    
    individual_results_json = "/Users/ns/Desktop/projects/extracthero/individual_analysis_20250710_164134.json"
    overall_results_filename = None
    
    result = run_overall_analyze_only(individual_results_json, overall_results_filename)
    
    if result:
        print("\n✨ Overall analysis completed successfully!")
        print(f"📄 Results saved to: {result['overall_filename']}")
        print(f"📊 Analyzed {result['successful_analyses']}/{result['total_analyses']} successful individual results")
    else:
        print("\n❌ Overall analysis failed!")
        sys.exit(1)



def main():
    """Main function to run the analysis script."""
    
    json_file_path="/Users/ns/Desktop/projects/extracthero/filter_strategy_experiment_20250710_154903.json"

    individual_anaylis_json_file_path=""


    
    # json_file_path = "./extracthero/filter_strategy_experiment_20250710_154903.json"
    result = analyze_filter_experiment(json_file_path)

    result = analyze_filter_experiment(json_file_path)
    
    if result:
        print("\n✨ Analysis completed successfully!")
    else:
        print("\n❌ Analysis failed!")
        sys.exit(1)

if __name__ == "__main__":
    # main()
    main_overall_only()