const defaultConfig = {
  trending_region: "united_states",
  videos_per_day: 4,
  output_dir: "output",
  assets_dir: "assets",
  youtube_category_id: "23",
  tags: ["shorts", "cartoon", "comedy"],
  video_title_template: "{topic} - Cartoon Comedy Short",
  video_description_template: "A quick cartoon short riffing on {topic}. Script: {script}",
  youtube_privacy_status: "private",
  youtube_client_secrets_file: "credentials/client_secret.json",
  youtube_token_file: "credentials/token.json",
  background_music_file: ""
};

const formatJson = (value) => JSON.stringify(value, null, 2);

const form = document.getElementById("config-form");
const preview = document.getElementById("config-preview");
const lastUpdated = document.getElementById("last-updated");
const videosQueued = document.getElementById("videos-queued");
const topicsAnalysed = document.getElementById("topics-analysed");
const uploadsComplete = document.getElementById("uploads-complete");
const statusPill = document.getElementById("status-pill");
const downloadButtons = [
  document.getElementById("download-config"),
  document.getElementById("download-config-secondary")
].filter(Boolean);
const copyConfigButton = document.getElementById("copy-config");
const copyCommandButton = document.getElementById("copy-command");
const commandButtons = Array.from(document.querySelectorAll(".command-card button"));
const primaryCommandEl = document.getElementById("primary-command");
const dryRunCommandEl = document.getElementById("dry-run-command");
const topicCommandEl = document.getElementById("topic-command");

const setCurrentYear = () => {
  const el = document.getElementById("current-year");
  if (el) {
    el.textContent = new Date().getFullYear();
  }
};

const populateForm = (config) => {
  form.trending_region.value = config.trending_region;
  form.videos_per_day.value = config.videos_per_day;
  form.output_dir.value = config.output_dir;
  form.assets_dir.value = config.assets_dir;
  form.youtube_category_id.value = config.youtube_category_id;
  form.tags.value = config.tags.join(", ");
  form.youtube_client_secrets_file.value = config.youtube_client_secrets_file;
  form.youtube_token_file.value = config.youtube_token_file;
  form.youtube_privacy_status.value = config.youtube_privacy_status;
  form.video_title_template.value = config.video_title_template;
  form.video_description_template.value = config.video_description_template;
  form.background_music_file.value = config.background_music_file;
};

const normalisePath = (value) => value.trim().replace(/\\/g, "/");

const generateConfig = () => {
  const videosPerDay = Math.max(1, Number(form.videos_per_day.value) || defaultConfig.videos_per_day);
  const tags = form.tags.value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);

  const config = {
    trending_region: form.trending_region.value.trim() || defaultConfig.trending_region,
    videos_per_day: videosPerDay,
    output_dir: normalisePath(form.output_dir.value) || defaultConfig.output_dir,
    assets_dir: normalisePath(form.assets_dir.value) || defaultConfig.assets_dir,
    youtube_category_id: form.youtube_category_id.value.trim() || defaultConfig.youtube_category_id,
    tags: tags.length ? tags : [...defaultConfig.tags],
    video_title_template: form.video_title_template.value.trim() || defaultConfig.video_title_template,
    video_description_template:
      form.video_description_template.value.trim() || defaultConfig.video_description_template,
    youtube_privacy_status:
      form.youtube_privacy_status.value || defaultConfig.youtube_privacy_status,
    youtube_client_secrets_file:
      normalisePath(form.youtube_client_secrets_file.value) || defaultConfig.youtube_client_secrets_file,
    youtube_token_file:
      normalisePath(form.youtube_token_file.value) || defaultConfig.youtube_token_file,
    background_music_file: form.background_music_file.value.trim()
      ? normalisePath(form.background_music_file.value)
      : null
  };

  return config;
};

const updateDashboard = (config) => {
  if (videosQueued) {
    videosQueued.textContent = config.videos_per_day;
  }
  if (topicsAnalysed) {
    const estimated = Math.max(config.videos_per_day * 3, 12);
    topicsAnalysed.textContent = estimated;
  }
  if (uploadsComplete) {
    uploadsComplete.textContent = 0;
  }
  if (statusPill) {
    const statusMap = {
      private: "Uploads saved as Private",
      unlisted: "Uploads shared as Unlisted",
      public: "Uploads published instantly"
    };
    statusPill.textContent = statusMap[config.youtube_privacy_status] || "Ready for launch";
  }
};

const updateCommands = (config) => {
  const baseCommand = "python -m automation.main --config config.json";
  const countCommand = config.videos_per_day !== defaultConfig.videos_per_day
    ? `${baseCommand} --count ${config.videos_per_day}`
    : baseCommand;
  primaryCommandEl.textContent = countCommand;
  dryRunCommandEl.textContent = `${baseCommand} --dry-run`;
  topicCommandEl.textContent = `${baseCommand} --topic \"Space Tourism\"`;
};

const refreshPreview = () => {
  const config = generateConfig();
  preview.textContent = formatJson(config);
  lastUpdated.textContent = `Updated ${new Date().toLocaleTimeString()}`;
  updateDashboard(config);
  updateCommands(config);
};

const downloadConfig = () => {
  const config = generateConfig();
  const blob = new Blob([formatJson(config)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "config.json";
  document.body.appendChild(link);
  link.click();
  URL.revokeObjectURL(link.href);
  document.body.removeChild(link);
};

const copyToClipboard = async (text, button) => {
  try {
    await navigator.clipboard.writeText(text);
    if (button) {
      const original = button.textContent;
      button.textContent = "Copied!";
      button.disabled = true;
      setTimeout(() => {
        button.textContent = original;
        button.disabled = false;
      }, 1600);
    }
  } catch (error) {
    console.error("Clipboard copy failed", error);
  }
};

form.addEventListener("submit", (event) => {
  event.preventDefault();
  refreshPreview();
});

document.getElementById("reset-config").addEventListener("click", () => {
  populateForm(defaultConfig);
  refreshPreview();
});

downloadButtons.forEach((button) => {
  button.addEventListener("click", downloadConfig);
});

if (copyConfigButton) {
  copyConfigButton.addEventListener("click", () => copyToClipboard(preview.textContent, copyConfigButton));
}

if (copyCommandButton) {
  copyCommandButton.addEventListener("click", () => copyToClipboard(primaryCommandEl.textContent, copyCommandButton));
}

commandButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const targetId = button.getAttribute("data-command");
    const commandElement = document.getElementById(targetId);
    if (commandElement) {
      copyToClipboard(commandElement.textContent, button);
    }
  });
});

form.addEventListener("input", () => {
  refreshPreview();
});

setCurrentYear();
populateForm(defaultConfig);
refreshPreview();
