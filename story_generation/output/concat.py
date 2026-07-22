import json
import pandas as pd
import glob
import os

models = ['gpt-4.1']
for model_name in models:
    # Construct the path to the directory containing the .jsonl files
    json_dir = os.path.join(os.path.dirname(__file__), model_name)
    
    # Check if the directory exists
    if not os.path.exists(json_dir):
        print(f"Directory {json_dir} does not exist.")
        continue

    # Get all .json files in the directory
    json_files = glob.glob(os.path.join(json_dir, '*', "*.json"))
    json_files.sort()

    # Read and concatenate all files into a single DataFrame
    for f in json_files:
        with open(f, 'r') as file:
            data= json.load(file)
        
        df_temp = pd.DataFrame([data])

        code1 = df_temp.loc[0, 'Code1']
        code2 = df_temp.loc[0, 'Code2']
        urg1 = df_temp.loc[0, 'Urgency1']
        urg2 = df_temp.loc[0, 'Urgency2']
        exp1 = df_temp.loc[0, 'Expectation_No1']
        exp2 = df_temp.loc[0, 'Expectation_No2']

        df_temp.loc[0, 'key'] = f"{code1}-{code2}_{urg1}-{urg2}_{exp1}-{exp2}"
        
        concat_df = pd.concat([concat_df, df_temp], ignore_index=True) if 'concat_df' in locals() else df_temp

    # Save the concatenated DataFrame to a new .csv file
    output_file = os.path.join(f"{model_name}", "combined_output.csv")
    concat_df.to_csv(output_file, index=False)
