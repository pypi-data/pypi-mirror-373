---
# Global deck settings
theme: default
title: Your Presentation Title
info: |
  Professional presentation template with dark theme
  20 slides with modern components
class: text-left
mdc: true
transition: slide-left
fonts:
  sans: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial
  mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace
css: |
  @import "./style.css";
---

# PROJECT TITLE
<div class="title-slide with-hero-glow">
  <div class="hero-copy">
    <h2 class="text-hero">Transform Your Business with Innovation</h2>
    <p class="subtitle text-md">A comprehensive solution for modern enterprises</p>
    <div class="subtitle text-xs">Presenter Name • Date • contact@example.com</div>
    <div class="hero-ctas mt-2">
      <button class="btn-primary">Get Started</button>
      <button class="btn-secondary">Learn More</button>
    </div>
  </div>
</div>

---

# The Challenge

<div class="problem-grid">
  <div class="problem-card">
    <div class="eyebrow">Current State</div>
    <h3 class="feature-title">Market Inefficiencies</h3>
    <ul class="points-clean">
      <li>Complex processes and workflows</li>
      <li>Disconnected systems and data silos</li>
      <li>High operational costs</li>
    </ul>
  </div>

  <div class="problem-card">
    <div class="eyebrow">Industry Trends</div>
    <h3 class="feature-title">Rapid Digital Evolution</h3>
    <ul class="points-clean">
      <li>Accelerating technology adoption</li>
      <li>Changing customer expectations</li>
      <li>New competitive pressures</li>
    </ul>
  </div>

  <div class="problem-card">
    <div class="eyebrow">Gap Analysis</div>
    <h3 class="feature-title">Missing Capabilities</h3>
    <ul class="points-clean">
      <li>Limited automation tools</li>
      <li>Insufficient analytics</li>
      <li>Poor integration options</li>
      <li>Lack of scalability</li>
    </ul>
  </div>
</div>

---

# Our Solution

A comprehensive platform that addresses key business challenges

<div class="stats-band mt-2">
  <div class="stat-card">
    <div class="stat-number">10x</div>
    <div class="stat-label">Faster Processing</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">50%</div>
    <div class="stat-label">Cost Reduction</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">99.9%</div>
    <div class="stat-label">Uptime</div>
  </div>
</div>

<div class="card-grid three mt-2">
  <div class="feature-card">
    <div class="eyebrow">Core</div>
    <h3 class="feature-title">Intelligent Automation</h3>
    <p class="muted">Streamline workflows with AI-powered processes</p>
  </div>

  <div class="feature-card">
    <div class="eyebrow">Integration</div>
    <h3 class="feature-title">Seamless Connectivity</h3>
    <p class="muted">Connect all your tools and systems effortlessly</p>
  </div>

  <div class="feature-card">
    <div class="eyebrow">Analytics</div>
    <h3 class="feature-title">Real-time Insights</h3>
    <p class="muted">Make data-driven decisions with powerful analytics</p>
  </div>
</div>

---

# Key Features

<div class="split-cols mt-2">
  <div class="left">
    <div class="feature-card">
      <h3 class="feature-title">Smart Dashboard</h3>
      <p class="muted">Centralized control and monitoring</p>
    </div>
    <div class="feature-card">
      <h3 class="feature-title">Advanced Analytics</h3>
      <p class="muted">Deep insights and predictive modeling</p>
    </div>
    <div class="feature-card">
      <h3 class="feature-title">Workflow Automation</h3>
      <p class="muted">Streamline repetitive tasks</p>
    </div>
  </div>
  <div class="right">
    <div class="glass-frame tall">
      <div class="placeholder">Product Screenshot / Dashboard UI</div>
    </div>
  </div>
</div>

---

# Architecture Overview

