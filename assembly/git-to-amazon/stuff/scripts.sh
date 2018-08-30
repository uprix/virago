aws cloudformation create-stack \
--stack-name CodePipelineLambdaStack \
--template-body https://raw.githubusercontent.com/stelligent/cloudformation_templates/master/labs/codepipeline/codepipeline-cross-account-pipeline.json \
--region eu-central-1
--disable-rollback --capabilities="CAPABILITY_IAM"  \
--parameters ParameterKey=KeyName,ParameterValue=GitLab
