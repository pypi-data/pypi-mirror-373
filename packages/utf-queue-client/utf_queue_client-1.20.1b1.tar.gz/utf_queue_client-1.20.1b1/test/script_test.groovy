pipeline {
    agent {
        dockerfile {
            filename 'test/Dockerfile.script_test'
            label "Docker_Linux"
        }
    }
    options {
        disableConcurrentBuilds()
    }
    stages {
        stage("environment setup") {
            steps {
                sh '''
                    rm -rf venv
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install ubai_client
                    pip install .
                '''
            }
        }
        stage('Run Tests') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'sqatest_readwrite', passwordVariable: 'UTF_QUEUE_PASSWORD', usernameVariable: 'UTF_QUEUE_USERNAME')]) {
                    sh '''
                    . venv/bin/activate

                    ubai_search_cli --name test --extension .hex --metadata app_name ubai_unit_test
                    '''
                }


            }
        }
    }
}