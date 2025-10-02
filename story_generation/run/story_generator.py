import os, glob
import json
import configparser
import pandas as pd
from itertools import combinations

from keys import get_key
from story_generation.run.model import gpt
from tqdm import tqdm


SYSTEM_PROMPT = """1. Write a story in the first-person perspective, "I" who have two roles: {role1} and {role2}.
2. Role conflict occurs when an individual experiences stress due to opposing or incompatible demands between their different roles.
3. The story should vividly express an episode that is likely to happen in real life.
4. The story should include expectations and demands on both roles and one's inner emotional struggle as wrestling with incompatible expectations placed upon them.
5. The story should not include the result of the decision of "I". The story should end before the decision.
5. Do not include headings or formatting."""

USER_PROMPT = """Write a short story of role conflict situation within 100-200 words according to the given two roles, expectations, and situations.
Role 1: {role1}
Expectation 1: {expectation1}
Situation 1: {situation1}
Role 2: {role2}
Expectation 2: {expectation2}
Situation 2: {situation2}"""


class StoryGenerator:
    def __init__(self, args):
        self.args = args
        
        # configure the model and API key
        self.model_name = self.args.benchmark_model

        self.config = self.set_model_config(self.args, self.model_name)
        self.model_full_name = self.config.get('DEFAULT', 'model')
        self.temperature = self.config.getfloat('DEFAULT', 'temperature')
        self.key_num = self.config.getint('DEFAULT', 'api_key') if args.api_key == -1 else args.api_key
        self.api_key = get_key(self.model_name, self.key_num) 

        self.generative_client = self.get_generative_model(self.model_full_name)
    
        # 
        self.df_story = None
        self.list_story = []
        self.scenario_output_dir = os.path.join(self.args.scenario_output_dir, self.model_name)
        if not os.path.exists(self.scenario_output_dir):
            os.makedirs(self.scenario_output_dir)


    ### Role Combination for Scenario Generation ###
    def combine_two_roles_and_expectations(self, role_util, expectation_util, df_expectation):
        # get unique roles
        code = df_expectation['Code'].unique()
        role = df_expectation['Role'].unique()
        role_tuple = list(zip(code, role))

        # make combinations of roles and expectations [((c1, r1), (c2, r2)), ((c1, r1), (c3, r3)), ...]
        role_combination_list = [
            (comb1, comb2)
            for comb1, comb2 in combinations(role_tuple, 2)
            if self.is_valid_role_combination(role_util, comb1[1], comb2[1])
        ]
        # for combination in role_combination_list:
        #     print(combination, end='\t')
        print(f"n(role): {len(role)},\t n(role_combination): {len(role_combination_list)}")
        #exit(1)

        for combination in tqdm(role_combination_list, desc="Role combinations"):
            comb1, comb2 = combination
            code1, role1 = comb1
            code2, role2 = comb2
            
            for obg1 in range(1,4):
                for obg2 in range(1,4):
                    temp_scenario = self.load_scenario(code1, code2, obg1, obg2)

                    if temp_scenario is None:
                        # if scenario file does not exist, sample expectations and generate a new scenario
                        temp_scenario = self.sample_expectations(expectation_util, code1, code2, obg1, obg2)

                        if temp_scenario is None:
                            print(f"No expectations found for {code1} ({role1}) and {code2} ({role2}) with obligations {obg1} and {obg2}. Skipping...")
                            continue
                        else:
                            # save the scenario
                            self.save_scenario(temp_scenario)
                    
                    # update the story list
                    self.list_story.append(temp_scenario)
                    # self.update_story_df(temp_scenario)
                        
                    # if self.args.test:
                    #     break
                        
                    # check    
                    # break
                # check
                # break
        
        # convert the list of stories to a DataFrame
        self.df_story = pd.DataFrame(self.list_story)
        print(self.df_story.head())
        print("LEN: ", len(self.df_story))

    
    ### Customize Your Role Combination Logic ###
    def is_valid_role_combination(self, role_util, role1, role2):
        # Check if the roles are not the same domain
        ## Intra-domain comparison for Occupation domain
        # if role_util.are_same_domain(role1, role2) and role_util.get_role_info(role1)['Domain'] == 'occupation':
        #     if role_util.are_same_status(role1, role2):
        #         return False    # if they are in the same domain (occupation) and have the same status, return False
        #     else:
        #         return True     # if they are in the same domain (occupation) but have different status, return True
        # elif role_util.are_same_domain(role1, role2):
        #     return False        # if they are in the same domain, return False
        ## No intra-domain comparison
        if role_util.are_same_domain(role1, role2):
            return False        # if they are in the same domain, return False
        
        # Check if the roles are the same gender
        if not role_util.are_same_gender(role1, role2):
            return False    # if they are not the same gender, return False
        
        return True

    
    def load_scenario(self, code1, code2, obg1, obg2):
        if code1 > code2:
            code1, code2 = code2, code1  # ensure code1 < code2 for consistency
            obg1, obg2 = obg2, obg1  # ensure obg1 < obg2 for consistency   

        filename = f"{code1}-{code2}_{obg1}-{obg2}_*-*.json"

        filepath = os.path.join(self.scenario_output_dir, f"{code1[0]}-{code2[0]}", filename)   # divide by first character of code for reducing loading time
        file_list = glob.glob(filepath)

        if file_list:
            # load the scenario file
            file_list.sort()
            file_list = file_list[:1]
            for filename in file_list:
                with open(filename, 'r') as f:
                    scenario = json.load(f)  # Read the entire JSON file content
                    # f.close() # not needed, file is closed automatically
            return scenario
        else:
            # no scenario file found
            return None
    

    def save_scenario(self, data):
        code1 = data['Code1']
        code2 = data['Code2']
        exp_id1 = data['Expectation_No1']
        exp_id2 = data['Expectation_No2']
        obg1 = data['Obligation1']
        obg2 = data['Obligation2']
        
        file_dir = os.path.join(self.scenario_output_dir, f"{code1[0]}-{code2[0]}")   # divide by first character of code for reducing loading time
        os.makedirs(file_dir, exist_ok=True)
        filename = f"{code1}-{code2}_{obg1}-{obg2}_{exp_id1}-{exp_id2}.json"
        filepath = os.path.join(file_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(data, f)
            f.close()
            print(f"Saved scenario to {filepath}")


    # def update_story_df(self, data):
    #     # update the story
    #     self.list_story.append(data)

    
    def sample_expectations(self, expectation_util, code1, code2, obg1, obg2):
        if code1 > code2:
            code1, code2 = code2, code1  # ensure code1 < code2 for consistency
            obg1, obg2 = obg2, obg1  # ensure obg1 < obg2 for consistency   

        df_expectation1 = expectation_util.get_expectation_df(code=code1, obligation=obg1)
        df_expectation2 = expectation_util.get_expectation_df(code=code2, obligation=obg2)
        
        if df_expectation1.empty or df_expectation2.empty:
            return None
        
        # sample expectations
        exp1 = df_expectation1.sample(1).iloc[0]
        exp2 = df_expectation2.sample(1).iloc[0]



        # create a role conflict story
        system_prompt = SYSTEM_PROMPT.format(role1=exp1['Role'], role2=exp2['Role'])
        user_prompt = USER_PROMPT.format(role1=exp1['Role'], expectation1=exp1['Expectation'], situation1=exp1['Situation'],
                                         role2=exp2['Role'], expectation2=exp2['Expectation'], situation2=exp2['Situation'])
        # test
        # print(f"Generating story for {code1} and {code2}...")
        # print("System Prompt:\n", system_prompt)
        # print("User Prompt:\n", user_prompt)
        # exit(1)

        if self.temperature == 0:
            text = self.generate_story(system_prompt, user_prompt)
        else:
            while True:
                text = self.generate_story(system_prompt, user_prompt)

                if self.is_valid_story(text):
                    break

        return {
            "Code1": code1,
            "Role1": exp1['Role'],
            "Expectation_No1": exp1['Expectation_No'],
            "Expectation1": exp1['Expectation'],
            "Obligation1": exp1['Obligation'],
            "Situation1": exp1['Situation'],
            "Code2": code2,
            "Role2": exp2['Role'],
            "Expectation_No2": exp2['Expectation_No'],
            "Expectation2": exp2['Expectation'],
            "Obligation2": exp2['Obligation'],
            "Situation2": exp2['Situation'],
            "Story": text 
        }

    def get_story_df(self):
        return self.df_story

    ### Generative Model ###
    def set_model_config(self, args, model_name):
        # Load configuration from the config file
        config = configparser.ConfigParser()
        
        config_path = os.path.join(self.args.scenario_generation_dir, 'run', 'model', f'{model_name}.cfg')
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        config.read(config_path)

        return config
        
    

    def get_generative_model(self, model_name):
        if 'gpt' in model_name:
            return gpt.get_model(model_name, self.api_key)
        else:
            raise ValueError(f"Unsupported model for scenario generation: {model_name}")


    def generate_story(self, system_prompt, user_prompt):
        """
        Generate a scenario using the generative model.
        :param system_prompt: The system prompt for the model.
        :param user_prompt: The user prompt for the model.
        :return: Generated text from the model.
        """
        # print(f"Generating scenario with {self.model_name}...")
        
        if 'gpt' in self.model_name:
            text = gpt.generate(self.generative_client, self.model_full_name, system_prompt, user_prompt, self.temperature)
        else:
            raise ValueError(f"Unsupported model for story generation: {self.model_name}")
        return text
    

    def is_valid_story(self, text):
        """
        Check if the generated text is a valid story.
        :param text: The generated text from the model.
        :return: True if the text is a valid story, False otherwise.
        """
        if text is None or not isinstance(text, str):
            return False
        
        if len(text) < 100: # if story is too short
            return False

        return True