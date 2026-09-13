// C.I.D. — Operation Monsoon (DEMO). Entirely fictional data.
// All entities, relationships, evidence, leads, and events are simulated.

export const INVESTIGATIONS = [
  {
    id: "inv-monsoon",
    title: "Operation Monsoon",
    caseRef: "DEMO/OPS-MONSOON/2024",
    status: "active",
    summary:
      "Coordinated analysis of a suspected smuggling and parallel-financing network operating across coastal and urban nodes. DEMO dataset.",
    opened: "2024-02-14",
    lead: "Demo Investigator",
    tags: ["smuggling", "financial", "communication"],
  },
  {
    id: "inv-harbor",
    title: "Harbor Ledger",
    caseRef: "DEMO/OPS-HARBOR/2024",
    status: "active",
    summary: "Follow-up financial-flow analysis linked to coastal logistics. DEMO dataset.",
    opened: "2024-05-02",
    lead: "Demo Investigator",
    tags: ["financial", "logistics"],
  },
  {
    id: "inv-orchid",
    title: "Orchid Realty Probe",
    caseRef: "DEMO/OPS-ORCHID/2024",
    status: "reviewing",
    summary: "Examination of property holdings and shell-ownership patterns. DEMO dataset.",
    opened: "2024-06-21",
    lead: "Demo Investigator",
    tags: ["property", "organization"],
  },
];

