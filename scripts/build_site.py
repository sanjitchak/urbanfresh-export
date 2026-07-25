#!/usr/bin/env python3
"""Build the UrbanFresh international buyer website."""

from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://urbanfreshrice.com"
BUILD_DATE = date.today().isoformat()
LAUNCH_READY = True

PHONE_DISPLAY = "+91 94335 69217"
PHONE_LINK = "+919433569217"
WHATSAPP = "https://wa.me/919433569217?text=Hello%20UrbanFresh%2C%20I%20would%20like%20to%20send%20an%20international%20rice%20RFQ."
LINKEDIN = "https://www.linkedin.com/company/urbanfreshin"
MAP_URL = "https://local.google.com/place?placeid=ChIJEXtmKGRxDjkRqoJCBUKpPQI"


PAGES: list[dict[str, str]] = [
    {
        "slug": "",
        "nav": "Home",
        "title": "Indian Rice Mill for International Buyers | UrbanFresh",
        "description": "Source specification-led basmati rice from UrbanFresh Rice Mills in Karnal, India. Review mill capability, quality process and RFQ requirements.",
        "image": "mill-processing-plant.webp",
        "body": """
<section class="hero" style="--hero-image:url('/assets/images/ricefarm/mill-processing-plant.webp')">
  <div class="container hero-inner"><div class="hero-copy">
    <p class="eyebrow">Karnal, India · International buyer desk</p>
    <h1>Rice sourcing begins with a <span>written specification.</span></h1>
    <p class="hero-lede">UrbanFresh is a family-operated rice mill established in 1978. We help importers, distributors and merchant exporters evaluate basmati rice against product, quality, packing and destination requirements before quotation.</p>
    <div class="hero-actions"><a class="button button-gold" href="contact.html#rfq">Send an international RFQ</a><a class="button button-ghost" href="quality-residue-testing.html">Review our quality approach</a></div>
    <div class="hero-proof"><div><strong>Mill-side answers</strong><span>Product and production feasibility</span></div><div><strong>Lot-specific review</strong><span>Specification and evidence per offer</span></div><div><strong>Buyer-defined brief</strong><span>Destination, packing and shipment needs</span></div></div>
  </div></div>
</section>
<section class="section"><div class="container grid-2">
  <div class="photo-card"><img src="assets/images/ricefarm/mill-campus-office.webp" alt="UrbanFresh Rice Mills office building at the Karnal manufacturing campus" width="956" height="1280"><div class="photo-stamp"><strong>First-party mill photography</strong><br>Village Daha, Madanpur, Karnal, Haryana, India.</div></div>
  <div><p class="eyebrow" style="color:var(--leaf)">A buyer-verification website</p><h2 class="section-title">Built to answer the questions that come before price.</h2><p class="section-lede">A meaningful rice quote depends on the variety, process, crop, quantity, destination, pack and accepted quality limits. This site keeps those decisions visible instead of hiding them behind a generic product catalogue.</p>
  <ul class="check-list"><li>Mill and infrastructure evidence from our Karnal site.</li><li>Specification fields that must be agreed for every offered lot.</li><li>Residue-testing and document questions handled against the destination brief.</li><li>A structured RFQ that gives the mill enough information to review feasibility.</li></ul>
  <p><a class="button button-outline" href="about-mill-infrastructure.html">See the mill</a></p></div>
</div></section>
<section class="section surface"><div class="container"><div class="section-head"><div><p class="eyebrow" style="color:var(--leaf)">The sourcing path</p><h2 class="section-title">From buyer brief to an order-ready offer.</h2></div><p class="section-lede">Each step exists to reduce ambiguity before production, testing, packing and shipment commitments are made.</p></div>
<div class="card-grid"><article class="card"><span class="number">01</span><h3>Define the rice</h3><p>Variety, processing style, crop, grain length, moisture, broken tolerance, packing and volume.</p><a href="1121-basmati-rice.html">See a specification page</a></article><article class="card"><span class="number">02</span><h3>Match the destination</h3><p>Share destination rules, residue limits, required documents, lab expectations and labelling constraints.</p><a href="quality-residue-testing.html">Review quality questions</a></article><article class="card"><span class="number">03</span><h3>Confirm the offer</h3><p>Accept the current sample, specification, evidence, commercial terms and shipment plan in writing.</p><a href="contact.html#rfq">Start an RFQ</a></article></div>
</div></section>
<section class="section"><div class="container"><div class="section-head"><div><p class="eyebrow" style="color:var(--leaf)">Initial export range</p><h2 class="section-title">Three basmati specification starting points.</h2></div><p class="section-lede">These pages do not publish a universal specification. They show the fields that must be confirmed for the offered crop and lot.</p></div>
<div class="product-grid"><article class="product-card"><img src="assets/images/ricefarm/category-1121.webp" alt="1121 Basmati rice grains from the UrbanFresh range" width="900" height="620"><div><small>Long-grain basmati</small><h3>1121 Basmati Rice</h3><p>Raw, steam, sella and golden sella enquiries.</p><a href="1121-basmati-rice.html">Build the 1121 brief</a></div></article><article class="product-card"><img src="assets/images/ricefarm/category-1509.webp" alt="1509 Basmati rice grains from the UrbanFresh range" width="900" height="620"><div><small>Early-maturing basmati</small><h3>1509 Basmati Rice</h3><p>Compare processing and lot-specific quality fields.</p><a href="1509-basmati-rice.html">Build the 1509 brief</a></div></article><article class="product-card"><img src="assets/images/ricefarm/category-1401.webp" alt="1401 Basmati rice grains from the UrbanFresh range" width="900" height="620"><div><small>Basmati specification</small><h3>1401 Basmati Rice</h3><p>Define grain, processing, residue and packing needs.</p><a href="1401-basmati-rice.html">Build the 1401 brief</a></div></article></div>
</div></section>
<section class="section surface-dark"><div class="container grid-2"><div><p class="eyebrow">Evidence before assurance</p><h2 class="section-title">Compliance is tied to the destination and offered lot.</h2><p class="section-lede">“Export quality” is not a specification. Buyers should send the applicable residue limits and document checklist. UrbanFresh then confirms what current evidence can be supplied for the proposed order.</p><p><a class="button button-gold" href="quality-residue-testing.html">Quality and residue process</a></p></div><div class="photo-card"><img src="assets/images/ricefarm/mill-quality.webp" alt="Quality checking area at the UrbanFresh rice mill" loading="lazy" width="1000" height="760"></div></div></section>
""",
    },
    {
        "slug": "about-mill-infrastructure.html",
        "nav": "Mill",
        "title": "UrbanFresh Rice Mill & Infrastructure in Karnal",
        "description": "See the UrbanFresh rice mill in Karnal, India, including first-party plant photography and the processing stages behind export rice enquiries.",
        "image": "mill-infrastructure.webp",
        "kicker": "The mill behind the offer",
        "h1": "A family-operated rice mill in Karnal, India.",
        "lede": "UrbanFresh Rice Mills operates from Village Daha, Madanpur, Karnal. The business was established in 1978 and handles paddy preparation, rice processing, sorting and packing.",
        "body": """
<section class="section"><div class="container grid-2"><div class="photo-card"><img src="assets/images/ricefarm/mill-processing-plant.webp" alt="UrbanFresh rice processing and grain handling structures in Karnal" width="896" height="1280"></div><div><h2 class="section-title">The physical mill is part of buyer due diligence.</h2><p class="section-lede">International buyers need to know who will review the order, where the rice is processed and which production steps are handled at the mill. These first-party photographs show the site behind the UrbanFresh brand.</p><ul class="check-list"><li>Village Daha, Madanpur manufacturing address.</li><li>Family-operated rice business established in 1978.</li><li>Published mill capability of 230 metric tons per day across three production units.</li><li>Cleaning, parboiling, drying, milling, sorting, polishing and packing systems.</li></ul><div class="notice"><strong>Order-specific confirmation:</strong> available line capacity and production timing are confirmed for the requested rice and shipment window.</div></div></div></section>
<section class="section surface"><div class="container"><div class="section-head"><div><p class="eyebrow" style="color:var(--leaf)">Processing flow</p><h2 class="section-title">Connected stages from paddy to pack.</h2></div></div><div class="card-grid"><article class="card"><span class="number">01</span><h3>Prepare</h3><p>Paddy procurement, drying, warehousing, pre-cleaning, de-stoning and grading.</p></article><article class="card"><span class="number">02</span><h3>Process</h3><p>Parboiling where applicable, mechanised drying, de-husking, milling and polishing.</p></article><article class="card"><span class="number">03</span><h3>Finish</h3><p>Sorting, separation, magnets, accepted packing and shipment coordination.</p></article></div></div></section>
<section class="section"><div class="container grid-2"><div><p class="eyebrow" style="color:var(--leaf)">Mill-side verification</p><h2 class="section-title">What an importer can request.</h2><p class="section-lede">Ask for current company records, mill photographs, the proposed product specification, sample arrangements, applicable test evidence and packing details. Document validity and scope should be checked for the legal operating entity and intended market.</p><p><a class="button" href="contact.html#rfq">Request due-diligence documents</a></p></div><div class="photo-card"><img src="assets/images/ricefarm/mill-campus-chimney.webp" alt="RI-marked chimney at the UrbanFresh Rice Mills production campus" loading="lazy" width="751" height="1280"></div></div></section>
""",
    },
    {
        "slug": "quality-residue-testing.html",
        "nav": "Quality",
        "title": "Rice Quality, MRL Review & Lot Testing | UrbanFresh",
        "description": "Understand how UrbanFresh handles buyer rice specifications, destination pesticide-residue limits, lot-specific evidence and certificate-of-analysis review.",
        "image": "mill-quality.webp",
        "kicker": "Specification and evidence",
        "h1": "Quality claims should resolve to a lot, limit and document.",
        "lede": "Destination rules and buyer programmes differ. UrbanFresh reviews residue and quality requirements against the proposed rice, crop, lot and testing scope before acceptance.",
        "body": """
<section class="section"><div class="container content-layout"><article class="prose"><h2>Start with the applicable limit</h2><p>Terms such as “pesticide residue free”, “EU compliant” or “export quality” are incomplete unless the buyer identifies the destination standard, analyte list, reporting limit, sampling method and accepted laboratory evidence.</p><div class="notice"><strong>Evidence boundary:</strong> UrbanFresh confirms the applicable laboratory evidence against the offered lot and buyer brief. This page does not claim one permanent numerical limit or one universal test scope for every destination.</div><h2>The review sequence</h2><ol class="process-list"><li><strong>Buyer supplies the destination brief.</strong><br>Country, product, applicable MRL schedule, private standard and any named laboratory requirement.</li><li><strong>Mill reviews product feasibility.</strong><br>Variety, processing type, crop, volume, production window and evidence required.</li><li><strong>Sampling and testing scope are agreed.</strong><br>The parties identify the sample, stage, analytes, method and report recipient.</li><li><strong>Current evidence is reviewed.</strong><br>Acceptance is tied to the offered lot and buyer-approved report, not a permanent website promise.</li></ol><h2>What a certificate-of-analysis discussion should cover</h2><table class="spec-table"><tr><th>Identity</th><td>Product, crop, lot or batch reference and sampling date.</td></tr><tr><th>Physical specification</th><td>Moisture, broken, grain length, purity, damage, discolouration and foreign matter as applicable.</td></tr><tr><th>Residue scope</th><td>Destination-specific analytes, limits, reporting units and laboratory method.</td></tr><tr><th>Decision</th><td>Buyer review, exceptions, retest rules and relationship to the final shipment.</td></tr></table><h2>Certificates and registrations</h2><p>Available mill records include ISO 22000:2018, FSSAI, APEDA, U.S. FDA registration, Importer Exporter Code and rice-mill registrations. Buyers should request current copies and verify issuer, legal entity, unit, scope, validity and destination relevance before relying on them.</p></article><aside class="info-panel"><h2>Send the compliance brief</h2><p>Include destination, rice, volume, target limits, required lab or accreditation, document checklist and shipment window.</p><a class="button button-gold" href="contact.html#rfq">Send quality requirements</a></aside></div></section>
<section class="section surface"><div class="container"><p class="eyebrow" style="color:var(--leaf)">Buyer questions</p><h2 class="section-title">Quality and MRL FAQ.</h2><div class="faq-list"><details class="faq"><summary>Does UrbanFresh publish one universal pesticide-residue claim?</summary><p>No. Residue requirements differ by destination and buyer programme. Current lot-specific evidence must be reviewed against the applicable limits.</p></details><details class="faq"><summary>Can the buyer name a laboratory or test scope?</summary><p>Yes. Include the laboratory, accreditation, analyte list, sampling stage and reporting requirements in the RFQ for feasibility review.</p></details><details class="faq"><summary>Are website certificate names enough for approval?</summary><p>No. Request current full-resolution documents and verify the legal entity, unit, product scope, market relevance and expiry.</p></details></div></div></section>
""",
    },
    {
        "slug": "export-documents.html",
        "nav": "Export process",
        "title": "Rice Export Documents & Buyer Checklist | UrbanFresh",
        "description": "Build a rice export document checklist with UrbanFresh covering destination, buyer, product, inspection, origin and shipment requirements.",
        "image": "mill-campus-office.webp",
        "kicker": "Document the transaction",
        "h1": "Agree the export document pack before production.",
        "lede": "The required documents depend on the legal exporter, importing country, port, buyer programme, product and shipment terms. UrbanFresh reviews the checklist before accepting an order.",
        "body": """
<section class="section"><div class="container content-layout"><article class="prose"><h2>A checklist, not a generic promise</h2><p>Rice shipments may involve commercial, customs, origin, plant-health, fumigation, food-safety, inspection, transport and insurance records. Which party obtains each document must be written into the order because the mill, merchant exporter, freight forwarder and buyer may have different responsibilities.</p><h2>Five document groups to define</h2><table class="spec-table"><tr><th>Commercial</th><td>Quotation, pro forma invoice, commercial invoice, packing list, payment and Incoterm records.</td></tr><tr><th>Exporter identity</th><td>Legal exporter, IEC and any destination or commodity registrations relevant to the shipment.</td></tr><tr><th>Product evidence</th><td>Accepted specification, certificate of analysis, inspection or other buyer-required quality evidence.</td></tr><tr><th>Plant and origin</th><td>Any applicable phytosanitary, fumigation, health, origin or treatment documentation.</td></tr><tr><th>Transport</th><td>Container, seal, weight, shipping instruction, bill of lading and insurance responsibilities.</td></tr></table><div class="notice"><strong>Responsibility must be explicit:</strong> listing a document here does not claim UrbanFresh is the issuing authority or legal exporter for every order.</div><h2>Information the buyer should provide</h2><ul class="check-list"><li>Importer and consignee legal names and destination.</li><li>Required rice specification, pack, labels and shipment volume.</li><li>Named certificates, inspection bodies and laboratory rules.</li><li>Preferred port, Incoterm, payment method and delivery window.</li><li>Any destination pre-registration or prior-notice requirement.</li></ul></article><aside class="info-panel"><h2>Have a document checklist?</h2><p>Attach or paste it into the RFQ. UrbanFresh will identify what needs mill, exporter or logistics confirmation.</p><a class="button button-gold" href="contact.html#rfq">Send the checklist</a></aside></div></section>
""",
    },
    {
        "slug": "packing-container-logistics.html",
        "nav": "Packing",
        "title": "Rice Export Packing & Container Planning | UrbanFresh",
        "description": "Plan rice export packing and container requirements with UrbanFresh by defining bag format, artwork, net weight, loading method and destination.",
        "image": "mill-processing-plant.webp",
        "kicker": "Pack and shipment planning",
        "h1": "The bag choice changes the container plan.",
        "lede": "Net loading depends on rice, bag size, material, palletisation, container limits and destination rules. UrbanFresh confirms the configuration only after the packing brief is reviewed.",
        "body": """
<section class="section"><div class="container content-layout"><article class="prose"><h2>Define the pack before asking for container tonnage</h2><p>A reliable loading answer needs the bag's nominal and filled dimensions, net and gross weight, material, closure, pallet requirement, dunnage or liner requirement and container payload limits. A single “MT per container” figure without those inputs can mislead the buyer.</p><table class="spec-table"><tr><th>Primary pack</th><td>Material, construction, net weight, print method, handle or closure and food-contact requirements.</td></tr><tr><th>Artwork</th><td>Final files, colours, barcode, language, importer details, origin statements and destination labelling rules.</td></tr><tr><th>Master handling</th><td>Loose bags, bales, cartons or pallets; stretch-wrap, corner protection and stacking constraints.</td></tr><tr><th>Container</th><td>20-ft or 40-ft, floor-loaded or palletised, payload, liner, desiccant, fumigation and seal requirements.</td></tr><tr><th>Acceptance</th><td>Approved sample, print proof, packing tolerance, inspection and loading evidence.</td></tr></table><div class="notice"><strong>Configuration is quoted per order:</strong> the mill confirms supported pack, MOQ, lead time and net container loading after reviewing the rice, bag and shipment brief.</div><h2>The correct planning sequence</h2><ol class="process-list"><li>Share destination labelling and handling requirements.</li><li>Choose rice, processing type, pack material and net weight.</li><li>Approve artwork, sample and packing specification.</li><li>Confirm container type, loading method and verified payload.</li><li>Accept production, inspection and dispatch milestones.</li></ol></article><aside class="info-panel"><h2>Plan a shipment</h2><p>Send pack size, material, artwork status, target container, destination and volume.</p><a class="button button-gold" href="contact.html#rfq">Send packing brief</a></aside></div></section>
""",
    },
    {
        "slug": "private-label-rice.html",
        "nav": "Private label",
        "title": "Private Label Rice Packing for Export Brands | UrbanFresh",
        "description": "Discuss private-label rice packing with UrbanFresh using a destination-led brief covering rice, artwork, labels, pack format and order volume.",
        "image": "category-1121.webp",
        "kicker": "Buyer-brand packing",
        "h1": "Private label begins with destination-compliant artwork.",
        "lede": "UrbanFresh reviews buyer-brand enquiries against the rice specification, pack construction, legal label content, artwork readiness, volume and production timeline.",
        "body": """
<section class="section"><div class="container content-layout"><article class="prose"><h2>What the brand owner controls</h2><p>The buyer should supply the brand authority, approved artwork, destination labelling brief, importer details, barcode and any claims that require evidence. UrbanFresh reviews print and production feasibility; the buyer remains responsible for approving the final legal label.</p><h2>Private-label intake</h2><table class="spec-table"><tr><th>Rice</th><td>Variety, process, crop, quality limits and accepted sample.</td></tr><tr><th>Pack</th><td>Net weight, material, dimensions, construction, closure and master handling.</td></tr><tr><th>Artwork</th><td>Editable files, colour references, print method, language, barcode and importer panel.</td></tr><tr><th>Market</th><td>Destination labelling law, claims, mandatory declarations and retailer requirements.</td></tr><tr><th>Order</th><td>Quantity per SKU, target shipment date, container plan and inspection needs.</td></tr></table><h2>Approval gates</h2><ol class="process-list"><li>Commercial and production feasibility review.</li><li>Rice sample and written specification acceptance.</li><li>Artwork and print-proof approval.</li><li>Packing sample or pre-production confirmation.</li><li>Lot evidence, inspection and loading plan acceptance.</li></ol><div class="notice"><strong>MOQ and lead time are order-specific.</strong> They depend on the rice, pack, print setup, number of SKUs and production window.</div></article><aside class="info-panel"><h2>Build a brand brief</h2><p>Send your destination, rice, pack sizes, material, artwork status, SKU count and volume.</p><a class="button button-gold" href="contact.html#rfq">Discuss private label</a></aside></div></section>
""",
    },
    {
        "slug": "1121-basmati-rice.html",
        "nav": "Rice",
        "title": "1121 Basmati Rice Export Specification | UrbanFresh",
        "description": "Build a lot-specific 1121 Basmati rice enquiry with UrbanFresh covering process, crop, grain, moisture, broken, residue, packing and destination.",
        "image": "category-1121.webp",
        "product": "1121 Basmati Rice",
        "kicker": "Lot-specific product brief",
        "h1": "1121 Basmati Rice for specification-led buying.",
        "lede": "UrbanFresh reviews raw, steam, sella and golden sella 1121 enquiries against the buyer's physical, cooking, residue, packing and shipment requirements.",
    },
    {
        "slug": "1509-basmati-rice.html",
        "nav": "Rice",
        "title": "1509 Basmati Rice Export Specification | UrbanFresh",
        "description": "Build a lot-specific 1509 Basmati rice enquiry with UrbanFresh covering process, crop, grain, moisture, broken, residue, packing and destination.",
        "image": "category-1509.webp",
        "product": "1509 Basmati Rice",
        "kicker": "Lot-specific product brief",
        "h1": "1509 Basmati Rice for specification-led buying.",
        "lede": "UrbanFresh reviews raw, steam, sella and golden sella 1509 enquiries against the buyer's physical, cooking, residue, packing and shipment requirements.",
    },
    {
        "slug": "1401-basmati-rice.html",
        "nav": "Rice",
        "title": "1401 Basmati Rice Export Specification | UrbanFresh",
        "description": "Build a lot-specific 1401 Basmati rice enquiry with UrbanFresh covering process, crop, grain, moisture, broken, residue, packing and destination.",
        "image": "category-1401.webp",
        "product": "1401 Basmati Rice",
        "kicker": "Lot-specific product brief",
        "h1": "1401 Basmati Rice for specification-led buying.",
        "lede": "UrbanFresh reviews raw, steam, sella and golden sella 1401 enquiries against the buyer's physical, cooking, residue, packing and shipment requirements.",
    },
    {
        "slug": "contact.html",
        "nav": "RFQ",
        "title": "International Rice RFQ | Contact UrbanFresh",
        "description": "Send UrbanFresh a structured international rice request with variety, processing, volume, packing, destination, quality and shipment details.",
        "image": "mill-campus-office.webp",
        "kicker": "International buyer desk",
        "h1": "Send one complete rice request for mill review.",
        "lede": "A complete brief helps UrbanFresh assess product, quality, packing, evidence and production fit before a commercial response.",
        "body": """
<section class="section" id="rfq"><div class="container content-layout"><div><p class="eyebrow" style="color:var(--leaf)">Request for quotation</p><h2 class="section-title">Tell us what must be true for this order.</h2><p class="section-lede">Required fields capture the minimum information needed to route the enquiry. Use the notes field for quality limits, residue standards, document requirements and commercial terms.</p>
<form data-quote-form>
  <div class="form-grid">
    <div class="field"><label for="name">Name or company *</label><input id="name" name="name" autocomplete="organization" required></div>
    <div class="field"><label for="phone">Phone / WhatsApp *</label><input id="phone" name="phone" type="tel" autocomplete="tel" required></div>
    <div class="field"><label for="email">Business email</label><input id="email" name="email" type="email" autocomplete="email"></div>
    <div class="field"><label for="buyer_type">Buyer type</label><select id="buyer_type" name="buyer_type"><option value="">Select</option><option>Importer</option><option>Distributor / wholesaler</option><option>Merchant exporter</option><option>Private-label brand</option><option>Institutional buyer</option><option>Other</option></select></div>
    <div class="field"><label for="location">Destination country / port *</label><input id="location" name="location" required></div>
    <div class="field"><label for="variety">Rice variety</label><select id="variety" name="variety"><option value="">Please advise</option><option>1121 Basmati</option><option>1509 Basmati</option><option>1401 Basmati</option><option>Other basmati</option><option>Non-basmati</option></select></div>
    <div class="field"><label for="processing">Processing</label><select id="processing" name="processing"><option value="">Please advise</option><option>Raw</option><option>Steam</option><option>Sella / parboiled</option><option>Golden sella</option></select></div>
    <div class="field"><label for="quantity">Approximate quantity *</label><input id="quantity" name="quantity" placeholder="Example: 1 x 20-ft container or 25 MT" required></div>
    <div class="field"><label for="packaging">Packing brief</label><input id="packaging" name="packaging" placeholder="Net weight, material, private label"></div>
    <div class="field"><label for="timeline">Target shipment window</label><input id="timeline" name="timeline" placeholder="Month or required date"></div>
    <div class="field full"><label for="message">Specification, MRL, documents and commercial notes</label><textarea id="message" name="message" placeholder="Include moisture, broken, grain length, residue limits, lab or certificate needs, Incoterm, payment terms and any sample requirement."></textarea></div>
  </div>
  <p><button class="button" type="submit">Submit international RFQ</button></p>
  <div class="form-status" data-form-status tabindex="-1" aria-live="polite"></div>
</form></div><aside class="info-panel"><h2>Mill contact</h2><p>UrbanFresh Rice Mills<br>119/6, Highway, Village Daha, Madanpur<br>Karnal 132001, Haryana, India</p><p><a href="tel:+919433569217">+91 94335 69217</a><br><a href="https://wa.me/919433569217?text=Hello%20UrbanFresh%2C%20I%20would%20like%20to%20send%20an%20international%20rice%20RFQ." target="_blank" rel="noopener">WhatsApp the buyer desk</a></p></aside></div></section>
""",
    },
    {
        "slug": "thank-you.html",
        "nav": "",
        "title": "RFQ Received | UrbanFresh Rice Mills",
        "description": "Your international rice request has been received by UrbanFresh Rice Mills. Continue on WhatsApp to share specifications, artwork or documents.",
        "image": "mill-campus-office.webp",
        "kicker": "Request received",
        "h1": "Thank you. Your rice brief is ready for review.",
        "lede": "Continue on WhatsApp if you need to share a specification sheet, label artwork, certificate checklist or shipment document.",
        "body": """
<section class="section completion-section"><div class="container"><div class="card completion-card"><h2>Keep the full buying brief together.</h2><p>Use the button below to continue the same request on WhatsApp. You can attach product specifications, artwork and document checklists there.</p><p><a class="button" data-whatsapp-follow-up href="https://wa.me/919433569217" target="_blank" rel="noopener">Continue on WhatsApp</a></p><p><a class="completion-link" href="index.html">Return to the international site</a></p></div></div></section>
""",
    },
]


