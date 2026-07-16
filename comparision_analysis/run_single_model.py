"""
Workflow:
	1.Switch model in Copilot CLI UI
	2.Ask the agent: "run the MSFT 10-k scoring as [model_name]"
	3.The agent calls: python run_single_model.py --prepare --model gpt-4o (Outputs promots to score)
	4.The agent scores each prompt and calls:
		python run run_single_model.py --save --model gtp-4o --year 2024 --event COVID_19_Pandemic --result '{..}'
	5.After all 4 models done: python run_signle_model.py --report

Commands:
	python run_single_model.py --prepare   # Show what needs scoring
	python run_single_model.py --prompt --year 2024  --event COVID_19_Pandemic # Print a single prompt
	python run_single_model.py --save --model gtp-4o --year 2024 --event COVID_19_Pandemic --result-file result.json  # Show what needs scoring
	python run_single_model.py --prepare   
	python run_single_model.py --status   # Show scoring progress
	python run_single_model.py --report   # Generate HTML from all saved results
"""

import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DNA_DIR = BASE_DIR / "dna"
DATA_DIR = DNA_DIR / "Data"
LLM_DIR = DATA_DIR / "LLM"
TENK_DIR = DATA_DIR / "10-k" / "item_1a_7"
OUTPUT_DIR = BASE_DIR / "comparison_output"
RESULTS_DIR = BASE_DIR / "model_results"

MSFT_FILES = {
    2021: TENK_DIR / "MSFT_2021_07-29.txt",
    2022: TENK_DIR / "MSFT_2022_07-29.txt",
    2023: TENK_DIR / "MSFT_2023_07-29.txt",
    2024: TENK_DIR / "MSFT_2024_07-29.txt"
}

MODELS = ["gpt-5.3-codex","gemini-3.1-pro","claude-opus-4.5"]

# Load risk events

def load_risk_events():
    with open(LLM_DIR / "risk_events_8.json","r",encoding = "utf-8") as f:
        return json.load(f)
        
def load_prompt_template():
    with open(LLM_DIR / "prompt_template_v6.txt","r",encoding = "utf-8") as f:
        return f.read()
        
def get_format_instructions():
    return """ Output a single valid JSON object with this exact structure:
{
    "holistic_analysis": "Your chain-of-thought analysis paragraph here",
    "evidence_list" : [
    {
        "snippet" : "The exact sentence from the document",
        "score_calculation" : {
            "components" : [
                {"reason" : "Why these points", "points": 3},
                {"reason" : "Mitigating factore" , "points":-1}
            ],
            "final_snippet_score" :2 
        },
        "reasoning_summary" : "Brief justification for this snippe's score "
        
    }
    ]
}

Rules: final_snippet_score must be 0-10. Points can be positive (aggravating) or negative (mitigating). Empty evidence_list if no relevant content found. """


# Commands

def cmd_prepare():
    events = load_risk_events()
    years = sorted(MSFT_FILES.keys())
    
    print("\n" + "=" * 60)
    print("MICROSOFT 10-k SCORING MATRIX")
    print("=" * 60)
    print(f"\nFilings: {years}")
    print(f"Events: {len(events)}")
    print(f"Models: {MODELS}")
    # print(f"Total evaluations needed: {len(years)} * (this is U+00d7 "x") {len(events)} * {len(MODELS)} = {len(years)*len(events)*len(MODELS)} ")
    # print(f"\nPer model: {len(years)}years * {len(events)}*events = {len(years)*len(events)} evaluations")
    
    print("\nRisk Events:")
    for i,ev in enumerate(events, 1):
        print(f" {i}.{ev['event_name']} ({ev['event_timeframe'][:20]}...)")
    # show progress
    print("\n"+"-"*60)
    cmd_status()
    
def cmd_status():
    # show scoring pregress for all models.
    events = load_risk_events()
    years = sorted(MSFT_FILES.keys())
    total_per_model = len(years) * len(events)
    
    print ("\nScoring Progress:")
    print("_" * 50)
    
    for model in MODELS:
        model_dir = RESULTS_DIR / model
        if model_dir.exists():
            done = len(list(model_dir.glob("*.json")))
        else:
            done = 0
        pct = (done / total_per_model *100) if total_per_model >0 else 0
        bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
        print (f" {model:< 22} [{bar}] {done}/{total_per_model} ({pct: .0f}%)")
        
    print()
    
def cmd_prompt(year: int, event_name:str , max_chars: int = 80000):
    # print the full prompt for a specific year + event combination.
    events = load_risk_events()
    event = next((e for e in events if e["event_name"] == event_name), None)
    if not event:
        print(f"Error: Event '{event_name}' not found. ")
        print(f"Avalible: {[e['event_name'] for e in events]}")
        return
    
    filepath = MSFT_FILES.get(year)
    if not filepath or not filepath.exists():
        print(f"Error: No filling found for year {year}")
        return
    
    template = load_prompt_template()
    with open(filepath, "r", encoding="utf-8") as f:
        document_text = f.read()
        
    if len(document_text) > max_chars:
        document_text = document_text[:max_chars]
        print(f"File is too big")
    
    prompt = template.format(
        company_name = "Microsoft Coporation",
        filling_date = FILING_DATES[year],
        event_name = event["event_name"]
        event_description = event["event_description"]
        document_text = document_text,
        format_instructions = get_format_instructions(),
        )
    
    print(prompt)


