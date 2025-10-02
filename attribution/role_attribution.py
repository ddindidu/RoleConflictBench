import os
import pandas as pd


class Role:
    """
    Class to represent a role in the attribution data.
    """

    def __init__(self, args, source_dir: str = None):
        if source_dir is None:
            source_dir = args.attribution_dir
        self.df = pd.read_csv(os.path.join(source_dir, 'role.csv'))
        # Nan values are replaced with None
        self.df = self.df.where(pd.notnull(self.df), None)
        
    
    def get_role_data(self, domain: str = None, show = False) -> pd.DataFrame:
        """
        Get attribution data from the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            domain (str): The domain for filtering the attribution data.

        Returns:
            pd.DataFrame: A DataFrame with the attribution data.
        """
        
        if domain is None or domain == 'None':
            df = self.df   
        else:
            df = self.df[self.df['Domain'] == domain].reset_index(drop=True)

        if show:
            print(df.head())
            print(f"Total number of roles in {domain} domain: {len(df)}")
        
        return df

    def get_domains(self) -> list:
        """
        Get unique domains from the DataFrame.

        Returns:
            list: A list of unique domains.
        """
        return self.df['Domain'].unique().tolist()

    def get_domains(self, domain=True, gender=False, status=True):
        # domain
        unique_domain = self.df['Domain'].unique()
        # status in professional
        unique_status = self.df['Status'].unique()
        print(unique_status)
        unique_gender = self.df['Gender'].unique()

        if (domain == True) and (gender == False) and (status == False):
            return {domain: len(self.df[self.df['Domain'] == domain]) for domain in unique_domain}
        
        if (domain == True) and (gender == False) and (status == True):
            return {
                f"{domain}_{status if status is not None else 'None'}": len(
                    self.df[(self.df['Domain'] == domain) & ((self.df['Status'] == status) | (pd.isnull(self.df['Status']) & (status is None)))]
                )
                for domain in unique_domain for status in unique_status
            }

        if (domain == True) and (gender == True) and (status == True):
            return {
                f"{domain}_{gender if gender is not None else 'None'}_{status if status is not None else 'None'}": 
                    len(self.df[(self.df['Domain'] == domain) & 
                                ((self.df['Status'] == status) | (pd.isnull(self.df['Status']) & (status is None))) & 
                                ((self.df['Gender'] == gender) | (pd.isnull(self.df['Gender']) & (gender is None)))])
                    for domain in unique_domain for gender in unique_gender for status in unique_status
            }

        raise ValueError("Invalid parameters for domain, gender, or status.")
 
    def get_role_info(self, role: str) -> pd.DataFrame:
        """
        Get information about a specific role.

        Args:
            role (str): The role to get information about.

        Returns:
            pd.DataFrame: A DataFrame with the role information.
        """
        df_temp = self.df[self.df['Role'] == role].reset_index(drop=True)
        return {
            'Role': role,
            'Domain': df_temp['Domain'].values[0],
            'Gender': df_temp['Gender'].values[0],
            'Status': df_temp['Status'].values[0],
        }
    
    def are_same_gender(self, role1: str, role2: str) -> bool:
        """
        Check if two roles are of the same
        """
        role1_gender = self.get_role_info(role1)['Gender']
        role2_gender = self.get_role_info(role2)['Gender']

        # if role1_gender is None and role2_gender is None:
        #     return True
        if role1_gender is None or role2_gender is None:
            return True
        elif role1_gender == 'neutral' or role2_gender == 'neutral':
            return True
        elif role1_gender == role2_gender:
            return True
        else:
            #print(role1_gender, role2_gender)
            return False


    def are_same_domain(self, role1: str, role2: str) -> bool:
        """
        Check if two roles are in the same domain.
        """
        role1_domain = self.get_role_info(role1)['Domain']
        role2_domain = self.get_role_info(role2)['Domain']

        if role1_domain == role2_domain:
            return True
        else:
            return False
        
    
    def are_same_status(self, role1: str, role2: str) -> bool:
        """
        Check if two roles are of the same status.
        """
        role1_status = self.get_role_info(role1)['Status']
        role2_status = self.get_role_info(role2)['Status']

        if role1_status is None and role2_status is None:
            return True
        elif role1_status is None or role2_status is None:
            return True
        elif role1_status == role2_status:
            return True
        else:
            return False

    def get_role_of_domain(self, domain: str, status = None) -> list:
        """
        Get roles of a specific domain.
        Args:
            domain (str): The domain to filter roles by.
        Returns:
            pd.DataFrame: A DataFrame containing roles of the specified domain.
        """
        if domain is None or domain == 'None':
            return self.df['Role'].tolist()
        elif domain in self.df['Domain'].unique():
            return self.df[self.df['Domain'] == domain]['Role'].tolist()
        elif domain in self.df['Domain'].unique() and status is not None and status in self.df['Status'].unique():
            return self.df[(self.df['Domain'] == domain) & (self.df['Status'] == status)]['Role'].tolist()
        else:
            raise ValueError(f"Domain '{domain}' and Status '{status}' not found in the data.")
        

def get_args():
    """
    Get the command line arguments.

    Returns:
        Namespace: The command line arguments.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Get attribution data.")
    parser.add_argument("--source_dir", type=str, default='./')
    parser.add_argument("--domain", type=str, default='family')
    
    return parser.parse_args()

if __name__ == "__main__":
    import os
    
    args = get_args()

    # Add the parent directory to the system path
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    role_instance = Role(args)

    df_total = role_instance.get_role_data(None)
    print(df_total)

    df_family = role_instance.get_role_data('family')
    print(df_family)

    df_prof = role_instance.get_role_data('professional')
    print(df_prof)

    print(role_instance.are_same_gender('mother', 'father'))