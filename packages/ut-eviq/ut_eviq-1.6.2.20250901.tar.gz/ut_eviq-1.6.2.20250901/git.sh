# Navigate to Your Project Directory: Open your terminal and navigate to the directory where your project is located:

cd path/to/your/project

# ------------------------------------------------
# Initialize Git: Initialize a new Git repository:
# ------------------------------------------------
git init

# hint: Using 'master' as the name for the initial branch. This default branch name
# hint: is subject to change. To configure the initial branch name to use in all
# hint: of your new repositories, which will suppress this warning, call:
# hint: 
# hint: 	git config --global init.defaultBranch <name>
# hint: 
# hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
# hint: 'development'. The just-created branch can be renamed via this command:
# hint: 
# hint: 	git branch -m <name>
# Initialized empty Git repository in /mnt/hgfs/SOURCE/python/ut_eviq/.git/

# Add Remote Repository: Link your local repository to the GitHub repository you created:
git config --global --add safe.directory /mnt/hgfs/SOURCE/python/ut_eviq
git remote add ui_otev_srr https://github.com/bs291048/ut_eviq.git

# fatal: detected dubious ownership in repository at '/mnt/hgfs/SOURCE/python/ut_eviq'
# To add an exception for this directory, call:
# git config --global --add safe.directory /mnt/hgfs/SOURCE/python/ut_eviq

# ------------------------------------------------------
# Add Files: Add your project files to the staging area:
# ------------------------------------------------------
git add .

# --------------------------------------------------------------
# Commit Changes: Commit your changes with a meaningful message:
# --------------------------------------------------------------
git config --global user.email "bernd.stroehle@kosakya.de"
git config --global user.name "Bernd Stroehle"
git commit -m "Initial commit"

# -----------------------------------------------------------
# Push to GitHub: Push your changes to the GitHub repository:
# -----------------------------------------------------------
git push -u ut_eviq
