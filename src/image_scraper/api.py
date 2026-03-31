from fastapi import FastAPI
from pydantic import BaseModel

from image_scraper.main import run_scraper


app = FastAPI()


class ScrapeRequest(BaseModel):
    target_url: str
    pdf_name: str
    output_dir: str = "output/images"

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.post("/scrape")
def scrape(req: ScrapeRequest):
    run_scraper(
        target_url=req.target_url,
        output_dir=req.output_dir,
        pdf_name=req.pdf_name
    )

    return {
        "status": "ok",
        "message": "Scraping completed",
        "pdf": f"{req.output_dir}/{req.pdf_name if req.pdf_name.endswith('.pdf') else req.pdf_name + '.pdf'}"
    }