def cmd_save(model:str, year:int, event_name: str, result: dict, latency: float=0):
    # save a signle scroing results.
    model_dir = RESULTS_DIR / model
    model_dir.mkdir(parent=True, exist_ok = True)
    
    filename = f"{year}_{event_name}.json"
    output = {
        
        "model": model,
        "year": year,
        "filling_date" : FILING_DATES[year],
        "event_name": event_name,
        "company" : "Microsoft Corporation",
        "timestamp" : datetime.now().isoformat(),
        "latency_seconds": latency,
        "result": result,
    }
    
    with open(model_dir/filename,"w", encoding="utf-8") as f:
        json.dump(output, f, indent = 2, ensure_ascii=False)
        
    # Calculate summary 
    evidence_list = result.get("evidence_list",[])
    total_score = sum(
        e.get("score_calculation",{}).get("final_snippet_score",0)
        for e in evidence_list
        )
    total_score = max(0,min(100, total_score))
    
    print(f" Saved: {model}/{filename}")
    

def cmd_save_batch(model:str, year:int, results: dict):
    events = load_risk_events()
    saved = 0
    
    for event_name, result in results.items():
        if isinstance(result, dict) and "result" in result:
            actual_result = result["result"]
            latency = result.get("latency_seconds",0)
        else:
            actual_result = result
            latency = 0
        
        cmd_save(model, year, event_name, actual_result, latency)
        saved += 1
    
    print(f"\n Batch saved: {saved} results for {model} /{year}")
    
def cmd_report(output_path: str=None):
    output_path = output_path or str(OUTPUT_DIR / "model_comparison_report.html")
    
    if not RESULTS_DIR.exists():
        print("Error: not results found. run scoring first.")
        return
    
    all_results = {}
    
    for model_dir in RESULTS_DIR.iterdir():
        if not model_dir.is_dir():
            continue
        model = model_dir.name
        
        for result_file in model_dir.glob("*.json"):
            with open(result_file,"r",encoding="utf-8") as f:
                data = json.load(f)
            
            year = data["year"]
            if year not in all_results:
                all_results[year] = {}
            if model not in all_results[year]:
                all_results[year][model] = []
            
            # extract metrics from result
            result = data["result"]
            evidence_list = result.get("evidence_list",[])
            
            total_score = 0
            all_snippet_scores = []
            total_components = 0
            postive_points = 0 
            negative_points = 0 
            
            for ev in evidence_list:
                sc = ev.get("score_calculation", {})
                snippet_score = sc.get("final_snippet_score", 0)
                total_score += snippet_score
                all_snippet_scores.append(snippet_score)
                components = sc.get("components",[])
                total_components += len(components)
                for comp in components:
                    pts = comp.get("points",0)
                    if pts >0 :
                        postive_points += pts
                    else:
                        negative_points += pts
                        
                total_score = max(0, min(100, total_score))
                
                all_results[year][model].append({
                    "event_name": data["event_name"],
                    "total_score": total_score,
                    "evidence_count": len(evidence_list),
                    "avg_snippt_score":(
                        round(sum(all_snippet_scores)/len(all_snippet_scores),2 ) if all_snippet_scores else 0),
                    "postive_points_total" : postive_points,
                    "negative_points_total": negative_points,
                    "holistic_analysis_length": len(result.get("holistic_analysis","")),
                    "holistic_analysis": result.get("holistic_analysis",""),
                    "latency_seconds":data.get("latency_seconds",0),
                    "error": None,
                    "raw_response":None,
                    
                    })
                    
        if not all_results:
            print ("Error: no results loaded.")
            return
        
        # save as cache 
        cache_path = str(OUTPUT_DIR / "results_cache.json")
        with open(cache_path,"w", encoding="utf-8") as f:
            json.dump(all_results,f, indent=2, ensure_ascii=False)
        
        # generate html To add it later
        # from compare_models import generate_html_res
        
        print("done")
        
    def cmd_list_events():
        events= load_risk_events()
         for ev in events:
             print (ev["event_name"])
        
    # main
    
    def main():
        parser = argparse.ArgumentParser(description = "DNA single-Model Scorer")
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--prepare", action="score_true", help="Show scoring matrix")
        group.add_argument("--status", action="score_true", help="Show progress")
        group.add_argument("--prompt", action="score_true", help="print promt")
        group.add_argument("--prepare", action="score_true", help="Show scoring matrix")
        group.add_argument("--save", action="score_true", help="Show scoring matrix")
        group.add_argument("--save-batch", action="score_true", help="Show scoring matrix")
        group.add_argument("--report", action="score_true", help="Show scoring matrix")
        group.add_argument("--list-events", action="score_true", help="Show scoring matrix")
        
        parser.add_argument("--model", type =str, help="Model name")
        parser.add_argument("--year", type =int, help="Model name")
        parser.add_argument("--event", type =str, help="Model name")
        parser.add_argument("--result-file", type =str, help="Model name")
        parser.add_argument("--output", type =str, help="Model name")
        parser.add_argument("--max-chars", type =int, default=80000, help="Model name")
        
        args = parser.parse_args()
        
        if args.prepare:
            cmd_prepare()
        elif args.status:
            cmd_status()
        elif args.list_events:
            cmd_list_events()
        elif args.prompt:
            if not args.year or not args.event:
                parser.error("--prompt requires --year and --event")
            cmd_prompt(args.year, args.event, args.max_chars)
        elif args.save:
            if not all([args.model, args.year, args.event, args.result_file]):
                parser.error("--save requires --model, --year, --event, --result-file")
            with open(args.result_file, "r",encoding="utf-8") as f:
                result = json.load(f)
            cmd_save(args.model, args.year, args.result)
        elif args.save_batch:
            with open(args.result_file, "r", encoding="utf-8" ) as f:
                results = json.load(f)
            cmd_save_batch(args.model, args.year, results)
        elif args.report:
            cmd_report(args.output)
    
    if __name__ == "__main__":
        main()
            
            
        
        
            
            
            
            
            
    
    
    
    
    
    
    
    
    
    
    













