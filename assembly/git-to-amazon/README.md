# POC: Interconnect gitlab or any other external git with AWS-Virago

## Summary
* Use ```git2s3```-quick start template to set up a virago endpoint for git-push-triggers
* setup a test git, connect it to the endpoint and play around with push-events
* reuse this to connent DevOpsLabs-Gitlab with AWS-Virago-baseline CI/CD

## Step 1: Setup AWS-Virago endpoint
* goto https://aws.amazon.com/quickstart/architecture/git-to-s3-using-webhooks/ or https://github.com/aws-quickstart/quickstart-git2s3
* NOTICE: the stack creation will not work locally on the commandline as the template is too huge - you must load it into a s3-bucket
* set allowed IP's to '0.0.0.0/0' (as we currently do not know the gitlab-server IP)
* hint: template is here: https://aws-quickstart.s3.amazonaws.com/quickstart-git2s3/templates/git2s3.template

### Result
```
Stack name:

    Git-to-Amazon-S3

Stack ID:

    arn:aws:cloudformation:eu-central-1:297193019640:stack/Git-to-Amazon-S3/62576a70-8fec-11e8-8e3a-500c52a6ce62
```

## Step 2: connect repo to endpoint
* create a test repo on git side, create and permit a user accessto this repo
* create access via key for this user and copy the ```PublicSSHKey``` into it
* copy the ```GitPullWebHookApi```-URL and add it on the git-side (add webhook typically) (e.g. https://wvjiy5gc19.execute-api.eu-central-1.amazonaws.com/Prod/gitpull)

### Result
* Pushes into the test-git lead to S3-events which pull the git repo and store it into a zip
* e.g. (see directory-structure!) ```https://s3.eu-central-1.amazonaws.com/virago-baseline/stl/baseline/branch/master/stl_baseline_branch_master.zip```
* i.e. branches are covered within folders

## Step 3: [WIP] optional: simulate a pipeline

### create pipeline
* see https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-create.html#pipelines-create-cli
```
aws --region eu-central-1 codepipeline create-pipeline --cli-input-json file://assembly/git-to-amazon/cli-pipeline.json
```

### create cloudwatch event
* see https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-trigger-source-repo-changes-cli.html
* or even better: https://docs.aws.amazon.com/codepipeline/latest/userguide/create-cloudtrail-S3-source-cli.html
```
aws cloudtrail create-trail --name virago-baseline-trail --s3-bucket-name virago-baseline/stl/baseline/branch/master
```

### Result
* the pipeline is triggered after pushes

## tbd
* script and automate all that

## Alternative approach
* https://aws.amazon.com/blogs/devops/using-custom-source-actions-in-aws-codepipeline-for-increased-visibility-for-third-party-source-control/
* see CF-template in Launch-Links: https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/new?stackName=CustomSourceActionDemo&templateURL=https://custom-source-action-blog-eu-west-1.s3.amazonaws.com/cloudformation_arch_1.yaml

## References
* Precedent Version: https://aws.amazon.com/blogs/devops/integrating-git-with-aws-codepipeline/
