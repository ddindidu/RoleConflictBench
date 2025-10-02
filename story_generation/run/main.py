import os, sys, json, argparse
from itertools import combinations

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from attribution.role_attribution import Role
from expectation_generation.run.expectation import Expectation
from story_generation.run.story_generator import StoryGenerator
# from utils import save_jsonl, match_id
from keys import get_key



def main(args, expectation_util=None):
    # args
    # model = args.benchmark_model
    # key_num = args.api_key

    role_dir = args.attribution_dir

    # role list
    role_util = Role(args, source_dir=role_dir)
    df_role = role_util.get_role_data(args.domain, show=True if args.test else False)   # columns = ['Domain', 'Gender', 'Status', 'Role']

    # role selection if it is needed
    if args.test:
        # by index
        #ind = [1,7,]
        ind = range(40,65)
        df_role = df_role.iloc[ind]    

        # by code
        #codes = ['F02', 'F08', 'I08', 'O31', 'O67', 'R03']
        #df_role = df_role[df_role['Code'].isin(codes)]

        # pass


    # get expectation list
    if expectation_util is None:
        # load or generate expectations
        expectation_util = Expectation(args, df_role)   # load or generate expectations
    df_expectation = expectation_util.get_expectation_df()

    # 
    story_util = StoryGenerator(args)
    ## load or generate scenarios
    story_util.combine_two_roles_and_expectations(role_util, expectation_util, df_expectation)

    return story_util


    


def get_args():
    parser = argparse.ArgumentParser()
    
    # base directory ('./') is the root directory of the project
    parser.add_argument("--attribution_dir", type=str, default='./attribution')
    parser.add_argument("--scenario_prompt_dir", type=str, default='./prompt')
    parser.add_argument("--scenario_output_dir", type=str, default='./output/')


    parser.add_argument("--domain", type=str, default='None')

    parser.add_argument("--benchmark_model", type=str, default='gpt-4o-mini')
    parser.add_argument("--batch", action='store_true') # batch mode for openai
    parser.add_argument("--temperature", type=int, default=1)
    parser.add_argument("--api_key", type=int, default=0)

    parser.add_argument("--iteration", type=int, default=5)
    
    parser.add_argument("--test", action='store_true', help="Test mode")

    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    print(args)

    main(args)