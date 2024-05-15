from __future__ import annotations

import logging
import os
import pandas as pd
import numpy as np
from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.python import is_venv_installed

log = logging.getLogger(__name__)

# Check if virtualenv is installed
if not is_venv_installed():
    log.warning("The tutorial_taskflow_api_virtualenv example DAG requires virtualenv, please install it.")
else:
    @dag(schedule_interval=None, start_date=datetime(2021, 1, 1), catchup=False, tags=["big_data"])
    def homework2_data_pipeline_demo():
        """
        ### TaskFlow API example using virtualenv
        This is a simple data pipeline example which demonstrates the use of the TaskFlow API using three simple tasks for Extract, Transform, and Load.
        """

        @task.virtualenv(
            use_dill=True,
            system_site_packages=False,
            requirements=["funcsigs", "pandas"],  # Updated requirements
        )
        def data_acquisition():
            """
            #### Data Acquisition
            This task will download data from an internet data source and save data to a specific location that is "shareable" with the other tasks.
            """
            import pandas as pd
            import os

            # Define data acquisition parameters
            data_id = "Metro_zori_uc_sfrcondomfr_sm_month.csv"
            data_path = "/storage/acquire/" + data_id

            # Create directories if they don't exist
            os.makedirs(os.path.dirname(data_path), exist_ok=True)

            # Simulate data acquisition
            df = pd.read_csv(data_path)


            
            # Save data as CSV
            df.to_csv(data_path, index=False)



            return {"status": "success", "data_path": data_path}

        @task()
        def data_cleanse(data_package: dict):
            """
            #### Data Cleanse
            This task cleans the data given a path to the recently acquired data.
            """
            import pandas as pd
            import os

            # Retrieve CSV file path from the data package
            csv_file_path = data_package.get("data_path")  

            # Read CSV file
            try:
                df = pd.read_csv(csv_file_path)
            except Exception as e:
                return {"status": "failed", "error": str(e)}  # Return failure status if reading CSV fails

            # Filter data
            
            df = df[df["StateName"] == "CA"]

            
            # Define cleanse folder and file path
            cleanse_folder = "/storage/cleanse"
            os.makedirs(cleanse_folder, exist_ok=True)
            cleanse_file_path = os.path.join(cleanse_folder, os.path.basename(csv_file_path))

            # Save cleansed data as CSV
            try:
                df.to_csv(cleanse_file_path, index=False)
            except Exception as e:
                return {"status": "failed", "error": str(e)}  # Return failure status if writing CSV fails

            return {"status": "success", "cleanse_path": cleanse_file_path}



        @task()
        def data_analysis(data_package: dict):
            """
            #### Analysis
            This task performs statistical analysis on the data given a path to the recently cleansed data.
            """
            import os
            import logging


            # Retrieve cleansed file path from the data package
            cleanse_file_path = data_package.get("cleanse_path")

            # Read the cleansed CSV file
            try:
                df = pd.read_csv(cleanse_file_path)
            except Exception as e:
                return {"status": "failed", "error": str(e)}  # Return failure status if reading CSV fails

            # Perform quantitative statistical analysis
            quantitative_results = {}
            # Example: calculate mean, median, standard deviation
            quantitative_results['mean_price'] = df['Price'].mean()
            quantitative_results['median_price'] = df['Price'].median()
            quantitative_results['std_price'] = df['Price'].std()

            # Perform qualitative statistical analysis
            qualitative_results = {}
            # Example: count of unique values in a column
            qualitative_results['unique_count_state'] = df['StateName'].nunique()
            # Example: value counts of a categorical variable
            qualitative_results['value_counts_city'] = df['City'].value_counts()

            # Save the statistical analysis results
            analysis_results = {
                "quantitative": quantitative_results,
                "qualitative": qualitative_results
            }

            # Define analysis data path
            analysis_folder = "/storage/analysis"
            os.makedirs(analysis_folder, exist_ok=True)
            analysis_file_path = os.path.join(analysis_folder, "analysis_results.csv")

            # Save analysis results as CSV
            try:
                pd.DataFrame(analysis_results).to_csv(analysis_file_path, index=False)
            except Exception as e:
                return {"status": "failed", "error": str(e)}  # Return failure status if writing CSV fails

            return {"status": "success", "analysis_path": analysis_file_path}

        
        @task()
        def visualize(data_package: dict):
            """
            #### Visualize
            This task performs visualization on the data given path to
            """
            # Placeholder visualization task
            log.info("Visualization task completed.")

        # Define data flow
        data_a = data_acquisition()
        data_b = data_cleanse(data_a)
        data_c = data_analysis(data_b)

        visualize(data_c)

    python_demo_dag = homework2_data_pipeline_demo()



