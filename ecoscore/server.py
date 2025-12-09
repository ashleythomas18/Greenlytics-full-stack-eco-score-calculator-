# from pymongo import MongoClient
# from datetime import datetime
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse, FileResponse
# import pytesseract
# from PIL import Image
# import pdf2image
# import io
# import re
# import cv2
# import numpy as np
# import spacy
# from typing import List, Optional
# import logging
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI(title="EcoScore OCR API", version="1.0.0")

# client = MongoClient("mongodb://localhost:27017/")
# db = client["ecoscore"]
# collection = db["bills"]

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ProductExtractor:
#     """Strict product name extractor"""
    
#     def __init__(self):
#         try:
#             self.nlp = spacy.load("en_core_web_sm")
#         except Exception as e:
#             logger.error(f"Failed to load spaCy model: {e}")
#             raise HTTPException(status_code=500, detail="Failed to initialize NLP model")
        
#         # Strict patterns to filter out non-products
#         self.filter_patterns = [
#             r'^[^a-zA-Z0-9]+$',  # Lines without alphanumeric characters
#             r'^\d+$',  # Pure numbers
#             r'^\d+\.\d+$',  # Decimal numbers
#             r'^\$?\d+\.?\d*$',  # Prices
#             r'^[A-Z\s]+$',  # All caps (likely headers)
#             r'^store\s*#',  # Store numbers
#             r'^thank you',  # Thank you messages
#             r'^[a-zA-Z]+\s*\d+$',  # Single word with numbers
#         ]
        
#         # Common product patterns to look for
#         self.product_patterns = [
#             r'^[A-Z][a-z]+(?:\s+[A-Za-z]+)+$',  # Properly capitalized product names
#             r'^[A-Za-z]+\s+[A-Za-z]+$',  # Two word products
#             r'^[A-Za-z]+$',  # Single word products (if long enough)
#         ]

#     def preprocess_image(self, image: Image.Image) -> Image.Image:
#         """Enhanced image preprocessing"""
#         try:
#             image_np = np.array(image)
            
#             # Convert to grayscale if needed
#             if len(image_np.shape) > 2:
#                 gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
#             else:
#                 gray = image_np
            
#             # Apply adaptive thresholding
#             thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
#                                          cv2.THRESH_BINARY, 11, 2)
            
#             # Apply slight blur to reduce noise
#             blurred = cv2.GaussianBlur(thresh, (3, 3), 0)
            
#             return Image.fromarray(blurred)
#         except Exception as e:
#             logger.error(f"Image preprocessing failed: {e}")
#             return image

#     def extract_text_from_image(self, image: Image.Image) -> str:
#         """Extract text with strict OCR configuration"""
#         try:
#             processed_image = self.preprocess_image(image)
#             custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789- "'
#             text = pytesseract.image_to_string(processed_image, config=custom_config)
#             logger.debug(f"Raw extracted text:\n{text}")
#             return text
#         except Exception as e:
#             logger.error(f"OCR extraction failed: {e}")
#             raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

#     def extract_products(self, text: str) -> List[str]:
#         """Strict product name extraction"""
#         if not text.strip():
#             return []
        
#         products = []
#         lines = [line.strip() for line in text.split('\n') if line.strip()]
        
#         for line in lines:
#             # First clean the line
#             cleaned = self._clean_product_line(line)
#             if not cleaned:
#                 continue
                
#             # Skip if matches filter patterns
#             if self._should_filter_line(cleaned):
#                 continue
                
#             # Check if it matches product patterns
#             if self._is_product_line(cleaned):
#                 products.append(cleaned)
        
#         # Remove duplicates while preserving order
#         seen = set()
#         unique_products = [p for p in products if not (p.lower() in seen or seen.add(p.lower()))]
        
#         logger.info(f"Extracted clean products: {unique_products}")
#         return unique_products

#     def _should_filter_line(self, line: str) -> bool:
#         """Check if line should be filtered out"""
#         line_lower = line.lower()
#         for pattern in self.filter_patterns:
#             if re.fullmatch(pattern, line_lower):
#                 return True
#         return False

#     def _is_product_line(self, line: str) -> bool:
#         """Check if line looks like a product name"""
#         for pattern in self.product_patterns:
#             if re.fullmatch(pattern, line):
#                 return True
#         return False

#     def _clean_product_line(self, line: str) -> str:
#         """Strict cleaning of product lines"""
#         # Remove trailing numbers/quantities
#         line = re.sub(r'[\s\-]*\d+[\.,]?\d*\s*[a-zA-Z]*\s*$', '', line)
#         line = re.sub(r'[\s\-]*\d+\s*x\s*\d+\s*$', '', line)
        
