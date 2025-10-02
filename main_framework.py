import os, sys, argparse
import json
import random as rand

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from expectation_generation.run.main import main as expectation_main
from story_generation.run.main import main as scenario_main
from story_generation.output import concat as scenario_concat
from evaluation.run.main import main as eval_main
# import evaluation.run.utils as utils

def get_args():
    parser = argparse.ArgumentParser(description="Main framework for role conflict evaluation.")

    # args for framework (module)
    parser.add_argument("--generate_expectation", action='store_true', help="Generate triplets for scenarios")
    parser.add_argument("--generate_scenario", action='store_true', help="Generate scenarios")
    parser.add_argument("--make_benchmark", action='store_true', help="Make benchmark data")
    parser.add_argument("--evaluate", action='store_true', help="Evaluate the model's decision")

    # paths
    parser.add_argument("--attribution_dir", type=str, default='./attribution')
    #
    parser.add_argument("--expectation_dir", type=str, default='./expectation_generation')
    parser.add_argument("--expectation_output_dir", type=str, default='./expectation_generation/output/')
    parser.add_argument('--expectation_output_file', type=str, default='{code}_{name}.jsonl')
    #
    parser.add_argument("--scenario_generation_dir", type=str, default='./story_generation')
    parser.add_argument("--scenario_output_dir", type=str, default='./story_generation/output/')
    

    # scenario generation
    parser.add_argument("--domain", type=str, default='None')
    parser.add_argument("--benchmark_model", type=str, default='gpt-4.1')   # scenario_generator

    # evaluation
    parser.add_argument("--evaluation_dir", type=str, default='./evaluation')
    parser.add_argument("--evaluation_output_dir", type=str, default='./evaluation/output/')
    parser.add_argument("--evaluatee_model", type=str, default='gpt-4.1')
    parser.add_argument("--evaluate_index", type=int, default=0)
    parser.add_argument("--speaker", type=str, default='None') # None or speaker name
    parser.add_argument("--preliminary", action='store_true', help="Preliminary exp without story")

    # generative model
    parser.add_argument("--api_key", type=int, default=-1)
    parser.add_argument("--temperature", type=int, default=1)

    # test
    parser.add_argument("--test", action='store_true', help="Test mode")

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    print(args)
    
    rand.seed(42)  # for reproducibility

    # Make expectation data ... generate expectations
    expectation_util = None
    if args.generate_expectation:
        expectation_util = expectation_main(args)
    
    # Make benchmark data ... generate scenarios
    story_util = None
    if args.generate_scenario:
        # Generate scenarios
        story_util = scenario_main(args, expectation_util)
        # concatenate scenario outputs
        scenario_concat.concat(args.benchmark_model)

    # Evaluate the model's decision
    if args.evaluate:
        # Evaluate the model's decision
        eval_main(args, expectation_util, story_util)


