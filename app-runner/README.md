# App Runner Deployment (Simple)

Den här mappen innehåller ett enkelt sätt att köra **backend-minimal** på **AWS App Runner**.

## Förutsättningar
- ECR-repo med din image (workflow skapar `ai-realtime-backend`).
- En **App Runner service** som *redan* har:
  - Access Role (IAM) med `AWSAppRunnerServicePolicyForECRAccess` för att dra från ECR.
  - En definierad **Secret** i AWS Secrets Manager med din OpenAI-nyckel.
- OIDC-roll för GitHub Actions (`AWS_OIDC_ROLE_ARN`) som får:
  - Push till ECR
  - `apprunner:UpdateService` på din service
  - `secretsmanager:GetSecretValue` (indirekt via App Runner räcker)

## Skapa tjänsten första gången (CLI)
Fyll i variablerna nedan och kör skriptet:

```bash
export AWS_REGION=eu-north-1
export ECR_URI="<ACCOUNT>.dkr.ecr.${AWS_REGION}.amazonaws.com/ai-realtime-backend:latest"
export APP_RUNNER_ROLE_ARN="arn:aws:iam::<ACCOUNT>:role/AppRunnerECRAccessRole"
export OPENAI_API_KEY_SECRET_ARN="arn:aws:secretsmanager:${AWS_REGION}:<ACCOUNT>:secret:openai/prod-xxxxx"

aws apprunner create-service \
  --service-name ai-realtime-backend \
  --source-configuration '{
    "AuthenticationConfiguration": {
      "AccessRoleArn": "'"${APP_RUNNER_ROLE_ARN}"'"
    },
    "ImageRepository": {
      "ImageIdentifier": "'"${ECR_URI}"'",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8080",
        "RuntimeEnvironmentVariables": [
          {"Name":"OPENAI_MODEL","Value":"gpt-4o"}
        ],
        "RuntimeEnvironmentSecrets": [
          {"Name":"OPENAI_API_KEY","Value":"'"${OPENAI_API_KEY_SECRET_ARN}"'"}
        ]
      }
    }
  }'
```

Spara ut **Service ARN** och lägg den som GitHub secret `APP_RUNNER_SERVICE_ARN`.

## GitHub Secrets (krav)
- `AWS_OIDC_ROLE_ARN` — IAM Role som GitHub Actions får *assume* (ECR push + App Runner update)
- `APP_RUNNER_SERVICE_ARN` — din App Runner service ARN
- `OPENAI_API_KEY_SECRET_ARN` — ARN till Secrets Manager-hemligheten
