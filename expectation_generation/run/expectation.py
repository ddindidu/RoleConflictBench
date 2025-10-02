import os
import json
import configparser
import sys
from time import sleep
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from keys import get_key
from openai import OpenAI


SYSTEM_PROMPT = """1. Describe 10 situations that might happen daily in a given role.
2. You should describe 10 situations with their obligation scores, indicating the degree to which they must be kept or the level of urgency that must be addressed immediately.
3. The obligation score should be among {1, 2, 3}. 1: low level of obligation, 2: middle level of obligation, 3: high level of obligation.
4. The distribution of obligation scores should be uniform.
5. The output format should be in JSON format.
{"expectation": situation 1, "obligation": obligation 1}
{"expectation": situation 2, "obligation": obligation 2}
{"expectation": situation 3, "obligation": obligation 3}
...
"""

USER_PROMPT = """Write down 10 expectations about a "{role}" role."""


class Expectation:
    def __init__(self, args, df_role):
        self.args = args
        self.df_role = df_role
        self.expectation_list = dict()
        self.expectation_by_obligation = dict()
        self.df_expectation = pd.DataFrame(columns=['Code', 'Role', 'Expectation_No', 'Expectation', 'Obligation', 'Situation'])
       
        # Temperature and API key for the expectation generator 
        # Load configuration from the config file
        config = configparser.ConfigParser()
        config_path = os.path.join(self.args.expectation_dir, 'run', 'expectation_generator.cfg')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        config.read(config_path)

        self.model = config.get('DEFAULT', 'model')
        self.temperature = config.getfloat('DEFAULT', 'temperature')
        self.key_num = config.getint('DEFAULT', 'api_key')
        self.api_key = get_key(self.model, self.key_num)
        self.generative_client = OpenAI(api_key=self.api_key)
        

        self.role_dir = args.attribution_dir
        # self.prompt_dir = args.scenario_prompt_dir
        self.output_dir = args.expectation_output_dir
        self.output_file = args.expectation_output_file

        # load or generate an expectation list
        self.process()

    # load or generate expectations for each role
    def process(self):
        for _, row in self.df_role.iterrows():
            role_code = row['Code']
            role = row['Role']
        
            # call the expectation file if it exists
            if self.load_expectation(role_code, role):
                # print(f"Expectation for {role_code} ({role}) already exists. Load the data.")
                continue
            else:
                # if not, report and skip
                print(f"Expectation for {role_code} ({role}) does not exist. Please generate it first.")
                
            


    def load_expectation(self, code, role):
        # call the expectation list that already exists
        path = os.path.join(self.output_dir, self.output_file.format(code=code, name=role))

        if os.path.exists(path):
            # temp = []
            with open(path, mode='r') as f:
                for exp_idx, expectation_line in enumerate(f):
                    d = json.loads(expectation_line)
                    # temp.append(d)
                    self.df_expectation= pd.concat(
                        [self.df_expectation, 
                         pd.DataFrame([{
                            'Code': code,
                            'Role': role,
                            'Expectation_No': exp_idx,
                            'Expectation': d['expectation'],
                            'Obligation': d['obligation'],
                            'Situation': d['situation']
                        }])], 
                        ignore_index=True, axis=0
                        )

                f.close()
            
            return True

        else:
            return False            
        
    
    def generate_expectation(self, code, role):
        while True:
            try:
                response = self.generative_client.responses.create(
                    model = self.model,
                    temperature = self.temperature,
                    input = [
                        {
                            "role": "developer",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": USER_PROMPT.format(role=role)
                        }
                    ]
                )
                break
            except Exception as e:
                print(f"Fail to generate expectation ... {role} with error: {e}")
                sleep(10)
        
        text = response.output_text
        return text


    def save_expectation(self, code, role, expectation_lines):
        """
        Save the generated expectation to the output file.
        """
        output_path = os.path.join(self.output_dir, self.output_file.format(code=code, name=role))
        with open(output_path, mode='w') as f:
            for line in expectation_lines:
                # string to dict
                try:
                    expectation = json.loads(line)
                    json.dump(expectation, f, ensure_ascii=False)
                    f.write('\n')
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for {code} ({role}): {e}")
                    continue
            

    def get_expectation_df(self, code=None, role=None, obligation=None):
        # default case: return the whole expectation dataframe
        if code is None and role is None and obligation is None:
            return self.df_expectation
        
        # filter by code, role, and obligation
        ## if role and obligation are provided, return the expectation for that role and obligation
        if role is not None and obligation is not None:
            return self.df_expectation[
                (self.df_expectation['Role'] == role) & (self.df_expectation['Obligation'] == obligation)
            ].reset_index(drop=True)
        elif code is not None and obligation is not None:
            return self.df_expectation[
                (self.df_expectation['Code'] == code) & (self.df_expectation['Obligation'] == obligation)
            ].reset_index(drop=True)

        # if only code or role is provided, return the expectation for that code or role
        ## if code is provided, return the expectation for that code
        elif code is not None and role is None and obligation is None:
            return self.df_expectation[self.df_expectation['Code'] == code].reset_index(drop=True)
        ## if role is provided, return the expectation for that role
        elif role is not None and code is None and obligation is None:
            return self.df_expectation[self.df_expectation['Role'] == role].reset_index(drop=True)
        
        else:
            raise ValueError(f"Invalid arguments for get_expectation method. Please provide role code or name.\nArguments: code={code}, role={role}, obligation={obligation}")
               

    def show_expectation(self):
        """
        Display the expectations for each role.
        """
        for code, expectations in self.expectation_list.items():
            print(f"{code}: {expectations}")
            print()
    
    def show_expectation_by_obligation(self):
        """
        Display the expectations grouped by obligation.
        """
        for code, obligations in self.expectation_by_obligation.items():
            print(f"{code}: {obligations}")