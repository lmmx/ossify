const $ = s => document.querySelector(s);

let ALL = [];
let grid;

function fmtAge(iso) {
  if (!iso) return "—";
  const days = Math.floor((Date.now() - new Date(iso)) / 86400000);
  if (days < 1) return "today";
  if (days < 30) return `${days}d`;
  if (days < 365) return `${Math.floor(days / 30)}mo`;
  return `${(days / 365).toFixed(1)}y`;
}

function stateBadges(r) {
  const b = [];
  if (r.archived) b.push(`<span class="badge b-archived">archived</span>`);
  if (r.state_failing) b.push(`<span class="badge b-failing">failing</span>`);
  if (r.state_unmaintained) b.push(`<span class="badge b-zombie">unmaintained</span>`);
  if (r.state_inactive) b.push(`<span class="badge b-inactive">inactive</span>`);
  if (r.state_ok && b.length === 0) b.push(`<span class="badge b-ok">ok</span>`);
  return b.join(" ");
}

function filtered() {
  const hideArchived = $("#hide-archived").checked;
  const hideOk = $("#hide-ok").checked;
  const onlyFailing = $("#only-failing").checked;
  const onlyPriority = $("#only-priority").checked;
  return ALL.filter(r => {
    if (hideArchived && r.archived) return false;
    if (hideOk && r.state_ok) return false;
    if (onlyFailing && !r.state_failing) return false;
    if (onlyPriority && !r.priority) return false;
    return true;
  });
}

function row(r) {
  return [
    r.priority ? "★" : "",
    r.url ? `<a href="${r.url}" target="_blank">${r.owner}/${r.name}</a>` : `${r.owner}/${r.name}`,
    r.packages.join(", "),
    stateBadges(r),
    fmtAge(r.last_commit_at),
    fmtAge(r.last_human_commit_at),
    r.human_ratio_window == null ? "—" : (r.human_ratio_window * 100).toFixed(0) + "%",
    r.version_count,
    fmtAge(r.last_release_at),
    r.release_cadence_days == null ? "—" : Math.round(r.release_cadence_days) + "d",
    r.has_tests ? "✓" : "",
    r.has_ci ? "✓" : "",
    r.ci_runs_tests ? "✓" : "",
    r.precommit_configured ? "✓" : "",
    r.publish_mode,
    r.publish_auth,
    r.bots.join(", "),
    r.build_system,
    r.drift_pdm_to_uv ? "PDM→uv" : "",
    r.drift_token_to_trusted ? "token→TP" : "",
    r.readme_badges,
  ].map(c => ({ data: c, formatted: typeof c === "string" && c.includes("<") ? gridjs.html(c) : c }));
}

async function init() {
  const j = await (await fetch("data.json")).json();
  ALL = j.repos;
  $("#stats").textContent = `${ALL.length} repos · generated ${new Date(j.generated_at).toLocaleString()}`;

  grid = new gridjs.Grid({
    columns: [
      "★", "Repo", "Packages", "State",
      "Last commit", "Last human", "Human %",
      "Versions", "Last release", "Cadence",
      "Tests", "CI", "CI tests", "pre-commit",
      "Publish", "Auth", "Bots", "Build",
      "PDM drift", "Token drift", "Badges",
    ],
    data: () => filtered().map(row).map(cells => cells.map(c => c.formatted ?? c.data)),
    sort: true,
    resizable: true,
    search: true,
    pagination: { limit: 100 },
  }).render($("#table"));

  for (const id of ["hide-archived", "hide-ok", "only-failing", "only-priority"]) {
    $("#" + id).onchange = () => grid.forceRender();
  }
}

init();