def product_body(name: str) -> str:
    escaped = html.escape(name)
    return f"""
<section class="section"><div class="container content-layout"><article class="prose"><h2>Choose the processing style first</h2><p>{escaped} enquiries may be discussed as raw, steam, sella/parboiled or golden sella rice. Processing affects appearance, cooking behaviour, moisture management, price and destination preference, so comparisons should be like for like.</p><h2>Build the written specification</h2><table class="spec-table"><tr><th>Variety and process</th><td>{escaped}; raw, steam, sella or golden sella.</td></tr><tr><th>Crop and ageing</th><td>Confirm crop year and any ageing requirement for the offered lot.</td></tr><tr><th>Physical limits</th><td>Average grain length, moisture, broken, purity, damaged/discoloured grains, foreign matter and polish.</td></tr><tr><th>Cooking</th><td>Aroma, elongation, texture and controlled sample method where required.</td></tr><tr><th>Residue and safety</th><td>Destination MRL schedule, analyte scope, laboratory and other buyer evidence.</td></tr><tr><th>Packing and shipment</th><td>Pack material/size, private label, volume, container plan, destination and shipment window.</td></tr></table><div class="notice"><strong>No universal numerical specification is published.</strong> Agricultural lots and buyer programmes vary. The accepted sample, written specification and current evidence govern the proposed order.</div><h2>Before price comparison</h2><ul class="check-list"><li>Compare the same variety, process, crop and ageing position.</li><li>State whether price includes packing, inland logistics and port responsibilities.</li><li>Identify the destination residue and document rules.</li><li>Confirm payment, inspection, shipment and claim terms in writing.</li></ul></article><aside class="info-panel"><h2>Quote {escaped}</h2><p>Send processing, crop, volume, pack, destination, shipment window and target quality limits.</p><a class="button button-gold" href="contact.html#rfq">Build this RFQ</a></aside></div></section>
<section class="section surface"><div class="container"><p class="eyebrow" style="color:var(--leaf)">Buyer questions</p><h2 class="section-title">{escaped} FAQ.</h2><div class="faq-list"><details class="faq"><summary>Can I ask for a sample before ordering?</summary><p>Include the sample size, destination, courier arrangement and specification to be evaluated. Availability and terms are confirmed per enquiry.</p></details><details class="faq"><summary>Can the rice be packed under my brand?</summary><p>Private-label feasibility depends on pack material, size, artwork readiness, SKU count, volume and destination labelling requirements.</p></details><details class="faq"><summary>How is residue compliance handled?</summary><p>Share the applicable destination limits and required evidence. Any acceptance is tied to the agreed testing scope and offered lot.</p></details></div></div></section>
"""