```mermaid
%%{init: {
  "theme": "dark",
  "themeVariables": {
    "primaryTextColor": "#E6EDF3",
    "primaryColor": "#0B1220",
    "lineColor": "#6E7681"
  }
}}%%

flowchart TD
    UI[🖥️ User Interface] --> API[⚙️ API Gateway]
    API --> Auth[🔐 Authentication]
    API --> Core[💼 Core Services]
    Core --> DB[(📊 Database)]
    Core --> Cache[(⚡ Cache)]
    Core --> Queue[📬 Message Queue]
    Queue --> Workers[🤖 Background Workers]
    
    style UI fill:#1C1A2B,stroke:#6B7FEB
    style API fill:#1C1A2B,stroke:#6B7FEB
    style Core fill:#1C1A2B,stroke:#6B7FEB
    style DB fill:#2B2931,stroke:#40D79E
    style Cache fill:#2B2931,stroke:#FFC75A
```

---

# Use Cases

<div class="card-grid three mt-2">
  <div class="feature-card"><h3 class="feature-title">Enterprise Resource Planning</h3><p class="muted">Unified business management</p></div>
  <div class="feature-card"><h3 class="feature-title">Customer Relationship Management</h3><p class="muted">360-degree customer view</p></div>
  <div class="feature-card"><h3 class="feature-title">Supply Chain Optimization</h3><p class="muted">End-to-end visibility</p></div>
  <div class="feature-card"><h3 class="feature-title">Financial Analytics</h3><p class="muted">Real-time financial insights</p></div>
  <div class="feature-card"><h3 class="feature-title">HR Management</h3><p class="muted">Streamlined HR processes</p></div>
  <div class="feature-card"><h3 class="feature-title">Project Management</h3><p class="muted">Collaborative project tracking</p></div>
</div>

---

# Market Opportunity

<div class="split-cols mt-2">
  <div class="left">
    <div class="feature-card">
      <div class="eyebrow">TAM</div>
      <h3 class="feature-title">Total Addressable Market</h3>
      <p class="muted">$100B+ globally</p>
    </div>
    <div class="feature-card">
      <div class="eyebrow">Growth</div>
      <h3 class="feature-title">Market Expansion</h3>
      <p class="muted">25% CAGR expected</p>
    </div>
    <div class="feature-card">
      <div class="eyebrow">Segments</div>
      <ul class="points-clean">
        <li>Enterprise (500+ employees)</li>
        <li>Mid-market (50-500)</li>
        <li>SMB (under 50)</li>
      </ul>
    </div>
  </div>
  <div class="right">
    <div class="glass-frame">
      <div class="placeholder">Market Size Chart</div>
    </div>
  </div>
</div>

---

# Competitive Landscape

<div class="glass-frame wide mt-2">
  <div class="placeholder">Competitive Positioning Matrix</div>
</div>

<div class="card-grid three mt-2">
  <div class="feature-card">
    <h3 class="feature-title">Our Advantages</h3>
    <ul class="points-clean">
      <li>Superior technology</li>
      <li>Better user experience</li>
      <li>Competitive pricing</li>
    </ul>
  </div>
  <div class="feature-card">
    <h3 class="feature-title">Market Position</h3>
    <ul class="points-clean">
      <li>Leader in innovation</li>
      <li>Strong brand recognition</li>
      <li>Growing market share</li>
    </ul>
  </div>
  <div class="feature-card">
    <h3 class="feature-title">Differentiators</h3>
    <ul class="points-clean">
      <li>AI-powered features</li>
      <li>Seamless integrations</li>
      <li>Enterprise-grade security</li>
    </ul>
  </div>
</div>

---

# Implementation Timeline

<div class="timeline mt-2">
  <div class="time-node">
    <div class="time-dot"></div>
    <div class="time-card">
      <div class="eyebrow">Phase 1: Q1 2025</div>
      <h4>Foundation</h4>
      <ul class="points-clean">
        <li>System architecture design</li>
        <li>Core infrastructure setup</li>
        <li>Initial team formation</li>
      </ul>
    </div>
  </div>
  <div class="time-node">
    <div class="time-dot"></div>
    <div class="time-card">
      <div class="eyebrow">Phase 2: Q2 2025</div>
      <h4>Development</h4>
      <ul class="points-clean">
        <li>MVP development</li>
        <li>Beta testing program</li>
        <li>Initial customer feedback</li>
      </ul>
    </div>
  </div>
  <div class="time-node">
    <div class="time-dot future"></div>
    <div class="time-card">
      <div class="eyebrow">Phase 3: Q3 2025</div>
      <h4>Launch</h4>
      <ul class="points-clean">
        <li>Public release</li>
        <li>Marketing campaign</li>
        <li>Customer onboarding</li>
      </ul>
    </div>
  </div>
