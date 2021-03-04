## Introduction
Visor rest api project will support Visor apis namely
- Get a Session
- Upload a image
- Get a Session

## Deployment Pipeline with Bitbucke and AWS Code Deploy
We will be configuring AWS Code deploy to automate the deployments to AWS EC2, below are the steps

### References
- follow the document below to setup the instance
https://medium.com/technext/bitbucket-to-aws-ec2-continuous-deployment-pipeline-using-aws-code-deploy-for-php-application-e39004243cd9

- Install Code Deploy Agent
Follow instructions in
https://docs.aws.amazon.com/codedeploy/latest/userguide/codedeploy-agent-operations-install-ubuntu.html

 - wget https://aws-codedeploy-us-west-1.s3.us-west-1.amazonaws.com/latest/install

## Step1 - EC2 configuration
``` ssh -i "testkey.pem" ubuntu@ec2-13-56-151-146.us-west-1.compute.amazonaws.com ```

## Step2 - AWS Configuration
### Setup users and roles
- refer ot the medium document above for user and roles changes

## Step3 - Add the Codedeploy script and start and stop scripts

## Step4 - write the bitbucket yaml file

## How to build and make changes
- Make the changes
- git push
- bitbucket will deploy the changes to EC2 with aws codedeploy