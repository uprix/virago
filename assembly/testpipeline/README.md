# Setup a test pipeline

Source/Ref: https://stelligent.com/2016/02/15/mocking-aws-codepipeline-pipelines-with-lambda/

1. create/use a s3-bucket with versioning enabled
2. upload 'Archive.zip' (which contains the mock-lambda)
3. upload a dummy-code-artifact 'license.txt'
4. deploy stack
```
aws cloudformation create-stack --stack-name mockPipeline --template-body file://assembly/testpipeline/mockedPipeline.json --capabilities="CAPABILITY_IAM"
```
5. switch source to github
