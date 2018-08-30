getStackInstanceState.py

This python lambda function checks stack instance status. 
Stacksetname is hardcoded!

role must be able to write to cloudwatch logs, and get access for cloudformation, currently provisiamrole is used
----

provisionIamAdmin.py

This lambda function creates AWSCloudFormationStackSetExecutionRole role in the target account

role currently is provisioniamrole
----

createCloudFormationInstance.py

This lambda function creates a stack instance on the target account from the stack set fullv3 (hardcoded value).

role currently is provisioniamrole
----

createPasswordPolicy.py

This lambda function creates password policy on the target account

role currently is provisioniamrole
----

