Mapping a custom domain to Render services

Prerequisites

- You control the DNS for your domain (example: example.com) via a DNS provider (Cloudflare, GoDaddy, Namecheap, Route53, etc.).

Frontend (static) service - recommended for custom domain

1. In Render dashboard, open `sam-portfolio-frontend` → Settings → Custom Domains → Add Custom Domain.
2. Add the domain or subdomain (e.g., portfolio.example.com or www.example.com).
3. Render will show the DNS record(s) to add. Typically:
   - For subdomain (www or portfolio): add a CNAME record
     - Host: `www` or `portfolio`
     - Value: `sam-portfolio-frontend.onrender.com` (Render will show exact target)
   - For apex/root domain (example.com): use your DNS provider’s ALIAS/ANAME to point to Render, or follow Render docs to use A records if offered.
4. After adding DNS records, wait for propagation and Render will provision TLS automatically.

Backend (API) service

- If you want a custom domain for API (optional): add custom domain to `sam-portfolio-api` and map a subdomain (e.g., api.example.com) via CNAME to `sam-portfolio-api.onrender.com`.
- Ensure `ALLOWED_ORIGINS` in Render env includes your frontend domain (e.g., https://portfolio.example.com).

DNS tips per provider

- Cloudflare: use CNAME for subdomains. If using Cloudflare proxy, keep proxy enabled only if you want Cloudflare features; otherwise set to DNS-only for easier TLS provisioning by Render.
- AWS Route53: create an Alias (ALIAS) record pointing to Render's target as instructed.

Verify

- After propagation, visit your frontend domain in a browser and check TLS is active.
- Test API requests using the domain and verify CORS and endpoints.

If you share your domain and DNS provider name, I can provide exact DNS records and a step-by-step guide for your provider.
