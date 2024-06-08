#push the changes made in the repository to github
git add .
read -p 'Commit message: ' commit
git commit -m "$commit"
git push