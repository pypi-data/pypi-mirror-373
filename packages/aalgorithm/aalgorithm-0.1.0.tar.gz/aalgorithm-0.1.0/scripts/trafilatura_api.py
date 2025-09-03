# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "trafilatura",
#     "pydantic",
#     "loguru",
# ]
# ///
from encodings.punycode import T
import json
from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import trafilatura
from loguru import logger
import sys
import os

# Configure logger
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

app = FastAPI(
    title="Trafilatura API",
    description="API for extracting clean text content from HTML using Trafilatura",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request and response models
class ContentRequest(BaseModel):
    raw_content: str = Field(..., description="Raw HTML content to be processed")
    url: Optional[str] = Field(None, description="Optional URL source of the content")
    include_comments: bool = Field(False, description="Whether to include comments in extraction")
    include_tables: bool = Field(True, description="Whether to include tables in extraction")
    include_links: bool = Field(True, description="Whether to include links in extraction")
    include_images: bool = Field(False, description="Whether to include image descriptions")
    
class ContentResponse(BaseModel):
    text: str = Field("", description="Extracted clean text")
    metadata: Dict[str, Any] = Field({}, description="Metadata extracted from the content")
    status: str = Field("success", description="Processing status")
    success: bool = Field(True, description="Whether extraction was successful")

@app.post("/extract", response_model=ContentResponse)
async def extract_content(request: ContentRequest):
    """
    Extract clean text from raw HTML content using Trafilatura
    
    - **raw_content**: Raw HTML content to be processed
    - **url**: Optional URL source of the content
    - **include_comments**: Whether to include comments in extraction
    - **include_tables**: Whether to include tables in extraction
    - **include_links**: Whether to include links in extraction
    - **include_images**: Whether to include image descriptions
    """
    logger.info(f"Processing content extraction request")
    
    if not request.raw_content:
        raise HTTPException(status_code=400, detail="Raw content cannot be empty")
    
    try:
        # Extract text using trafilatura
        extracted_text = trafilatura.extract(
            request.raw_content,
            include_comments=request.include_comments,
            include_tables=request.include_tables,
            include_links=request.include_links,
            include_images=request.include_images,
            output_format='txt',  # 修改为 'txt' 而不是 'text'
            with_metadata=True
        )
        
        # Handle extraction failure
        if extracted_text is None:
            logger.warning("Trafilatura couldn't extract text from the provided content")
            return ContentResponse(
                text="",
                metadata={},
                status="extraction_failed",
                success=False
            )
        
        # Extract metadata if available
        if isinstance(extracted_text, tuple) and len(extracted_text) == 2:
            text, metadata = extracted_text
        else:
            text = extracted_text
            metadata = {}
        
        logger.success(f"Successfully extracted {len(text)} characters")
        
        return ContentResponse(
            text=text,
            metadata=metadata,
            status="success",
            success=True
        )
    
    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")
        return ContentResponse(
            text="",
            metadata={},
            status=f"error: {str(e)}",
            success=False
        )

@app.post("/extract_from_url")
async def extract_from_url(url: str = Body(..., embed=True)):
    """
    Extract clean text directly from a URL using Trafilatura
    
    - **url**: URL to fetch and process
    """
    logger.info(f"Processing URL extraction request: {url}")
    
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    try:
        # Download content from URL
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.warning(f"Failed to download content from URL: {url}")
            return ContentResponse(
                text="",
                metadata={},
                status="download_failed",
                success=False
            )
        
        # Extract from downloaded content
        result = trafilatura.extract(
            downloaded,
            output_format='txt',
            with_metadata=True,
            include_comments=False,
            include_tables=True,
            include_links=False,
            include_images=True,
        )
        
        # Handle extraction failure
        if result is None:
            logger.warning(f"Trafilatura couldn't extract text from URL: {url}")
            return ContentResponse(
                text="",
                metadata={},
                status="extraction_failed",
                success=False
            )
        
        # Extract metadata if available
        if isinstance(result, tuple) and len(result) == 2:
            text, metadata = result
        else:
            text = result
            metadata = {}
        
        logger.success(f"Successfully extracted {len(text)} characters from URL")
        
        return ContentResponse(
            text=text,
            metadata=metadata,
            status="success",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error during URL extraction: {str(e)}")
        return ContentResponse(
            text="",
            metadata={},
            status=f"error: {str(e)}",
            success=False
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting Trafilatura API server on port {port}")
    uvicorn.run("trafilatura_api:app", host="0.0.0.0", port=port, reload=True)