from io import BytesIO
from http import HTTPStatus
from types import SimpleNamespace

from .api.configuration import delete_configuration, get_configuration, list_configurations, save_configuration
from .api.document import upload_files, process_document, upload_document
from .api.document.process_document import asyncio_detailed as process_document_async, sync_detailed as process_document_sync
from .api.document.process_document_with_configuration import asyncio_detailed as process_document_with_configuration_async, sync_detailed as process_document_with_configuration_sync
from .api.document.upload_files import asyncio_detailed as upload_files_async, sync_detailed as upload_files_sync
from .api.document.ocr_document import asyncio_detailed as ocr_document_async, sync_detailed as ocr_document_sync
from .api.job import result, status
from .api.cases.create_case import asyncio_detailed as create_case_async, sync_detailed as create_case_sync
from .api.cases.get_case import asyncio_detailed as get_case_async, sync
from .api.cases.list_cases import asyncio_detailed as list_cases_async, sync_detailed as list_cases_sync
from .api.cases.upload_case_document import asyncio_detailed as upload_case_document_async, sync_detailed as upload_case_document_sync
from .api.document.upload_document import asyncio_detailed as upload_document_async, sync_detailed as upload_document_sync
from .api.operations.submit_operation import asyncio as submit_operation_async, sync as submit_operation_sync
from .api.operations.get_operation_status import asyncio as get_operation_status_async, sync as get_operation_status_sync
from .api.operations.get_operation_result import asyncio_detailed as get_operation_result_async, sync_detailed as get_operation_result_sync
from .api.operations.create_generative_task import asyncio as create_generative_task_async, sync as create_generative_task_sync
from .api.template import delete_template, fill, list_templates, metadata
from .client import AuthenticatedClient
from .models import UploadCommand, UploadDocumentBody, OcrType, LlmType, OcrCommand
from .models.template_fill_request import TemplateFillRequest
from .models.generative_task_request import GenerativeTaskRequest

# New imports for concrete parameters:
from .models.upload_files_body import UploadFilesBody
from .types import File, Unset

import asyncio
import time
from typing import Optional
from types import SimpleNamespace


