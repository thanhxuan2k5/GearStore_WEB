import uvicorn
import sys

if __name__ == "__main__":
    # Fix Unicode/emoji output on Windows terminals (cp1252)
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    print("=========================================================")
    print("GEARVN TECH STORE & AI/ML ECOSYSTEM IS STARTING...")
    print("Storefront:        http://127.0.0.1:8000/")
    print("Admin & ML Portal: http://127.0.0.1:8000/admin/dashboard")
    print("RAG Chatbot:       http://127.0.0.1:8000/admin/rag")
    print("API Docs:          http://127.0.0.1:8000/docs")
    print("=========================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

