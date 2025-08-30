import os
import logging

from daytona_sdk import AsyncDaytona, DaytonaConfig, CreateSandboxFromSnapshotParams, AsyncSandbox, SessionExecuteRequest, Resources, SandboxState

class DyaSandboxHelper:
    def __init__(self):
        api_key  = os.getenv("DAYTONA_API_KEY")
        api_url = os.getenv("DAYTONA_SERVER_URL", "https://app.self.daytona.io/api")
        target = os.getenv("DAYTONA_TARGET", "us")

        self.sandbox_image_name = os.getenv("DAYTONA_IMAGE_NAME", "kortix/suna:0.1.3")
        self.daytona = AsyncDaytona(DaytonaConfig(api_key=api_key, api_url=api_url,target=target))


    async def get_or_start_sandbox(self, sandbox_id: str) -> AsyncSandbox:
        """Retrieve a sandbox by ID, check its state, and start it if needed."""

        logging.info(f"Getting or starting sandbox with ID: {sandbox_id}")

        try:
            sandbox = await self.daytona.get(sandbox_id)

            # Check if sandbox needs to be started
            if sandbox.state == SandboxState.ARCHIVED or sandbox.state == SandboxState.STOPPED:
                logging.info(f"Sandbox is in {sandbox.state} state. Starting...")
                try:
                    await self.daytona.start(sandbox)
                    # Wait a moment for the sandbox to initialize
                    # sleep(5)
                    # Refresh sandbox state after starting
                    sandbox = await self.daytona.get(sandbox_id)

                    # Start supervisord in a session when restarting
                    await self.start_supervisord_session(sandbox)
                except Exception as e:
                    logging.error(f"Error starting sandbox: {e}")
                    raise e

            logging.info(f"Sandbox {sandbox_id} is ready")
            return sandbox

        except Exception as e:
            logging.error(f"Error retrieving or starting sandbox: {str(e)}")
            raise e

    async def start_supervisord_session(self, sandbox: AsyncSandbox):
        """Start supervisord in a session."""
        session_id = "supervisord-session"
        try:
            logging.info(f"Creating session {session_id} for supervisord")
            await sandbox.process.create_session(session_id)

            # Execute supervisord command
            await sandbox.process.execute_session_command(session_id, SessionExecuteRequest(
                command="exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf",
                var_async=True
            ))
            logging.info(f"Supervisord started in session {session_id}")
        except Exception as e:
            logging.error(f"Error starting supervisord session: {str(e)}")
            raise e

    async def create_sandbox(self, password: str, project_id: str = None) -> AsyncSandbox:
        """Create a new sandbox with all required services configured and running."""

        logging.debug("Creating new Daytona sandbox environment")
        logging.debug("Configuring sandbox with snapshot and environment variables")

        labels = None
        if project_id:
            logging.debug(f"Using sandbox_id as label: {project_id}")
            labels = {'id': project_id}

        params = CreateSandboxFromSnapshotParams(
            snapshot=self.sandbox_image_name,
            public=True,
            labels=labels,
            env_vars={
                "CHROME_PERSISTENT_SESSION": "true",
                "RESOLUTION": "1024x768x24",
                "RESOLUTION_WIDTH": "1024",
                "RESOLUTION_HEIGHT": "768",
                "VNC_PASSWORD": password,
                "ANONYMIZED_TELEMETRY": "false",
                "CHROME_PATH": "",
                "CHROME_USER_DATA": "",
                "CHROME_DEBUGGING_PORT": "9222",
                "CHROME_DEBUGGING_HOST": "localhost",
                "CHROME_CDP": ""
            },
            resources=Resources(
                cpu=2,
                memory=4,
                disk=5,
            ),
            auto_stop_interval=15,
            auto_archive_interval=2 * 60,
        )

        # Create the sandbox
        sandbox = await self.daytona.create(params)
        # print("*"*100)
        # print(sandbox.get_preview_link)
        logging.debug(f"Sandbox created with ID: {sandbox.id}")

        # Start supervisord in a session for new sandbox
        await self.start_supervisord_session(sandbox)

        logging.debug(f"Sandbox environment successfully initialized")
        return sandbox

    async def delete_sandbox(self, sandbox_id: str) -> bool:
        """Delete a sandbox by its ID."""
        logging.info(f"Deleting sandbox with ID: {sandbox_id}")

        try:
            # Get the sandbox
            sandbox = await self.daytona.get(sandbox_id)

            # Delete the sandbox
            await self.daytona.delete(sandbox)

            logging.info(f"Successfully deleted sandbox {sandbox_id}")
            return True
        except Exception as e:
            logging.error(f"Error deleting sandbox {sandbox_id}: {str(e)}")
            raise e