export const ENTITIES = [
  // People
  { id: "P1", name: "Ravi Menon", type: "person", cluster: "core", role: "Central coordinator", notes_bio: "Coastal businessman; frequent traveler." },
  { id: "P2", name: "Imran Qureshi", type: "person", cluster: "logistics", role: "Logistics handler" },
  { id: "P3", name: "Sana Kapoor", type: "person", cluster: "finance", role: "Account signatory" },
  { id: "P4", name: "Vikram Desai", type: "person", cluster: "core", role: "Intermediary" },
  { id: "P5", name: "Meera Nair", type: "person", cluster: "finance", role: "Bookkeeper" },
  { id: "P6", name: "Arjun Reddy", type: "person", cluster: "logistics", role: "Driver" },
  { id: "P7", name: "Fatima Sheikh", type: "person", cluster: "urban", role: "Courier" },
  { id: "P8", name: "Karan Malhotra", type: "person", cluster: "urban", role: "Broker" },
  { id: "P9", name: "Priya Bhatt", type: "person", cluster: "finance", role: "Account holder" },
  { id: "P10", name: "Usman Ali", type: "person", cluster: "logistics", role: "Warehouse contact" },
  { id: "P11", name: "Deepak Rao", type: "person", cluster: "urban", role: "Retired inspector (associate)" },
  { id: "P12", name: "Nadia Joshi", type: "person", cluster: "core", role: "Property owner" },
  { id: "P13", name: "Suresh Pillai", type: "person", cluster: "logistics", role: "Port liaison" },
  { id: "P14", name: "Tara Singh", type: "person", cluster: "finance", role: "Cash courier" },
  { id: "P15", name: "Bilal Khan", type: "person", cluster: "urban", role: "Repair shop owner" },
  { id: "P16", name: "Anita Verma", type: "person", cluster: "finance", role: "Consultant" },

  // Phones
  { id: "PH1", name: "+91 98•••• 2210", type: "phone", cluster: "core", carrier: "DemoCell" },
  { id: "PH2", name: "+91 98•••• 7741", type: "phone", cluster: "logistics", carrier: "DemoCell" },
  { id: "PH3", name: "+91 90•••• 1180", type: "phone", cluster: "finance", carrier: "AirTel-Demo" },
  { id: "PH4", name: "+91 70•••• 9932", type: "phone", cluster: "urban", carrier: "DemoCell" },
  { id: "PH5", name: "+91 80•••• 4455", type: "phone", cluster: "core", carrier: "AirTel-Demo" },
  { id: "PH6", name: "+91 99•••• 6612", type: "phone", cluster: "logistics", carrier: "DemoCell" },
  { id: "PH7", name: "+91 73•••• 0098", type: "phone", cluster: "finance", carrier: "DemoCell" },
  { id: "PH8", name: "+91 88•••• 3321", type: "phone", cluster: "urban", carrier: "AirTel-Demo" },

  // Vehicles
  { id: "V1", name: "KA-01 AB 4421", type: "vehicle", cluster: "core", model: "SUV (Demo)" },
  { id: "V2", name: "MH-02 CD 8870", type: "vehicle", cluster: "logistics", model: "Cargo van (Demo)" },
  { id: "V3", name: "DL-08 EF 1290", type: "vehicle", cluster: "urban", model: "Sedan (Demo)" },
  { id: "V4", name: "GA-03 GH 5567", type: "vehicle", cluster: "logistics", model: "Truck (Demo)" },
  { id: "V5", name: "TN-22 IJ 7741", type: "vehicle", cluster: "finance", model: "Hatchback (Demo)" },
  { id: "V6", name: "KL-07 KL 9032", type: "vehicle", cluster: "core", model: "Pickup (Demo)" },

  // Locations
  { id: "L1", name: "Blue Harbor Warehouse", type: "location", cluster: "logistics", region: "Coastal" },
  { id: "L2", name: "Pier 9 Storage", type: "location", cluster: "logistics", region: "Coastal" },
  { id: "L3", name: "Zenith Office Tower", type: "location", cluster: "finance", region: "Urban" },
  { id: "L4", name: "Orchid Residency", type: "location", cluster: "urban", region: "Urban" },
  { id: "L5", name: "North Market Yard", type: "location", cluster: "urban", region: "Urban" },
  { id: "L6", name: "Coastal Transit Depot", type: "location", cluster: "core", region: "Coastal" },

  // Organizations
  { id: "O1", name: "Coastal Logistics Pvt Ltd", type: "organization", cluster: "logistics" },
  { id: "O2", name: "Zenith Trading Co", type: "organization", cluster: "finance" },
  { id: "O3", name: "Meridian Exports", type: "organization", cluster: "logistics" },
  { id: "O4", name: "Orchid Realty", type: "organization", cluster: "urban" },
  { id: "O5", name: "Blue Harbor Shipping", type: "organization", cluster: "core" },

  // Cases
  { id: "C1", name: "FIR-1042", type: "case", cluster: "core", status: "open" },
  { id: "C2", name: "FIR-1187", type: "case", cluster: "logistics", status: "open" },
  { id: "C3", name: "FIR-2031", type: "case", cluster: "finance", status: "under-investigation" },

  // Accounts
  { id: "A1", name: "Acct ••4421 (Zenith)", type: "account", cluster: "finance", bank: "Demo Bank" },
  { id: "A2", name: "Acct ••8870 (Coastal)", type: "account", cluster: "logistics", bank: "Demo Bank" },
  { id: "A3", name: "Acct ••1290 (Meridian)", type: "account", cluster: "logistics", bank: "Demo Bank" },
  { id: "A4", name: "Acct ••5567 (Orchid)", type: "account", cluster: "urban", bank: "Demo Bank" },
  { id: "A5", name: "Acct ••9032 (personal)", type: "account", cluster: "core", bank: "Demo Bank" },

  // Events
  { id: "E1", name: "Port Meeting — Mar 2024", type: "event", cluster: "logistics" },
  { id: "E2", name: "Warehouse Raid — May 2024", type: "event", cluster: "logistics" },
  { id: "E3", name: "Offshore Transfer — Jul 2024", type: "event", cluster: "finance" },
];

