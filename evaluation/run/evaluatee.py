import os, json, configparser
from ver3.keys import get_key
from ver3.evaluation.model import gpt, claude, gemini, qwen3, gpt_oss, qwen_openrouter, olmo_openrouter

class Evaluatee:
    def __init__(self, args): # expectation_util=None, story_util=None):
        self.args = args
        self.model_name = args.evaluatee_model
        self.preliminary = args.preliminary
        self.speaker = args.speaker

        # self.expectation_util = expectation_util
        # self.story_util = story_util

        self.evaluation_dir = args.evaluation_dir
        self.evaluation_output_dir = os.path.join(args.evaluation_output_dir, self.model_name)
        if self.preliminary:
            self.evaluation_output_dir = os.path.join(self.evaluation_output_dir, 'preliminary')
        else:
            if self.speaker == 'None' or self.speaker is None:
                self.speaker = 'base'        
            self.evaluation_output_dir = os.path.join(self.evaluation_output_dir, self.speaker)
            
        os.makedirs(self.evaluation_output_dir, exist_ok=True)
        print("Evaluation output directory:", self.evaluation_output_dir)


        # Load the model configuration
        self.config = self.get_model_config(self.model_name)
        self.model_full_name = self.config.get('DEFAULT', 'model')
        self.temperature = self.config.getfloat('DEFAULT', 'temperature')
        self.key_num = self.config.getint('DEFAULT', 'api_key') if args.api_key == -1 else args.api_key
        self.api_key = get_key(self.model_name, self.key_num) 

        # Initialize the generative model or client
        self.generative_client = self.get_generative_model(self.model_full_name)


    def get_model_config(self, model_name):
        # Load configuration from the config file
        config = configparser.ConfigParser()
        
        config_path = os.path.join(self.evaluation_dir, 'model', f'{model_name}.cfg')
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        config.read(config_path)

        return config
    

    def get_generative_model(self, model_name):
        if 'gpt-oss' in model_name:
            return gpt_oss.get_model(model_name, self.api_key)
        elif 'qwen3-30b-a3b' in model_name or 'qwen3-30b-a3b-instruct' in model_name:
            return qwen_openrouter.get_model(model_name, self.api_key)
        elif 'allenai/olmo-2-0325-32b-instruct' in model_name:
            return olmo_openrouter.get_model(model_name, self.api_key)
        elif 'gpt' in model_name:
            return gpt.get_model(model_name, self.api_key)
        elif 'claude' in model_name:
            return claude.get_model(model_name, self.api_key)
        elif 'gemini' in model_name:
            return gemini.get_model(model_name, self.api_key)
        elif 'qwen' in model_name.lower():
            return qwen3.get_model(model_name, self.api_key)
        else:
            raise ValueError(f"Unsupported model for scenario generation: {model_name}")

    
    def generate(self, system_prompt, user_prompt):
        if 'gpt-oss' in self.model_full_name:
            text = gpt_oss.generate(self.generative_client, self.model_full_name,
                                system_prompt, user_prompt, 
                                self.temperature)
        elif 'qwen3-30b-a3b' in self.model_full_name or 'qwen3-30b-a3b-instruct' in self.model_full_name:
            text = qwen_openrouter.generate(self.generative_client, self.model_full_name,
                                system_prompt, user_prompt, 
                                self.temperature)
        elif 'allenai/olmo-2-0325-32b-instruct' in self.model_full_name:
            text = olmo_openrouter.generate(self.generative_client, self.model_full_name,
                                system_prompt, user_prompt, 
                                self.temperature)
        elif 'gpt' in self.model_full_name:
            text = gpt.generate(self.generative_client, self.model_full_name,
                                system_prompt, user_prompt, 
                                self.temperature)
        elif 'claude' in self.model_full_name:
            text = claude.generate(self.generative_client, self.model_full_name,
                                    system_prompt, user_prompt, 
                                    self.temperature)
        elif 'gemini' in self.model_full_name:
            text = gemini.generate(self.generative_client, self.model_full_name,
                                    system_prompt, user_prompt, 
                                    self.temperature)
        elif 'qwen' in self.model_full_name.lower():
            text = qwen3.generate(self.generative_client, self.model_full_name,
                                    system_prompt, user_prompt,
                                    self.temperature)
        else:
            raise ValueError(f"Unsupported model for story generation: {self.model_name}")
        
        return text

    
    def exists(self, code1, code2, obg1, obg2, exp_id1, exp_id2):
        if self.preliminary:
            filename = f"{code1}-{code2}.json"
        else:
            filename = f"{code1}-{code2}_{obg1}-{obg2}_{exp_id1}-{exp_id2}.json"
        filepath = os.path.join(self.evaluation_output_dir, f"{code1[0]}-{code2[0]}", filename)
        return os.path.exists(filepath) or os.path.exists(filepath.replace('.json', '.jsonl'))  # json or jsonl


    def save_response(self, code1, code2, obg1, obg2, exp_id1, exp_id2, response_dict, options, raw_response):
        save_dir = os.path.join(self.evaluation_output_dir, f"{code1[0]}-{code2[0]}")
        if self.preliminary:
            save_file = f"{code1}-{code2}.json"
        else:
            save_file = f"{code1}-{code2}_{obg1}-{obg2}_{exp_id1}-{exp_id2}.json"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, save_file)

        response_dict['Option'] = options

        if response_dict['Answer'] == 'A':
            response_dict['Selected'] = options[0]
        elif response_dict['Answer'] == 'B':
            response_dict['Selected'] = options[1]
        else:
            response_dict['Selected'] = None

        response_dict['Raw_Response'] = raw_response
        
        with open(save_path, 'w') as f:
            json.dump(response_dict, f, indent=4, ensure_ascii=False)

        print(f"Response saved to {save_path}")
