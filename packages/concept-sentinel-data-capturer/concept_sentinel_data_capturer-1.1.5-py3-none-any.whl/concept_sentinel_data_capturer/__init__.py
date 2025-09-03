import asyncio
from datetime import datetime
from .mappers import ContextRequest, env_variables

import os

class concept_sentinel_data_capturer:
    flag_env_variables = False
    @staticmethod
    def insertion_with_context(payload: ContextRequest):
        """
        Insert data with context. Can be called both synchronously and asynchronously.
        
        Args:
            payload (ContextRequest): The context request payload
            
        Returns:
            Response or Coroutine: Returns response directly if called sync, 
            or coroutine if called from async context
        """
        if not concept_sentinel_data_capturer.flag_env_variables:
            raise RuntimeError("Environment variables must be set using set_env_variables() before using this function")
        
        # Check if we're already in an async context
        try:
            loop = asyncio.get_running_loop()
            # If we get here, we're in an async context
            return concept_sentinel_data_capturer._async_insertion_with_context(payload)
        except RuntimeError:
            # No running loop, we're in sync context
            return concept_sentinel_data_capturer._sync_insertion_with_context(payload)
    
    @staticmethod
    async def _async_insertion_with_context(payload: ContextRequest):
        from .service import insertion_with_context
        """Internal async implementation"""
        try:
            start_time = datetime.now()
            print(f"start_time: {start_time}")
            print("before invoking records_insertion service (async)")
            response = await insertion_with_context(payload)
            print("after invoking records_insertion service (async)")
            print("exit create usecase routing method")
            end_time = datetime.now()
            print(f"end_time: {end_time}")
            total_time = end_time - start_time
            print(f"total_time: {total_time}")
            return response
        except Exception as e:
            print(e)
            raise
    
    @staticmethod
    def _sync_insertion_with_context(payload: ContextRequest):
        from .service import insertion_with_context
        """Internal sync implementation"""
        try:
            start_time = datetime.now()

            print(f"start_time: {start_time}")
            print("before invoking records_insertion service (sync)")
            response = asyncio.run(insertion_with_context(payload))
            print("after invoking records_insertion service (sync)")
            print("exit create usecase routing method")
            end_time = datetime.now()
            print(f"end_time: {end_time}")
            total_time = end_time - start_time
            print(f"total_time: {total_time}")
            return response
        except Exception as e:
            print(e)
            raise

    @staticmethod
    def set_env_variables(env_vars: env_variables)-> None:
        """
        Validate the environment variables against the defined schema.And setup environment variables.
        
        Args:
            env_vars (env_variables): An instance of env_variables containing the environment variables.
        """
        try:
            for key, value in env_vars.model_dump().items():
                os.environ[key] = value
            concept_sentinel_data_capturer.flag_env_variables = True
            print("Environment variables set successfully.")
        except Exception as e:
            print(f"Validation error: {e}")