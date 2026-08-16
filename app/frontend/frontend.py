import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Real Estate Voice Agent", page_icon="🎙️", layout="centered"
)

st.title("🎙️ Real Estate Voice Agent")
st.caption("Real-Time WebRTC Assistant Powered by Pipecat AI")

webrtc_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #f9f9fb;
            margin: 0;
            padding: 20px;
        }
        .card {
            background: #ffffff;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            text-align: center;
            width: 100%;
            max-width: 440px;
            box-sizing: border-box;
        }
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            background: #e9ecef;
            color: #495057;
            margin-bottom: 20px;
        }
        .status-badge.connected { background: #d4edda; color: #155724; }
        .status-badge.connecting { background: #fff3cd; color: #856404; }

        button {
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 14px 24px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: background 0.2s;
            width: 100%;
        }
        button:hover { background-color: #e03e3e; }
        button.active { background-color: #212529; }
        button:disabled { background-color: #cccccc; cursor: not-allowed; }

        #logConsole {
            margin-top: 15px;
            padding: 10px;
            background: #1e1e1e;
            color: #4af626;
            font-family: monospace;
            font-size: 11px;
            border-radius: 8px;
            text-align: left;
            max-height: 140px;
            overflow-y: auto;
            width: 100%;
            box-sizing: border-box;
            white-space: pre-wrap;
            word-break: break-word;
        }
        audio { display: none; }
    </style>
</head>
<body>
    <div class="card">
        <div id="statusBadge" class="status-badge">Disconnected</div>
        <button id="callBtn">Start Conversation</button>
        <div id="logConsole">> Ready to connect...</div>
        <audio id="botAudio" autoplay></audio>
    </div>

    <script>
        const callBtn = document.getElementById("callBtn");
        const statusBadge = document.getElementById("statusBadge");
        const logConsole = document.getElementById("logConsole");
        const botAudio = document.getElementById("botAudio");

        let pc = null;
        let dc = null;
        let localStream = null;

        function log(msg) {
            console.log("[Pipecat]", msg);
            logConsole.innerHTML += "<br>> " + msg;
            logConsole.scrollTop = logConsole.scrollHeight;
        }

        callBtn.onclick = async () => {
            if (pc) {
                stopCall();
                return;
            }

            try {
                callBtn.disabled = true;
                statusBadge.innerText = "Connecting...";
                statusBadge.className = "status-badge connecting";

                // 1. Get Microphone stream
                localStream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    }
                });

                const audioTrack = localStream.getAudioTracks()[0];
                log(`🎤 Device Label: ${audioTrack.label}`);

                // Warning check for Stereo Mix
                if (audioTrack.label.toLowerCase().includes("stereo mix")) {
                    log("⚠️ WARNING: Stereo Mix selected! Switch browser mic to your real microphone!");
                }

                // 2. Setup WebRTC PeerConnection
                pc = new RTCPeerConnection({
                    iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
                });

                // ✅ FIX: Explicitly create 'rtvi-ai' Data Channel expected by Pipecat SmallWebRTC
                dc = pc.createDataChannel("rtvi-ai", { ordered: true });
                dc.onopen = () => log("⚡ RTVI Data Channel OPENED!");
                dc.onmessage = (e) => {
                    if (!e.data.includes('"type":"metrics"')) {
                        log(`[RTVI]: ${e.data}`);
                    }
                };

                // Add microphone track
                localStream.getTracks().forEach(track => pc.addTrack(track, localStream));

                // Bot audio track listener
                pc.ontrack = (event) => {
                    log("🔊 Bot Audio Stream Received!");
                    botAudio.srcObject = event.streams[0];
                };

                // ICE connection state
                pc.oniceconnectionstatechange = () => {
                    log(`🌐 ICE State: ${pc.iceConnectionState}`);
                    if (pc.iceConnectionState === "failed" || pc.iceConnectionState === "disconnected") {
                        stopCall();
                    }
                };

                // 3. Create Offer
                const offer = await pc.createOffer();
                await pc.setLocalDescription(offer);

                // Wait for ICE gathering
                if (pc.iceGatheringState !== "complete") {
                    log("⏳ Waiting for ICE candidates...");
                    await new Promise((resolve) => {
                        const checkIce = () => {
                            if (pc.iceGatheringState === "complete") {
                                pc.removeEventListener("icegatheringstatechange", checkIce);
                                resolve();
                            }
                        };
                        pc.addEventListener("icegatheringstatechange", checkIce);
                    });
                }
                log("🌐 ICE Gathering complete.");

                // 4. Send Offer to Backend
                log("📤 Sending WebRTC offer to backend...");
                const response = await fetch("http://localhost:7860/offer", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ sdp: pc.localDescription.sdp, type: pc.localDescription.type })
                });

                if (!response.ok) throw new Error("Backend HTTP error " + response.status);

                const answer = await response.json();
                log("📥 SDP Answer received.");
                await pc.setRemoteDescription(new RTCSessionDescription(answer));

                statusBadge.innerText = "🟢 Live - Speak Now!";
                statusBadge.className = "status-badge connected";
                callBtn.innerText = "End Conversation";
                callBtn.classList.add("active");
                callBtn.disabled = false;
                log("🟢 Connected! Speak into your physical microphone.");

            } catch (err) {
                log("❌ ERROR: " + err.message);
                stopCall();
            }
        };

        function stopCall() {
            if (dc) { dc.close(); dc = null; }
            if (pc) { pc.close(); pc = null; }
            if (localStream) {
                localStream.getTracks().forEach(track => track.stop());
                localStream = null;
            }
            botAudio.srcObject = null;
            callBtn.innerText = "Start Conversation";
            callBtn.classList.remove("active");
            callBtn.disabled = false;
            statusBadge.innerText = "Disconnected";
            statusBadge.className = "status-badge";
            log("Session stopped.");
        }
    </script>
</body>
</html>
"""

components.html(webrtc_html, height=420)