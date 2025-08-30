# -*- coding: utf-8 -*-
"""
This script demonstrates a basic Model Context Protocol (MCP) client
using the fastmcp library. It defines a simple model and registers it
with the client, making it ready to receive requests.
"""

import logging
from fastmcp import Client, Model
from fastmcp.context import Context
from fastmcp.model import ModelInput, ModelOutput

# Configure logging for better visibility of fastmcp operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExampleModel(Model):
    """
    A simple example model that processes text input and returns a modified text.
    This model demonstrates how to define a model and implement its 'call' method.
    """

    def __init__(self):
        super().__init__()
        self.name = "example-model"
        self.version = "1.0.0"
        logger.info(f"Initialized {self.name} v{self.version}")

    async def call(self, inputs: ModelInput, context: Context) -> ModelOutput:
        """
        The core method where the model's logic resides.
        It takes ModelInput and Context, and returns ModelOutput.

        Args:
            inputs (ModelInput): The input data for the model.
                                 Expected to contain a 'text' field.
            context (Context): The context object providing access to
                               session information, logging, etc.

        Returns:
            ModelOutput: The output data from the model.
                         Contains a 'processed_text' field.
        """
        logger.info(f"Model '{self.name}' received a call.")
        
        # Access input data. ModelInput is typically a dictionary-like object.
        input_text = inputs.get("text", "No text provided")
        logger.info(f"Input text: '{input_text}'")

        # Simulate some processing
        processed_text = f"Processed: {input_text.upper()} (by {self.name})"

        # You can also access context information, e.g., session ID
        session_id = context.session_id
        logger.info(f"Processing for session ID: {session_id}")

        # Return the processed output as a ModelOutput object
        return ModelOutput({"processed_text": processed_text})

async def main():
    """
    Main function to initialize and run the fastmcp client.
    """
    logger.info("Starting FastMCP client setup...")

    # Create an instance of the FastMCP client
    # You can specify the host and port where the client will listen for requests.
    # By default, it listens on 0.0.0.0:8000
    client = Client(host="0.0.0.0", port=8000)
    logger.info(f"FastMCP client initialized on {client.host}:{client.port}")

    # Create an instance of your custom model
    example_model = ExampleModel()

    # Register the model with the client
    # The model will be accessible via its name (e.g., "example-model")
    client.register_model(example_model)
    logger.info(f"Model '{example_model.name}' registered with the client.")

    # Start the client. This will block and listen for incoming requests.
    # For a real application, you might integrate this into a larger ASGI server
    # or a systemd service.
    logger.info("FastMCP client is starting to listen for requests...")
    await client.start()

if __name__ == "__main__":
    # To run this script, you would typically use an ASGI server like Uvicorn:
    # uvicorn your_script_name:main --factory
    #
    # However, for a simple direct run to see it initialize, you can use:
    import asyncio
    asyncio.run(main())
    # Note: Running directly with asyncio.run(main()) will start the server,
    # but you'll need to send requests to it from another process.
    # For proper testing, use `uvicorn your_script_name:client.app` after
    # changing `await client.start()` to `return client.app` in `main()`
    # and importing `main` as the ASGI app.
