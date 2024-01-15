# FAI23_Proj2_G02

# READ ME PLEASE:

This are the very first instructions you must follow before executing any code:

## Install:

***NOTE: All code presented on this repository was built under Python 3.10.13 (Anaconda) on Windows Platform in VsCode***

**Process (may take some time):**

   *1.* Clone the repository to your machine

   *2.* Install Anaconda/Miniconda

   *3.* Open your Anaconda prompt

   *4.* For Windows:
        Create a virtual environment with the ml_env.yml file (Windows Build) located in the repository, typing in the console:
      
           conda env create -n your_new_envname -f ml_env.yml (your machine path to this file)

   *5.* No builds (all Operating Systems):
        Create a virtual environment with the ml_env_noBuilds.yml file located in the repository, typing in the console:
      
           conda env create -n your_new_envname -f ml_env_noBuilds.yml (your machine path to this file)
           
   *6.* Add Jupyter Kernel:
   
           conda activate your_new_envname
           python -m ipykernel install --user --name=your_new_envname

## Structure:

This project is divided in two jupyter notebooks. One for the supervised learning (Supervised_Learning.ipynb) and the other for the unsupervised learning (Unsupervised_Learning.ipynb).
