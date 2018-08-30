# create gitea-server

... as gitlab-mock for test-pipeline

```
KEYNAME=gitea
aws ec2 create-key-pair --key-name $KEYNAME --output json | jq -r '.KeyMaterial'  > $KEYNAME.pem
chmod 400 $KEYNAME.pem
aws cloudformation create-stack --stack-name gitea --template-body file://assembly/testpipeline/gitea/giteaServer.yaml --parameters ParameterKey=KeyName,ParameterValue=gitea
ssh -i "gitea.pem" ec2-user@ec2-18-184-173-153.eu-central-1.compute.amazonaws.com
```

# alternatively: use github!
