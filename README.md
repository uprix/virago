# Virago repository

## Subject
TBD

## Directory structure
### assembly
contains code to assemble the product via CI/CD

### src
The src-directory contains all of the necessary items to recreate the provison process, currently the following directories contains the component settings/templates used for this:
* Cloudformation_template - templates for provision
* Lambda - Lambda functions used for provision process
* Roles - Roles to run and process the provision on the target account
* Stepfunction - State machine codes

### test
contains QA-code to accompany the assembling process and test the product
DEVELOP