// Relationships. documented=true => supported by a source record.
// confidence (0-1) applies to inferred relationships.
export const RELATIONSHIPS = [
  // Core cluster
  { id: "R1", source: "P1", target: "PH1", type: "registered to", category: "communication", documented: true, evidence: ["EV-CDR-1"], first: "2024-01-04", last: "2024-08-12", confidence: 1 },
  { id: "R2", source: "P1", target: "V1", type: "registered to", category: "vehicles", documented: true, evidence: ["EV-VEH-1"], first: "2023-11-02", last: "2024-07-30", confidence: 1 },
  { id: "R3", source: "P1", target: "P4", type: "associated with", category: "all", documented: true, evidence: ["EV-FIR-1"], first: "2024-02-10", last: "2024-08-01", confidence: 1 },
  { id: "R4", source: "P1", target: "O5", type: "connected to", category: "organizations", documented: true, evidence: ["EV-INT-1"], first: "2024-01-20", last: "2024-07-15", confidence: 1 },
  { id: "R5", source: "P1", target: "L6", type: "present at", category: "locations", documented: true, evidence: ["EV-INT-1"], first: "2024-03-05", last: "2024-06-18", confidence: 1 },
  { id: "R6", source: "P1", target: "P12", type: "associated with", category: "all", documented: false, evidence: ["EV-INT-3"], first: "2024-03-12", last: "2024-07-02", confidence: 0.62, reason: "Overlapping presence at Coastal Transit Depot and shared associate P4." },
  { id: "R7", source: "P1", target: "C1", type: "named in", category: "all", documented: true, evidence: ["EV-FIR-1"], first: "2024-02-14", last: "2024-02-14", confidence: 1 },

  // P4 intermediary
  { id: "R8", source: "P4", target: "PH5", type: "registered to", category: "communication", documented: true, evidence: ["EV-CDR-2"], first: "2024-01-10", last: "2024-08-09", confidence: 1 },
  { id: "R9", source: "P4", target: "P12", type: "associated with", category: "all", documented: true, evidence: ["EV-FIR-2"], first: "2024-03-01", last: "2024-07-20", confidence: 1 },
  { id: "R10", source: "P4", target: "O2", type: "connected to", category: "organizations", documented: false, evidence: [], first: "2024-04-02", last: "2024-06-30", confidence: 0.54, reason: "Shared meeting location with Zenith signatories; no direct record." },
  { id: "R11", source: "P4", target: "L3", type: "present at", category: "locations", documented: true, evidence: ["EV-INT-2"], first: "2024-04-02", last: "2024-06-15", confidence: 1 },

  // Logistics cluster
  { id: "R12", source: "P2", target: "PH2", type: "registered to", category: "communication", documented: true, evidence: ["EV-CDR-3"], first: "2024-01-15", last: "2024-08-10", confidence: 1 },
  { id: "R13", source: "P2", target: "O1", type: "connected to", category: "organizations", documented: true, evidence: ["EV-INT-4"], first: "2024-02-01", last: "2024-07-25", confidence: 1 },
  { id: "R14", source: "P2", target: "L1", type: "located at", category: "locations", documented: true, evidence: ["EV-VEH-2"], first: "2024-02-05", last: "2024-07-30", confidence: 1 },
  { id: "R15", source: "P2", target: "V2", type: "registered to", category: "vehicles", documented: true, evidence: ["EV-VEH-2"], first: "2024-01-20", last: "2024-08-01", confidence: 1 },
  { id: "R16", source: "P2", target: "P6", type: "associated with", category: "all", documented: true, evidence: ["EV-INT-4"], first: "2024-02-10", last: "2024-07-28", confidence: 1 },
  { id: "R17", source: "P6", target: "V4", type: "registered to", category: "vehicles", documented: true, evidence: ["EV-VEH-3"], first: "2024-02-12", last: "2024-07-22", confidence: 1 },
  { id: "R18", source: "P6", target: "L2", type: "present at", category: "locations", documented: true, evidence: ["EV-INT-5"], first: "2024-03-01", last: "2024-07-10", confidence: 1 },
  { id: "R19", source: "P10", target: "O3", type: "connected to", category: "organizations", documented: true, evidence: ["EV-INT-6"], first: "2024-02-20", last: "2024-07-05", confidence: 1 },
  { id: "R20", source: "P10", target: "L1", type: "located at", category: "locations", documented: true, evidence: ["EV-INT-6"], first: "2024-02-20", last: "2024-07-05", confidence: 1 },
  { id: "R21", source: "P13", target: "L1", type: "present at", category: "locations", documented: true, evidence: ["EV-INT-5"], first: "2024-03-10", last: "2024-06-25", confidence: 1 },
  { id: "R22", source: "P13", target: "P2", type: "associated with", category: "all", documented: false, evidence: [], first: "2024-03-10", last: "2024-06-25", confidence: 0.58, reason: "Repeated co-presence at Blue Harbor Warehouse across multiple dates." },
  { id: "R23", source: "P2", target: "C2", type: "named in", category: "all", documented: true, evidence: ["EV-FIR-3"], first: "2024-05-12", last: "2024-05-12", confidence: 1 },
  { id: "R24", source: "O1", target: "O3", type: "connected to", category: "organizations", documented: true, evidence: ["EV-INT-4"], first: "2024-02-15", last: "2024-07-20", confidence: 1 },

  // Finance cluster
  { id: "R25", source: "P3", target: "A1", type: "signatory of", category: "financial", documented: true, evidence: ["EV-TXN-1"], first: "2024-01-25", last: "2024-08-05", confidence: 1 },
  { id: "R26", source: "P3", target: "PH3", type: "registered to", category: "communication", documented: true, evidence: ["EV-CDR-4"], first: "2024-01-25", last: "2024-08-08", confidence: 1 },
  { id: "R27", source: "P3", target: "O2", type: "connected to", category: "organizations", documented: true, evidence: ["EV-TXN-1"], first: "2024-01-25", last: "2024-08-05", confidence: 1 },
  { id: "R28", source: "P5", target: "A1", type: "operates", category: "financial", documented: true, evidence: ["EV-TXN-2"], first: "2024-02-01", last: "2024-07-30", confidence: 1 },
  { id: "R29", source: "P5", target: "P3", type: "associated with", category: "all", documented: true, evidence: ["EV-TXN-2"], first: "2024-02-01", last: "2024-07-30", confidence: 1 },
  { id: "R30", source: "P9", target: "A4", type: "signatory of", category: "financial", documented: true, evidence: ["EV-TXN-3"], first: "2024-03-05", last: "2024-07-18", confidence: 1 },
  { id: "R31", source: "P9", target: "P3", type: "transacted with", category: "financial", documented: true, evidence: ["EV-TXN-3"], first: "2024-03-05", last: "2024-07-18", confidence: 1 },
  { id: "R32", source: "P14", target: "A2", type: "operates", category: "financial", documented: true, evidence: ["EV-TXN-4"], first: "2024-02-20", last: "2024-07-12", confidence: 1 },
  { id: "R33", source: "P14", target: "P2", type: "transacted with", category: "financial", documented: false, evidence: ["EV-TXN-4"], first: "2024-02-20", last: "2024-07-12", confidence: 0.66, reason: "Cash deposits to Coastal Logistics account within 48h of warehouse activity windows." },
  { id: "R34", source: "A1", target: "A2", type: "transacted with", category: "financial", documented: true, evidence: ["EV-TXN-5"], first: "2024-03-15", last: "2024-07-01", confidence: 1 },
  { id: "R35", source: "P3", target: "C3", type: "named in", category: "all", documented: true, evidence: ["EV-FIR-4"], first: "2024-06-10", last: "2024-06-10", confidence: 1 },
  { id: "R36", source: "P16", target: "A5", type: "signatory of", category: "financial", documented: true, evidence: ["EV-TXN-6"], first: "2024-04-01", last: "2024-07-22", confidence: 1 },
  { id: "R37", source: "P16", target: "P1", type: "transacted with", category: "financial", documented: false, evidence: ["EV-TXN-6"], first: "2024-04-01", last: "2024-07-22", confidence: 0.49, reason: "Consultancy invoices to a personal account tied to P1; pattern not yet corroborated." },

  // Urban cluster
  { id: "R38", source: "P7", target: "PH4", type: "registered to", category: "communication", documented: true, evidence: ["EV-CDR-5"], first: "2024-02-05", last: "2024-08-06", confidence: 1 },
  { id: "R39", source: "P7", target: "L5", type: "present at", category: "locations", documented: true, evidence: ["EV-INT-7"], first: "2024-02-10", last: "2024-07-20", confidence: 1 },
  { id: "R40", source: "P8", target: "O4", type: "connected to", category: "organizations", documented: true, evidence: ["EV-INT-8"], first: "2024-03-01", last: "2024-07-15", confidence: 1 },
  { id: "R41", source: "P8", target: "L4", type: "located at", category: "locations", documented: true, evidence: ["EV-INT-8"], first: "2024-03-01", last: "2024-07-15", confidence: 1 },
  { id: "R42", source: "P8", target: "P7", type: "associated with", category: "all", documented: false, evidence: [], first: "2024-03-08", last: "2024-07-01", confidence: 0.51, reason: "Shared location windows at North Market Yard; no direct communication record." },
  { id: "R43", source: "P15", target: "V3", type: "registered to", category: "vehicles", documented: true, evidence: ["EV-VEH-4"], first: "2024-02-18", last: "2024-07-09", confidence: 1 },
  { id: "R44", source: "P15", target: "P7", type: "associated with", category: "all", documented: true, evidence: ["EV-INT-7"], first: "2024-02-18", last: "2024-07-20", confidence: 1 },
  { id: "R45", source: "P11", target: "P8", type: "associated with", category: "all", documented: false, evidence: ["EV-INT-9"], first: "2024-04-10", last: "2024-06-30", confidence: 0.44, reason: "Reported social contact; unverified intelligence note." },

  // Cross-cluster bridges (the interesting ones)
  { id: "R46", source: "P1", target: "P2", type: "called", category: "communication", documented: true, evidence: ["EV-CDR-6"], first: "2024-03-04", last: "2024-07-29", confidence: 1 },
  { id: "R47", source: "P2", target: "P3", type: "transacted with", category: "financial", documented: false, evidence: ["EV-TXN-5"], first: "2024-03-15", last: "2024-07-01", confidence: 0.6, reason: "Coastal Logistics and Zenith accounts share transfer windows aligned with port meetings." },
  { id: "R48", source: "P4", target: "P8", type: "associated with", category: "all", documented: false, evidence: [], first: "2024-04-02", last: "2024-06-15", confidence: 0.47, reason: "Both present at Zenith Office Tower on overlapping dates; no shared record." },
  { id: "R49", source: "P12", target: "O4", type: "connected to", category: "organizations", documented: true, evidence: ["EV-FIR-2"], first: "2024-03-01", last: "2024-07-20", confidence: 1 },
  { id: "R50", source: "P1", target: "P3", type: "transacted with", category: "financial", documented: false, evidence: ["EV-TXN-5"], first: "2024-03-15", last: "2024-07-01", confidence: 0.71, reason: "Strong temporal overlap between P1's port meetings and Zenith account inflows; multiple corroborating signals." },
];

