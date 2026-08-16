import CONFIG from "./config.js";

const $ = (id) => document.getElementById(id);

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function formatMoney(value) {
  if (value === null || value === undefined || value === "") return "Price on request";
  const num = Number(value);
  if (Number.isNaN(num)) return String(value);
  return "£" + num.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

function formatClock(totalSeconds) {
  const mins = Math.floor(totalSeconds / 60);
  const secs = Math.floor(totalSeconds % 60);
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function formatDateTime(value) {
  if (!value) return "TBC";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const AGENT_STATUS_COPY = {
  idle: ["Ready when you are", "Nova will greet you as soon as you connect."],
  listening: ["Listening", "Tell me what you're looking for."],
  thinking: ["Thinking", "Nova is putting together a reply."],
  speaking: ["Speaking", "Nova is talking — feel free to jump in."],
  searching: ["Searching listings", "Nova is checking the database for matches."],
  comparing: ["Comparing properties", "Nova is lining up the details side by side."],
  scheduling: ["Scheduling your visit", "Nova is booking the viewing."],
  analyzing: ["Wrapping up", "Nova is preparing your call summary."],
  finished: ["Call finished", "Thanks for talking with Nova."],
};

const ORB_STATE_MAP = {
  idle: "idle",
  listening: "listening",
  thinking: "thinking",
  speaking: "speaking",
  searching: "tool",
  comparing: "tool",
  scheduling: "tool",
  analyzing: "tool",
  finished: "idle",
};


class VoiceAgent {
  constructor() {
    this.pc = null;
    this.dataChannel = null;
    this.localStream = null;
    this.remoteStream = new MediaStream();

    this.callStartTime = null;
    this.timerInterval = null;

    this.isMuted = false;
    this.isConnected = false;
    this.isConnecting = false;

    this.transcriptOrder = [];
    this.transcriptById = new Map();
    this.interimMessagesById = new Map();
    this.properties = new Map();
    this.activityLog = [];
    this.booking = null;
    this.report = null;
    this.sessionId = null;

    this.initializeUI();
  }


  initializeUI() {
    this.appEl = $("app");

    this.callBtn = $("call-btn");
    this.callBtnLabel = $("call-btn-label");
    this.muteBtn = $("mute-btn");
    this.reconnectBtn = $("reconnect-btn");

    this.connBadge = $("conn-badge");
    this.connLabel = $("conn-label");
    this.timerEl = $("timer");

    this.orb = $("site-plan-wrap");
    this.agentStatusEl = $("agent-status");
    this.agentSubstatusEl = $("agent-substatus");

    this.transcriptEl = $("transcript");
    this.transcriptEmpty = $("transcript-empty");
    this.transcriptPanel = $("panel-transcript"); 

    this.propertiesEl = $("properties");
    this.propertiesEmpty = $("properties-empty");
    this.propertiesCountBadge = $("properties-count");
    this.propertiesPanel = $("panel-properties");
    this.propertiesToolbar = $("properties-toolbar");
    this.propertiesTotalEl = $("properties-total");
    this.propertiesSortEl = $("properties-sort");
    this.propertiesSortKey = "recommended";

    this.activityEl = $("activity");
    this.activityEmpty = $("activity-empty");
    this.activityPanel = $("panel-activity")
    this.bookingCard = $("booking-card");

    this.summaryOverlay = $("summary-overlay");
    this.summaryBody = $("summary-body");
    this.summaryDuration = $("summary-duration");

    this.toastEl = $("toast");
    this.remoteAudio = $("remoteAudio");
    this.propertyModalOverlay = $("property-modal-overlay");
    this.propertyModalBody = $("modal-property-body");
    this.propertyModalTitle = $("modal-property-title");
    this.propertyModalLocation = $("modal-property-location");
    this.modalExternalLink = $("modal-external-link");
    this.modalCloseBtn = $("modal-close-btn");
    this.modalBackBtn = $("modal-back-btn");

    this.callBtn.addEventListener("click", () => this.handleCallButton());
    this.muteBtn.addEventListener("click", () => this.toggleMute());
    this.reconnectBtn.addEventListener("click", () => this.startConversation());
    $("new-call-btn").addEventListener("click", () => this.resetForNewCall());
    $("download-summary-btn").addEventListener("click", () => this.downloadSummary());
    this.modalCloseBtn.addEventListener("click", () => this.closePropertyModal());
    this.modalBackBtn.addEventListener("click", () => this.closePropertyModal());
    this.propertyModalOverlay.addEventListener("click", (event) => {
      if (event.target === this.propertyModalOverlay) this.closePropertyModal();
    });

    document.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", () => this.switchTab(tab.dataset.tab));
    });

    this.propertiesSortEl.addEventListener("change", () => {
      this.propertiesSortKey = this.propertiesSortEl.value;
      this.rebuildPropertiesTab();
    });

    this.setAgentState("idle");
  }

  switchTab(name) {
    document.querySelectorAll(".tab").forEach((t) => {
      const active = t.dataset.tab === name;
      t.classList.toggle("active", active);
      t.setAttribute("aria-selected", String(active));
    });
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.toggle("active", p.id === `panel-${name}`));
  }

  showToast(message, tone = "info") {
    this.toastEl.textContent = message;
    this.toastEl.dataset.tone = tone;
    this.toastEl.hidden = false;
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => {
      this.toastEl.hidden = true;
    }, 4000);
  }

  handleCallButton() {
    if (this.isConnected) {
      this.endConversation();
    } else if (!this.isConnecting) {
      this.startConversation();
    }
  }

  async getMicrophone() {
    try {
      this.localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      return true;
    } catch (err) {
      console.error(err);
      this.showToast("Please allow microphone access to start a call.", "error");
      return false;
    }
  }

  async createPeerConnection() {
    this.pc = new RTCPeerConnection({ iceServers: CONFIG.ICE_SERVERS });

    this.dataChannel = this.pc.createDataChannel("pipecat");
    this.dataChannel.onmessage = (event) => this.handleDataChannelMessage(event.data);
    this.dataChannel.onopen = () => console.log("Data channel open");
    this.dataChannel.onerror = (e) => console.warn("Data channel error", e);

    this.localStream.getTracks().forEach((track) => {
      this.pc.addTrack(track, this.localStream);
    });

    this.pc.ontrack = (event) => {
      event.streams[0].getTracks().forEach((track) => this.remoteStream.addTrack(track));
      this.remoteAudio.srcObject = this.remoteStream;
      this.remoteAudio.play().catch(() => {});
    };

    this.pc.onconnectionstatechange = () => {
      const state = this.pc.connectionState;

      if (state === "failed" || state === "closed") {
        clearTimeout(this._disconnectGraceTimer);
        if (this.isConnected) this.handleUnexpectedDisconnect();
        return;
      }

      if (state === "disconnected") {
        if (!this._disconnectGraceTimer) {
          this._disconnectGraceTimer = setTimeout(() => {
            this._disconnectGraceTimer = null;
            if (this.isConnected && this.pc && this.pc.connectionState === "disconnected") {
              this.handleUnexpectedDisconnect();
            }
          }, 6000);
        }
        return;
      }


      if (state === "connected") {
        clearTimeout(this._disconnectGraceTimer);
        this._disconnectGraceTimer = null;
      }
    };
  }

  async startConversation() {
    if (this.isConnected || this.isConnecting) return;
    this.isConnecting = true;
    this.reconnectBtn.hidden = true;

    this.setConnBadge("connecting", "Connecting…");
    this.callBtnLabel.textContent = "Connecting…";
    this.callBtn.disabled = true;

    const micGranted = await this.getMicrophone();
    if (!micGranted) {
      this.isConnecting = false;
      this.resetUI();
      return;
    }

    await this.createPeerConnection();
    await this.performHandshake();
  }

  async performHandshake() {
    try {
      const offer = await this.pc.createOffer({ offerToReceiveAudio: true });
      await this.pc.setLocalDescription(offer);

      const response = await fetch(CONFIG.BACKEND_URL + CONFIG.OFFER_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sdp: offer.sdp, type: offer.type }),
      });

      if (!response.ok) throw new Error(`Backend handshake failed (${response.status}).`);

      const answer = await response.json();
      await this.pc.setRemoteDescription(new RTCSessionDescription({ sdp: answer.sdp, type: answer.type }));

      this.connectionEstablished();
    } catch (err) {
      console.error(err);
      this.showToast("Couldn't connect to Nova. Please try again.", "error");
      this.setConnBadge("failed", "Connection failed");
      this.isConnecting = false;
      this.resetUI();
    }
  }

  connectionEstablished() {
    this.isConnecting = false;
    this.isConnected = true;
    this.callStartTime = Date.now();
    this.startTimer();

    this.callBtn.disabled = false;
    this.callBtn.classList.add("is-ending");
    this.callBtnLabel.textContent = "End call";
    this.muteBtn.disabled = false;

    this.setConnBadge("connected", "Connected");
    this.setAgentState("listening");
  }

  handleUnexpectedDisconnect() {
    this.showToast("The call was disconnected.", "error");
    this.endConversation({ unexpected: true });
  }

  async endConversation() {
    const hadReport = !!this.report;

    clearTimeout(this._disconnectGraceTimer);
    this._disconnectGraceTimer = null;

    if (this.dataChannel) {
      try { this.dataChannel.close(); } catch (e) {}
      this.dataChannel = null;
    }
    if (this.pc) {
      this.pc.close();
      this.pc = null;
    }
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
    this.remoteAudio.srcObject = null;
    clearInterval(this.timerInterval);

    const durationSeconds = this.callStartTime ? Math.floor((Date.now() - this.callStartTime) / 1000) : 0;

    this.resetUI();
    this.setConnBadge("disconnected", "Not connected");
    this.setAgentState("finished");

    if (durationSeconds > 0) {
      this.showSummaryOverlay(durationSeconds, hadReport);
    }
  }

  resetUI() {
    this.isConnected = false;
    this.isConnecting = false;

    this.callBtn.disabled = false;
    this.callBtn.classList.remove("is-ending");
    this.callBtnLabel.textContent = "Start call";

    this.muteBtn.disabled = true;
    this.muteBtn.classList.remove("is-active");
    this.muteBtn.querySelector("span").textContent = "Mute";
    this.isMuted = false;

    this.timerEl.textContent = "00:00";
  }

  resetForNewCall() {
    this.summaryOverlay.hidden = true;

    this.transcriptOrder = [];
    this.transcriptById.clear();
    this.properties.clear();
    this.activityLog = [];
    this.booking = null;
    this.report = null;
    this.sessionId = null;

    this.transcriptEl.innerHTML = "";
    this.transcriptEl.appendChild(this.transcriptEmpty);
    this.transcriptEmpty.hidden = false;

    this.propertiesEl.innerHTML = "";
    this.propertiesEl.appendChild(this.propertiesEmpty);
    this.propertiesEmpty.hidden = false;
    this.propertiesCountBadge.hidden = true;
    this.propertiesToolbar.hidden = true;
    this.propertiesSortEl.value = "recommended";
    this.propertiesSortKey = "recommended";

    this.activityEl.innerHTML = "";
    this.activityEl.appendChild(this.activityEmpty);
    this.activityEmpty.hidden = false;

    this.bookingCard.hidden = true;
    this.bookingCard.innerHTML = "";

    this.switchTab("transcript");
    this.setAgentState("idle");
    this.setConnBadge("disconnected", "Not connected");
  }

  toggleMute() {
    if (!this.localStream) return;
    this.isMuted = !this.isMuted;
    this.localStream.getAudioTracks().forEach((track) => (track.enabled = !this.isMuted));
    this.muteBtn.classList.toggle("is-active", this.isMuted);
    this.muteBtn.querySelector("span").textContent = this.isMuted ? "Unmute" : "Mute";
  }

  startTimer() {
    this.timerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - this.callStartTime) / 1000);
      this.timerEl.textContent = formatClock(elapsed);
    }, 1000);
  }

  setConnBadge(state, label) {
    this.connBadge.dataset.state = state;
    this.connLabel.textContent = label;
  }

  setAgentState(status) {
    const orbState = ORB_STATE_MAP[status] || "idle";
    this.appEl.dataset.agentState = orbState;
    const [title, sub] = AGENT_STATUS_COPY[status] || AGENT_STATUS_COPY.idle;
    this.agentStatusEl.textContent = title;
    this.agentSubstatusEl.textContent = sub;
  }

  handleDataChannelMessage(raw) {
    let data;
    try {
      data = JSON.parse(raw);
    } catch (e) {
      return;
    }

    switch (data.type) {
      case "call_started":
        this.sessionId = data.session_id;
        break;

      case "agent_status":
        this.setAgentState(data.status);
        break;

      case "user_speaking":
        break;

      case "transcript":
        this.upsertTranscriptMessage(data);
        break;

      case "tool_activity":
        this.upsertActivity(data);
        break;

      case "properties":
        this.renderProperties(data);
        break;

      case "booking":
        this.renderBooking(data.booking);
        break;

      case "summary":
        this.report = data.report;
        this.callUsage = data.usage_summary || this.callUsage;
        break;

      case "call_finalized":
        this.callUsage = data.usage_summary || this.callUsage;
        break;

      case "call_ended":
        break;

      case "error":
        console.warn("Agent error:", data.message);
        break;

      default:
        break;
    }
  }


  upsertTranscriptMessage({ id, role, text, final }) {
    this.transcriptEmpty.hidden = true;

    if (!final) {
      this.interimMessagesById.set(id, { role, text, timestamp: new Date() });
      return;
    }

    let row = this.transcriptById.get(id);
    if (!row) {
      row = document.createElement("div");
      row.className = `bubble-row role-${role}`;
      row.innerHTML = `
        <div class="bubble"></div>
        <div class="bubble-meta">${role === "user" ? "You" : "Nova"} · ${new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })}</div>
      `;
      this.transcriptEl.appendChild(row);
      this.transcriptById.set(id, row);
      this.transcriptOrder.push(id);
      this.interimMessagesById.delete(id);
    }

    const bubble = row.querySelector(".bubble");
    bubble.textContent = text;

    if (this.transcriptPanel) {
      this.transcriptPanel.scrollTop = this.transcriptPanel.scrollHeight;
    }
  }


  upsertActivity({ tool, label, status }) {
    this.activityEmpty.hidden = true;

    let item = this.activityEl.querySelector(`[data-tool-key="${tool}-pending"]`);

    if (status === "started") {
      item = document.createElement("div");
      item.className = "activity-item";
      item.dataset.status = "started";
      item.dataset.toolKeyPending = "";
      item.setAttribute("data-tool-key", `${tool}-pending`);
      item.innerHTML = `
        <span class="activity-icon">⋯</span>
        <div class="activity-text">
          <span class="activity-label">${escapeHtml(label)}</span>
          <span class="activity-time">${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
        </div>
      `;
      this.activityEl.appendChild(item);
      this.activityLog.push(label);
    } else if (item) {
      item.dataset.status = status;
      item.removeAttribute("data-tool-key");
      const icon = item.querySelector(".activity-icon");
      icon.textContent = status === "error" ? "!" : "✓";
      const labelEl = item.querySelector(".activity-label");
      labelEl.textContent = status === "error" ? `${label} — couldn't complete` : label.replace(/\.\.\.$/, "");
    } else {
      item = document.createElement("div");
      item.className = "activity-item";
      item.dataset.status = status;
      item.innerHTML = `
        <span class="activity-icon">${status === "error" ? "!" : "✓"}</span>
        <div class="activity-text">
          <span class="activity-label">${escapeHtml(label)}</span>
          <span class="activity-time">${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
        </div>
      `;
      this.activityEl.appendChild(item);
    }

    if (this.activityPanel) {
      this.activityPanel.scrollTop = this.activityPanel.scrollHeight;
    }
  }


  renderProperties({ source, properties, summary }) {
    if (!properties || !properties.length) return;

    const signature = `${source}:${properties.map((p) => p.property_id).sort().join(",")}`;
    if (signature === this._lastPropertiesSignature) return;
    this._lastPropertiesSignature = signature;

    const now = Date.now();
    properties.forEach((p) => {
      const existing = this.properties.get(p.property_id);
      this.properties.set(p.property_id, {
        ...(existing || {}),
        ...p,
        _firstSeenAt: existing?._firstSeenAt ?? now,
      });
    });

    this.propertiesCountBadge.hidden = false;
    this.propertiesCountBadge.textContent = this.properties.size;

    const propTab = document.querySelector('.tab[data-tab="properties"]');
    if (!document.getElementById("panel-properties").classList.contains("active")) {
      propTab.style.color = "var(--gold)";
      setTimeout(() => (propTab.style.color = ""), 2500);
    }

    if (source === "details" || source === "comparison") {
      this.renderPropertyChatCards(properties, summary);
    }
    if (source === "search") {
      this.renderTopMatchesInChat(properties);
    }

    this.rebuildPropertiesTab();
  }


  cityOf(p) {
    const candidates = [p.city, p.locality, p.location, p.area, p.address, p.postcode]
      .flatMap((value) => Array.isArray(value) ? value : [value])
      .map((value) => String(value || "").trim())
      .filter(Boolean);

    const selected = candidates.find((value) => value && !/^(unknown|location on request)$/i.test(value));
    if (!selected) return "Other areas";

    const normalized = selected
      .replace(/\s+,\s+/g, ", ")
      .replace(/\s+\|\s+/g, ", ")
      .replace(/\s*\(.*?\)\s*/g, "")
      .trim();

    const parts = normalized.split(/[,,/]/).map((part) => part.trim()).filter(Boolean);
    const finalCandidate = parts.length ? parts[parts.length - 1] : normalized;
    return finalCandidate || "Other areas";
  }

  sortedProperties(list) {
    const sorted = [...list];
    switch (this.propertiesSortKey) {
      case "recent":
        sorted.sort((a, b) => (b._firstSeenAt ?? 0) - (a._firstSeenAt ?? 0));
        break;
      case "price_low":
        sorted.sort((a, b) => (Number(a.price) || Infinity) - (Number(b.price) || Infinity));
        break;
      case "price_high":
        sorted.sort((a, b) => (Number(b.price) || -Infinity) - (Number(a.price) || -Infinity));
        break;
      case "bedrooms":
        sorted.sort((a, b) => (b.bedrooms ?? -1) - (a.bedrooms ?? -1));
        break;
      case "recommended":
      default:
        sorted.sort((a, b) => (b.match_score ?? -1) - (a.match_score ?? -1) || (a._firstSeenAt ?? 0) - (b._firstSeenAt ?? 0));
        break;
    }
    return sorted;
  }

  rebuildPropertiesTab() {
    if (!this.properties.size) {
      this.propertiesToolbar.hidden = true;
      return;
    }

    this.propertiesEmpty.hidden = true;
    this.propertiesToolbar.hidden = false;
    this.propertiesTotalEl.textContent = `${this.properties.size} propert${this.properties.size === 1 ? "y" : "ies"} found`;

    const groups = new Map();
    this.properties.forEach((p) => {
      const city = this.cityOf(p);
      if (!groups.has(city)) groups.set(city, []);
      groups.get(city).push(p);
    });

    this.propertiesEl.innerHTML = "";
    this.propertiesEl.appendChild(this.propertiesEmpty);

    groups.forEach((list, city) => {
      const group = document.createElement("div");
      group.className = "location-group";

      const header = document.createElement("div");
      header.className = "location-group-header";
      header.innerHTML = `
        <span class="location-group-name">${escapeHtml(city)}</span>
        <span class="location-group-count">${list.length}</span>
      `;
      group.appendChild(header);

      const grid = document.createElement("div");
      grid.className = "property-grid";
      this.sortedProperties(list).forEach((p) => grid.appendChild(this.buildPropertyCard(p)));
      group.appendChild(grid);

      this.propertiesEl.appendChild(group);
    });

    if (this.propertiesPanel) {
      this.propertiesPanel.scrollTop = this.propertiesPanel.scrollHeight;
    }
  }

  buildPropertyCard(p) {
    const card = document.createElement("div");
    card.className = "property-card";
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `Open details for ${p.title || "property"}`);

    const title = p.title || "Untitled property";
    const price = formatMoney(p.price);
    const location = p.location || p.city || "Location on request";
    const beds = p.bedrooms ?? "–";
    const baths = p.bathrooms ?? "–";
    const type = p.property_type ? p.property_type[0].toUpperCase() + p.property_type.slice(1) : null;
    const images = Array.isArray(p.image_urls) ? p.image_urls.filter(Boolean) : [];
    const firstImage = p.image_url || images[0] || null;

    const media = document.createElement("div");
    media.className = "property-media";

    if (firstImage) {
      const img = document.createElement("img");
      img.src = firstImage;
      img.alt = title;
      img.loading = "lazy";
      media.appendChild(img);
    } else {
      media.textContent = "🏡";
    }

    if (typeof p.match_score === "number") {
      const badge = document.createElement("span");
      badge.className = "property-match-badge";
      badge.textContent = `${Math.round(p.match_score * 100)}% match`;
      media.appendChild(badge);
    }

    const body = document.createElement("div");
    body.className = "property-body";
    body.innerHTML = `
      <div class="property-top">
        <span class="property-title">${escapeHtml(title)}</span>
        <span class="property-price">${escapeHtml(price)}</span>
      </div>
      <span class="property-location">📍 ${escapeHtml(location)}</span>
      <div class="property-specs">
        <span>🛏️ ${escapeHtml(String(beds))} bed</span>
        <span>🚿 ${escapeHtml(String(baths))} bath</span>
        ${type ? `<span>${escapeHtml(type)}</span>` : ""}
      </div>
      ${
        Array.isArray(p.highlights) && p.highlights.length
          ? `<ul class="property-why">${p.highlights
              .slice(0, 3)
              .map((h) => `<li>${escapeHtml(h)}</li>`)
              .join("")}</ul>`
          : p.description
          ? `<p class="property-desc">${escapeHtml(p.description)}</p>`
          : ""
      }
      <div class="property-actions">
        <button type="button" class="btn-view-details">View property</button>
      </div>
    `;

    const actionBtn = body.querySelector(".btn-view-details");
    const openDetails = (event) => {
      if (event && event.target.closest("a,button") && event.target !== actionBtn) return;
      this.openPropertyModal(p);
    };

    card.addEventListener("click", openDetails);
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        this.openPropertyModal(p);
      }
    });
    actionBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      this.openPropertyModal(p);
    });

    card.appendChild(media);
    card.appendChild(body);
    return card;
  }

  normalizePropertyImages(property) {
    const list = [];
    const raw = Array.isArray(property?.image_urls) ? property.image_urls : [];
    raw.forEach((url) => {
      if (typeof url === "string" && url.trim()) list.push(url.trim());
    });
    if (property?.image_url && !list.includes(property.image_url)) list.unshift(property.image_url);
    return list.length ? list : ["https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80"];
  }

  openPropertyModal(property) {
    if (!property) return;

    const images = this.normalizePropertyImages(property);
    const title = property.title || "Untitled property";
    const price = formatMoney(property.price);
    const location = property.location || property.city || "Location on request";
    const type = property.property_type || "property";

    this.propertyModalTitle.textContent = title;
    this.propertyModalLocation.textContent = location;
    this.modalExternalLink.href = property.property_url || "#";
    this.modalExternalLink.setAttribute("aria-disabled", property.property_url ? "false" : "true");
    this.modalExternalLink.style.pointerEvents = property.property_url ? "auto" : "none";
    this.modalExternalLink.style.opacity = property.property_url ? "1" : "0.5";

    this.propertyModalBody.innerHTML = "";

    const gallery = document.createElement("div");
    gallery.className = "modal-gallery-wrap";

    const mainWrap = document.createElement("div");
    mainWrap.className = "modal-gallery-main-wrap";

    const mainImg = document.createElement("img");
    mainImg.className = "modal-gallery-main";
    mainImg.src = images[0];
    mainImg.alt = title;
    mainImg.loading = "eager";

    const prevBtn = document.createElement("button");
    prevBtn.type = "button";
    prevBtn.className = "modal-gallery-nav nav-prev";
    prevBtn.textContent = "‹";
    prevBtn.setAttribute("aria-label", "Previous photo");

    const nextBtn = document.createElement("button");
    nextBtn.type = "button";
    nextBtn.className = "modal-gallery-nav nav-next";
    nextBtn.textContent = "›";
    nextBtn.setAttribute("aria-label", "Next photo");

    const counter = document.createElement("span");
    counter.className = "modal-gallery-counter";
    counter.textContent = `1 / ${images.length}`;

    let currentIndex = 0;
    const setImage = (index) => {
      currentIndex = (index + images.length) % images.length;
      mainImg.src = images[currentIndex];
      counter.textContent = `${currentIndex + 1} / ${images.length}`;
      thumbs.forEach((thumb, thumbIndex) => thumb.classList.toggle("active", thumbIndex === currentIndex));
    };

    prevBtn.addEventListener("click", () => setImage(currentIndex - 1));
    nextBtn.addEventListener("click", () => setImage(currentIndex + 1));
    mainWrap.appendChild(mainImg);
    mainWrap.appendChild(prevBtn);
    mainWrap.appendChild(nextBtn);
    mainWrap.appendChild(counter);
    gallery.appendChild(mainWrap);

    const thumbs = [];
    if (images.length > 1) {
      const thumbStrip = document.createElement("div");
      thumbStrip.className = "modal-gallery-thumbs";
      images.forEach((src, index) => {
        const thumb = document.createElement("img");
        thumb.className = "modal-gallery-thumb" + (index === 0 ? " active" : "");
        thumb.src = src;
        thumb.alt = `${title} photo ${index + 1}`;
        thumb.loading = "lazy";
        thumb.addEventListener("click", () => setImage(index));
        thumbs.push(thumb);
        thumbStrip.appendChild(thumb);
      });
      gallery.appendChild(thumbStrip);
    }

    const details = document.createElement("div");
    details.className = "property-modal-details";

    const specsGrid = document.createElement("div");
    specsGrid.className = "property-modal-specs";
    const specs = [
      ["Price", price],
      ["Type", String(type).replace(/^\w/, (char) => char.toUpperCase())],
      ["Bedrooms", property.bedrooms != null ? `${property.bedrooms}` : "—"],
      ["Bathrooms", property.bathrooms != null ? `${property.bathrooms}` : "—"],
      ["Status", property.status || "Available"],
      ["Area", this.cityOf(property)],
    ];
    specs.forEach(([label, value]) => {
      const item = document.createElement("div");
      item.className = "property-modal-spec";
      item.innerHTML = `<span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>`;
      specsGrid.appendChild(item);
    });

    const summary = document.createElement("div");
    summary.className = "property-modal-summary";
    const description = property.description || property.summary || "This home is a strong fit for the buyer's brief and is ready for a more detailed view.";
    summary.innerHTML = `<h3>Property Overview</h3><p>${escapeHtml(description)}</p>`;

    const featureList = document.createElement("div");
    featureList.className = "property-modal-features";
    const highlights = Array.isArray(property.highlights) ? property.highlights : [];
    const featureItems = [...highlights.slice(0, 6), property.tenure, property.garden, property.parking, property.balcony]
      .filter(Boolean)
      .map((item) => `<li>${escapeHtml(String(item))}</li>`)
      .join("");
    if (featureItems) {
      featureList.innerHTML = `<h3>Key features</h3><ul>${featureItems}</ul>`;
    }

    details.appendChild(specsGrid);
    details.appendChild(summary);
    if (featureItems) details.appendChild(featureList);

    this.propertyModalBody.appendChild(gallery);
    this.propertyModalBody.appendChild(details);
    this.propertyModalOverlay.hidden = false;
  }

  closePropertyModal() {
    this.propertyModalOverlay.hidden = true;
  }

   
  renderTopMatchesInChat(properties) {
    this.transcriptEmpty.hidden = true;

    const hasScores = properties.some((p) => typeof p.match_score === "number");
    const top = (hasScores ? [...properties].sort((a, b) => (b.match_score ?? 0) - (a.match_score ?? 0)) : properties).slice(0, 3);

    if (!top.length) return;

    const totalFound = this.properties.size || properties.length;
    const row = document.createElement("div");
    row.className = "bubble-row role-assistant row-recommendations";

    const intro = document.createElement("div");
    intro.className = "bubble";
    intro.textContent = `I found ${totalFound} properties that fit what you're looking for. These are the three I'd start with.`;
    row.appendChild(intro);

    const topGrid = document.createElement("div");
    topGrid.className = "top3-cards-grid";
    top.forEach((p) => topGrid.appendChild(this.buildTopRecommendationCard(p)));
    row.appendChild(topGrid);

    const viewAllWrap = document.createElement("div");
    viewAllWrap.className = "view-all-properties-bar";
    const viewAllBtn = document.createElement("button");
    viewAllBtn.type = "button";
    viewAllBtn.className = "view-all-properties-btn";
    viewAllBtn.textContent = `View all ${totalFound} properties →`;
    viewAllBtn.addEventListener("click", () => this.switchTab("properties"));
    viewAllWrap.appendChild(viewAllBtn);
    row.appendChild(viewAllWrap);

    const meta = document.createElement("div");
    meta.className = "bubble-meta";
    meta.textContent = `Nova · ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
    row.appendChild(meta);

    this.transcriptEl.appendChild(row);

    if (this.transcriptPanel) {
      this.transcriptPanel.scrollTop = this.transcriptPanel.scrollHeight;
    }
  }

  buildTopRecommendationCard(p) {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "top3-card";

    const title = p.title || "Untitled property";
    const price = formatMoney(p.price);
    const location = p.location || p.city || "Location on request";
    const specs = [
      p.bedrooms != null ? `${p.bedrooms} bed` : null,
      p.bathrooms != null ? `${p.bathrooms} bath` : null,
      p.property_type || null,
    ].filter(Boolean).join(" · ");
    const image = p.image_url || (Array.isArray(p.image_urls) ? p.image_urls.find(Boolean) : null);
    const highlights = Array.isArray(p.highlights) ? p.highlights.slice(0, 2) : [];

    const mediaWrap = document.createElement("div");
    mediaWrap.className = "top3-card-media";
    if (image) {
      const img = document.createElement("img");
      img.src = image;
      img.alt = title;
      img.loading = "lazy";
      mediaWrap.appendChild(img);
    }
    const badge = document.createElement("span");
    badge.className = "top3-match-tag";
    badge.textContent = typeof p.match_score === "number" ? `${Math.round(p.match_score * 100)}% match` : "Featured";
    mediaWrap.appendChild(badge);
    card.appendChild(mediaWrap);

    const body = document.createElement("div");
    body.className = "top3-card-body";
    body.innerHTML = `
      <span class="top3-price">${escapeHtml(price)}</span>
      <span class="top3-title">${escapeHtml(title)}</span>
      <span class="top3-specs">${escapeHtml(specs)}</span>
      <span class="top3-location">${escapeHtml(location)}</span>
      ${highlights.length ? `<span class="top3-highlights">${escapeHtml(highlights.join(" · "))}</span>` : ""}
      <span class="top3-action-link">View property →</span>
    `;
    card.appendChild(body);

    card.addEventListener("click", () => this.openPropertyModal(p));
    return card;
  }

  /**
   * Builds a small self-contained gallery: a main image plus a thumbnail
   * strip. Clicking a thumbnail (or the prev/next arrows) swaps the main
   * image. No external state - everything lives on the returned element.
   */
  buildImageGallery(images, altText) {
    const wrap = document.createElement("div");
    wrap.className = "gallery";

    let index = 0;

    const main = document.createElement("img");
    main.className = "gallery-main";
    main.src = images[0];
    main.alt = altText || "Property photo";
    main.loading = "lazy";

    const counter = document.createElement("span");
    counter.className = "gallery-counter";

    const updateCounter = () => {
      counter.textContent = `${index + 1} / ${images.length}`;
    };

    const setIndex = (newIndex) => {
      index = (newIndex + images.length) % images.length;
      main.src = images[index];
      updateCounter();
      thumbs.forEach((t, i) => t.classList.toggle("active", i === index));
    };

    wrap.appendChild(main);

    if (images.length > 1) {
      const prevBtn = document.createElement("button");
      prevBtn.type = "button";
      prevBtn.className = "gallery-nav gallery-nav--prev";
      prevBtn.setAttribute("aria-label", "Previous photo");
      prevBtn.textContent = "‹";
      prevBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        setIndex(index - 1);
      });

      const nextBtn = document.createElement("button");
      nextBtn.type = "button";
      nextBtn.className = "gallery-nav gallery-nav--next";
      nextBtn.setAttribute("aria-label", "Next photo");
      nextBtn.textContent = "›";
      nextBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        setIndex(index + 1);
      });

      wrap.appendChild(prevBtn);
      wrap.appendChild(nextBtn);
      wrap.appendChild(counter);
    }

    const thumbs = [];

    if (images.length > 1) {
      const strip = document.createElement("div");
      strip.className = "gallery-thumbs";

      images.forEach((src, i) => {
        const thumb = document.createElement("img");
        thumb.className = "gallery-thumb" + (i === 0 ? " active" : "");
        thumb.src = src;
        thumb.loading = "lazy";
        thumb.alt = `${altText || "Property"} photo ${i + 1}`;
        thumb.addEventListener("click", (e) => {
          e.stopPropagation();
          setIndex(i);
        });
        thumbs.push(thumb);
        strip.appendChild(thumb);
      });

      wrap.appendChild(strip);
    }

    updateCounter();
    return wrap;
  }

  renderPropertyChatCards(properties, summary) {
    this.transcriptEmpty.hidden = true;

    const timeNow = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });


    if (summary && properties.length > 1) {
      const summaryRow = document.createElement("div");
      summaryRow.className = "bubble-row role-assistant";
      summaryRow.innerHTML = `
        <div class="bubble">${escapeHtml(summary)}</div>
        <div class="bubble-meta">Nova · ${timeNow()}</div>
      `;
      this.transcriptEl.appendChild(summaryRow);
    }

    properties.forEach((p) => {
      const images = Array.isArray(p.image_urls) && p.image_urls.length
        ? p.image_urls.filter(Boolean)
        : (p.image_url ? [p.image_url] : []);

      const title = p.title || "Untitled property";
      const price = formatMoney(p.price);
      const specs = [
        p.bedrooms != null ? `${p.bedrooms} bed` : null,
        p.bathrooms != null ? `${p.bathrooms} bath` : null,
      ]
        .filter(Boolean)
        .join(" · ");
      const url = p.property_url || "#";

      const row = document.createElement("div");
      row.className = "bubble-row role-assistant row-property";

      const card = document.createElement("div");
      card.className = "property-chat-card";

      const header = document.createElement("div");
      header.className = "property-chat-header";
      header.innerHTML = `
        <span class="property-chat-title">${escapeHtml(title)}</span>
        <span class="property-chat-meta">${escapeHtml(price)}${specs ? " · " + escapeHtml(specs) : ""}</span>
      `;
      card.appendChild(header);

      if (images.length) {
        const imgWrap = document.createElement("div");
        imgWrap.className = "property-chat-images" + (images.length === 1 ? " single" : "");
        images.forEach((src) => {
          const img = document.createElement("img");
          img.src = src;
          img.alt = title;
          img.loading = "lazy";
          imgWrap.appendChild(img);
        });
        card.appendChild(imgWrap);
      }

      const link = document.createElement("a");
      link.className = "property-chat-link";
      link.href = url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "Visit property page →";
      card.appendChild(link);

      row.appendChild(card);

      const meta = document.createElement("div");
      meta.className = "bubble-meta";
      meta.textContent = `Nova · ${timeNow()}`;
      row.appendChild(meta);

      this.transcriptEl.appendChild(row);
    });

    if (this.transcriptPanel) {
      this.transcriptPanel.scrollTop = this.transcriptPanel.scrollHeight;
    }
  }


  renderBooking(booking) {
    if (!booking) return;
    this.booking = booking;

    const prop = this.properties.get(booking.property_id);
    const propTitle = prop ? prop.title : `Property ${booking.property_id}`;
    const status = booking.success === false ? "failed" : "confirmed";
    const statusLabel = status === "confirmed" ? "Confirmed" : "Couldn't confirm";

    this.bookingCard.hidden = false;
    this.bookingCard.innerHTML = `
      <span class="booking-title"> Viewing scheduled</span>
      <span class="booking-main">${escapeHtml(propTitle)}</span>
      <span class="booking-meta">
        <span>${escapeHtml(formatDateTime(booking.scheduled_datetime))}</span>
        ${booking.viewing_id ? `<span>Ref ${escapeHtml(booking.viewing_id).slice(0, 8)}</span>` : ""}
      </span>
      <span class="booking-status" data-status="${status}">${statusLabel}</span>
    `;
  }



  showSummaryOverlay(durationSeconds, hadReport) {
    this.summaryDuration.textContent = `Duration — ${formatClock(durationSeconds)}`;

    const sections = [];
    const report = this.report;

    if (report?.preferences) {
      const prefs = report.preferences;
      const chips = [
        prefs.city,
        prefs.property_type,
        prefs.listing_type,
        prefs.bedrooms ? `${prefs.bedrooms} bed` : null,
        prefs.max_budget ? `Up to ${formatMoney(prefs.max_budget)}` : null,
      ].filter(Boolean);

      if (chips.length) {
        sections.push(`
          <div class="summary-section">
            <h3>Requirements collected</h3>
            <div class="summary-chips">
              ${chips.map((c) => `<span class="summary-chip">${escapeHtml(String(c))}</span>`).join("")}
            </div>
          </div>
        `);
      }
    }

    if (this.properties.size) {
      const names = Array.from(this.properties.values())
        .map((p) => p.title)
        .filter(Boolean);
      sections.push(`
        <div class="summary-section">
          <h3>Properties discussed (${this.properties.size})</h3>
          <ul>${names.map((n) => `<li>${escapeHtml(n)}</li>`).join("")}</ul>
        </div>
      `);
    }

    if (this.booking) {
      sections.push(`
        <div class="summary-section">
          <h3>Viewing scheduled</h3>
          <p>${escapeHtml(formatDateTime(this.booking.scheduled_datetime))}${
        this.booking.success === false ? " — could not be confirmed" : ""
      }</p>
        </div>
      `);
    }

    if (this.callUsage) {
      const llmUsage = this.callUsage.llm?.[0];
      const sttUsage = this.callUsage.stt?.[0];
      const ttsUsage = this.callUsage.tts?.[0];

      const usageText = [];
      if (llmUsage) {
        usageText.push(`<div class="summary-section"><h3>AI / LLM usage</h3><p>${escapeHtml(llmUsage.provider)} ${escapeHtml(llmUsage.model || "")}: input ${Number(llmUsage.input_tokens || 0).toLocaleString()} · output ${Number(llmUsage.output_tokens || 0).toLocaleString()} · total ${Number(llmUsage.total_tokens || 0).toLocaleString()}</p></div>`);
      }
      if (sttUsage) {
        usageText.push(`<div class="summary-section"><h3>Speech-to-text</h3><p>${escapeHtml(sttUsage.provider)} · ${sttUsage.usage_source === "actual" ? "actual" : "estimated"} audio: ${sttUsage.audio_seconds ? `${Number(sttUsage.audio_seconds).toLocaleString()} sec` : "unavailable"}</p></div>`);
      }
      if (ttsUsage) {
        usageText.push(`<div class="summary-section"><h3>Text-to-speech</h3><p>${escapeHtml(ttsUsage.provider)} · ${Number(ttsUsage.characters || 0).toLocaleString()} characters · ${escapeHtml(ttsUsage.model || "")}</p></div>`);
      }
      if (usageText.length) sections.push(...usageText);
    }

    if (report?.insights?.summary) {
      sections.push(`
        <div class="summary-section">
          <h3>Summary</h3>
          <p>${escapeHtml(report.insights.summary)}</p>
        </div>
      `);
    }

    if (report?.insights?.recommended_next_action) {
      sections.push(`
        <div class="summary-section">
          <h3>Next action</h3>
          <p>${escapeHtml(report.insights.recommended_next_action)}</p>
        </div>
      `);
    }

    if (!sections.length) {
      sections.push(`
        <div class="summary-section">
          <p>No structured summary was generated for this call. The transcript is still available in the Transcript tab.</p>
        </div>
      `);
    }

    this.summaryBody.innerHTML = sections.join("");
    this.summaryOverlay.hidden = false;
  }

  downloadSummary() {
    const payload = {
      session_id: this.sessionId,
      report: this.report,
      properties: Array.from(this.properties.values()),
      booking: this.booking,
      transcript: this.transcriptOrder.map((id) => {
        const row = this.transcriptById.get(id);
        return {
          role: row.classList.contains("role-user") ? "user" : "assistant",
          text: row.querySelector(".bubble")?.textContent || "",
        };
      }),
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `nova-call-summary-${this.sessionId || Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new VoiceAgent();
});

export default VoiceAgent;