def organization_schema() -> dict[str, object]:
    return {
        "@type": "Organization",
        "name": "UrbanFresh Rice Mills",
        "url": f"{DOMAIN}/",
        "logo": f"{DOMAIN}/assets/images/urbanfresh-logo.webp",
        "image": [
            f"{DOMAIN}/assets/images/ricefarm/mill-processing-plant.webp",
            f"{DOMAIN}/assets/images/ricefarm/mill-campus-office.webp",
        ],
        "telephone": PHONE_LINK,
        "foundingDate": "1978",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "119/6, Highway, Village Daha, Madanpur",
            "addressLocality": "Karnal",
            "addressRegion": "Haryana",
            "postalCode": "132001",
            "addressCountry": "IN",
        },
        "hasMap": MAP_URL,
        "sameAs": [LINKEDIN, "https://urbanfresh.in/"],
        "areaServed": "International",
    }


def page_schema(page: dict[str, str]) -> dict[str, object]:
    slug = page["slug"]
    url = f"{DOMAIN}/{slug}" if slug else f"{DOMAIN}/"
    page_type = "WebPage"
    main: dict[str, object] = {
        "@type": page_type,
        "name": page["title"],
        "url": url,
        "description": page["description"],
        "isPartOf": {"@type": "WebSite", "name": "UrbanFresh International", "url": f"{DOMAIN}/"},
    }
    if page.get("product"):
        main["@type"] = "ItemPage"
        main["mainEntity"] = {
            "@type": "Thing",
            "name": page["product"],
            "description": page["lede"],
            "url": url,
        }
    return {"@context": "https://schema.org", "@graph": [organization_schema(), main]}


