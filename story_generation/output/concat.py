import json
import pandas as pd
import glob
import os


def concat(benchmark_model='gpt-4.1'):
    model_name = benchmark_model

    # Construct the path to the directory containing the .jsonl files
    json_dir = os.path.join(os.path.dirname(__file__), model_name)
    
    # Check if the directory exists
    if not os.path.exists(json_dir):
        print(f"Directory {json_dir} does not exist.")
        return

    # Get all .json files in the directory
    json_files = glob.glob(os.path.join(json_dir, '*', "*.json"))
    json_files.sort()

    # Read and concatenate all files into a single DataFrame
    for f in json_files:
        with open(f, 'r') as file:
            data= json.load(file)
        
        df_temp = pd.DataFrame([data])
        concat_df = pd.concat([concat_df, df_temp], ignore_index=True) if 'concat_df' in locals() else df_temp

    # Save the concatenated DataFrame to a new .csv file
    output_file = os.path.join(f"{model_name}", "combined_output.csv")
    concat_df.to_csv(output_file, index=False)