#         # Remove special characters
#         line = re.sub(r'[^a-zA-Z0-9\s\-]', '', line)
        
#         # Standardize spaces and trim
#         line = re.sub(r'\s+', ' ', line).strip()
        
#         # Only keep if it has at least 3 letters
#         if sum(c.isalpha() for c in line) < 3:
#             return ""
            
#         return line

# # Initialize the product extractor
# extractor = ProductExtractor()

# @app.get("/")
# async def root():
#     return FileResponse("index.html")

# def calculate_eco_score(product):
#     score = 0
#     if product["recyclable"]: score += 2
#     if product["reusable"]: score += 2

#     if product["carbon_footprint"] < 1.5:
#         score += 2
#     elif product["carbon_footprint"] < 3:
#         score += 1

#     if len(product["eco_certifications"]) > 0: score += 1
#     if "locally-produced" in product["sustainability_tags"]: score += 1
#     if product["user_sentiment_score"] > 0.7: score += 1

#     return min(score, 10)

# @app.post("/upload-bill")
# async def upload_bill(file: UploadFile = File(...)):
#     try:
#         if not file.content_type:
#             raise HTTPException(status_code=400, detail="File type not specified")
            
#         content = await file.read()
#         if not content:
#             raise HTTPException(status_code=400, detail="Empty file uploaded")

#         # Process file based on type
#         if file.content_type.startswith('image/'):
#             image = Image.open(io.BytesIO(content))
#             text = extractor.extract_text_from_image(image)
#         elif file.content_type == 'application/pdf':
#             try:
#                 images = pdf2image.convert_from_bytes(content)
#                 text = '\n'.join([extractor.extract_text_from_image(img) for img in images])
#             except Exception as e:
#                 logger.error(f"PDF processing failed: {e}")
#                 raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
#         else:
#             raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

#         # Extract only clean product names
#         products_raw = extractor.extract_products(text)

#         # Product database (same as before)
#         product_db = {
#             "large eggs": { ... },  # Your existing product data
#             "cottage cheese": { ... },
#             "natural yogurt": { ... },
#             "cheesy tomatoes": { ... },
#             "bananas": { ... },
#             "chocolate cookies": { ... },
#             "canned tuna": { ... },
#             "chicken breast": { ... },
#             # ... rest of your product database
#         }

#         # Process products and calculate scores
#         detailed_products = []
#         total_score = 0

#         for product in products_raw:
#             product_key = product.lower().strip()
#             matched_data = product_db.get(product_key)

#             if matched_data:
#                 score = calculate_eco_score(matched_data)
#             else:
#                 score = 0  # Default score for unknown products

#             detailed_products.append({
#                 "name": product,
#                 "eco_score": score
#             })
#             total_score += score

#         average_score = round(total_score / len(detailed_products), 2) if detailed_products else 0

#         # Save to MongoDB
#         bill_data = {
#             "filename": file.filename,
#             "products": detailed_products,
#             "total_products": len(detailed_products),
#             "average_score": average_score,
#             "timestamp": datetime.utcnow()
#         }
#         collection.insert_one(bill_data)