export const EVIDENCE = [
  { id: "EV-FIR-1", kind: "FIR", ref: "FIR-1042", date: "2024-02-14", title: "FIR — Coastal smuggling (excerpt)", status: "documented",
    excerpt: "...named persons Ravi Menon and Vikram Desai were identified during inspection of container cargo at the Coastal Transit Depot on 14 Feb... DEMO content." },
  { id: "EV-FIR-2", ref: "FIR-1187", kind: "FIR", date: "2024-05-12", title: "FIR — Warehouse raid", status: "documented",
    excerpt: "...Vikram Desai and Nadia Joshi listed as directors of Orchid Realty during the raid on the Blue Harbor Warehouse... DEMO content." },
  { id: "EV-FIR-3", ref: "FIR-1187", kind: "FIR", date: "2024-05-12", title: "FIR — Logistics handler named", status: "documented",
    excerpt: "...Imran Qureshi identified as the on-site logistics handler during the warehouse raid... DEMO content." },
  { id: "EV-FIR-4", ref: "FIR-2031", kind: "FIR", date: "2024-06-10", title: "FIR — Parallel financing", status: "documented",
    excerpt: "...Sana Kapoor named as signatory in suspicious transfer pattern under FIR-2031... DEMO content." },
  { id: "EV-CDR-1", kind: "CDR", ref: "CDR-2087", date: "2024-03-04", title: "Call Detail Record — PH1", status: "documented",
    excerpt: "Subscriber +91 98•••• 2210 (DemoCell) placed 14 calls to PH2 between Mar–Jul 2024. DEMO records." },
  { id: "EV-CDR-2", kind: "CDR", ref: "CDR-2088", date: "2024-04-02", title: "Call Detail Record — PH5", status: "documented",
    excerpt: "Subscriber +91 80•••• 4455 contacted multiple urban-cluster numbers on overlapping dates. DEMO records." },
  { id: "EV-CDR-3", kind: "CDR", ref: "CDR-2089", date: "2024-02-20", title: "Call Detail Record — PH2", status: "documented",
    excerpt: "PH2 (Imran Qureshi) shows a recurring evening call pattern to PH6. DEMO records." },
  { id: "EV-CDR-4", kind: "CDR", ref: "CDR-2090", date: "2024-03-15", title: "Call Detail Record — PH3", status: "documented",
    excerpt: "PH3 (Sana Kapoor) contacted PH7 repeatedly around Zenith transfer dates. DEMO records." },
  { id: "EV-CDR-5", kind: "CDR", ref: "CDR-2091", date: "2024-03-08", title: "Call Detail Record — PH4", status: "documented",
    excerpt: "PH4 (Fatima Sheikh) shows short calls to PH8 near North Market Yard. DEMO records." },
  { id: "EV-CDR-6", kind: "CDR", ref: "CDR-2092", date: "2024-03-04", title: "Call Detail Record — P1→P2 bridge", status: "documented",
    excerpt: "Direct calls between PH1 (Ravi Menon) and PH2 (Imran Qureshi) across the full observation window. DEMO records." },
  { id: "EV-TXN-1", kind: "TXN", ref: "TXN-3091", date: "2024-03-15", title: "Transaction — Zenith inflow", status: "documented",
    excerpt: "Acct ••4421 received DEMO ₹ in 6 tranches between Mar–Jul 2024; signatory Sana Kapoor. DEMO records." },
  { id: "EV-TXN-2", kind: "TXN", ref: "TXN-3092", date: "2024-02-01", title: "Transaction — Bookkeeper access", status: "documented",
    excerpt: "Meera Nair operated Acct ••4421 with deposit/withdrawal rights. DEMO records." },
  { id: "EV-TXN-3", kind: "TXN", ref: "TXN-3093", date: "2024-03-05", title: "Transaction — Cross-account", status: "documented",
    excerpt: "Priya Bhatt (Acct ••5567) transferred to Acct ••4421 (Sana Kapoor). DEMO records." },
  { id: "EV-TXN-4", kind: "TXN", ref: "TXN-3094", date: "2024-02-20", title: "Transaction — Coastal deposits", status: "documented",
    excerpt: "Tara Singh made cash deposits to Acct ••8870 (Coastal Logistics) within 48h of warehouse activity. DEMO records." },
  { id: "EV-TXN-5", kind: "TXN", ref: "TXN-3095", date: "2024-03-15", title: "Transaction — Inter-account transfer", status: "documented",
    excerpt: "Transfer from Acct ••4421 (Zenith) to Acct ••8870 (Coastal) aligned with port meeting dates. DEMO records." },
  { id: "EV-TXN-6", kind: "TXN", ref: "TXN-3096", date: "2024-04-01", title: "Transaction — Consultancy invoice", status: "documented",
    excerpt: "Anita Verma raised consultancy invoices to a personal account tied to P1. DEMO records." },
  { id: "EV-VEH-1", kind: "VEH", ref: "VEH-4072", date: "2023-11-02", title: "Vehicle — Registration", status: "documented",
    excerpt: "KA-01 AB 4421 registered to Ravi Menon. DEMO RC record." },
  { id: "EV-VEH-2", kind: "VEH", ref: "VEH-4073", date: "2024-01-20", title: "Vehicle — Cargo van", status: "documented",
    excerpt: "MH-02 CD 8870 registered to Imran Qureshi; logged at Blue Harbor Warehouse. DEMO RC record." },
  { id: "EV-VEH-3", kind: "VEH", ref: "VEH-4074", date: "2024-02-12", title: "Vehicle — Truck", status: "documented",
    excerpt: "GA-03 GH 5567 operated by Arjun Reddy; sighted at Pier 9 Storage. DEMO record." },
  { id: "EV-VEH-4", kind: "VEH", ref: "VEH-4075", date: "2024-02-18", title: "Vehicle — Sedan", status: "documented",
    excerpt: "DL-08 EF 1290 registered to Bilal Khan. DEMO RC record." },
  { id: "EV-INT-1", kind: "INT", ref: "INT-5014", date: "2024-01-20", title: "Intelligence — Harbor meeting", status: "documented",
    excerpt: "Source report places Ravi Menon at the Coastal Transit Depot meeting Blue Harbor Shipping reps. DEMO intelligence." },
  { id: "EV-INT-2", kind: "INT", ref: "INT-5015", date: "2024-04-02", title: "Intelligence — Zenith office", status: "documented",
    excerpt: "Vikram Desai observed at Zenith Office Tower on multiple dates. DEMO intelligence." },
  { id: "EV-INT-3", kind: "INT", ref: "INT-5016", date: "2024-03-12", title: "Intelligence — Depot overlap", status: "inferred",
    excerpt: "Nadia Joshi and Ravi Menon both reported near Coastal Transit Depot; no shared record. DEMO intelligence." },
  { id: "EV-INT-4", kind: "INT", ref: "INT-5017", date: "2024-02-15", title: "Intelligence — Logistics link", status: "documented",
    excerpt: "Imran Qureshi acts as liaison between Coastal Logistics and Meridian Exports. DEMO intelligence." },
  { id: "EV-INT-5", kind: "INT", ref: "INT-5018", date: "2024-03-01", title: "Intelligence — Pier activity", status: "documented",
    excerpt: "Arjun Reddy and Suresh Pillai observed at Pier 9 Storage across multiple nights. DEMO intelligence." },
  { id: "EV-INT-6", kind: "INT", ref: "INT-5019", date: "2024-02-20", title: "Intelligence — Warehouse contact", status: "documented",
    excerpt: "Usman Ali identified as Meridian Exports' warehouse contact at Blue Harbor. DEMO intelligence." },
  { id: "EV-INT-7", kind: "INT", ref: "INT-5020", date: "2024-02-10", title: "Intelligence — Market courier", status: "documented",
    excerpt: "Fatima Sheikh and Bilal Khan linked to North Market Yard courier activity. DEMO intelligence." },
  { id: "EV-INT-8", kind: "INT", ref: "INT-5021", date: "2024-03-01", title: "Intelligence — Realty broker", status: "documented",
    excerpt: "Karan Malhotra brokers Orchid Realty transactions at Orchid Residency. DEMO intelligence." },
  { id: "EV-INT-9", kind: "INT", ref: "INT-5022", date: "2024-04-10", title: "Intelligence — Social contact (unverified)", status: "inferred",
    excerpt: "Reported social contact between Deepak Rao and Karan Malhotra; unverified. DEMO intelligence." },
];

