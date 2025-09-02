# create a new repository on the command line
git init

# stage all changes
git add .

# commit changes
git commit -m "first commit"
git commit -m "second commit"
git commit -m "third commit"

git config --global --add safe.directory /mnt/hgfs/SOURCE/python/ui_eviq_srr
git config --global user.email "bernd.stroehle@gmail.com"
git config --global user.name "Bernd Stroehle"

# push an existing repository from the command line
git remote add origin.ui_eviq_srr https://github.com/bs2910/ui_eviq_srr.git
git branch -M main
git push -u origin.ui_eviq_srr main