</div>

---

# Success Metrics

<div class="stats-grid mt-2">
  <div class="stat-card">
    <div class="stat-number">1M+</div>
    <div class="stat-label">Active Users</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">$50M</div>
    <div class="stat-label">ARR</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">95%</div>
    <div class="stat-label">Retention Rate</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">150</div>
    <div class="stat-label">Enterprise Clients</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">4.8</div>
    <div class="stat-label">Customer Rating</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">24/7</div>
    <div class="stat-label">Support</div>
  </div>
</div>

---

# Case Study

<div class="split-cols mt-2">
  <div class="left">
    <div class="feature-card">
      <div class="eyebrow">Client</div>
      <h3 class="feature-title">Fortune 500 Company</h3>
      <ul class="points-clean">
        <li>10,000+ employees</li>
        <li>Global operations</li>
        <li>Complex IT infrastructure</li>
      </ul>
    </div>
    <div class="feature-card">
      <div class="eyebrow">Challenge</div>
      <ul class="points-clean">
        <li>Fragmented systems</li>
        <li>Manual processes</li>
        <li>Limited visibility</li>
      </ul>
    </div>
  </div>
  <div class="right">
    <div class="feature-card glass">
      <div class="eyebrow">Results</div>
      <h3 class="feature-title">Transformation Achieved</h3>
      <ul class="points-clean">
        <li>60% efficiency improvement</li>
        <li>$5M annual savings</li>
        <li>Real-time insights</li>
      </ul>
    </div>
    <div class="glass-frame short">
      <div class="placeholder">ROI Chart</div>
    </div>
  </div>
</div>

---

# Pricing & Plans

<div class="card-grid three mt-2">
  <div class="feature-card">
    <div class="eyebrow">Starter</div>
    <h3 class="feature-title">$99/month</h3>
    <ul class="points-clean">
      <li>Up to 10 users</li>
      <li>Basic features</li>
      <li>Email support</li>
      <li>5GB storage</li>
    </ul>
    <button class="btn-secondary mt-2">Choose Plan</button>
  </div>
  <div class="feature-card">
    <div class="pill">Popular</div>
    <h3 class="feature-title">$299/month</h3>
    <ul class="points-clean">
      <li>Up to 50 users</li>
      <li>Advanced features</li>
      <li>Priority support</li>
      <li>100GB storage</li>
      <li>API access</li>
    </ul>
    <button class="btn-primary mt-2">Choose Plan</button>
  </div>
  <div class="feature-card">
    <div class="eyebrow">Enterprise</div>
    <h3 class="feature-title">Custom</h3>
    <ul class="points-clean">
      <li>Unlimited users</li>
      <li>All features</li>
      <li>Dedicated support</li>
      <li>Unlimited storage</li>
      <li>Custom integrations</li>
    </ul>
    <button class="btn-secondary mt-2">Contact Sales</button>
  </div>
</div>

---

# Technology Stack

<div class="feature-grid mt-2">
  <div class="feature-card">
    <div class="eyebrow">Frontend</div>
    <ul class="points-clean">
      <li>React / Vue.js / Angular</li>
      <li>TypeScript</li>
      <li>Tailwind CSS</li>
    </ul>
  </div>
  <div class="feature-card">
    <div class="eyebrow">Backend</div>
    <ul class="points-clean">
      <li>Node.js / Python / Go</li>
      <li>GraphQL / REST APIs</li>
      <li>Microservices</li>
    </ul>
  </div>
  <div class="feature-card">
    <div class="eyebrow">Infrastructure</div>
    <ul class="points-clean">
      <li>AWS / Azure / GCP</li>
      <li>Kubernetes</li>
      <li>CI/CD pipelines</li>
    </ul>
  </div>
  <div class="feature-card">
    <div class="eyebrow">Data</div>
    <ul class="points-clean">
      <li>PostgreSQL / MongoDB</li>
      <li>Redis</li>
      <li>Elasticsearch</li>
    </ul>
  </div>
  <div class="feature-card">
    <div class="eyebrow">Security</div>
    <ul class="points-clean">
      <li>End-to-end encryption</li>
      <li>OAuth 2.0 / SAML</li>
      <li>SOC 2 compliant</li>
    </ul>
  </div>
  <div class="feature-card">
    <div class="eyebrow">Monitoring</div>
    <ul class="points-clean">
      <li>Prometheus / Grafana</li>
      <li>ELK Stack</li>
      <li>APM tools</li>
    </ul>
  </div>
