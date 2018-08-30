# CI/CD-Pipeline Design

## Summary for Discussion/Presentation on Wednesday, 25th July 2018

### Status
1. the POC setup ```git-repo <-> AWS S3 <-> AWS CodePipeline``` is done
2. it's done for ```gitea``` example git and for AWS private account of stephan
3. pipelining is not working .... only triggered manually and has permission problems
4. see [README](git-to-amazon/README.md)

### Next steps
1. setup endpoint in a virago test CI/CD account (see issue 'set up an CI/CD-testaccount' from below)
2. setup webhook in DevOpsLab-Gitlab
3. continue pipelining with real baseline-code


## Summary for Discussion/Presentation on Friday, 20th July 2018
### Status
1. we have gitlab working (accesses, repo, git-connectivity, stale code content, new branch for Jira-81)
2. there is an [AWS Quick Start](#integrate-gitlab) how to run AWS codepipeline together with gitlab

### Proposed next steps until wednesday 25th july (my last day before vacation until 10th august)
1. setup interoparability from DevOpsLab (our Gitlab) to AWS 275662325630
2. setup CI-codepipeline for merges into develop-branch

### Issues
1. permissions for cloudformation for arn:aws:iam::275662325630:mfa/A319557
 * --> Andrej: CI/CD should not be developed within master account
 * --> set up an CI/CD-testaccount, to isolate development from the master account
2. clarifying use cases
 * --> not discussed. Andrej/Gabor state that
3. clarifying deployment environments, is distinction of environments only done via suffix _DEV, _TEST, _PROD??
  * --> yes, understanding is right, everything goes currently into master account
  * --> defintion of account-designations is needed
  * --> creating high level pictures of workflow graphs (gabor will start this task after vacation on 3rd august)
  * --> gabor updates code asap, latestly after coming back from vacation
  * --> lets have a all team meeting e.g. in september

## Top Level View: Pipelining means WorkFlow
![aws-flow]
### Definitions
* Continuous Integration (CI):
  1. make resp. **'build'** the software as a whole working i.e. 'runnable' _in the context of the runtime environment_
  1. CI happens when a commit to the 'develop'-branch was fulfilled. If the status is not 'success' the commit will be reverted.
  1. just record the process and give feedback to the engineers & don't care about outputs - throw them away
  1. the pull request into develop-branch is subject to the team. Typically at the moment of reviewing the PR the team already has a 'passing-feedback' from a branch-pipeline which build-tested the branch.
  1. build tests include unit, integration, sw-quality tests
* Continuous Delivery (CD):
  1. Put the built software under **functional and system test stress**
  1. **certify** its quality
  1. deliver the software as a **runnable artifact** into a drawer - _not_ into production
  1. CD happens when a commit to the 'master'-branch was fulfilled. 'master' is claimed to be **'always release ready'**
  1. thus the pull request into master is subject to the team and the product owner. At the moment of reviewing the PR there is a 'passing-feedback' from the preceeded test of the develop-branch pipeline. This is a bit quirky and depends and the concrete workflow and pipelines within the project.
* Continuous Deployment (CDP):
  1. deploy the built software into a **production environment**
  1. test and validate its quality under production conditions
  1. rollback to last version if not succeeded

### Flow Visualization
The underlying flow of the pipelines should be visualized in terms of stages, environments, engines, actions, status. In the following we'll see a nice example which just is meant to emphasise the idea:

#### Emphasize on Actions and Engines
![oncoscape-cicd]
![oncoscape-cicd-highlighted]

#### Emphasize on Stages and Environments
![Stages in AWS CodePipeline][aws-cicd]

# Use Cases relevant for CI/CD (WIP ... tbd)

# business use cases
1. productive stacksets are used by BMC to create new Client Accounts
1. productive stacksets are used to configure existing client accounts
1. developing a new Baseline version results in updating productive CF Templates and Stacksets
1. Updating the Baseline version on an individual AWS Account results in attaching the account to new productive CF Stacksets

## developing use cases
1. A developer develops new 'code' (i.e. cf templates, policies, lambdas, roles, stepfunctions). In an - ideally - test driven approach he or she first defines unit tests. These tests are run when pushing to his or her upstream branch in DevOpsLab.
2. Same holds for changing code.
3. tbc

# Implementation

## CodePipeline

### General
* https://aws.amazon.com/blogs/devops/category/developer-tools/aws-codepipeline/
* https://docs.aws.amazon.com/de_de/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html
* https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-create.html#pipelines-create-cli
* https://aws.amazon.com/blogs/devops/using-aws-step-functions-state-machines-to-handle-workflow-driven-aws-codepipeline-actions/
* https://aws.amazon.com/blogs/devops/continuous-delivery-of-nested-aws-cloudformation-stacks-using-aws-codepipeline/

### create own Actions
* https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-invoke-lambda-function.html

`In this blog post, we discussed how state machines in AWS Step Functions can be used to handle workflow-driven actions. We showed how a Lambda function can be used to fully decouple the pipeline and the state machine and manage their interaction. The use of a state machine greatly simplified the associated CodePipeline action, allowing us to build a much simpler and cleaner pipeline while drilling down into the state machine’s execution for troubleshooting or debugging.`

* https://aws.amazon.com/blogs/devops/using-aws-step-functions-state-machines-to-handle-workflow-driven-aws-codepipeline-actions/
* https://github.com/aws-samples/aws-codepipeline-stepfunctions

### Different environments

* https://aws.amazon.com/premiumsupport/knowledge-center/test-prod-environments-codepipeline/
* https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-basic-walkthrough.html

## Test
### Policy-Simulation via CLI
* https://docs.aws.amazon.com/de_de/IAM/latest/UserGuide/access_policies_testing-policies.html#policies-simulator-using-api

## Lambda

### Configuration Environment Variables

#### AWS

##### 12factor App Paradigm
* https://12factor.net/config
*  https://aws.amazon.com/blogs/compute/applying-the-twelve-factor-app-methodology-to-serverless-applications/

##### AWS Best Practices & EnvVars
* https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html
* https://docs.aws.amazon.com/lambda/latest/dg/env_variables.html
* https://docs.aws.amazon.com/lambda/latest/dg/tutorial-env_cli.html
* https://aws.amazon.com/blogs/aws/new-for-aws-lambda-environment-variables-and-serverless-application-model/

##### CLI Usage  (some excerpts from the links above)
```
aws lambda create-function \
    --region us-east-1
    --function-name myTestFunction
    --zip-file fileb://path/package.zip
    --role role-arn
    --environment Variables="{LD_LIBRARY_PATH=/usr/bin/test/lib64}"
    --handler index.handler
    --runtime nodejs6.10
    --profile default
```
```
aws lambda update-function-configuration
--function-name ReturnBucketName \
--region us-east-1 \
--environment Variables={S3_BUCKET=Prod}
```

#### Python Implementation

####  The `import os` way
```
...
import os
...
print("S3_BUCKET environment variable: " + os.environ['S3_BUCKET'])
```

##### The `.env` way (does this work for lambda ???)
* https://github.com/theskumar/python-dotenv

##### Interesting alternative file-based approach with decoration
Just for information and an interesting programming design, should nout be nescessary:
*  https://gist.github.com/patrickbrandt/21fc41459fe6a6a19e31

### Deploy

#### specific
* https://github.com/aws-samples/aws-lambda-deploy
* https://docs.aws.amazon.com/lambda/latest/dg/deploying-lambda-apps.html
* https://aws.amazon.com/de/blogs/devops/secure-aws-codecommit-with-multi-factor-authentication/
* https://docs.aws.amazon.com/lambda/latest/dg/automating-deployment.html

#### generic
* https://github.com/Miserlou/Zappa
* google://serverless aws python cicd

## awslabs
* https://github.com/awslabs

## step functions
tbd

## lambda & step-functions
tbd

### generic
* https://serverless.com/blog/how-to-manage-your-aws-step-functions-with-serverless/

## Integrate Gitlab
### setup gitlab test server with CF (Alternative: setup gitea)
* https://gitlab.com/gitlab-org/gitlab-aws-quickstart

#### create bucket to store gitlab stuff
```
# https://docs.aws.amazon.com/cli/latest/reference/s3api/create-bucket.html
# variante 1
stl@W4DEUMSY9003054 MINGW64 ~/Documents/git
$ aws s3 mb s3://stl-gitlab-quickstart-bucket
make_bucket: stl-gitlab-quickstart-bucket

# variante 2
stl@W4DEUMSY9003054 MINGW64 ~/Documents/git
$ aws --region eu-central-1 s3api create-bucket --bucket stl-gitlab-quickstart-bucket-2 --acl public-read --create-bucket-configuration LocationConstraint=eu-central-1
{
    "Location": "http://stl-gitlab-quickstart-bucket-2.s3.amazonaws.com/"
}
```
#### create KeyPair
```
KEYNAME=GitLab
aws ec2 create-key-pair --key-name $KEYNAME --output json | jq -r '.KeyMaterial'  > $KEYNAME.pem
```

### connect gitlab server with virago-account
* https://aws.amazon.com/quickstart/architecture/git-to-s3-using-webhooks/
* https://aws-quickstart.s3.amazonaws.com/quickstart-git2s3/doc/git-to-amazon-s3-using-webhooks.pdf
```
who are planning to implement AWS  services that use Amazon S3 as a source
in the AWS Cloud. Examples of such services include AWS CodePipeline, AWS CodeBuild, and AWS CodeDeploy
```
```
aws --region eu-west-1 cloudformation create-stack --stack-name gitlab2s3 --template-body file://git2s3.template --capabilities CAPABILITY_IAM
... at 'templateBody' failed to satisfy constraint: Member must have length less than or equal to 51200
```
```
stl@amplatz ~/git/ViragoProject/assembly  (develop *) $ aws s3api create-bucket --bucket stltemplates --region eu-central-1 --create-bucket-configuration LocationConstraint=eu-central-1
{
    "Location": "http://stltemplates.s3.amazonaws.com/"
}
```

# log / issues
* 19.07.2019, arn:aws:iam::275662325630:mfa/A319557
  * github integration works
  * codepipeline fails - no permissions for codebuild
  * User: ```arn:aws:iam::275662325630:user/A319557 is not authorized to perform: cloudformation:CreateStack on resource: arn:aws:cloudformation:eu-west-1:275662325630:stack/gitlab2s3/*```

# References
[aws-cicd]: https://d1.awsstatic.com/Projects/CICD%20Pipeline/setup-cicd-pipeline2.5cefde1406fa6787d9d3c38ae6ba3a53e8df3be8.png
[oncoscape]: https://www.slideshare.net/Robert_McDermott/anatomy-of-a-continuous-integration-and-delivery-cicd-pipeline
[oncoscape-cicd-origin]: https://image.slidesharecdn.com/swag-cicd-oncoscape-160527152155/95/anatomy-of-a-continuous-integration-and-delivery-cicd-pipeline-8-638.jpg?cb=1464363420
[oncoscape-cicd-highlighted-origin]:
https://image.slidesharecdn.com/swag-cicd-oncoscape-160527152155/95/anatomy-of-a-continuous-integration-and-delivery-cicd-pipeline-9-1024.jpg?cb=1464363420
[cisco-aws-cicd]: https://gblogs.cisco.com/ch-tech/cloud-agnostic-cicd-pipeline-for-devops-building-blocks/?doing_wp_cron=1532073413.3931450843811035156250
[aws-flow]: https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRI5mKThaQlkwvbQA0qsDcAmqiddlLRXFHV5Rq59IuOtqWQPyFRkQ
[atlassian-ci-cd]: https://www.atlassian.com/continuous-delivery/ci-vs-ci-vs-cd
[trunkbaseddevelopment]: https://trunkbaseddevelopment.com
[humble-farley-cicd]:
https://continuousdelivery.com/implementing/patterns/
[oncoscape-cicd]: ./doc/_assets/anatomy-of-a-continuous-integration-and-delivery-cicd-pipeline-8-638.jpg
[oncoscape-cicd-highlighted]:
./doc/_assets/anatomy-of-a-continuous-integration-and-delivery-cicd-pipeline-9-1024.jpg