export const TIMELINE_EVENTS = [
  { id: "T1", date: "2024-01-04", kind: "communication", title: "PH1 activated", entities: ["P1", "PH1"], evidence: ["EV-CDR-1"] },
  { id: "T2", date: "2024-02-14", kind: "case", title: "FIR-1042 filed", entities: ["P1", "P4", "C1"], evidence: ["EV-FIR-1"] },
  { id: "T3", date: "2024-03-04", kind: "communication", title: "First P1→P2 call window", entities: ["P1", "P2"], evidence: ["EV-CDR-6"] },
  { id: "T4", date: "2024-03-15", kind: "financial", title: "Zenith → Coastal transfer", entities: ["A1", "A2", "P3"], evidence: ["EV-TXN-5"] },
  { id: "T5", date: "2024-05-12", kind: "case", title: "Warehouse raid (FIR-1187)", entities: ["P2", "P10", "C2"], evidence: ["EV-FIR-2", "EV-FIR-3"] },
  { id: "T6", date: "2024-06-10", kind: "case", title: "FIR-2031 — parallel financing", entities: ["P3", "C3"], evidence: ["EV-FIR-4"] },
  { id: "T7", date: "2024-06-18", kind: "movement", title: "P1 present at Coastal Depot", entities: ["P1", "L6"], evidence: ["EV-INT-1"] },
  { id: "T8", date: "2024-07-01", kind: "financial", title: "Final inter-account transfer", entities: ["A1", "A2"], evidence: ["EV-TXN-5"] },
  { id: "T9", date: "2024-07-15", kind: "movement", title: "Karan at Orchid Residency", entities: ["P8", "L4"], evidence: ["EV-INT-8"] },
  { id: "T10", date: "2024-07-22", kind: "financial", title: "Consultancy invoice (Anita)", entities: ["P16", "A5"], evidence: ["EV-TXN-6"] },
  { id: "T11", date: "2024-07-29", kind: "communication", title: "Last P1→P2 call", entities: ["P1", "P2"], evidence: ["EV-CDR-6"] },
  { id: "T12", date: "2024-08-12", kind: "communication", title: "PH1 last activity", entities: ["P1", "PH1"], evidence: ["EV-CDR-1"] },
];

