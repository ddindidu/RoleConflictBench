import os, sys, argparse
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from attribution.role_attribution import Role
from expectation_generation.run.expectation import Expectation
# from utils import save_jsonl, match_id
from keys import get_key


def process_jsonl(file_path):
    print("Processing JSONL file to ensure correct format...")
    with open(file_path, 'r') as f:
        lines = f.readlines()
        data_string = ''.join(lines)

        if data_string[-1] == '\n':
            data_string = data_string[:-1]  # Remove trailing newline if exists
        data_string = data_string.replace(",\n  ",  ", ")
        data_string = data_string.replace("{\n ", "{")  # Remove carriage returns
        data_string = data_string.replace("{\n", "{")  # Remove carriage returns    

        data_string = data_string.replace(", \n  ",  ", ")
        data_string = data_string.replace(", \n ",  ", ")
        data_string = data_string.replace(",\n",  ", ")
        data_string = data_string.replace("\n}", "}")
        data_string = data_string.replace("}{", "}\n{")  # Ensure each JSON object is on a new line
    
    split_lines = data_string.split('\n')

    if len(split_lines) != 9:
        print(f"Warning: Expected 9 lines but found {len(split_lines)} lines in {file_path}. Please check the file.")
        for line in split_lines:
            print(line)
        return
    
    # check if each line is a valid JSON
    for line in split_lines:
        line = line.strip()
        if line:
            try:
                json.loads(line)
            except json.JSONDecodeError:
                print(f"Invalid JSON line skipped: {line}")
                return
            
    # if all lines are valid, rewrite the file
    with open(file_path, 'w') as f:
        for line in split_lines:
            f.write(line + '\n')
        f.close()
    

def make_triplet(args):
    # args
    role_dir = args.attribution_dir

    # role list
    role_util = Role(args, source_dir=role_dir)
    df_role = role_util.get_role_data(args.domain, show=True if args.test else False)   # columns = ['Domain', 'Gender', 'Status', 'Role']

    # role selection if it is needed
    if args.test:
        # by index
        # ind = [0,1,2,]#9,10,11,16,25,26,48,60,61,68,97,98,100,103,108,109,114,116,117]
        # df_role = df_role.iloc[ind]

        # by code
        codes = ['F02', 'F08', 'I08', 'O31', 'O67', 'R03']
        df_role = df_role[df_role['Code'].isin(codes)]    

    # if jsonl file has wrong format, process it again
    for _, row in df_role.iterrows():
        role_code = row['Code']
        role = row['Role']
        path = os.path.join(args.expectation_output_dir, args.expectation_output_file.format(code=role_code, name=role))
        
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    _ = json.loads(f.readline())
                    f.close()
            except:
                process_jsonl(path)

    expectation_util = Expectation(args, df_role)   # load or generate expectations
    # expectation_util.show_expectation()
    # expectation_util.show_expectation_by_obligation()
    # print(expectation_util.get_expectation_df())

    return expectation_util









def get_args():
    parser = argparse.ArgumentParser()
    
    # base directory ('./') is the root directory of the project
    parser.add_argument("--attribution_dir", type=str, default='./attribution')
    # parser.add_argument("--scenario_prompt_dir", type=str, default='./prompt')
    parser.add_argument("--expectation_output_dir", type=str, default='./output/')
    parser.add_argument('--expectation_output_file', type=str, default='{code}_{name}.jsonl')

    parser.add_argument("--domain", type=str, default='None')

    parser.add_argument("--benchmark_model", type=str, default='gpt-4o-mini')
    parser.add_argument("--batch", action='store_true') # batch mode for openai
    parser.add_argument("--temperature", type=int, default=1)
    parser.add_argument("--api_key", type=int, default=0)

    parser.add_argument("--iteration", type=int, default=5)

    parser.add_argument("--make_triplet", action='store_true', help="Generate triplets for scenarios")
    
    parser.add_argument("--test", action='store_true', help="Test mode")

    return parser.parse_args()


def main(args):
    make_triplet(args)
    
    # make_scenario(args)