def header(active: str) -> str:
    links = [
        ("index.html", "Home", active == ""),
        ("about-mill-infrastructure.html", "The mill", active == "about-mill-infrastructure.html"),
        ("quality-residue-testing.html", "Quality & MRL", active == "quality-residue-testing.html"),
        ("export-documents.html", "Export process", active == "export-documents.html"),
        ("private-label-rice.html", "Private label", active == "private-label-rice.html"),
    ]
    rendered = "".join(
        f'<a{" class=\"active\"" if selected else ""} href="{href}">{label}</a>'
        for href, label, selected in links
    )
    return f"""
<div class="topbar"><div class="container topbar-inner"><span>UrbanFresh Rice Mills · Karnal, India</span><span><a href="tel:{PHONE_LINK}">{PHONE_DISPLAY}</a> · International enquiries</span></div></div>
<header class="site-header"><div class="container nav-wrap">
  <a class="brand" href="index.html" aria-label="UrbanFresh International home"><img src="assets/images/urbanfresh-logo.webp" width="48" height="48" alt="UrbanFresh rice grain and sunrise logo"><span class="brand-copy"><span class="brand-name">UrbanFresh</span><span class="brand-tag">International buyer desk</span></span></a>
  <button class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false" data-menu-toggle></button>
  <nav class="main-nav" aria-label="Main navigation" data-main-nav>{rendered}<a class="button button-sm" href="contact.html#rfq">Send RFQ</a></nav>
</div></header>"""


