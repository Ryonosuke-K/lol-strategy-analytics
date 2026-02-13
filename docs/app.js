(function () {
  function fmt(value, suffix) {
    if (value === null || value === undefined) return "N/A";
    return String(value) + (suffix || "");
  }

  function metricCard(title, value) {
    return '<article class="metric"><h3>' + title + "</h3><p>" + value + "</p></article>";
  }

  function renderHome(snapshot) {
    var sample = snapshot.sample || {};
    var objA = (snapshot.objective_value || {}).three_grubs_one_or_less_dragon || {};
    var objB = (snapshot.objective_value || {}).two_or_more_dragons_one_or_less_grub || {};
    var climber = snapshot.climber_traits || {};

    var meta = document.getElementById("snapshot-meta");
    var kpis = document.getElementById("snapshot-home-kpis");
    if (!meta || !kpis) return;

    meta.innerHTML =
      metricCard("Updated", snapshot.generated_at_utc || "N/A") +
      metricCard("Matches", fmt(sample.matches_analyzed)) +
      metricCard("Players", fmt(sample.challenger_players));

    kpis.innerHTML =
      metricCard("Dragon-Heavy Win Rate", fmt(objB.win_rate_percent, "%")) +
      metricCard("Grub-Heavy Win Rate", fmt(objA.win_rate_percent, "%")) +
      metricCard("Climber Sample Win Rate", fmt(climber.win_rate_percent, "%"));
  }

  function renderAnalysis1(snapshot) {
    var sample = snapshot.sample || {};
    var objA = (snapshot.objective_value || {}).three_grubs_one_or_less_dragon || {};
    var objB = (snapshot.objective_value || {}).two_or_more_dragons_one_or_less_grub || {};
    var objective = document.getElementById("snapshot-objective");
    var objectiveSummary = document.getElementById("objective-summary");
    if (!objective) return;

    var delta = null;
    if (objA.win_rate_percent !== null && objA.win_rate_percent !== undefined &&
        objB.win_rate_percent !== null && objB.win_rate_percent !== undefined) {
      delta = (objB.win_rate_percent - objA.win_rate_percent).toFixed(2);
    }

    objective.innerHTML =
      metricCard("Matches Analyzed", fmt(sample.matches_analyzed)) +
      metricCard("3+ Grubs and <=1 Dragon", fmt(objA.win_rate_percent, "%")) +
      metricCard(">=2 Dragons and <=1 Grub", fmt(objB.win_rate_percent, "%")) +
      metricCard("Win Rate Gap (Dragon - Grub)", delta === null ? "N/A" : delta + "%");

    if (objectiveSummary) {
      objectiveSummary.textContent =
        delta === null
          ? "Dummy interpretation: this sample is exploratory and requires broader segmentation."
          : "Dummy interpretation: dragon-heavy segments currently lead by " +
            delta + " percentage points, subject to further SQL segmentation.";
    }
  }

  function renderAnalysis2(snapshot) {
    var climber = snapshot.climber_traits || {};
    var climberNode = document.getElementById("snapshot-climber");
    var climberSummary = document.getElementById("climber-summary");
    if (!climberNode) return;

    climberNode.innerHTML =
      metricCard("Sample Win Rate", fmt(climber.win_rate_percent, "%")) +
      metricCard("Avg Vision Score", fmt(climber.avg_vision_score)) +
      metricCard("Avg Control Wards", fmt(climber.avg_control_wards_bought)) +
      metricCard("Avg Deaths", fmt(climber.avg_deaths));

    if (climberSummary) {
      climberSummary.textContent =
        "Dummy interpretation: this profile suggests vision-first behavior with controlled risk, to be validated by role and patch slices in SQL.";
    }
  }

  function renderAnalysis3(snapshot) {
    var sample = snapshot.sample || {};
    var meta = document.getElementById("snapshot-meta");
    if (!meta) return;

    meta.innerHTML =
      metricCard("Snapshot Time", snapshot.generated_at_utc || "N/A") +
      metricCard("Sample Matches", fmt(sample.matches_analyzed)) +
      metricCard("Sample Rows", fmt(sample.player_match_rows));
  }

  fetch("./data/live-snapshot.json", { cache: "no-store" })
    .then(function (r) { return r.json(); })
    .then(function (snapshot) {
      var page = document.body.getAttribute("data-page");
      if (page === "analysis1") {
        renderAnalysis1(snapshot);
      } else if (page === "analysis2") {
        renderAnalysis2(snapshot);
      } else if (page === "analysis3") {
        renderAnalysis3(snapshot);
      } else {
        renderHome(snapshot);
      }
    })
    .catch(function () {
      var meta = document.getElementById("snapshot-meta");
      if (meta) {
        meta.innerHTML = metricCard("Snapshot Error", "Run: python generate_snapshot.py");
      }
    });
})();