</div>

---

# Team

<div class="card-grid four mt-2">
  <div class="feature-card">
    <h4 class="feature-title">CEO</h4>
    <p class="muted small">20+ years experience</p>
    <p class="muted small">Former Fortune 500 exec</p>
  </div>
  <div class="feature-card">
    <h4 class="feature-title">CTO</h4>
    <p class="muted small">15+ years in tech</p>
    <p class="muted small">Ex-FAANG engineer</p>
  </div>
  <div class="feature-card">
    <h4 class="feature-title">CPO</h4>
    <p class="muted small">Product visionary</p>
    <p class="muted small">3 successful exits</p>
  </div>
  <div class="feature-card">
    <h4 class="feature-title">CFO</h4>
    <p class="muted small">Finance expert</p>
    <p class="muted small">IPO experience</p>
  </div>
</div>

<div class="card mt-2">
  <h3>Advisory Board</h3>
  <ul class="points-clean">
    <li>Industry veterans from leading tech companies</li>
    <li>Domain experts in enterprise software</li>
    <li>Strategic advisors with deep market connections</li>
  </ul>
</div>

---

# Customer Testimonials

<div class="card-grid two mt-2">
  <div class="feature-card glass">
    <p class="muted">"This platform transformed our operations. We've seen incredible efficiency gains and cost savings."</p>
    <div class="mt-2">
      <strong>John Smith</strong><br>
      <span class="text-xs muted">CTO, Tech Corp</span>
    </div>
  </div>
  <div class="feature-card glass">
    <p class="muted">"The best investment we've made. ROI was evident within the first quarter."</p>
    <div class="mt-2">
      <strong>Jane Doe</strong><br>
      <span class="text-xs muted">CEO, Innovation Inc</span>
    </div>
  </div>
</div>

---

# Next Steps

<div class="cta-band">
  <div>
    <div class="overline">Get Started Today</div>
    <h2 class="text-hero">Ready to Transform Your Business?</h2>
    <p class="muted">Join thousands of companies already using our platform</p>
    <div class="cta-actions">
      <button class="btn-primary">Start Free Trial</button>
      <button class="btn-secondary">Schedule Demo</button>
    </div>
  </div>
  <div>
    <div class="card">
      <div class="eyebrow">Contact</div>
      <ul class="points-clean">
        <li>Sales: sales@example.com</li>
        <li>Support: support@example.com</li>
        <li>Phone: 1-800-EXAMPLE</li>
      </ul>
      <div class="muted small mt-4">www.example.com</div>
    </div>
  </div>
</div>

---

# Appendix

<div class="card-grid two mt-2">
  <div class="feature-card">
    <h3 class="feature-title">Resources</h3>
    <ul class="points-clean">
      <li>Technical documentation</li>
      <li>API reference</li>
      <li>Video tutorials</li>
      <li>Community forum</li>
    </ul>
  </div>
  <div class="feature-card">
    <h3 class="feature-title">Legal</h3>
    <ul class="points-clean">
      <li>Terms of service</li>
      <li>Privacy policy</li>
      <li>Security compliance</li>
      <li>SLA agreements</li>
    </ul>
  </div>
</div>

---
layout: center
class: text-center
---

# Thank You

Questions?

<div class="mt-4 subtle">Press S for presenter mode • Press E to open editor • Use arrow keys to navigate</div>
