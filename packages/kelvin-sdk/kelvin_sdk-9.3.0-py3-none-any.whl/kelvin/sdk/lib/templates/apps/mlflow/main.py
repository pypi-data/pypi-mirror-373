import asyncio
from datetime import timedelta

import mlflow
import pandas as pd
from mlflow.pyfunc import PyFuncModel

from kelvin.application import KelvinApp
from kelvin.krn import KRNAsset
from kelvin.message import Recommendation


async def run_model(app: KelvinApp, asset: str, df: pd.DataFrame, model: PyFuncModel) -> None:
    # Print data frame
    print(f"Asset: {asset}\n\n{df}\n\n")

    # Clean up df by dropping rows with missing values
    df = df.dropna()

    if not df.empty:
        try:
            # Perform prediction using the loaded model
            prediction = model.predict(df)

            print(f"Prediction: {prediction}")

            # Create and Publish a Recommendation
            await app.publish(
                Recommendation(
                    resource=KRNAsset(asset),
                    type="prediction",
                    expiration_date=timedelta(hours=1),
                    description=f"Model has predicted the following value: {prediction}",
                    control_changes=[],
                )
            )

        except Exception as e:
            print(f"Error during prediction: {str(e)}")


async def main() -> None:
    # Load the MLflow model
    model = mlflow.pyfunc.load_model("model")
    print("Model successfully loaded")

    # Creating instance of Kelvin App Client
    app = KelvinApp()
    await app.connect()
    print("App connected successfully")

    async for asset, df in app.hopping_window(
        window_size=timedelta(minutes=1),
        hop_size=timedelta(seconds=30),
        round_to=timedelta(seconds=5),
    ).stream():
        # Run model
        await run_model(app=app, asset=asset, df=df, model=model)


if __name__ == "__main__":
    asyncio.run(main())