class DocuDevsClient:
    def __init__(self, api_url: str = "https://api.docudevs.ai", token: Optional[str] = None):
        # Create the openapi-python-client AuthenticatedClient
        if token is None:
            raise ValueError("token is required")
        self._client = AuthenticatedClient(base_url=api_url, token=token)

    async def list_configurations(self):
        """List all named configurations."""
        return await list_configurations.asyncio_detailed(client=self._client)

    async def get_configuration(self, name: str):
        """Get a named configuration."""
        return await get_configuration.asyncio_detailed(client=self._client, name=name)

    async def save_configuration(self, name: str, body: UploadCommand):
        """Save a named configuration."""
        return await save_configuration.asyncio_detailed(client=self._client, name=name, body=body)

    async def delete_configuration(self, name: str):
        """Delete a named configuration."""
        return await delete_configuration.asyncio_detailed(client=self._client, name=name)

    async def upload_files(self, body: UploadFilesBody):
        """Upload multiple files."""
        return await upload_files_async(client=self._client, body=body)

    async def upload_document(self, body: UploadDocumentBody):
        """Upload a single document."""
        return await upload_document_async(client=self._client, body=body)

    async def list_templates(self):
        """List document templates."""
        return await list_templates.asyncio_detailed(client=self._client)

    async def metadata(self, template_id: str):
        """Get metadata for a template."""
        return await metadata.asyncio_detailed(client=self._client, name=template_id)

    async def delete_template(self, template_id: str):
        """Delete template by ID."""
        return await delete_template.asyncio_detailed(client=self._client, name=template_id)

    async def ocr_document(self, guid: str, body: OcrCommand, ocr_format: str | None = None):
        """Process document with OCR-only mode."""
        return await ocr_document_async(client=self._client, guid=guid, body=body, format_=ocr_format)

    async def process_document(self, guid: str, body: UploadCommand):
        """Process a document."""
        return await process_document_async(client=self._client, guid=guid, body=body)

    async def process_document_with_configuration(self, guid: str, configuration: str | Unset = Unset):
        """Process a document."""
        return await process_document_with_configuration_async(client=self._client, guid=guid, configuration_name=configuration)

    async def result(self, uuid: str):
        """Get job result."""
        return await result.asyncio_detailed(client=self._client, uuid=uuid)

    async def status(self, guid: str):
        """Get job status."""
        return await status.asyncio_detailed(client=self._client, guid=guid)

    async def fill(self, name: str, body: TemplateFillRequest):
        """Fill a template."""
        return await fill.asyncio_detailed(client=self._client, name=name, body=body)

    # Cases management methods
    async def create_case(self, body):
        """Create a new case."""
        return await create_case_async(client=self._client, body=body)

    async def list_cases(self):
        """List all cases."""
        return await list_cases_async(client=self._client)

    async def get_case(self, case_id: str):
        """Get a specific case."""
        return await get_case_async(client=self._client, case_id=case_id)

    async def upload_case_document(self, case_id: str, body):
        """Upload a document to a case."""
        return await upload_case_document_async(client=self._client, case_id=case_id, body=body)

    async def submit_operation(self, job_guid: str, operation_type: str):
        """Submit an operation for a completed job."""
        from .models.submit_operation_request import SubmitOperationRequest
        
        body = SubmitOperationRequest(job_guid=job_guid, type_=operation_type)
        return await submit_operation_async(client=self._client, body=body)

    async def submit_operation_with_parameters(self, job_guid: str, operation_type: str, llm_type: Optional[str] = None, custom_parameters: Optional[dict] = None):
        """Submit an operation for a completed job with parameters.
        
        Args:
            job_guid: The job GUID to submit operation for
            operation_type: The type of operation to submit (e.g., "error-analysis")
            llm_type: Optional LLM type to use ("DEFAULT", "MINI", "PREMIUM")
            custom_parameters: Optional dict of custom parameters
            
        Returns:
            The operation submission response
        """
        from .models.submit_operation_request import SubmitOperationRequest
        from .models.operation_parameters import OperationParameters
        from .models.operation_parameters_custom_parameters_type_1 import OperationParametersCustomParametersType1
        from .types import UNSET
        
        # Build parameters if any are provided
        parameters = UNSET
        if llm_type is not None or custom_parameters is not None:
            # Convert custom_parameters dict to the expected model
            custom_params_model = UNSET
            if custom_parameters:
                custom_params_model = OperationParametersCustomParametersType1()
                for key, value in custom_parameters.items():
                    custom_params_model[key] = str(value)  # Ensure values are strings
            
            # Cast llm_type to proper type if provided
            llm_type_value = UNSET
            if llm_type:
                from .models.llm_type import check_llm_type
                llm_type_value = check_llm_type(llm_type)
            
            parameters = OperationParameters(
                llm_type=llm_type_value,
                custom_parameters=custom_params_model
            )
        
        body = SubmitOperationRequest(job_guid=job_guid, type_=operation_type, parameters=parameters)
        return await submit_operation_async(client=self._client, body=body)

    async def get_operation_status(self, job_guid: str):
        """Get status of all operations for a job."""
        return await get_operation_status_async(client=self._client, job_guid=job_guid)

    async def get_operation_result(self, job_guid: str, operation_type: str):
        """Get result of a specific operation."""
        response = await get_operation_result_async(client=self._client, job_guid=job_guid, operation_type=operation_type)
        if response.status_code == HTTPStatus.OK:
            # Parse JSON response manually since the generated parser doesn't handle it
            import json
            response_data = json.loads(response.content.decode('utf-8'))
            return SimpleNamespace(**response_data)
        return response

    async def submit_and_wait_for_operation(self, job_guid: str, operation_type: str, timeout: int = 120, poll_interval: float = 2.0):
        """Submit an operation and wait for result.
        
        Args:
            job_guid: The job GUID to submit operation for
            operation_type: The type of operation to submit (e.g., "error-analysis")
            timeout: Maximum time to wait in seconds (default: 120)
            poll_interval: Time between status checks in seconds (default: 2.0)
            
        Returns:
            The operation result once complete
            
        Raises:
            TimeoutError: If the operation doesn't complete within the timeout
            Exception: If the operation fails or errors occur
        """
        # Submit the operation
        submit_response = await self.submit_operation(job_guid=job_guid, operation_type=operation_type)
        if not submit_response:
            raise Exception(f"Error submitting {operation_type} operation: No response received")
        
        # Get the operation job GUID from the response  
        operation_job_guid = submit_response.job_guid
        
        if not operation_job_guid:
            raise Exception(f"No operation job GUID returned from submit {operation_type} operation")
        
        # Wait for the operation to complete using operation status polling
        import asyncio
        import time
        start_time = time.time()
        operation_completed = False
        
        while time.time() - start_time < timeout:
            status_response = await self.get_operation_status(job_guid=job_guid)
            if status_response and hasattr(status_response, 'operations'):
                target_ops = [op for op in status_response.operations if op.operation_type == operation_type]
                
                if target_ops and target_ops[0].status == "COMPLETED":
                    operation_completed = True
                    break
                elif target_ops and target_ops[0].status == "ERROR":
                    raise Exception(f"Operation failed with error: {target_ops[0].error}")
            
            await asyncio.sleep(poll_interval)
        
        if not operation_completed:
            raise TimeoutError(f"Operation {operation_type} did not complete within {timeout} seconds")
        
        # Get the result
        result_response = await self.get_operation_result(job_guid=job_guid, operation_type=operation_type)
        # The get_operation_result method returns either a SimpleNamespace (success) or Response (failure)
        # If it's a SimpleNamespace, it's already parsed; if it's a Response, check status code
        if hasattr(result_response, 'status_code'):
            if result_response.status_code != HTTPStatus.OK:
                content_str = result_response.content.decode('utf-8', errors='replace')
                raise Exception(f"Error getting operation result: {content_str}")
            # Parse the response manually
            import json
            response_data = json.loads(result_response.content.decode('utf-8'))
            return SimpleNamespace(**response_data)
        else:
            # Already parsed as SimpleNamespace
            return result_response

    async def submit_and_wait_for_error_analysis(self, job_guid: str, timeout: int = 120, poll_interval: float = 2.0):
        """Submit error analysis operation and wait for result.
        
        Args:
            job_guid: The job GUID to analyze errors for
            timeout: Maximum time to wait in seconds (default: 120)
            poll_interval: Time between status checks in seconds (default: 2.0)
            
        Returns:
            The error analysis result once complete
            
        Raises:
            TimeoutError: If the operation doesn't complete within the timeout
            Exception: If the operation fails or errors occur
        """
        return await self.submit_and_wait_for_operation(job_guid=job_guid, operation_type="error-analysis", timeout=timeout, poll_interval=poll_interval)

    async def create_generative_task(self, parent_job_id: str, prompt: str, model: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None):
        """Create a generative task for a completed job.
        
        Args:
            parent_job_id: The parent job GUID to create generative task for
            prompt: The prompt to send to the AI model
            model: Optional model to use
            temperature: Optional temperature parameter (0.0 to 1.0)
            max_tokens: Optional maximum tokens to generate
            
        Returns:
            The generative task creation response
        """
        from .types import UNSET
        
        body = GenerativeTaskRequest(
            prompt=prompt,
            model=model if model is not None else UNSET,
            temperature=temperature if temperature is not None else UNSET,
            max_tokens=max_tokens if max_tokens is not None else UNSET
        )
        return await create_generative_task_async(client=self._client, parent_job_id=parent_job_id, body=body)

    async def submit_and_wait_for_generative_task(self, parent_job_id: str, prompt: str, model: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None, timeout: int = 120, poll_interval: float = 2.0):
        """Create a generative task and wait for result.
        
        Args:
            parent_job_id: The parent job GUID to create generative task for
            prompt: The prompt to send to the AI model
            model: Optional model to use
            temperature: Optional temperature parameter (0.0 to 1.0)
            max_tokens: Optional maximum tokens to generate
            timeout: Maximum time to wait in seconds (default: 120)
            poll_interval: Time between status checks in seconds (default: 2.0)
            
        Returns:
            The generative task result once complete
            
        Raises:
            TimeoutError: If the operation doesn't complete within the timeout
            Exception: If the operation fails or errors occur
        """
        # Create the generative task
        response = await self.create_generative_task(
            parent_job_id=parent_job_id,
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if not response:
            raise Exception("Error creating generative task: No response received")
        
        # Get the generative task job GUID from the response  
        task_job_guid = response.job_guid
        
        if not task_job_guid:
            raise Exception("No job GUID returned from create generative task")
        
        # Wait for the generative task to complete using operation status polling
        start_time = time.time()
        task_completed = False
        
        while time.time() - start_time < timeout:
            status_response = await self.get_operation_status(job_guid=parent_job_id)
            if status_response and hasattr(status_response, 'operations'):
                generative_ops = [op for op in status_response.operations if op.operation_type == "generative-task"]
                
                if generative_ops and generative_ops[0].status == "COMPLETED":
                    task_completed = True
                    break
                elif generative_ops and generative_ops[0].status == "ERROR":
                    raise Exception(f"Generative task failed with error: {generative_ops[0].error}")
            
            await asyncio.sleep(poll_interval)
        
        if not task_completed:
            raise TimeoutError(f"Generative task did not complete within {timeout} seconds")
        
        # Get the result
        result_response = await self.get_operation_result(job_guid=parent_job_id, operation_type="generative-task")
        # The get_operation_result method returns either a SimpleNamespace (success) or Response (failure)
        # If it's a SimpleNamespace, it's already parsed; if it's a Response, check status code
        if hasattr(result_response, 'status_code'):
            if result_response.status_code != HTTPStatus.OK:
                content_str = result_response.content.decode('utf-8', errors='replace')
                raise Exception(f"Error getting generative task result: {content_str}")
            # Parse the response manually
            import json
            response_data = json.loads(result_response.content.decode('utf-8'))
            return SimpleNamespace(**response_data)
        else:
            # Already parsed as SimpleNamespace
            return result_response

    async def submit_and_wait_for_operation_with_parameters(self, job_guid: str, operation_type: str, llm_type: Optional[str] = None, custom_parameters: Optional[dict] = None, timeout: int = 120, poll_interval: float = 2.0):
        """Submit an operation with parameters and wait for result.
        
        Args:
            job_guid: The job GUID to submit operation for
            operation_type: The type of operation to submit (e.g., "error-analysis")
            llm_type: Optional LLM type to use ("DEFAULT", "MINI", "PREMIUM")
            custom_parameters: Optional dict of custom parameters
            timeout: Maximum time to wait in seconds (default: 120)
            poll_interval: Time between status checks in seconds (default: 2.0)
            
        Returns:
            The operation result once complete
            
        Raises:
            TimeoutError: If the operation doesn't complete within the timeout
            Exception: If the operation fails or errors occur
        """
        # Submit the operation with parameters
        submit_response = await self.submit_operation_with_parameters(
            job_guid=job_guid, 
            operation_type=operation_type, 
            llm_type=llm_type, 
            custom_parameters=custom_parameters
        )
        if not submit_response:
            raise Exception(f"Error submitting {operation_type} operation: No response received")
        
        # Get the operation job GUID from the response  
        operation_job_guid = submit_response.job_guid
        
        if not operation_job_guid:
            raise Exception(f"No operation job GUID returned from submit {operation_type} operation")
        
        # Wait for the operation to complete using operation status polling
        start_time = time.time()
        operation_completed = False
        
        while time.time() - start_time < timeout:
            status_response = await self.get_operation_status(job_guid=job_guid)
            if status_response and hasattr(status_response, 'operations'):
                target_ops = [op for op in status_response.operations if op.operation_type == operation_type]
                
                if target_ops and target_ops[0].status == "COMPLETED":
                    operation_completed = True
                    break
                elif target_ops and target_ops[0].status == "ERROR":
                    raise Exception(f"Operation failed with error: {target_ops[0].error}")
            
            await asyncio.sleep(poll_interval)
        
        if not operation_completed:
            raise TimeoutError(f"Operation {operation_type} did not complete within {timeout} seconds")
        
        # Get the result
        result_response = await self.get_operation_result(job_guid=job_guid, operation_type=operation_type)
        # The get_operation_result method returns either a SimpleNamespace (success) or Response (failure)
        # If it's a SimpleNamespace, it's already parsed; if it's a Response, check status code
        if hasattr(result_response, 'status_code'):
            if result_response.status_code != HTTPStatus.OK:
                content_str = result_response.content.decode('utf-8', errors='replace')
                raise Exception(f"Error getting operation result: {content_str}")
            # Parse the response manually
            import json
            response_data = json.loads(result_response.content.decode('utf-8'))
            return SimpleNamespace(**response_data)
        else:
            # Already parsed as SimpleNamespace
            return result_response

    async def submit_and_process_document(
        self,
        document: BytesIO,
        document_mime_type: str,
        prompt: str = "",
        schema: str = "",
        ocr: str = None,
        barcodes: bool = None,
        llm: str = None,
        extraction_mode=None,
        describe_figures: bool | None = None,
    ) -> str:
        # Check mimetype
        if not document_mime_type:
            raise ValueError("document_mime_type is required")
        if not document:
            raise ValueError("document is required")

        document_file = File(payload=document, file_name="omitted", mime_type=document_mime_type)
        # Create the upload document body
        upload_body = UploadDocumentBody(document=document_file)

        # Upload the document
        upload_response = await self.upload_document(body=upload_body)
        if upload_response.status_code != HTTPStatus.OK:
            # Decode bytes to string to avoid escaped byte representation
            content_str = upload_response.content.decode('utf-8', errors='replace')
            raise Exception(f"Error uploading document: {content_str}")
        # Process the uploaded document
        guid = upload_response.parsed.guid


        process_body = UploadCommand(
            prompt=prompt,
            schema=schema,
            mime_type=document_mime_type,
            ocr=ocr,
            barcodes=barcodes,
            llm=llm,
            extraction_mode=extraction_mode,
            describe_figures=describe_figures if describe_figures is not None else Unset(),
        )
        process_resp = await self.process_document(guid=guid, body=process_body)
        if process_resp.status_code != HTTPStatus.OK:
            # Decode bytes and use process_resp for error content
            content_str = process_resp.content.decode('utf-8', errors='replace')
            raise Exception(f"Error processing document: {content_str}")
        return upload_response.parsed.guid


    async def submit_and_process_document_with_configuration(
        self,
        document: BytesIO,
        document_mime_type: str,
        configuration_name: str,
    ) -> str:
        """Upload a document and process it using a named configuration."""
        # Check mimetype
        if not document_mime_type:
            raise ValueError("document_mime_type is required")
        if not document:
            raise ValueError("document is required")

        document_file = File(payload=document, file_name="omitted", mime_type=document_mime_type)
        # Create the upload document body
        upload_body = UploadDocumentBody(document=document_file)

        # Upload the document
        upload_response = await self.upload_document(body=upload_body)
        if upload_response.status_code != HTTPStatus.OK:
            content_str = upload_response.content.decode('utf-8', errors='replace')
            raise Exception(f"Error uploading document: {content_str}")

        # Process the uploaded document with the specified configuration
        guid = upload_response.parsed.guid
        process_resp = await self.process_document_with_configuration(guid=guid, configuration=configuration_name)
        if process_resp.status_code != HTTPStatus.OK:
            content_str = process_resp.content.decode('utf-8', errors='replace')
            raise Exception(f"Error processing document: {content_str}")
        return guid

    async def submit_and_ocr_document(
        self,
        document: BytesIO,
        document_mime_type: str,
        ocr: OcrType = "DEFAULT",
        ocr_format: str = "markdown",
        describe_figures: bool | None = None,
    ) -> str:
        """Upload a document and process it with OCR-only mode."""
        # Check mimetype
        if not document_mime_type:
            raise ValueError("document_mime_type is required")
        if not document:
            raise ValueError("document is required")
        
        # Check for unsupported combination
        if describe_figures is True and ocr_format == "plain":
            raise ValueError("describe_figures=True is not supported with ocr_format='plain'")

        document_file = File(payload=document, file_name="omitted", mime_type=document_mime_type)
        # Create the upload document body
        upload_body = UploadDocumentBody(document=document_file)

        # Upload the document
        upload_response = await self.upload_document(body=upload_body)
        if upload_response.status_code != HTTPStatus.OK:
            content_str = upload_response.content.decode('utf-8', errors='replace')
            raise Exception(f"Error uploading document: {content_str}")

        # Process with OCR
        guid = upload_response.parsed.guid
        ocr_body = OcrCommand(
            ocr=ocr, 
            ocr_format=ocr_format, 
            mime_type=document_mime_type,
            describe_figures=describe_figures if describe_figures is not None else Unset()
        )
        ocr_resp = await self.ocr_document(guid=guid, body=ocr_body, ocr_format=ocr_format)
        if ocr_resp.status_code != HTTPStatus.OK:
            content_str = ocr_resp.content.decode('utf-8', errors='replace')
            raise Exception(f"Error processing document with OCR: {content_str}")
        return guid

    async def wait_until_ready(self, guid: str, timeout: int = 60, poll_interval: float = 1.0):
        """Wait for a job to complete (by polling status) and then return the result.

        Args:
            guid: The job GUID to wait for
            timeout: Maximum time to wait in seconds (default: 60)
            poll_interval: Time between status checks in seconds (default: 1.0)

        Returns:
            The job result once complete

        Raises:
            TimeoutError: If the job doesn't complete within the timeout
            Exception: If the job fails or errors occur
        """
        start_time = time.time()

        while True:
            # Check if we've exceeded the timeout
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Job {guid} did not complete within {timeout} seconds")

            # Poll status endpoint to know if job finished
            status_response = await self.status(guid=guid)
            if status_response.status_code == HTTPStatus.OK:
                job = status_response.parsed
                if job is not None:
                    job_status = getattr(job, "status", None)
                    if job_status == "COMPLETED":
                        break
                    if job_status == "ERROR":
                        job_error = getattr(job, "error", None)
                        raise Exception(f"Job {guid} failed: {job_error}")
                # Not completed yet, continue polling
            elif status_response.status_code != HTTPStatus.NOT_FOUND:
                content_str = status_response.content.decode("utf-8", errors="replace")
                raise Exception(
                    f"Error getting status: {content_str} (status code: {status_response.status_code})"
                )

            await asyncio.sleep(poll_interval)

        # When completed, fetch the result once
        result_response = await self.result(uuid=guid)
        if result_response.status_code == HTTPStatus.OK:
            parsed = result_response.parsed
            if parsed is not None:
                return parsed
            # Fallback for plain-text / OCR responses
            text = result_response.content.decode("utf-8", errors="replace")
            try:
                import json
                json_parsed = json.loads(text)
                return SimpleNamespace(result=text, parsed=json_parsed)
            except Exception:
                return SimpleNamespace(result=text)

        content_str = result_response.content.decode('utf-8', errors='replace')
        raise Exception(
            f"Error getting result after completion: {content_str} (status code: {result_response.status_code})"
        )


# Convenience facade: synchronous client wrapping sync_detailed and blocking calls


__all__ = [
    "DocuDevsClient",
    "UploadDocumentBody",
    "UploadCommand",
    "File",
    "UploadFilesBody",
    "TemplateFillRequest",
    "GenerativeTaskRequest",
    # ... add other models if needed ...
]
