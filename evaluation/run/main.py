from tqdm import tqdm

from attribution.role_attribution import Role
from expectation_generation.run.expectation import Expectation
from story_generation.run.story_generator import StoryGenerator
from evaluation.run import qa
from evaluation.run.evaluatee import Evaluatee
from evaluation.run.utils import is_valid_answer, parse_response

def main(args, expectation_util=None, story_util=None):
    role_dir = args.attribution_dir 

    # role list
    role_util = Role(args, source_dir=role_dir)
    df_role = role_util.get_role_data(args.domain, show=True if args.test else False)   # columns = ['Domain', 'Gender', 'Status', 'Role']
    
    if expectation_util is None:
        # load or generate expectations
        expectation_util = Expectation(args, df_role)   # load or generate expectations
    df_expectation = expectation_util.get_expectation_df()

    if story_util is None:
        # Initialize the scenario generator
        story_util = StoryGenerator(args)
        story_util.combine_two_roles_and_expectations(role_util, expectation_util, df_expectation)
    
    df_story = story_util.get_story_df()
    df_story = df_story.sort_values(by=['Code1', 'Code2'])

    # evaluatee model
    evaluatee = Evaluatee(args)

    if args.evaluate_index == 0:
        # evaluate all stories
        print("Evaluating all stories...")
    elif args.evaluate_index < len(df_story):
        # evaluate only the specified index
        print(f"Evaluating story from index {args.evaluate_index}...")
        df_story = df_story.iloc[args.evaluate_index:]  # include the specified index
    else:
        raise ValueError(f"Invalid evaluate_index: {args.evaluate_index}. It should be less than {len(df_story)}.")
    
    for idx, row in tqdm(df_story.iterrows(), total=len(df_story), desc="Evaluating"):
        if args.test:
            if idx > 5:
                break

        code1 = row['Code1']
        code2 = row['Code2']
        role1 = row['Role1']
        role2 = row['Role2']
        urgency1 = row['Urgency1']
        urgency2 = row['Urgency2']
        expectation1 = row['Expectation_No1']
        expectation2 = row['Expectation_No2']
        story = row['Story']

        # check if the evaluation result already exists
        if evaluatee.exists(code1, code2, urgency1, urgency2, expectation1, expectation2):
            # skip if the evaluation result already exists
            print(f"Evaluation result for {code1} - urgency {urgency1} and {code2} - urgency {urgency2} already exists. Skipping...")
            continue

        # shuffle the options
        randomness = expectation1 + expectation2
        if randomness % 2 == 0:
            options = [role1, role2]
        else:
            options = [role2, role1]

        # get the system prompt and user prompt
        system_prompt = qa.get_system_prompt(args.preliminary)

        speaker_prompt = qa.get_speaker_prompt(args.speaker, options[0], options[1], story)
        qa_prompt = qa.get_question_prompt(args.preliminary, options[0], options[1], story)
        user_prompt = qa_prompt if args.speaker == 'None' else speaker_prompt

        # generate the response
        retry_cnt = 0
        while True:
            response = evaluatee.generate(system_prompt, user_prompt)
            if args.test:
                print(f"Response: {response}")

            # check the validity of the response and parse it
            response_dict = None
            if is_valid_answer(response):
                response_dict = parse_response(response)

            if response_dict is not None:
                break
            else:
                print(f"Retrying due to invalid response in {code1}-{code2}_{urgency1}-{urgency2}_{expectation1}-{expectation2}")
                print(f"{response}")
            
            retry_cnt += 1

            if args.temperature == 0:
                if retry_cnt > 0:
                    break
            else:
                if retry_cnt > 3:
                    break

        # save the response
        if response_dict is not None:
            evaluatee.save_response(code1, code2, urgency1, urgency2, expectation1, expectation2,
                                    response_dict,
                                    options,
                                    response)
        else:
            print(f"Failed to generate a valid response for {code1} and {code2}. Skipping saving the response.")

    return