#         return JSONResponse(
#             content={
#                 "success": True,
#                 "filename": file.filename,
#                 "products": detailed_products,
#                 "total_products": len(detailed_products),
#                 "average_score": average_score
#             }
#         )
#     except Exception as e:
#         logger.error(f"Error processing bill: {str(e)}")
#         raise HTTPException(status_code=500, detail="An error occurred while processing the bill")

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "service": "EcoScore OCR API"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, port=8000)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import pytesseract
from PIL import Image
import pdf2image
import io
import re
import cv2
import numpy as np
import spacy
from transformers import pipeline
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EcoScore OCR API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductExtractor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"spaCy load failed: {e}")
            self.nlp = None

        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.zero_shot_labels = ["product", "price", "store info", "garbage", "date", "thank you", "invoice info"]

        self.filter_patterns = [
            r'^\d+[\.,]\d+$', r'^\$\d+[\.,]\d+$', r'^total:?', r'^subtotal:?', r'^tax:?', r'^discount:?',
            r'^qty:?', r'^\d+\s*x\s*\d+', r'^\d{1,2}/\d{1,2}/\d{2,4}', r'^\d{1,2}:\d{2}',
            r'^receipt\s*#', r'^store\s*#', r'^cashier:?', r'^thank\s*you', r'^visit\s*us', r'^www\.',
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', r'^\d{10,}$', r'^[+\-=\*]{3,}$',
            r'^[A-Za-z]+\s*[0-9]+[A-Za-z0-9\s,.-]$', r'^[A-Za-z]+\.\s[A-Za-z]+\.\s*[A-Za-z]+$',
            r'^GSTIN:', r'^net\s*amount:', r'^thanks\s*for'
        ]

        self.invoice_patterns = [
            r'(?:invoice|receipt|bill|BIT)\s*[#:]?\s*([A-Za-z0-9\-]+)',
            r'^\s*([A-Za-z0-9]{4,})\s*$',
            r'[A-Za-z0-9]{4,}\s*[-#]\s*[A-Za-z0-9]{4,}',
            r'BIT\s*No\s*:\s*(\d+)'
        ]

        self.min_product_length = 3
        self.max_product_length = 50

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        try:
            image_np = np.array(image)
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            if np.mean(gray) > 180:
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            else:
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                               cv2.THRESH_BINARY, 15, 5)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(thresh)
            denoised = cv2.fastNlMeansDenoising(enhanced)
            return Image.fromarray(denoised)
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image

    def extract_text_from_image(self, image: Image.Image) -> str:
        try:
            processed_image = self.preprocess_image(image)
            if processed_image.mode != 'RGB':
                processed_image = processed_image.convert('RGB')
            text = pytesseract.image_to_string(processed_image, config='--psm 6 --oem 3', lang='eng')
            logger.info(f"Extracted text length: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

    def extract_invoice_number(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for pattern in self.invoice_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                invoice = match.group(1)
                if len(invoice) >= 4 and re.match(r'^[A-Za-z0-9\-]+$', invoice):
                    return invoice
        return None

    def is_likely_product(self, line: str) -> bool:
        if not line or len(line.strip()) < 3:
            return False
        try:
            result = self.classifier(line, candidate_labels=self.zero_shot_labels)
            return result['labels'][0] == "product" and result['scores'][0] > 0.75
        except Exception as e:
            logger.warning(f"Zero-shot classification failed: {e}")
            return False

    def clean_and_filter_products_regex(self, text: str) -> List[str]:
        lines = text.split('\n')
        potential_products = []
        in_product_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if re.search(r'item\s*name|product|description', line.lower()):
                in_product_section = True
                continue

            if re.search(r'total|net\s*amount|thanks', line.lower()):
                break

            cleaned_line = self._clean_product_line(line)
            if (cleaned_line and
                self.min_product_length <= len(cleaned_line) <= self.max_product_length and
                self.is_likely_product(cleaned_line)):
                potential_products.append(cleaned_line)

        return potential_products

    def extract_products_nlp(self, text: str) -> List[str]:
        if not text.strip():
            return []

        products = self.clean_and_filter_products_regex(text)
        seen = set()
        return [p for p in products if not (p.lower() in seen or seen.add(p.lower()))]

    def _should_filter_line(self, line: str) -> bool:
        line_lower = line.lower().strip()
        for pattern in self.filter_patterns:
            if re.match(pattern, line_lower):
                return True
        if re.match(r'^[\d\s\.,\$\-\+\*/=]+$', line):
            return True
        return False

    def _clean_product_line(self, line: str) -> str:
        line = line.strip()
        line = re.sub(r'\s+\$?\d+[\.,]\d+\s*$', '', line)
        line = re.sub(r'^\d+\s*x\s*', '', line, flags=re.IGNORECASE)
        line = re.sub(r'\s*\d+\.?\d*\s*$', '', line)
        line = re.sub(r'[-\*\+\=\s]+$', '', line)
        line = re.sub(r'\s+', ' ', line).strip()
        return line

extractor = ProductExtractor()

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.post("/upload-bill")
async def upload_bill(file: UploadFile = File(...)):
    try:
        if not file.content_type:
            raise HTTPException(status_code=400, detail="File type not specified")
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        if file.content_type.startswith('image/'):
            image = Image.open(io.BytesIO(content))
            text = extractor.extract_text_from_image(image)
        elif file.content_type == 'application/pdf':
            images = pdf2image.convert_from_bytes(content)
            all_text = [extractor.extract_text_from_image(img) for img in images]
            text = '\n'.join(all_text)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

        products = extractor.extract_products_nlp(text)
        invoice_number = extractor.extract_invoice_number(text)

        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "products": products,
            "total_products": len(products),
            "invoice_number": invoice_number,
            "raw_text_length": len(text)
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "EcoScore OCR API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)