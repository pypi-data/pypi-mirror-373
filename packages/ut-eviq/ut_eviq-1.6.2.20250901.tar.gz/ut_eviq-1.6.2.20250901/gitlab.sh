# create a new repository on the command line
git init
git add .
git commit -m "first commit"

# stage all changes
git add .
# commit changes
git commit -m "2. commit"
git commit -m "3. commit"
git commit -m "4. commit"

git config --global --add safe.directory /mnt/hgfs/SOURCE/python/ut_eviq
git config --global user.email "bernd.stroehle@gmail.com"
git config --global user.name "Bernd Stroehle"

# push an existing repository from the command line
git remote add origin.gitlab.ui_otec_srr https://gitlab.com/bs29/ut_eviq.git
git remote add origin.gitlab https://gitlab.com/bs29/ut_eviq.git
git branch -M main
git push -uf origin.gitlab.ut_eviq main

# git remote add gitlab.ui_otec_srr git@gitlab.com:bs29/ut_eviq.git
git remote remove gitlab.ut_eviq
git remote add origin.gitlab https://gitlab.com/bs29/ut_eviq.git
git push --set-upstream origin.gitlab --all
git push --set-upstream origin --tags
