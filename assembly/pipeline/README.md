# Setup Virago-CodePipeline in an Account

## WIP: step by step

### 1. create roles needed by CodePipeline
```
aws cloudformation create-stack --stack-name codepipeline-roles --template-body file://assembly/pipeline/codepipeline-service-roles.yaml  --capabilities="CAPABILITY_NAMED_IAM"
```

### 2. setup a pipeline

#### deploy a draft
```
aws codepipeline create-pipeline --cli-input-json file://assembly/pipeline/pipeline.json
```

#### edit it in the webui
* set github Source
* set dummy action

# Finally: completely automted

## Pipeline

### Bucket
```
stl@W4DEUMSY9003054 MINGW64 ~
$ aws --region eu-central-1 s3api create-bucket --bucket 412318185247-pipeline --create-bucket-configuration LocationConstraint=eu-central-1            
{
    "Location": "http://412318185247-pipeline.s3.amazonaws.com/"
}
```
```
aws s3api put-bucket-versioning --bucket 412318185247-pipeline --versioning-configuration Status=Enabled

# provide files for pipline
# see https://stelligent.com/2016/02/15/mocking-aws-codepipeline-pipelines-with-lambda/
aws s3 cp assembly/testpipeline/Archive.zip s3://297193019640-pipeline
aws s3 cp assembly/testpipeline/dummy-file.txt s3://297193019640-pipeline
```

### CodePipeline
* github-Integration (OAuth-Token): https://docs.aws.amazon.com/codepipeline/latest/userguide/GitHub-rotate-personal-token-CLI.html

```
aws cloudformation create-stack --stack-name mockPipeline --template-body file://assembly/pipeline/mockedPipeline.json --capabilities="CAPABILITY_IAM"
aws cloudformation describe-stack-events --stack-name mockPipeline
aws cloudformation list-stacks --stack-status-filter ROLLBACK_FAILED CREATE_IN_PROGRESS ROLLBACK_COMPLETE
```