def footer() -> str:
    return f"""
<footer class="site-footer"><div class="container footer-grid">
  <div><a class="brand" href="index.html"><img src="assets/images/urbanfresh-logo.webp" width="48" height="48" alt=""><span class="brand-copy"><span class="brand-name">UrbanFresh</span><span class="brand-tag">International buyer desk</span></span></a><p>A family-operated rice mill in Village Daha, Madanpur, Karnal, India. Specifications, evidence, packing and terms are confirmed per enquiry.</p></div>
  <div><h2 class="footer-title">Buyer journey</h2><div class="footer-links"><a href="about-mill-infrastructure.html">Mill & infrastructure</a><a href="quality-residue-testing.html">Quality & MRL review</a><a href="export-documents.html">Export documents</a><a href="packing-container-logistics.html">Packing & containers</a></div></div>
  <div><h2 class="footer-title">Rice</h2><div class="footer-links"><a href="1121-basmati-rice.html">1121 Basmati</a><a href="1509-basmati-rice.html">1509 Basmati</a><a href="1401-basmati-rice.html">1401 Basmati</a><a href="private-label-rice.html">Private label</a></div></div>
  <div><h2 class="footer-title">Contact</h2><div class="footer-links"><a href="tel:{PHONE_LINK}">{PHONE_DISPLAY}</a><a href="{WHATSAPP}" target="_blank" rel="noopener">WhatsApp buyer desk</a><a href="contact.html#rfq">International RFQ</a><a href="https://urbanfresh.in/" rel="external">Domestic India sales: urbanfresh.in</a><a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn</a></div></div>
</div><div class="container footer-bottom"><span>© <span data-year></span> UrbanFresh Rice Mills.</span><span>Availability, specifications, evidence, packing and terms are confirmed per enquiry.</span></div></footer>
<div class="mobile-cta"><a class="button button-outline" href="{WHATSAPP}" target="_blank" rel="noopener">WhatsApp</a><a class="button" href="contact.html#rfq">Send RFQ</a></div>"""