export const LEADS = [
  {
    id: "LD1", title: "Unexplained P1 ↔ P3 financial bridge",
    status: "new", documented: false, confidence: 0.71, priority: "high",
    entities: ["P1", "P3", "A1", "A2"],
    evidence: ["EV-TXN-5", "EV-CDR-6"],
    why: [
      "P1's port meetings (EV-INT-1) align temporally with Zenith account inflows (EV-TXN-1).",
      "Inter-account transfer A1→A2 (EV-TXN-5) coincides with P1→P2 call windows (EV-CDR-6).",
      "No direct record links P1 to P3; connection is inferred from overlapping signals.",
    ],
    nextStep: "Request CDR cross-reference for PH1↔PH3 and statement analysis for Acct ••4421 signatories.",
  },
  {
    id: "LD2", title: "Cash deposits timed to warehouse activity",
    status: "reviewing", documented: false, confidence: 0.66, priority: "high",
    entities: ["P14", "P2", "A2"],
    evidence: ["EV-TXN-4"],
    why: [
      "Tara Singh's cash deposits to Coastal Logistics account cluster within 48h of warehouse activity windows.",
      "Imran Qureshi is the named on-site handler (EV-FIR-3).",
    ],
    nextStep: "Map deposit timestamps against CCTV availability at Blue Harbor Warehouse.",
  },
  {
    id: "LD3", title: "Possible P2 ↔ P3 financial link",
    status: "new", documented: false, confidence: 0.6, priority: "medium",
    entities: ["P2", "P3", "A1", "A2"],
    evidence: ["EV-TXN-5"],
    why: [
      "Coastal Logistics and Zenith accounts share transfer windows aligned with port meetings.",
      "No direct communication record between P2 and P3.",
    ],
    nextStep: "Trace intermediary signatories and reconcile invoice narratives.",
  },
  {
    id: "LD4", title: "Nadia Joshi — depot overlap with P1",
    status: "verified", documented: false, confidence: 0.62, priority: "medium",
    entities: ["P12", "P1", "L6"],
    evidence: ["EV-INT-3"],
    why: [
      "Both reported near Coastal Transit Depot on overlapping dates.",
      "Shared associate P4 (Vikram Desai) connects both clusters.",
    ],
    nextStep: "Confirm dates via additional surveillance reports; already partially corroborated.",
  },
  {
    id: "LD5", title: "Urban–finance bridge via Karan Malhotra",
    status: "new", documented: false, confidence: 0.51, priority: "low",
    entities: ["P8", "P4", "L3", "O4"],
    evidence: ["EV-INT-2", "EV-INT-8"],
    why: [
      "Vikram Desai and Karan Malhotra both present at Zenith Office Tower on overlapping dates.",
      "Orchid Realty connects P12 and P8 (EV-FIR-2).",
    ],
    nextStep: "Identify whether Malhotra brokered any Zenith-linked property transactions.",
  },
  {
    id: "LD6", title: "Documented: P1 named in FIR-1042",
    status: "verified", documented: true, confidence: 1, priority: "info",
    entities: ["P1", "P4", "C1"],
    evidence: ["EV-FIR-1"],
    why: ["Directly supported by source record FIR-1042."],
    nextStep: "No action — established fact within the demo dataset.",
  },
  {
    id: "LD7", title: "Anita Verma consultancy invoices to P1-linked account",
    status: "dismissed", documented: false, confidence: 0.49, priority: "low",
    entities: ["P16", "P1", "A5"],
    evidence: ["EV-TXN-6"],
    why: [
      "Consultancy invoices to a personal account tied to P1; pattern not yet corroborated.",
      "Dismissed pending legitimate-business explanation (reviewed by Demo Investigator).",
    ],
    nextStep: "Re-open only if corroborating financial signals emerge.",
  },
];

export const NOTES = [
  { id: "N1", scope: "entity:P1", author: "Demo Investigator", ts: "2024-08-20T10:12:00Z", text: "P1 appears to be the central coordinator. Verify travel records next.", pinned: true },
  { id: "N2", scope: "relationship:R50", author: "Demo Investigator", ts: "2024-08-21T09:30:00Z", text: "Strongest inferred link in the dataset. Multiple corroborating signals.", pinned: false },
  { id: "N3", scope: "evidence:EV-TXN-5", author: "Demo Investigator", ts: "2024-08-21T11:02:00Z", text: "Transfer timing is the key corroborator for LD1.", pinned: false },
];

export const RECENTLY_VIEWED = ["P1", "P2", "R50", "EV-TXN-5", "P3"];
export const PINNED = ["inv-monsoon", "inv-harbor"];
export const SAVED_LEADS = ["LD1", "LD4"];