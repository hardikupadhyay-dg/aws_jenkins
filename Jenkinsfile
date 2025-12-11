pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
        S3_BUCKET  = 'hardik-lambda-artifacts'     // change to your bucket
        LAMBDA_FN  = 'EmpLambda'
        ZIP_NAME   = 'lambda.zip'
        S3_KEY     = "artifacts/${env.JOB_NAME}/${env.BUILD_NUMBER}/${ZIP_NAME}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/hardikupadhyay-dg/aws_jenkins.git'
            }
        }

        stage('Package Lambda') {
            steps {
                sh '''
                  rm -f ${ZIP_NAME}
                  zip ${ZIP_NAME} lambda_function.py
                '''
            }
        }

        // Upload and deploy wrapped in withAWS which uses the aws_creds credential ID
        stage('Upload to S3') {
            steps {
                // withAWS comes from the AWS Steps plugin and will supply AWS credentials & region
                withAWS(credentials: 'aws_creds', region: "${AWS_REGION}") {
                    sh '''
                      set -e
                      aws s3 cp ${ZIP_NAME} s3://${S3_BUCKET}/${S3_KEY}
                    '''
                }
            }
        }

        stage('Deploy Lambda (create or update)') {
            steps {
                withAWS(credentials: 'aws_creds', region: "${AWS_REGION}") {
                    sh '''
                      set -e
                      # Check if Lambda exists; if so update code from S3, otherwise create using S3
                      if aws lambda get-function --function-name ${LAMBDA_FN} >/dev/null 2>&1; then
                        echo "Updating existing Lambda function..."
                        aws lambda update-function-code \
                          --function-name ${LAMBDA_FN} \
                          --s3-bucket ${S3_BUCKET} \
                          --s3-key ${S3_KEY}
                      else
                        echo "Creating Lambda function..."
                        aws lambda create-function \
                          --function-name ${LAMBDA_FN} \
                          --runtime python3.11 \
                          --role arn:aws:iam::<ACCOUNT_ID>:role/LambdaEmpExecRole \
                          --handler lambda_function.lambda_handler \
                          --code S3Bucket=${S3_BUCKET},S3Key=${S3_KEY} \
                          --environment Variables="{EMP_TABLE=Emp_Master}"
                      fi
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully."
        }
        failure {
            echo "Pipeline failed — check console output."
        }
    }
}