def page_hero(page: dict[str, str]) -> str:
    if not page.get("h1"):
        return ""
    return f"""
<section class="page-hero" style="--page-image:url('/assets/images/ricefarm/{html.escape(page["image"])}')"><div class="container">
  <div class="breadcrumbs"><a href="index.html">Home</a><span>{html.escape(page["nav"] or page["title"])}</span></div>
  <p class="eyebrow">{html.escape(page["kicker"])}</p><h1>{html.escape(page["h1"])}</h1><p>{html.escape(page["lede"])}</p>
</div></section>"""


def render(page: dict[str, str]) -> str:
    slug = page["slug"]
    canonical = f"{DOMAIN}/{slug}" if slug else f"{DOMAIN}/"
    robots = "index,follow,max-image-preview:large" if LAUNCH_READY and slug != "thank-you.html" else "noindex,nofollow"
    body = page.get("body") or product_body(page["product"])
    alternates = ""
    if slug == "about-mill-infrastructure.html":
        alternates = f"""
  <link rel="alternate" hreflang="en-IN" href="https://urbanfresh.in/about.html">
  <link rel="alternate" hreflang="en" href="{DOMAIN}/about-mill-infrastructure.html">"""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{html.escape(page["title"])}</title>
  <meta name="description" content="{html.escape(page["description"])}">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{canonical}">
  {alternates}
  <meta name="theme-color" content="#123c2d">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="UrbanFresh International">
  <meta property="og:title" content="{html.escape(page["title"])}">
  <meta property="og:description" content="{html.escape(page["description"])}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{DOMAIN}/assets/images/urbanfresh-export-social.png">
  <meta property="og:image:width" content="1734">
  <meta property="og:image:height" content="907">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(page["title"])}">
  <meta name="twitter:description" content="{html.escape(page["description"])}">
  <meta name="twitter:image" content="{DOMAIN}/assets/images/urbanfresh-export-social.png">
  <link rel="icon" href="assets/images/favicon.png" type="image/png">
  <link rel="stylesheet" href="assets/css/site.css?v=20260725-4">
  <script type="application/ld+json">{json.dumps(page_schema(page), separators=(",", ":"))}</script>
