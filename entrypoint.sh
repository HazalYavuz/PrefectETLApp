#!/bin/bash


prefect server start --host 0.0.0.0 &


echo "Waiting for Prefect server to be ready..."
until curl -s http://localhost:4200/api/health > /dev/null; do
    sleep 5
    echo "Prefect server is not ready yet..."
done
echo "Prefect server is ready!"


if ! prefect work-pool inspect docker-pool > /dev/null 2>&1; then
    echo "Creating work pool: docker-pool..."
    prefect work-pool create docker-pool --type process --overwrite
else
    echo "Work pool docker-pool already exists."
fi

echo "Deploying all flows..."
prefect deploy --all


declare -a deployments=("ETL Line/etl-flow-deployment" "Payment Insertion Flow/payment-insertion-deployment")

for deployment in "${deployments[@]}"; do
    echo "Running deployment: $deployment..."
    prefect deployment run "$deployment"

    if [ $? -eq 0 ]; then
        echo "Deployment $deployment successfully triggered."
    else
        echo "Error occurred while running deployment: $deployment"
        exit 1
    fi

    sleep 5
done

echo "Starting worker for pool: docker-pool..."
prefect worker start --pool docker-pool