# gstat
Install requirements.txt using pip install -r requirements.txt
Run ./git_stat --since 10 --repos_list_path <filepath to repos> --users_path <filepath to users> --token <gittoken> --output_path ./out.csv

repos_list_path is a path to file containing repos - 
Content should be like this
```
<org>/repo
<org2>/repo
```
