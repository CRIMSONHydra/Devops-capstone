# Ecommerce Admin

A small admin console for an online store. You add products and categories, keep track of customers, take orders, and watch sales on a dashboard. Cancel an order and the stock goes back on the shelf.

**How it fits together:** a React page talks to a FastAPI backend, which stores everything in Postgres (SQLite when developing). Run it with `docker compose up --build` and open http://localhost:3000.

**What happens when I push to `main`:**
1. Tests run and the frontend gets built.
2. Both Docker images are built and scanned with Trivy. Any HIGH or CRITICAL finding stops the pipeline.
3. If they're clean, the images go to GHCR, tagged with the commit SHA.
4. I then roll that tag out to Kubernetes with one `helm upgrade` (still a manual step), and Prometheus and Grafana keep an eye on the backend.

Terraform can also spin up the EKS cluster this runs on.

The slide deck is [Ecommerce-Admin-DevOps-Capstone.pptx](Ecommerce-Admin-DevOps-Capstone.pptx). 

Video is at [GDrive video](https://drive.google.com/drive/folders/1flqlCrmTKX2ilzgVaOVgTFfSM67XPGUn?usp=drive_link)

Screenshots for the assignment live in [assignment/ASSIGNMENT.md](assignment/ASSIGNMENT.md). 

Setup commands and the API list are in [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).
