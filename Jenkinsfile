pipeline {
    agent any

    triggers {
        cron('H 2,6,10,14,18,22 * * *')
    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timestamps()
    }

    stages {
        stage('Generate Configs') {
            steps {
                writeFile file: 'src/settings.json', text: params.MEDIA_SETTINGS_JSON
                writeFile file: '.env', text: "AI_KEYS=${params.AI_KEYS}\nAI_MODELS=${params.AI_MODELS}"
            }
        }
        stage('Run Bot') {
            steps {
                script {
                    sh 'docker-compose down || docker compose down'
                    sh 'docker-compose build || docker compose build'
                    sh 'docker-compose run --rm bot python -m src.main --once || docker compose run --rm bot python -m src.main --once'
                }
            }
        }
    }
}