</head>
<body class="{"page-thank-you" if slug == "thank-you.html" else ""}">
  <a class="skip-link" href="#main">Skip to content</a>
  {header(slug)}
  <main id="main">{page_hero(page)}{body}
  <section class="section-sm quote-band"><div class="container quote-band-inner"><div><h2>Have a complete buying brief?</h2><p>Send the rice, specification, volume, packing, destination and shipment window in one RFQ.</p></div><a class="button" href="contact.html#rfq">Send international RFQ</a></div></section>
  </main>
  {footer()}
  <script src="assets/js/site.js?v=20260725-1" defer></script>
</body>
</html>
"""


def write_sitemap() -> None:
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    root = ET.Element("{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")
    for page in PAGES:
        if page["slug"] == "thank-you.html":
            continue
        url = ET.SubElement(root, "{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        loc = ET.SubElement(url, "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        loc.text = f"{DOMAIN}/{page['slug']}" if page["slug"] else f"{DOMAIN}/"
        lastmod = ET.SubElement(url, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        lastmod.text = BUILD_DATE
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def main() -> None:
    for page in PAGES:
        destination = ROOT / (page["slug"] or "index.html")
        destination.write_text(render(page), encoding="utf-8")
    robots = (
        f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n"
        if LAUNCH_READY
        else "User-agent: *\nDisallow: /\n"
    )
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    write_sitemap()
    print(f"Built {len(PAGES)} pages (launch_ready={LAUNCH_READY}).")


if __name__ == "__main__":
    main()
