// Layout + graph math utilities for the C.I.D. knowledge graph.

export const ENTITY_META = {
  person:       { label: "Person",         color: "var(--c-person)",       icon: "User" },
  phone:        { label: "Phone",          color: "var(--c-phone)",        icon: "Phone" },
  vehicle:      { label: "Vehicle",        color: "var(--c-vehicle)",      icon: "Car" },
  location:     { label: "Location",       color: "var(--c-location)",     icon: "MapPin" },
  organization: { label: "Organization",   color: "var(--c-organization)",  icon: "Building2" },
  case:         { label: "Case",           color: "var(--c-case)",          icon: "FolderArchive" },
  account:      { label: "Account",        color: "var(--c-account)",       icon: "Landmark" },
  event:        { label: "Event",           color: "var(--c-event)",        icon: "CalendarClock" },
};

export function entityColor(type) {
  return ENTITY_META[type]?.color ?? "var(--muted-foreground)";
}

// Deterministic cluster layout. Nodes carry a `cluster` id; clusters are
// arranged on a large circle, nodes within each cluster on a smaller circle.
export function computeLayout(nodes, relationships, width = 1100, height = 820) {
  const clusters = {};
  nodes.forEach((n) => {
    const c = n.cluster ?? "core";
    (clusters[c] = clusters[c] || []).push(n);
  });
  const clusterIds = Object.keys(clusters);
  const cx = width / 2;
  const cy = height / 2;
  const clusterRadius = Math.min(width, height) * 0.34;
  const positions = {};

  clusterIds.forEach((cid, i) => {
    const angle = (i / clusterIds.length) * Math.PI * 2 - Math.PI / 2;
    const ccx = cx + Math.cos(angle) * clusterRadius;
    const ccy = cy + Math.sin(angle) * clusterRadius;
    const members = clusters[cid];
    members.forEach((n, j) => {
      if (members.length === 1) {
        positions[n.id] = { x: ccx, y: ccy };
      } else {
        const r = 70 + Math.min(members.length, 6) * 12;
        const a = (j / members.length) * Math.PI * 2;
        positions[n.id] = { x: ccx + Math.cos(a) * r, y: ccy + Math.sin(a) * r };
      }
    });
  });
  return positions;
}

// Adjacency helpers
export function buildAdjacency(nodes, relationships) {
  const adj = {};
  nodes.forEach((n) => { adj[n.id] = new Set(); });
  relationships.forEach((r) => {
    if (adj[r.source]) adj[r.source].add(r.target);
    if (adj[r.target]) adj[r.target].add(r.source);
  });
  return adj;
}

export function degree(nodeId, adj) {
  return adj[nodeId] ? adj[nodeId].size : 0;
}

// BFS shortest paths between two nodes (returns array of paths, max depth).
export function findPaths(nodes, relationships, sourceId, targetId, maxDepth = 5, maxResults = 6) {
  if (!sourceId || !targetId || sourceId === targetId) return [];
  const adj = buildAdjacency(nodes, relationships);
  const relMap = {};
  relationships.forEach((r) => {
    const k = `${r.source}|${r.target}`;
    relMap[k] = r;
    relMap[`${r.target}|${r.source}`] = r;
  });
  const results = [];
  const queue = [[sourceId, [sourceId]]];
  const visitedTopDepth = new Map();
  while (queue.length && results.length < maxResults) {
    const [cur, path] = queue.shift();
    const depth = path.length - 1;
    if (depth > maxDepth) continue;
    if (cur === targetId) {
      results.push(path.slice());
      continue;
    }
    const seen = visitedTopDepth.get(cur) ?? Infinity;
    if (depth >= seen) continue;
    visitedTopDepth.set(cur, depth);
    const neighbors = adj[cur] ? Array.from(adj[cur]) : [];
    for (const nb of neighbors) {
      if (path.includes(nb)) continue;
      queue.push([nb, [...path, nb]]);
    }
  }
  // convert node-id paths to {node, relationship} step lists
  return results.map((path) =>
    path.slice(1).map((nid, i) => ({
      from: path[i],
      to: nid,
      relationship: relMap[`${path[i]}|${nid}`],
    }))
  );
}

// Network metrics for disruption simulator
export function connectedComponents(nodeIds, adj) {
  const seen = new Set();
  const comps = [];
  for (const id of nodeIds) {
    if (seen.has(id)) continue;
    const stack = [id];
    const comp = [];
    while (stack.length) {
      const cur = stack.pop();
      if (seen.has(cur)) continue;
      seen.add(cur);
      comp.push(cur);
      (adj[cur] || new Set()).forEach((n) => {
        if (nodeIds.includes(n) && !seen.has(n)) stack.push(n);
      });
    }
    comps.push(comp);
  }
  return comps;
}

export function disruptionMetrics(nodes, relationships, removedIds) {
  const removed = new Set(removedIds);
  const remaining = nodes.filter((n) => !removed.has(n.id)).map((n) => n.id);
  const adj = {};
  remaining.forEach((id) => { adj[id] = new Set(); });
  let affectedRels = 0;
  let remainingRels = 0;
  relationships.forEach((r) => {
    if (removed.has(r.source) || removed.has(r.target)) {
      affectedRels++;
    } else {
      remainingRels++;
      adj[r.source]?.add(r.target);
      adj[r.target]?.add(r.source);
    }
  });
  const comps = connectedComponents(remaining, adj);
  const originalComps = connectedComponents(
    nodes.map((n) => n.id),
    buildAdjacency(nodes, relationships)
  );
  return {
    remainingEntities: remaining.length,
    removedEntities: removed.size,
    remainingRelationships: remainingRels,
    affectedRelationships: affectedRels,
    connectedComponents: comps.length,
    originalComponents: originalComps.length,
    disconnectedClusters: comps.filter((c) => c.length > 0).length,
    largestComponent: Math.max(0, ...comps.map((c) => c.length)),
  };
}